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
from typing import List
from pydantic import BaseModel, Field, HttpUrl, conint, confloat
from enum import Enum
# import urllib
# import urllib.request
import requests
import xml.etree.ElementTree as ET
from time import sleep
import http

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


class Measurement(BaseModel):
    """

    """
    MeasurementName: str = Field(..., description='The measurement name associated with the DataSource. The DataSourceName has been appended to the MeasurementName (in the form of MeasurementName [DataSourceName]), because this is the requirement for requests to the Hilltop web server.')
    # Item: int = Field(..., description='The Measurement item position in the Data when NumItems in the DataSource > 1.')
    Units: str = Field(None, description="The units of the data.")
    Precision: int = Field(..., description='The precision of the data as the number of decimal places.')
    Divisor: int = Field(None, description="Divide the data by the divisor to get the appropriate Units.")
    Precision: int = Field(..., description='The precision of the data as the number of decimal places.')
    MeasurementGroup: str = Field(None, description="I've only seen Virtual Measurements so far...")
    VMStart: datetime = Field(None, description="The start time of the virtual measurement.")
    VMFinish: datetime = Field(None, description="The end time of the virtual measurement.")

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
    Measurements: List[Measurement] = None

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


##############################################
### Functions


def get_hilltop_xml(url, timeout=60):
    """

    """
    counter = [10, 20, 30, None]
    for c in counter:
        try:
            with requests.get(url, timeout=timeout) as req:
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


def convert_value(text):
    """

    """
    if text is not None:
        val = text.encode('ascii', 'ignore').decode()
        if val in ['False', 'True']:
            val = bool(val)
        else:
            try:
                val = int(val)
            except:
                try:
                    val = float(val)
                except:
                    try:
                        val = pd.to_datetime(val, dayfirst=True)
                    except:
                        pass
    else:
        val = None

    return val


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
