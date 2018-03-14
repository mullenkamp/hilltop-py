# -*- coding: utf-8 -*-
"""
Hilltop read functions.
Hilltop uses a fixed base date as 1940-01-01, while the standard unix/POSIT base date is 1970-01-01.
"""
import Hilltop
from pandas import concat, to_datetime, DataFrame

#####################################################
#### New method - not ready yet...


def ht_sites(hts, sites=None):
    """
    Function to read all of the sites in an hts file and the associated site info.

    hts -- Path to hts file (str).\n
    sites -- Optional list, array, series of site names to return.
    """

    dfile1 = Hilltop.Connect(hts)
    site_list = Hilltop.SiteList(dfile1)

    if not site_list:
        print('No sites in ' + hts)
        return(DataFrame())

    if isinstance(sites, list):
        site_list = [i for i in site_list if i in sites]

    site_info = DataFrame()

    for i in site_list:
        try:
            info1 = Hilltop.MeasurementList(dfile1, i)
        except SystemError as err:
            print('Site ' + str(i) + " didn't work. Error: " + str(err))
            continue
        info1.loc[:, 'site'] = i.encode('ascii', 'ignore').decode()
        site_info = concat([site_info, info1])
    site_info.reset_index(drop=True, inplace=True)

    site_info.loc[:, 'Start Time'] = to_datetime(site_info.loc[:, 'Start Time'], format='%d-%b-%Y %H:%M:%S')
    site_info.loc[:, 'End Time'] = to_datetime(site_info.loc[:, 'End Time'], format='%d-%b-%Y %H:%M:%S')

    len_all = len(site_list)
    len_got = len(site_info.site.unique())
    print('Missing ' + str(len_all - len_got) + ' sites, which is ' + str(round(100 * ((len_all - len_got)/len_all), 1)) + '% of the total')

    Hilltop.Disconnect(dfile1)
    return site_info


def ht_get_data(hts, sites=None, from_date=None, to_date=None, agg_method='Average', interval='1 day', alignment='00:00', output_missing_sites=False):
    """

    """

    site_info = ht_sites(hts, sites=sites)

    if isinstance(from_date, str):
        from_date1 = to_datetime(from_date).strftime('%d-%b-%Y %H:%M')
    else:
        from_date1 = ''
    if isinstance(to_date, str):
        to_date1 = to_datetime(to_date).strftime('%d-%b-%Y %H:%M')
    else:
        to_date1 = ''

    data1 = []
    missing_site_data = DataFrame()

    dfile1 = Hilltop.Connect(hts)
    for i in site_info.index:
        site = site_info.loc[i, 'site']
        mtype = site_info.loc[i, 'Measurement']

        d1 = Hilltop.GetData(dfile1, site, mtype, from_date1, to_date1, method=agg_method, interval=interval, alignment=alignment)

        if d1.empty:
            missing_site_data = concat([missing_site_data, site_info.loc[i]])
            print('No data for site ' + str(site) + ' and mtype ' + str(mtype))
            continue

        if (interval == '1 day') & (alignment == '00:00'):
            d1.index = d1.index.normalize()
        d1.name = 'data'
        d1.index.name = 'time'
        d2 = d1.reset_index()
        d2.loc[:, 'site'] = site
        d2.loc[:, 'mtype'] = mtype
        print(site, mtype)

        data1.append(d2)

    try:
        data2 = concat(data1)
    except MemoryError:
        print('Not enough memory for a 32bit application')

    if missing_site_data.empty:
        print('No missing data for any sites/mtypes')
    else:
        print('No data for ' + str(len(missing_site_data)) + ' sites/mtype combos')
        if output_missing_sites:
            return(data2, missing_site_data)
    return data2

