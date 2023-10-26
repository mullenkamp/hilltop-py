# -*- coding: utf-8 -*-
"""
Created on Tue May 29 10:12:11 2018

@author: MichaelEK
"""
import pandas as pd
import numpy as np
from hilltoppy.utils import convert_value, DataSource, Measurement, get_hilltop_xml, build_url
import orjson


########################################
### Functions


def site_list(base_url, hts, location=None, measurement=None, collection=None, site_parameters=None, timeout=60, **kwargs):
    """
    SiteList request function. Returns a list of sites associated with the hts file.

    Parameters
    ----------
    base_url : str
        root Hilltop url str.
    hts : str
        hts file name including the .hts extension.
    location : str or bool
        Should the location be returned? Only applies to the SiteList request. 'Yes' returns the Easting and Northing, while 'LatLong' returns NZGD2000 lat lon coordinates.
    collection : str
        Get site list via a collection.
    site_parameters : list
        A list of the site parameters to be returned with the SiteList request. Make a call to site_info to find all of the possible options.
    timeout : int
        The http request timeout in seconds.
    **kwargs
        Optional keyword arguments passed to requests.

    Returns
    -------
    DataFrame
    """
    url = build_url(base_url, hts, 'SiteList', location=location, measurement=measurement, collection=collection, site_parameters=site_parameters)
    tree1 = get_hilltop_xml(url, timeout=timeout, **kwargs)

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


def site_info(base_url, hts, site, timeout=60, **kwargs):
    """
    SiteInfo request function. Returns all of the site data for a specific site. The Hilltop sites table has tons of fields, so you never know what you're going to get.

    Parameters
    ----------
    base_url : str
        root Hilltop url str.
    hts : str
        hts file name including the .hts extension.
    site : str or None
        The site to be extracted.
    timeout : int
        The http request timeout in seconds.
    **kwargs
        Optional keyword arguments passed to requests.

    Returns
    -------
    DataFrame
    """
    url = build_url(base_url, hts, 'SiteInfo', site=site)
    tree1 = get_hilltop_xml(url, timeout=timeout, **kwargs)

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


def collection_list(base_url, hts, timeout=60, **kwargs):
    """
    CollectionList request function. Returns a frame of collection and site names associated with the hts file.

    Parameters
    ----------
    base_url : str
        root Hilltop url str.
    hts : str
        hts file name including the .hts extension.
    timeout : int
        The http request timeout in seconds.
    **kwargs
        Optional keyword arguments passed to requests.

    Returns
    -------
    DataFrame
    """
    url = build_url(base_url, hts, 'CollectionList')
    tree1 = get_hilltop_xml(url, timeout=timeout, **kwargs)

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


def measurement_list(base_url, hts, site, measurement=None, timeout=60, **kwargs):
    """
    Function to query a Hilltop server for the measurement summary of a site.

    Parameters
    ----------
    base_url : str
        root Hilltop url str.
    hts : str
        hts file name including the .hts extension. Even if the file to be accessed is a dsn file, it must still have an hts extension for the web service.
    site : str or None
        The site to be extracted.
    measurement : str or None
        The measurement type name.
    timeout : int
        The http request timeout in seconds.
    **kwargs
        Optional keyword arguments passed to requests.

    Returns
    -------
    DataFrame
    """
    ### Make url
    url = build_url(base_url, hts, 'MeasurementList', site, measurement)

    ### Request data and load in xml
    tree1 = get_hilltop_xml(url, timeout=timeout, **kwargs)

    if tree1.find('Error') is not None:
        raise ValueError('No results returned from URL request')
    data_sources = tree1.findall('DataSource')

    ### Extract data into list of dict - to represent the Hilltop structure
    data_list = []

    if data_sources:
        for d in data_sources:
            ds_dict = {c.tag: c.text.encode('ascii', 'ignore').decode() for c in d if c.text is not None}
            if 'DataType' in ds_dict:
                if not ds_dict['DataType'] in ['HydSection', 'HydFacecard']:
                    ds_dict['SiteName'] = site
                    data_source_name = d.attrib['Name']
                    ds_dict['DataSourceName'] = data_source_name
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
    else:
        output1 = pd.DataFrame(columns=['SiteName', 'MeasurementName'])

    return output1


def get_data(base_url, hts, site, measurement, from_date=None, to_date=None, agg_method=None, agg_interval=None, alignment='00:00', quality_codes=False, apply_precision=False, tstype=None, timeout=60, **kwargs):
    """
    Function to query a Hilltop web server for time series data associated with a Site and Measurement.

    Parameters
    ----------
    base_url : str
        root Hilltop url str.
    hts : str
        hts file name including the .hts extension. Even if the file to be accessed is a dsn file, it must still have an hts extension for the web service.
    request : str
        The function request.
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
    timeout : int
        The http request timeout in seconds.
    **kwargs
        Optional keyword arguments passed to requests.

    Returns
    -------
    DataFrame
    """
    ### Make url
    url = build_url(base_url=base_url, hts=hts, request='GetData', site=site, measurement=measurement, from_date=from_date, to_date=to_date, agg_method=agg_method, agg_interval=agg_interval, alignment=alignment, quality_codes=quality_codes, tstype=tstype)

    ### Request data and load in xml
    tree1 = get_hilltop_xml(url, timeout=timeout, **kwargs)

    if tree1.find('Error') is not None:
        raise ValueError(tree1.find('Error').text)
    meas1 = tree1.find('Measurement')

    if meas1 is not None:
        ## Parse the data source and associated measurements
        ds = meas1.find('DataSource')
        ds_dict = {c.tag: c.text.encode('ascii', 'ignore').decode() for c in ds if c.text is not None}
        ds_dict['SiteName'] = site
        data_source_name = ds.attrib['Name']

        if ds_dict['DataType'] in ['HydSection', 'HydFacecard']:
            raise NotImplementedError(' and '.join(['HydSection', 'HydFacecard']) +  ' Data Types have not been implemented.')

        ds_dict['DataSourceName'] = data_source_name
        ds_dict1 = orjson.loads(DataSource(**ds_dict).json(exclude_none=True))

        ## Get the measurement info
        measurements = ds.findall('ItemInfo')

        for m in measurements:
            m_dict = {c.tag: convert_value(c.text) for c in m}
            m_name = m_dict.pop('ItemName')

            if measurement.lower() == m_name.lower():
                if 'Format' in m_dict:
                    f_text_list = m_dict['Format'].split('.')
                    if len(f_text_list) == 2:
                        precision = len(f_text_list[1])
                    else:
                        precision = 0
                else:
                    precision = 0

                m_dict['Precision'] = precision
                m_dict['MeasurementName'] = m_name
                m_dict['Item'] = int(m.attrib['ItemNumber'])

                m_dict1 = orjson.loads(Measurement(**m_dict).json(exclude_none=True))

                ds_dict1.update(m_dict1)

        ## Check if the measurement actually came through with the GetData request
        ## Hilltop seems oddly inconsistant when it returns the measurements...
        ## If not, then get the measurement data from the measurement_list function
        if 'Item' not in ds_dict1:
            ml = measurement_list(base_url, hts, site, measurement=measurement, output='dict', timeout=timeout)
            for m in ml:
                if m['MeasurementName'].lower() == measurement.lower():
                    ds_dict1.update(m)

        ## Parse the ts data
        item_num = str(ds_dict1['Item'])
        data1 = meas1.find('Data').findall('E')

        data_list = []
        append = data_list.append

        for val in data1:
            time = val.find('T').text.encode('ascii', 'ignore').decode()

            val_dict = {'Time': time}

            censor_code = None
            if ds_dict1['DataType'] == 'WQData':
                v1 = convert_value(val.find('Value').text)
                if isinstance(v1, str):
                    if '<' in v1:
                        censor_code = 'less_than'
                        v1 = convert_value(v1[1:])
                    elif '>' in v1:
                        censor_code = 'greater_than'
                        v1 = convert_value(v1[1:])

                qual_code = val.find('QualityCode')
            elif ds_dict1['DataType'] == 'WQSample':
                v1 = None
                qual_code = None
            else:
                v1 = convert_value(val.find('I' + item_num).text)
                qual_code = val.find('Q' + item_num)

            if apply_precision and isinstance(v1, (int, float)) and (censor_code is None):
                v1 = np.round(v1, ds_dict1['Precision'])
                if ds_dict1['Precision'] == 0:
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

        output1 = pd.DataFrame(data_list)
        output1['Time'] = pd.to_datetime(output1['Time'])
        output1['SiteName'] = site
        output1['MeasurementName'] = measurement
        output1 = output1.set_index(['SiteName', 'MeasurementName', 'Time']).reset_index()

        if 'CensorCode' in output1:
            output1.loc[output1['CensorCode'].isnull(), 'CensorCode'] = 'not_censored'

    else:
        output1 = pd.DataFrame(columns=['SiteName', 'MeasurementName', 'Time'])

    return output1
