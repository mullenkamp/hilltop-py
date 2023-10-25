# -*- coding: utf-8 -*-
"""
Utility functions for Hilltop functions.
"""
import os
import numpy as np
import pandas as pd
from datetime import datetime, date
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser as ConfigParser
import orjson
from typing import List, Union
from pydantic import BaseModel, Field, HttpUrl, conint, confloat
from enum import Enum
import requests
import xml.etree.ElementTree as ET
from time import sleep
import urllib.parse

##############################################
### Parameters

available_requests = ['SiteList', 'MeasurementList', 'CollectionList', 'GetData', 'SiteInfo']


##############################################
### Data models


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default, option=orjson.OPT_NON_STR_KEYS | orjson.OPT_OMIT_MICROSECONDS | orjson.OPT_SERIALIZE_NUMPY).decode()


class TSType(str, Enum):
    """
    The time series type according to Hilltop.
    """
    std_series = 'StdSeries'
    std_qual_series = 'StdQualSeries'
    check_series = 'CheckSeries'


class DataType(str, Enum):
    """
    The data type according to Hilltop.
    """
    simple_ts = 'SimpleTimeSeries'
    hyd_section = 'HydSection'
    hyd_facecard = 'HydFacecard'
    gauging_results = 'GaugingResults'
    wq_data = 'WQData'
    wq_sample = 'WQSample'
    meter_reading = 'MeterReading'


class Interpolation(str, Enum):
    """
    The method of Measurement and subsequently the kind of interpolation that should be applied to the Measurements.
    """
    discrete = 'Discrete'
    instant = 'Instant'
    incremental = 'Incremental'
    event = 'Event'
    quasi_continuous = 'Quasi-continuous'


class Site(BaseModel):
    """

    """
    SiteName: str = Field(..., description='The unique name of the site used by Hilltop.')
    Easting: Union[int, float] = Field(None, description='The easting probably in NZTM.')
    Northing: Union[int, float] = Field(None, description='The northing probably in NZTM.')
    Latitude: Union[int, float] = Field(None, description='The Latitude in WGS84 decimal degrees.')
    Longitude: Union[int, float] = Field(None, description='The Longitude in WGS84 decimal degrees.')
    properties: dict = Field(None, description='A variety of other site properties/data.')


class Measurement(BaseModel):
    """

    """
    MeasurementName: str = Field(..., description='The measurement name associated with the DataSource. The MeasurementName is derived from the RequestAs field provided by the Hilltop server. As such, this may include the DataSourceName appended onto the Measurement name with surrounding brackets.')
    # Item: int = Field(..., description='The Measurement item position in the Data when NumItems in the DataSource > 1.')
    Units: str = Field(None, description="The units of the data.")
    Precision: int = Field(..., description='The precision of the data as the number of decimal places.')
    Divisor: int = Field(None, description="Divide the data by the divisor to get the appropriate Units.")
    Precision: int = Field(..., description='The precision of the data as the number of decimal places.')
    MeasurementGroup: str = Field(None, description="I've only seen Virtual Measurements so far...")
    VMStart: datetime = Field(None, description="The start time of the virtual measurement.")
    VMFinish: datetime = Field(None, description="The end time of the virtual measurement.")
    Item: int = Field(None, description="The measurement item number to know which result goes with which measurement.")
    # RequestAs: str = Field(None, description="The minimum measurement name the Hilltop server uses for responses and requests.")

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class DataSource(BaseModel):
    """

    """
    SiteName: str
    DataSourceName: str
    # NumItems: int = Field(..., description='The Number of Measurements grouped per GetData request. If this is greater than 1, then any GetData request to a Measurement will return more than one Measurement Data.')
    TSType: TSType
    DataType: DataType
    Interpolation: Interpolation
    From: datetime = None
    To: datetime = None

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


##############################################
### Functions


def build_url(base_url: str, hts: str, request: str, site: str = None, measurement: str = None, collection: str = None, from_date: str = None, to_date: str = None, location: Union[str, bool] = None, site_parameters: List[str] = None, agg_method: str = None, agg_interval: str = None, alignment: str = None, quality_codes: bool = False, tstype: str = None, response_format: str = None, units: bool = None):
    """
    Function to generate the Hilltop url for the web service.

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
    collection : str or None
        The collection name.
    from_date : str or None
        The start date in the format 2001-01-01. None will put it to the beginning of the time series.
    to_date : str or None
        The end date in the format 2001-01-01. None will put it to the end of the time series.
    location : str or bool
        Should the location be returned? Only applies to the SiteList request. True returns the Easting and Northing, while 'LatLong' returns NZGD2000 lat lon coordinates.
    site_parameters : list of str
        A list of the site parameters to be returned with the SiteList request.
    agg_method : str
        The aggregation method to resample the data. e.g. Average, Total, Moving Average, Extrema.
    agg_interval : str
        The aggregation interval for the agg_method. e.g. '1 day', '1 week', '1 month'.
    alignment : str
        The time alignment in the form '00:00'.
    quality_codes : bool
        Should the quality codes get returned from the GetData function.
    tstype : str
        The timeseries type, one of Standard, Check or Quality
    response_format: str
        The Hilltop response structure. Options are None, Native, or WML2. Read the Hilltop server docs for more info.

    Returns
    -------
    str
        URL string for the Hilltop web server.
    """
    ### Check base parameters
    if not base_url.endswith('/'):
        base_url += '/'
    # if not hts.endswith('.hts'):
    #     raise ValueError('The hts file must end with .hts')
    if request not in available_requests:
        raise ValueError('request must be one of ' + str(available_requests))

    ### Collect data for a URL in a dict
    data = {'Service': 'Hilltop', 'Request': request}

    ### Ready the others
    if isinstance(site, str):
        data['Site'] = site
    if isinstance(measurement, str):
        data['Measurement'] = measurement
    if isinstance(collection, str):
        data['Collection'] = collection
    if units is True:
        data['Units'] = 'Yes'

    if request == 'SiteList':
        if isinstance(site_parameters, list):
            data['SiteParameters'] = ','.join(site_parameters)
        if location is True:
            data['Location'] = 'Yes'
        elif isinstance(location, str):
            if location == 'LatLong':
                data['Location'] = location
            else:
                raise ValueError('location must be either a bool or a str named LatLong.')

    if request == 'GetData':
        if quality_codes:
            data['ShowQuality'] = 'Yes'

        if isinstance(tstype, str):
            if tstype == 'Standard':
                data['tsType'] = 'StdSeries'
            elif tstype == 'Quality':
                data['tsType'] = 'StdQualSeries'
            elif tstype == 'Check':
                data['tsType'] = 'CheckSeries'

        if isinstance(response_format, str):
            data['Format'] = response_format

        ### Time interval goes last!
        if isinstance(agg_method, str):
            data['Method'] = agg_method
        if isinstance(agg_interval, str):
            data['Interval'] = agg_interval

        if from_date is None:
            from_date = '1800-01-01'
        if to_date is None:
            to_date = 'now'
        data['TimeInterval'] = str(from_date) + '/' + str(to_date)

        if isinstance(alignment, str):
            data['Alignment'] = alignment

    encoded_data = urllib.parse.urlencode(data, quote_via=urllib.parse.quote)

    return base_url + hts + '?' + encoded_data


def get_hilltop_xml(url, timeout=60, **kwargs):
    """

    """
    counter = [10, 20, 30, None]
    for c in counter:
        try:
            with requests.get(url, timeout=timeout, **kwargs) as req:
                tree1 = ET.fromstring(req.content)
            break
        # except ET.ParseError:
        #     raise ET.ParseError('Could not parse xml. Check to make sure the URL is correct.')

        # except http.client.RemoteDisconnected as err:
        #     print(str(err))

        #     if c is None:
        #         raise requests.exceptions.ConnectionError('The Hilltop request tried too many times...the server is probably down')

        #     print('Trying again in ' + str(c) + ' seconds.')
        #     sleep(c)

        # except requests.exceptions.ConnectionError:
        #     raise requests.exceptions.ConnectionError('Could not read the URL. Check to make sure the URL is correct.')

        except Exception as err:
            print(str(err))

            if c is None:
                raise requests.exceptions.ConnectionError('The Hilltop request tried too many times...the server is probably down')

            print('Trying again in ' + str(c) + ' seconds.')
            sleep(c)

    return tree1


def convert_mowsecs(mowsecs: int):
    """

    """
    time = pd.Timestamp(mowsecs - 946771200, unit='s')

    return time


def convert_value(text):
    """

    """
    if text is not None:
        val = text.encode('ascii', 'ignore').decode()

        if val in ['False', 'True']:
            val = bool(val)
        elif val == '-0':
            val = None
        else:
            try:
                val = int(val)
            except:
                try:
                    val = float(val)
                except:
                    try:
                        val = pd.to_datetime(val)
                    except:
                        pass
    else:
        val = None

    return val


# def parse_data_source(measurement):
#     """

#     """
#     if ' [' not in measurement:
#         raise ValueError('The measurement name must contain the data source name in brackets.')
#     m_name, ds_name = measurement.split(' [')
#     ds_name = ds_name[:-1]

#     return m_name, ds_name


def parse_dsn(dsn_path):
    """
    Function to parse a dsn file and all sub-dsn files into paths to hts files. Returns a list of hts paths.

    Parameters
    ----------
    dsn_path : str
        Path to the dsn file.

    Returns
    -------
    List of path strings to hts files.
    """

    base_path = os.path.dirname(dsn_path)

    dsn = ConfigParser()
    dsn.read(dsn_path)
    files1 = [os.path.join(base_path, i[1]) for i in dsn.items('Hilltop') if 'file' in i[0]]
    hts1 = [i for i in files1 if i.endswith('.hts')]
    dsn1 = [i for i in files1 if i.endswith('.dsn')]
    while dsn1:
        for f in dsn1:
            base_path = os.path.dirname(f)
            p1 = ConfigParser()
            p1.read(f)
            files1 = [os.path.join(base_path, i[1]) for i in p1.items('Hilltop') if 'file' in i[0]]
            hts1.extend([i for i in files1 if i.endswith('.hts')])
            dsn1.remove(f)
            dsn1[0:0] = [i for i in files1 if i.endswith('.dsn')]
    return hts1


def pytime_to_datetime(pytime):
    """
    Function to convert a PyTime object to a datetime object.
    """

    dt1 = datetime(year=pytime.year, month=pytime.month, day=pytime.day, hour=pytime.hour, minute=pytime.minute)
    return dt1


def time_switch(x):
    """
    Convenience codes to convert for time text to pandas time codes.
    """
    return {
        'min': 'Min',
        'mins': 'Min',
        'minute': 'Min',
        'minutes': 'Min',
        'hour': 'H',
        'hours': 'H',
        'day': 'D',
        'days': 'D',
        'week': 'W',
        'weeks': 'W',
        'month': 'M',
        'months': 'M',
        'year': 'A',
        'years': 'A',
        'water year': 'A-JUN',
        'water years': 'A-JUN',
    }.get(x, 'A')


def convert_site_names(names, rem_m=True):
    """
    Function to convert water usage site names.
    """

    names1 = names.str.replace(r'[:\.]', '/')
#    names1.loc[names1 == 'L35183/580-M1'] = 'L35/183/580-M1' What to do with this one?
#    names1.loc[names1 == 'L370557-M1'] = 'L37/0557-M1'
#    names1.loc[names1 == 'L370557-M72'] = 'L37/0557-M72'
#    names1.loc[names1 == 'BENNETT K38/0190-M1'] = 'K38/0190-M1'
    names1 = names1.str.upper()
    if rem_m:
        list_names1 = names1.str.findall(r'[A-Z]+\d+/\d+')
        names_len_bool = list_names1.apply(lambda x: len(x)) == 1
        names2 = names1.copy()
        names2[names_len_bool] = list_names1[names_len_bool].apply(lambda x: x[0])
        names2[~names_len_bool] = np.nan
    else:
        list_names1 = names1.str.findall(r'[A-Z]+\d+/\d+\s*-\s*M\d*')
        names_len_bool = list_names1.apply(lambda x: len(x)) == 1
        names2 = names1.copy()
        names2[names_len_bool] = list_names1[names_len_bool].apply(lambda x: x[0])
        names2[~names_len_bool] = np.nan

    return names2


def proc_ht_use_data_ws(ht_data):
    """
    Function to process the water usage data at daily resolution.
    """

    ### Groupby mtypes and sites
    grp = ht_data.groupby(level=['Measurement', 'Site'])

    res1 = []
    for index, data1 in grp:
        data = data1.copy()
        mtype, site = index
#        units = sites[(sites.site == site) & (sites.mtype == mtype)].unit

        ### Select the process sequence based on the mtype and convert to period volume

        data[data < 0] = np.nan

        if mtype == 'Water Meter':
            ## Check to determine whether it is cumulative or period volume
            count1 = float(data.count())
            diff1 = data.diff()
            neg_index = diff1 < 0
            neg_ratio = sum(neg_index.values)/count1
            if neg_ratio > 0.1:
                vol = data
            else:
                # Replace the negative values with zero and the very large values
                diff1[diff1 < 0] = data[diff1 < 0]
                vol = diff1
        elif mtype in ['Compliance Volume', 'Volume']:
            vol = data
        elif mtype == 'Flow [Flow]':
#            vol = (data * 60*60*24).fillna(method='ffill').round(4)
            vol = (data * 60*60*24)
        elif mtype == 'Average Flow':
#            vol = (data * 24).fillna(method='ffill').round(4)
            vol = (data * 24)
        else:
            continue

        res1.append(vol)

    ### Convert to dataframe
    df1 = pd.concat(res1).reset_index()

    ### Drop the mtypes level and uppercase the sites
    df2 = df1.drop('Measurement', axis=1)
    df2.loc[:, 'Site'] = df2.loc[:, 'Site'].str.upper()

    ### Remove duplicate WAPs
    df3 = df2.groupby(['Site', 'DateTime']).Value.last()

    return df3


def proc_ht_use_data(ht_data):
    """
    Function to process the water usage data at daily resolution.
    """

    ### Groupby mtypes and sites
    grp = ht_data.groupby(level=['Measurement', 'Site'])

    res1 = []
    for index, data1 in grp:
        data = data1.copy()
        mtype, site = index
#        units = sites[(sites.site == site) & (sites.mtype == mtype)].unit

        ### Select the process sequence based on the mtype and convert to period volume

        data[data < 0] = np.nan

        if mtype == 'Water Meter':
            ## Check to determine whether it is cumulative or period volume
            count1 = float(data.count())
            diff1 = data.diff()
            neg_index = diff1 < 0
            neg_ratio = sum(neg_index.values)/count1
            if neg_ratio > 0.1:
                vol = data
            else:
                # Replace the negative values with zero and the very large values
                diff1[diff1 < 0] = data[diff1 < 0]
                vol = diff1
        elif mtype in ['Compliance Volume', 'Volume']:
            vol = data
        elif mtype == 'Flow':
#            vol = (data * 60*60*24).fillna(method='ffill').round(4)
            vol = (data * 60*60*24)
        elif mtype == 'Average Flow':
#            vol = (data * 24).fillna(method='ffill').round(4)
            vol = (data * 24)
        else:
            continue

        res1.append(vol)

    ### Convert to dataframe
    df1 = pd.concat(res1).reset_index()

    ### Drop the mtypes level and uppercase the sites
    df2 = df1.drop('Measurement', axis=1)
    df2.loc[:, 'Site'] = df2.loc[:, 'Site'].str.upper()

    ### Remove duplicate WAPs
    df3 = df2.groupby(['Site', 'DateTime']).Value.last()

    return df3
