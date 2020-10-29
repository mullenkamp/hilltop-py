# -*- coding: utf-8 -*-
"""
Hilltop read functions for COM connection.
Hilltop uses a fixed base date as 1940-01-01, while the standard unix/POSIT base date is 1970-01-01.
"""
try:
    from win32com.client import Dispatch, pywintypes, makepy
except:
    print('Install pywin32 or com functions will not work')
from pandas import concat, to_datetime, to_numeric, DataFrame, merge
from hilltoppy.util import pytime_to_datetime, time_switch

######################################################
#### COM access method


def makepy_hilltop(hlib='Hilltop Data Access'):
    """
    Function to generate the Hilltop COM module.

    Parameters
    ----------
    hlib : str
        The name of the COM library.

    Returns
    -------
    None
    """
    makepy.GenerateFromTypeLibSpec(hlib, verboseLevel=1)


def measurement_list(hts, sites=None, mtypes=None, rem_wq_sample=True):
    """
    Function to read the site names, measurement types, and units of a Hilltop hts file. Returns a DataFrame.

    Parameters
    ----------
    hts : str
        Path to the hts file.
    sites : list or None
        A list of site names within the hts file.
    mtypes : list or None
        A list of measurement types that should be returned.
    rem_wq_sample : bool
        In Hilltop 'WQ Sample' is a measurement type placemarker for the additional sample data. It doesn't generally apply when querying for the combo of sites/measurement types. True removes this instance from the returned DataFrame.

    Returns
    -------
    DataFrame
    """

    cat = Dispatch("Hilltop.Catalogue")
    if not cat.Open(hts):
        raise ValueError(cat.errmsg)

    dfile = Dispatch("Hilltop.DataRetrieval")
    try:
        dfile.Open(hts)
    except ValueError:
        print(dfile.errmsg)

    sites_lst = []

    ### Iterate through all sites/datasources/mtypes
    cat.StartSiteEnum
    while cat.GetNextSite:
        site_name = str(cat.SiteName.encode('ascii', 'ignore').decode())
        if sites is None:
            pass
        elif site_name in sites:
            pass
        else:
            continue
        while cat.GetNextDataSource:
            ds_name = str(cat.DataSource.encode('ascii', 'ignore').decode())
            try:
                start1 = pytime_to_datetime(cat.DataStartTime)
                end1 = pytime_to_datetime(cat.DataEndTime)
            except ValueError:
                bool_site = dfile.FromSite(site_name, ds_name, 1)
                if bool_site:
                    start1 = pytime_to_datetime(cat.DataStartTime)
                    end1 = pytime_to_datetime(cat.DataEndTime)
                else:
                    print('No site data for ' + site_name + '...for some reason...')
            while cat.GetNextMeasurement:
                mtype1 = str(cat.Measurement.encode('ascii', 'ignore').decode())
                if mtype1 == 'Item2':
                    continue
                elif mtypes is None:
                    pass
                elif mtype1 in mtypes:
                    pass
                else:
                    continue
                divisor = cat.Divisor
                unit1 = str(cat.Units.encode('ascii', 'ignore').decode())
                if unit1 == '%':
#                    print('Site ' + name1 + ' has no units')
                    unit1 = ''
                sites_lst.append([site_name, ds_name, mtype1, unit1, divisor, str(start1), str(end1)])

    sites_df = DataFrame(sites_lst, columns=['site', 'data_source', 'mtype', 'unit', 'divisor', 'start_date', 'end_date'])
    if rem_wq_sample:
        sites_df = sites_df[~(sites_df.mtype == 'WQ Sample')]
    dfile.Close()
    cat.Close()
    return sites_df


def get_data_quantity(hts, sites=None, mtypes=None, start=None, end=None, agg_period=None, agg_n=1, fun=None, output_site_data=False, exclude_mtype=None, sites_df=None):
    """
    Function to read water quantity data from an hts file.

    Parameters
    ----------
    hts : str
        Path to the hts file.
    sites : list
        A list of site names within the hts file.
    mtypes : list
        A list of measurement types that should be returned.
    start : str
        The start date to retreive from the data in ISO format (e.g. '2011-11-30 00:00').
    end : str
        The end date to retreive from the data in ISO format (e.g. '2011-11-30 00:00').
    agg_period : str
        The resample period (e.g. 'day', 'month').
    agg_n : int
        The number of periods (e.g. 1 for 1 day).
    fun : str
        The resampling function.
    output_site_data : bool
        Should the sites data be output?
    sites_df : DataFrame
        The DataFrame return from the rd_hilltop_sites function. If this is passed than rd_hilltop_sites is not run.

    Returns
    -------
    DataFrame
    """

    agg_name_dict = {'sum': 4, 'count': 5, 'mean': 1}
    agg_unit_dict = {'l/s': 1, 'm3/s': 1, 'm3/hour': 1, 'mm': 1, 'm3': 4}
    unit_convert = {'l/s': 0.001, 'm3/s': 1, 'm3/hour': 1, 'mm': 1, 'm3': 1}

    ### First read all of the sites in the hts file and select the ones to be read
    if not isinstance(sites_df, DataFrame):
        sites_df = measurement_list(hts, sites=sites, mtypes=mtypes)
    sites_df = sites_df[sites_df.unit.isin(list(agg_unit_dict.keys()))]
    if isinstance(exclude_mtype, list):
        sites_df = sites_df[~sites_df.mtype.isin(exclude_mtype)]

    ### Select out the sites/mtypes within the date range
    if isinstance(start, str):
        sites_df = sites_df[sites_df.end_date >= start]
    if isinstance(end, str):
        sites_df = sites_df[sites_df.start_date <= end]

    ### Open the hts file
    dfile = Dispatch("Hilltop.DataRetrieval")
    try:
        dfile.Open(hts)
    except ValueError:
        print(dfile.errmsg)

    ### Iterate through he hts file
    df_lst = []
    for i in sites_df.index:
        site = sites_df.loc[i, 'site']
        mtype = sites_df.loc[i, 'mtype']
        unit = sites_df.loc[i, 'unit']
        if fun is None:
            agg_val = agg_unit_dict[unit]
        else:
            agg_val = agg_name_dict[fun]
        if dfile.FromSite(site, mtype, 1):

            ## Set up start and end times and aggregation initiation
            start_time = pytime_to_datetime(dfile.DataStartTime)
            end_time = pytime_to_datetime(dfile.DataEndTime)
            if (start_time.year < 1900) | (end_time.year < 1900):
                print('Site ' + site + ' has a start or end time prior to 1900')
                continue
            if (start is None):
                if (agg_period is not None):
                    start1 = str(to_datetime(start_time).ceil(str(agg_n) + time_switch(agg_period)))
                else:
                    start1 = dfile.DataStartTime
            else:
                start1 = start
            if end is None:
                end1 = dfile.DataEndTime
            else:
                end1 = end
            if not dfile.FromTimeRange(start1, end1):
                continue
            if (agg_period is not None):
                dfile.SetMode(agg_val, str(agg_n) + ' ' + agg_period)

            ## Extract data
            data = []
            time = []
            if dfile.getsinglevbs == 0:
                t1 = dfile.value
                if isinstance(t1, str):
                    print('site ' + site + ' has nonsense data')
                else:
                    data.append(t1)
                    time.append(str(pytime_to_datetime(dfile.time)))
                    while dfile.getsinglevbs != 2:
                        data.append(dfile.value)
                        time.append(str(pytime_to_datetime(dfile.time)))
                    if data:
                        df_temp = DataFrame({'time': time, 'data': data, 'site': site, 'mtype': mtype})
                        df_lst.append(df_temp)

    dfile.Close()
    if df_lst:
        df1 = concat(df_lst)
        df1.loc[:, 'time'] = to_datetime(df1.loc[:, 'time'])
        df2 = df1.set_index(['mtype', 'site', 'time']).data * unit_convert[unit]
    else:
        df2 = DataFrame([], index=['mtype', 'site', 'time'])
    if output_site_data:
        return df2, sites_df
    else:
        return df2


def get_data_quality(hts, sites=None, mtypes=None, start=None, end=None, dtl_method=None, output_site_data=False, mtype_params=None, sample_params=None, sites_df=None):
    """
    Function to read water quality data from an hts file.

    Parameters
    ----------
    hts : str
        Path to the hts file.
    sites : list
        A list of site names within the hts file.
    mtypes : list
        A list of measurement types that should be returned.
    start : str
        The start date to retreive from the data in ISO format (e.g. '2011-11-30 00:00').
    end : str
        The end date to retreive from the data in ISO format (e.g. '2011-11-30 00:00').
    dtl_method : None, 'standard', 'trend'
        The method to use to convert values under a detection limit to numeric. None does no conversion. 'standard' takes half of the detection limit. 'trend' is meant as an output for trend analysis with includes an additional column dtl_ratio referring to the ratio of values under the detection limit.
    output_site_data : bool
        Should the site data be output?
    sites_df : DataFrame
        The DataFrame return from the rd_hilltop_sites function. If this is passed than rd_hilltop_sites is not run.

    Returns
    -------
    DataFrame
    """

    ### First read all of the sites in the hts file and select the ones to be read
    if not isinstance(sites_df, DataFrame):
        sites_df = measurement_list(hts, sites=sites, mtypes=mtypes, rem_wq_sample=False)

    ### Select out the sites/mtypes within the date range
    if isinstance(start, str):
        sites_df = sites_df[sites_df.end_date >= start]
    if isinstance(end, str):
        sites_df = sites_df[sites_df.start_date <= end]

    ### Open the hts file
    wqr = Dispatch("Hilltop.WQRetrieval")
    dfile = Dispatch("Hilltop.DataFile")
    try:
        dfile.Open(hts)
    except ValueError:
        print(dfile.errmsg)

    ### Iterate through he hts file
    df_lst = []
    for i in sites_df.index:
        site_data = sites_df.loc[i]
        site = site_data['site']
        mtype = site_data['mtype']
        if mtype == 'WQ Sample':
            continue
        wqr = dfile.FromWQSite(site, mtype)

        ## Set up start and end times and aggregation initiation
        if start is None:
            start1 = wqr.DataStartTime
        else:
            start1 = pywintypes.TimeType.strptime(start, '%Y-%m-%d')
        if end is None:
            end1 = wqr.DataEndTime
        else:
            end1 = pywintypes.TimeType.strptime(end, '%Y-%m-%d')

        if not wqr.FromTimeRange(start1, end1):
            continue

        ## Extract data
        data = []
        time = []
        sample_p = []

        test_params = sites_df[sites_df.site == site].mtype.unique()
        if ('WQ Sample' in test_params) & (isinstance(mtype_params, list) | isinstance(sample_params, list)):
            mtype_p = []
            while wqr.GetNext:
                data.append(str(wqr.value.encode('ascii', 'ignore').decode()))
                time.append(str(pytime_to_datetime(wqr.time)))
                sample_p.append({sp: str(wqr.params(sp).encode('ascii', 'ignore').decode()) for sp in sample_params})
                mtype_p.append({mp: str(wqr.params(mp).encode('ascii', 'ignore').decode()) for mp in mtype_params})
        else:
            while wqr.GetNext:
                data.append(str(wqr.value.encode('ascii', 'ignore').decode()))
                time.append(str(pytime_to_datetime(wqr.time)))

        if data:
            df_temp = DataFrame({'time': time, 'data': data, 'site': site, 'mtype': mtype})
            if sample_p:
                df_temp = concat([df_temp, DataFrame(sample_p), DataFrame(mtype_p)], axis=1)
            df_lst.append(df_temp)

    dfile.Close()
    wqr.close()
    if df_lst:
        data = concat(df_lst)
        data.loc[:, 'time'] = to_datetime(data.loc[:, 'time'])
        data1 = to_numeric(data.loc[:, 'data'], errors='coerce')
        data.loc[data1.notnull(), 'data'] = data1[data1.notnull()]
        data = data.reset_index(drop=True)

        #### Convert detection limit values
        if dtl_method is not None:
            less1 = data['data'].str.match('<')
            if less1.sum() > 0:
                less1.loc[less1.isnull()] = False
                data2 = data.copy()
                data2.loc[less1, 'data'] = to_numeric(data.loc[less1, 'data'].str.replace('<', ''), errors='coerce') * 0.5
                if dtl_method == 'standard':
                    data3 = data2
                if dtl_method == 'trend':
                    df1 = data2.loc[less1]
                    count1 = data.groupby('mtype')['data'].count()
                    count1.name = 'tot_count'
                    count_dtl = df1.groupby('mtype')['data'].count()
                    count_dtl.name = 'dtl_count'
                    count_dtl_val = df1.groupby('mtype')['data'].nunique()
                    count_dtl_val.name = 'dtl_val_count'
                    combo1 = concat([count1, count_dtl, count_dtl_val], axis=1, join='inner')
                    combo1['dtl_ratio'] = (combo1['dtl_count'] / combo1['tot_count']).round(2)

                    ## conditionals
                    param2 = combo1[(combo1['dtl_ratio'] > 0.4) & (combo1['dtl_val_count'] != 1)]
                    over_40 = data['mtype'].isin(param2.index)

                    ## Calc detection limit values
                    data3 = merge(data, combo1['dtl_ratio'].reset_index(), on='mtype', how='left')
                    data3.loc[:, 'data_dtl'] = data2['data']

                    max_dtl_val = data2[over_40 & less1].groupby('mtype')['data'].transform('max')
                    max_dtl_val.name = 'dtl_data_max'
                    data3.loc[over_40 & less1, 'data_dtl'] = max_dtl_val
            else:
                data3 = data
        else:
            data3 = data

        if output_site_data:
            sites_df = sites_df[~(sites_df.mtype == 'WQ Sample')]
            return data3, sites_df
        else:
            return data3


def write_wq_data(hts, data):
    """
    Function to write water quality data to Hilltop hts files.

    Parameters
    ------------
    hts : str
        Path to the hts file to write to.
    data : dict
        A dictionary of the data in the following example structure
        {'SQ00001': {'2000-01-01 12:00:00': {'SiteParameter':
                                   {'Sample ID': '174759302',
                                    'Project': 'BPStreams'
                                    }
                               'Measurement':
                                   {'Conductivity (Field)':
                                        {'Value': '18.59',
                                         'MethodText': 'Unknown meter',
                                         'Lab': 'Field'
                                         }
                                        }
                                       }
                     }
         }

    Returns
    -------
    None
    """
    for s in data:
        print(s)
        dfile = Dispatch("Hilltop.WQInput")
        try:
            dfile.Open(hts)
        except ValueError:
            print(dfile.ErrorMsg)

        for d in data[s]:
            # print(d)
            q1 = data[s][d]

            dfile.PutSample(s, d) # Initialize the site and time
            if 'SiteParameter' in q1:
                sp4 = q1['SiteParameter']
                for key, val in sp4.items():
                    dfile.SetParam(key, val) # set the sample paremters, not associated with measurement types
            if 'Measurement' in q1:
                m1 = q1['Measurement']
                for key, val in m1.items():
                    dup = val.copy()
                    dfile.PutMeasurement(key, dup.pop('Value')) # Set a measurement value
                    if dup:
                        for mp, mpval in dup.items():
                            dfile.SetParam(mp, mpval) # sample parameters associated with the measurement parameter

        if len(dfile.ErrorMsg) > 0:
            raise ValueError(dfile.ErrorMsg)
        else:
            dfile.Close()   # commit data to the hts file
