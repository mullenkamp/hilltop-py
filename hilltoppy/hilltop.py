# -*- coding: utf-8 -*-
"""
Hilltop read functions.
"""
try:
    import Hilltop
except:
    pass
import pandas as pd
from hilltoppy.utils import time_switch

#####################################################
#### New method - might have issues


def site_list(hts):
    """
    Function to return a list of sites from an hts file. Exists for consistancy.

    Parameters
    ----------
    hts : str
        Path to hts file.

    Returns
    -------
    list
    """
    dfile1 = Hilltop.Connect(hts)
    site_list = Hilltop.SiteList(dfile1)
    Hilltop.Disconnect(dfile1)

    return site_list


def measurement_list(hts, sites=None):
    """
    Function to read all of the sites in an hts file and the associated site info.

    Parameters
    ----------
    hts : str
        Path to hts file.
    sites : list
        A list of site names to return.

    Returns
    -------
    DataFrame
    """

    dfile1 = Hilltop.Connect(hts)
    site_list = Hilltop.SiteList(dfile1)

    if not site_list:
        print('No sites in ' + hts)
        return None

    if isinstance(sites, list):
        site_list = [i for i in site_list if i in sites]
        if not site_list:
            print('No sites in ' + hts)
            return None

    site_info_list = []

    for i in site_list:
        try:
            info1 = Hilltop.MeasurementList(dfile1, i)
        except SystemError as err:
            print('Site ' + str(i) + " didn't work. Error: " + str(err))
            continue
        info1.loc[:, 'site'] = i.encode('ascii', 'ignore').decode()
        site_info_list.append(info1)
    site_info = pd.concat(site_info_list)

    site_info.loc[:, 'Start Time'] = pd.to_datetime(site_info.loc[:, 'Start Time'], format='%d-%b-%Y %H:%M:%S', errors='coerce')
    site_info.loc[:, 'End Time'] = pd.to_datetime(site_info.loc[:, 'End Time'], format='%d-%b-%Y %H:%M:%S', errors='coerce')

    bad_sites = site_info[site_info['Start Time'].isnull() | site_info['End Time'].isnull() | (site_info['Start Time'] < '1900-01-01') | (site_info['End Time'] > pd.Timestamp.today())]

    if not bad_sites.empty:
        print('There are ' + str(len(bad_sites)) + ' sites with bad times')
        print(bad_sites)
        site_info = site_info[~(site_info['Start Time'].isnull() | site_info['End Time'].isnull() | (site_info['Start Time'] < '1900-01-01') | (site_info['End Time'] > pd.Timestamp.today()))]

    len_all = len(site_list)
    len_got = len(site_info.site.unique())
    print('Missing ' + str(len_all - len_got) + ' sites, which is ' + str(round(100 * ((len_all - len_got)/len_all), 1)) + '% of the total')

    Hilltop.Disconnect(dfile1)
    return site_info


def get_data(hts, sites=None, mtypes=None, from_date=None, to_date=None, agg_method='Average', agg_n=1, agg_period='day', output_missing_sites=False, site_info=None):
    """
    Function to read time series from an hts file.

    Parameters
    ----------
    hts : str
        Path to the hts file.
    sites : list
        A list of site names within the hts file.
    mtypes : list
        A list of measurement types that should be returned.
    from_date : str
        The start date to retreive from the data in ISO format (e.g. '2011-11-30 00:00').
    to_date : str
        The end date to retreive from the data in ISO format (e.g. '2011-11-30 00:00').
    agg_method : str
        Options are '', 'Interpolate', 'Average', 'Total', 'Moving Average', and 'EP'.
    agg_period : str
        The resample period (e.g. 'day', 'month').
    agg_n : int
        The number of periods (e.g. 1 for 1 day).
    output_site_data : bool
        Should the sites data be output?
    sites_info : DataFrame
        The DataFrame return from the get_sites_mtypes function. If this is passed than get_sites_mtypes is not run.

    Returns
    -------
    DataFrame
    """

    if not isinstance(site_info, pd.DataFrame):
        site_info = measurement_list(hts, sites=sites)

    if isinstance(mtypes, list):
        site_info = site_info[site_info['Measurement'].isin(mtypes)]

    if isinstance(from_date, str):
        from_date1 = pd.to_datetime(from_date)
        site_info = site_info[site_info['End Time'] >= from_date1].copy()
        site_info.loc[site_info['Start Time'] < from_date1, 'Start Time'] = from_date1

    if isinstance(to_date, str):
        to_date1 = pd.to_datetime(to_date)
        site_info = site_info[site_info['Start Time'] <= to_date1].copy()
        site_info.loc[site_info['End Time'] > to_date1, 'End Time'] = to_date1

    ## Convert datetime and interval to hilltop specific formats
    pd_time_code = time_switch(agg_period)
    site_info.loc[:, 'Start Time'] = site_info.loc[:, 'Start Time'].dt.ceil(str(agg_n) + pd_time_code).dt.strftime('%d-%b-%Y %H:%M:%S')
    site_info.loc[:, 'End Time'] = site_info.loc[:, 'End Time'].dt.strftime('%d-%b-%Y %H:%M:%S')

    ht_interval = str(agg_n) + ' ' + agg_period

    ## Extract the ts data
    data1 = []

    dfile1 = Hilltop.Connect(hts)
    for i in site_info.index:
        site = site_info.loc[i, 'site']
        mtype = site_info.loc[i, 'Measurement']
        start = site_info.loc[i, 'Start Time']
        end = site_info.loc[i, 'End Time']

        try:
            d1 = Hilltop.GetData(dfile1, site, mtype, start, end, method=agg_method, interval=ht_interval, alignment='00:00')
        except Exception as err:
            err1 = err
            print(err1)
            print('Extraction failed for site ' + str(site) + ' and mtype ' + str(mtype))
            continue

        if d1.empty:
            print('No data for site ' + str(site) + ' and mtype ' + str(mtype))
            continue

        if (pd_time_code == 'D'):
            d1.index = d1.index.normalize()
        d1.name = 'data'
        d1.index.name = 'time'
        d2 = d1.reset_index()
        d2.loc[:, 'site'] = site
        d2.loc[:, 'mtype'] = mtype

        data1.append(d2)

    try:
        data2 = pd.concat(data1).set_index(['mtype', 'site', 'time']).data
    except MemoryError:
        print('Not enough RAM')

    return data2

