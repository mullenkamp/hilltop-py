# -*- coding: utf-8 -*-
"""
Utility functions for Hilltop functions.
"""
import os
import numpy as np
import pandas as pd
from datetime import datetime
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser as ConfigParser


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

    names1 = names.str.replace('[:\.]', '/')
#    names1.loc[names1 == 'L35183/580-M1'] = 'L35/183/580-M1' What to do with this one?
#    names1.loc[names1 == 'L370557-M1'] = 'L37/0557-M1'
#    names1.loc[names1 == 'L370557-M72'] = 'L37/0557-M72'
#    names1.loc[names1 == 'BENNETT K38/0190-M1'] = 'K38/0190-M1'
    names1 = names1.str.upper()
    if rem_m:
        list_names1 = names1.str.findall('[A-Z]+\d+/\d+')
        names_len_bool = list_names1.apply(lambda x: len(x)) == 1
        names2 = names1.copy()
        names2[names_len_bool] = list_names1[names_len_bool].apply(lambda x: x[0])
        names2[~names_len_bool] = np.nan
    else:
        list_names1 = names1.str.findall('[A-Z]+\d+/\d+\s*-\s*M\d*')
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