# -*- coding: utf-8 -*-
"""
Created on 2022-07-25

@author: MichaelEK
"""
import pandas as pd
import numpy as np
from hilltoppy.utils import convert_value, DataSource, Measurement, get_hilltop_xml, convert_mowsecs, build_url
from hilltoppy import web_service as ws
from typing import List, Optional, Union
import orjson

############################################
### Parameters



########################################
### Class


class Hilltop(object):
    """

    """
    def __init__(self, base_url: str, hts: str, timeout: int = 60, **kwargs):
        """
        Base Hilltop class.

        Parameters
        ----------
        base_url : str
            Root Hilltop url.
        hts : str
            hts file name including the .hts extension.
        timeout : int
            The http request timeout length in seconds.
        **kwargs
            Optional keyword arguments passed to requests.

        """
        self.timeout = timeout
        self.base_url = base_url
        self.hts = hts
        self._measurements = {}
        self._requests_kwargs = kwargs

        ## Test out Hilltop url
        sites = self.get_site_list()

        if sites.empty:
            raise ValueError('No sites found for the base_url and hts combo.')

        sites = sites['SiteName'].tolist()

        self.available_sites = sites


    def get_site_list(self, location: Union[str, bool] = None, measurement: str = None, collection: str = None, site_parameters: List[str] = None):
        """
        SiteList request function. Returns a list of sites associated with the hts file.

        Parameters
        ----------
        location : str, bool, or None
            Should the location be returned? Only applies to the SiteList request. 'Yes' returns the Easting and Northing, while 'LatLong' returns NZGD2000 lat lon coordinates.
        measurement : str or None
            The measurement name.
        collection : str or None
            Get site list via a collection.
        site_parameters : list or None
            A list of the site parameters to be returned with the SiteList request. Make a call to site_info to find all of the possible options.

        Returns
        -------
        DataFrame
        """
        url = build_url(self.base_url, self.hts, 'SiteList', location=location, measurement=measurement, collection=collection, site_parameters=site_parameters)
        tree1 = get_hilltop_xml(url, timeout=self.timeout, **self._requests_kwargs)

        site_tree = tree1.findall('Site')

        if site_tree:
            sites_list = []
            for s in site_tree:
                name = s.attrib['Name']
                site_dict = {'SiteName': name}
                for data in s:
                    site_dict[data.tag] = convert_value(data.text)
                sites_list.append(site_dict)

            sites_df = pd.DataFrame(sites_list)
        else:
            sites_df = pd.DataFrame(columns=['SiteName'])

        return sites_df


    def get_measurement_names(self, detailed=False):
        """
        Method to get all of the available Measurement Names in the hts. When detailed=False, then the request is relatively fast but only returns the names. When detailed=True, the method runs through as many sites as necessary to get additional data about the Measurements.

        Parameters
        ----------
        detailed : bool
            If True, the method runs through as many sites as necessary to get additional data about the Measurements. It may take several minutes to run this query.

        Returns
        -------
        DataFrame
        """
        if detailed:
            cols = ['DataSourceName', 'MeasurementName', 'Units', 'Precision', 'Item', 'TSType', 'DataType', 'Interpolation']
        else:
            cols = ['MeasurementName']

        url = build_url(self.base_url, self.hts, 'MeasurementList')
        tree1 = get_hilltop_xml(url, timeout=self.timeout, **self._requests_kwargs)

        if tree1.find('Error') is not None:
            raise ValueError(tree1.find('Error').text)
        meas1 = tree1.findall('Measurement')

        if meas1:
            meas_list = []
            m_names = set()
            for m in meas1:
                m_name = m.attrib['Name']
                if detailed:
                    if m_name.lower() not in m_names:
                        sites = self.get_site_list(measurement=m_name)['SiteName'].tolist()

                        if sites:
                            mtypes = self.get_measurement_list(sites[0])
                            m_cols = mtypes.columns
                            new_cols = m_cols[m_cols.isin(cols)]
                            mtypes = mtypes[new_cols].drop_duplicates('MeasurementName').set_index('MeasurementName').reset_index()
                            m_names.update(set(mtypes['MeasurementName'].str.lower().tolist()))
                            meas_list.append(mtypes)
                else:
                    meas_list.append(pd.DataFrame([m_name], columns=cols))

            meas_df = pd.concat(meas_list).drop_duplicates('MeasurementName')
        else:
            meas_df = pd.DataFrame(columns=cols)

        return meas_df


    def _get_site_info_single(self, site):
        """
        SiteInfo request function. Returns all of the site data for a specific site. The Hilltop sites table has tons of fields, so you never know what you're going to get.

        Parameters
        ----------
        site : str
            The site to be extracted.

        Returns
        -------
        DataFrame
        """
        ### Check if site exists in hts
        if site not in self.available_sites:
            raise ValueError('Requested site is not in hts file.')

        url = build_url(self.base_url, self.hts, 'SiteInfo', site=site)
        tree1 = get_hilltop_xml(url, timeout=self.timeout, **self._requests_kwargs)

        site_tree = tree1.find('Site')

        if site_tree is not None:
            data_dict = {'SiteName': site}
            for data in site_tree:
                key = data.tag
                if data.text is not None:
                    val = convert_value(data.text)

                    data_dict[key] = val

            site_df = pd.DataFrame([data_dict])
        else:
            site_df = pd.DataFrame(columns=['SiteName'])

        return site_df


    def get_site_info(self, sites: Union[str, List[str]] = None):
        """
        SiteInfo request function. Returns all of the site data for a specific site. The Hilltop sites table has tons of fields, so you never know what you're going to get.

        Parameters
        ----------
        sites : str, list of str, or None
            The site(s) to get the site info. You can pass a single site as a string, a list of sites, or None to get the site info for all available sites in the hts file.

        Returns
        -------
        DataFrame
        """
        if isinstance(sites, str):
            sites_df = self._get_site_info_single(sites)
        else:
            if sites is None:
                sites = self.available_sites.copy()

            sites_df_list = []
            for site in sites:
                sites_df0 = self._get_site_info_single(site)
                sites_df_list.append(sites_df0)
            sites_df = pd.concat(sites_df_list)

        return sites_df


    def get_collection_list(self):
        """
        CollectionList request method. Returns a dataframe of collection and site names associated with the hts file.

        Returns
        -------
        DataFrame
        """
        url = build_url(self.base_url, self.hts, 'CollectionList')
        tree1 = get_hilltop_xml(url, timeout=self.timeout, **self._requests_kwargs)

        collection_tree = tree1.findall('Collection')

        if collection_tree:
            collection_list = []
            for colitem in collection_tree:
                colname = colitem.attrib['Name']
                data_list = []
                for site in colitem:
                    row = dict([(col.tag, col.text.encode('ascii', 'ignore').decode()) for col in site if col.text is not None])
                    # if 'Measurement' in row:
                    #     row['Measurement'] = row['Measurement'].lower()
                    data_list.append(row)
                col_df = pd.DataFrame(data_list)
                col_df['CollectionName'] = colname
                collection_list.append(col_df)
            collection_df = pd.concat(collection_list).reset_index(drop=True).rename(columns={'Measurement': 'MeasurementName', 'Filename': 'FileName'})
        else:
            collection_df = pd.DataFrame(columns=['SiteName', 'MeasurementName', 'CollectionName', 'FileName'])

        return collection_df


    def _get_measurement_list_single(self, site, measurement=None):
        """
        Method to query a Hilltop server for the measurement summary of a site.

        Parameters
        ----------
        site : str or None
            The site to be extracted.
        measurement : str or None
            The measurement name.

        Returns
        -------
        DataFrame
        """
        ### Check if site exists in hts
        if site not in self.available_sites:
            raise ValueError('Requested site is not in hts file.')

        ### Make url
        url = build_url(self.base_url, self.hts, 'MeasurementList', site, measurement)

        ### Request data and load in xml
        tree1 = get_hilltop_xml(url, timeout=self.timeout, **self._requests_kwargs)

        if tree1.find('Error') is not None:
            return pd.DataFrame(columns=['SiteName', 'MeasurementName'])

        data_sources = tree1.findall('DataSource')

        ### Extract data into list of dict - to represent the Hilltop structure
        if site not in self._measurements:
            self._measurements[site] = {}

        data_list = []

        if data_sources:
            for d in data_sources:
                ds_dict = {c.tag: c.text.encode('ascii', 'ignore').decode() for c in d if c.text is not None}
                if 'DataType' in ds_dict:
                    if not ds_dict['DataType'] in ['HydSection', 'HydFacecard']:
                        ds_dict['SiteName'] = site
                        ds_dict['DataSourceName'] = d.attrib['Name']
                        try:
                            ds_dict1 = orjson.loads(DataSource(**ds_dict).json(exclude_none=True))

                            m_all = d.findall('Measurement')
                            for m in m_all:
                                m_dict = {c.tag: convert_value(c.text) for c in m}

                                if 'Format' in m_dict:
                                    f_text_list = m_dict['Format'].split('.')
                                    if len(f_text_list) == 2:
                                        precision = len(f_text_list[1])
                                    else:
                                        precision = 0
                                else:
                                    precision = 0

                                m_dict['Precision'] = precision

                                m_dict['MeasurementName'] = m_dict.pop('RequestAs')

                                m_dict1 = orjson.loads(Measurement(**m_dict).json(exclude_none=True))
                                m_dict1.update(ds_dict1)

                                self._measurements[site][m_dict['MeasurementName'].lower()] = m_dict1

                                data_list.append(m_dict1)
                        except:
                            pass

        ## Convert output
        if data_list:
            output1 = pd.DataFrame(data_list)

            output1['From'] = pd.to_datetime(output1['From'])
            output1['To'] = pd.to_datetime(output1['To'])

            if 'VMStart' in output1:
                output1['VMStart'] = pd.to_datetime(output1['VMStart'])
            if 'VMFinish' in output1:
                output1['VMFinish'] = pd.to_datetime(output1['VMFinish'])

            output1 = output1.set_index(['SiteName', 'MeasurementName']).reset_index()

            if isinstance(measurement, str):
                output1 = output1[output1['MeasurementName'].str.lower() == measurement.lower()].copy()
        else:
            output1 = pd.DataFrame(columns=['SiteName', 'MeasurementName'])

        return output1


    def get_measurement_list(self, sites: Union[str, List[str]] = None, measurement: str = None):
        """
        Method to query a Hilltop server for the measurement summary of a site or sites.

        Parameters
        ----------
        sites : str, list of str, or None
            The site(s) to get the measurements. You can pass a single site as a string, a list of sites, or None to get the measurements for all available sites in the hts file.
        measurement : str or None
            The measurement name to filter the sites by.

        Returns
        -------
        DataFrame
        """
        if isinstance(sites, str):
            m_df = self._get_measurement_list_single(sites, measurement=measurement)
        else:
            if sites is None:
                if isinstance(measurement, str):
                    sites = self.get_site_list(measurement=measurement)['SiteName'].tolist()
                else:
                    sites = self.available_sites.copy()

            m_df_list = []
            for site in sites:
                m_df0 = self._get_measurement_list_single(site, measurement=measurement)
                m_df_list.append(m_df0)

            m_df = pd.concat(m_df_list)

        return m_df


    def _get_data_single(self, site, measurement, from_date=None, to_date=None, agg_method=None, agg_interval=None, alignment='00:00', quality_codes=False, apply_precision=False, tstype=None):
        """
        Method to query a Hilltop web server for time series data associated with a Site and Measurement.

        Parameters
        ----------
        site : str or None
            The site to be extracted.
        measurement : str or None
            The measurement type name.
        from_date : str or None
            The start date in the format 2001-01-01. None will put it to the beginning of the time series.
        to_date : str or None
            The end date in the format 2001-01-01. None will put it to the end of the time series.
        agg_method : str
            The aggregation method to resample the data. e.g. Average, Total, Moving Average, Extrema.
        agg_interval : str
            The aggregation interval for the agg_method. e.g. '1 day', '1 week', '1 month'.
        alignment : str
            The start time alignment when agg_method is not None.
        quality_codes : bool
            Should the quality codes get returned?
        apply_precision : bool
            Should the precision according to Hilltop be applied to the data? Only use True if you're confident that Hilltop stores the correct precision, because it is not always correct.
        tstype : str or None
            The time series type; one of Standard, Check, or Quality.

        Returns
        -------
        DataFrame
        """
        ## Check if site exists in hts
        if site not in self.available_sites:
            raise ValueError('Requested site is not in hts file.')

        ## Make sure that the measurement data has already been stored
        if site not in self._measurements:
            _ = self._get_measurement_list_single(site, measurement)

        if measurement.lower() not in self._measurements[site]:
            _ = self._get_measurement_list_single(site, measurement)

        if measurement.lower() not in self._measurements[site]:
            return pd.DataFrame(columns=['SiteName', 'MeasurementName', 'Time'])

        ## Determine what response format to use
        m_dict1 = self._measurements[site][measurement.lower()]

        if m_dict1['DataType'] in ['HydSection', 'HydFacecard']:
            raise NotImplementedError(' and '.join(['HydSection', 'HydFacecard']) +  ' Data Types have not been implemented.')

        if (m_dict1['DataType'] in ['GaugingResults']) or (m_dict1['DataSourceName'] in ['Gauging Results']):
            response_format = 'Native'
        else:
            response_format = None

        ## Make url
        url = build_url(base_url=self.base_url, hts=self.hts, request='GetData', site=site, measurement=measurement, from_date=from_date, to_date=to_date, agg_method=agg_method, agg_interval=agg_interval, alignment=alignment, quality_codes=quality_codes, tstype=tstype, response_format=response_format)

        ## Request data and load in xml
        tree1 = get_hilltop_xml(url, timeout=self.timeout, **self._requests_kwargs)

        if tree1.find('Error') is not None:
            return pd.DataFrame(columns=['SiteName', 'MeasurementName', 'Time'])
        meas1 = tree1.find('Measurement')

        if meas1 is not None:
            item_num = m_dict1['Item']

            if (m_dict1['DataType'] in ['GaugingResults']) or (m_dict1['DataSourceName'] in ['Gauging Results']):
                data1 = meas1.find('Data').findall('V')

                data_list = []
                append = data_list.append

                for val in data1:
                    val_text = val.text.encode('ascii', 'ignore').decode()
                    mowsecs = int(val_text.split(' ')[0])
                    time = convert_mowsecs(mowsecs)

                    val_dict = {'Time': time}

                    v1 = val_text.split(' ')[item_num]

                    try:
                        v1 = int(v1)
                    except ValueError:
                        v1 = float(v1)

                    if v1 >= 0:
                        if 'Divisor' in m_dict1:
                            v1 = v1 / m_dict1['Divisor']

                        val_dict['Value'] = v1

                        append(val_dict)
            else:
                data1 = meas1.find('Data').findall('E')

                data_list = []
                append = data_list.append

                for val in data1:
                    time = val.find('T').text.encode('ascii', 'ignore').decode()

                    val_dict = {'Time': time}

                    censor_code = None
                    if m_dict1['DataType'] == 'WQData':
                        v1 = convert_value(val.find('Value').text)
                        if isinstance(v1, str):
                            if '<' in v1:
                                censor_code = 'less_than'
                                v1 = convert_value(v1[1:])
                            elif '>' in v1:
                                censor_code = 'greater_than'
                                v1 = convert_value(v1[1:])

                        qual_code = val.find('QualityCode')
                    elif m_dict1['DataType'] == 'WQSample':
                        v1 = None
                        qual_code = None
                    else:
                        v1 = convert_value(val.find('I' + str(item_num)).text)
                        qual_code = val.find('Q' + str(item_num))

                    if apply_precision and isinstance(v1, (int, float)) and (censor_code is None):
                        v1 = np.round(v1, m_dict1['Precision'])
                        if m_dict1['Precision'] == 0:
                            v1 = int(v1)

                    if v1 is not None:
                        val_dict['Value'] = v1
                    if censor_code is not None:
                        val_dict['CensorCode'] = censor_code

                    params = val.findall('Parameter')

                    if params:
                        for param in params:
                            p_name = param.attrib['Name']
                            p_val = convert_value(param.attrib['Value'])
                            val_dict[p_name] = p_val

                    if qual_code is not None:
                        val_dict['QualityCode'] = convert_value(qual_code.text)

                    append(val_dict)

            if data_list:
                output1 = pd.DataFrame(data_list)
                output1['Time'] = pd.to_datetime(output1['Time'])
                output1['SiteName'] = site
                output1['MeasurementName'] = measurement
                output1 = output1.set_index(['SiteName', 'MeasurementName', 'Time']).reset_index()

                if 'CensorCode' in output1:
                    output1.loc[output1['CensorCode'].isnull(), 'CensorCode'] = 'not_censored'
            else:
                output1 = pd.DataFrame(columns=['SiteName', 'MeasurementName', 'Time'])

        else:
            output1 = pd.DataFrame(columns=['SiteName', 'MeasurementName', 'Time'])

        return output1


    def get_data(self, sites: Union[str, List[str]], measurements: Union[str, List[str]], from_date: str = None, to_date: str = None, agg_method: str = None, agg_interval: str = None, alignment: str = '00:00', quality_codes: bool = False, apply_precision: bool = False, tstype: str = None):
        """
        Method to query a Hilltop web server for time series data associated with a Site and Measurement.

        Parameters
        ----------
        sites : str or list of str
            The site(s) to get the results. You can pass a single site as a string, or a list of sites.
        measurements : str or list of str
            The measurement(s) to get the results. If multiple sites and measurements are passed, all combinations must exist in Hilltop.
        from_date : str or None
            The start date in the format 2001-01-01. None will put it to the beginning of the time series.
        to_date : str or None
            The end date in the format 2001-01-01. None will put it to the end of the time series.
        agg_method : str or None
            The aggregation method to resample the data. e.g. Average, Total, Moving Average, Extrema.
        agg_interval : str or None
            The aggregation interval for the agg_method. e.g. '1 day', '1 week', '1 month'.
        alignment : str or None
            The start time alignment when agg_method is not None.
        quality_codes : bool
            Should the quality codes get returned?
        apply_precision : bool
            Should the precision according to Hilltop be applied to the data? Only use True if you're confident that Hilltop stores the correct precision, because it is not always correct.
        tstype : str or None
            The time series type; one of Standard, Check, or Quality.

        Returns
        -------
        DataFrame
        """
        if isinstance(sites, str):
            sites = [sites]
        if isinstance(measurements, str):
            measurements = [measurements]

        res_df_list = []
        for site in sites:
            for measurement in measurements:
                res_df0 = self._get_data_single(site, measurement, from_date=from_date, to_date=to_date, agg_method=agg_method, agg_interval=agg_interval, alignment=alignment, quality_codes=quality_codes, apply_precision=apply_precision, tstype=tstype)
                res_df_list.append(res_df0)

        res_df = pd.concat(res_df_list)

        return res_df


##################################################
### Testing












































































































