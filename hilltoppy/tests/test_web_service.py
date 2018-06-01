# -*- coding: utf-8 -*-
"""
Created on Wed May 30 12:05:46 2018

@author: MichaelEK
"""
from hilltoppy.web_service import measurement_list, measurement_list_all, site_list, get_data, wq_sample_parameter_list, build_url
import pandas as pd
import re

### WQ
base_url = 'http://wateruse.ecan.govt.nz'
hts = 'WQAll.hts'
site = 'BV24/0024'
measurement = 'Nitrate Nitrogen'
from_date = '2015-01-01'
to_date = '2017-01-01'

sites = site_list(base_url, hts)
mtype_df1 = measurement_list(base_url, hts, site)

mtypes_list = []
for s in sites:
    mtype_df1 = measurement_list(base_url, hts, s)
    mtypes_list.append(mtype_df1)
mtypes_all = pd.concat(mtypes_list)

url = build_url(base_url, hts, 'MeasurementList', s)


mtype_df2 = wq_sample_parameter_list(base_url, hts, site)
tsdata1 = get_data(base_url, hts, site, measurement, from_date=from_date, to_date=to_date)
tsdata2, extra2 = get_data(base_url, hts, site, measurement, parameters=True)
tsdata3 = get_data(base_url, hts, site, 'WQ Sample')

sample_param_list = []
for s in sites:
    site_sample_param = wq_sample_parameter_list(base_url, hts, s)
    sample_param_list.append(site_sample_param)

sample_param_df = pd.concat(sample_param_list)


### Usage
base_url = 'http://wateruse.ecan.govt.nz'
hts = 'WaterUse.hts'
site = 'M36/20310-M1'
measurement = 'Compliance Volume'
from_date = '2015-01-01'
to_date = '2017-01-01'
agg_method='Total'
agg_interval='1 day'

mtype_df_all = measurement_list_all(base_url, hts)
sites = site_list(base_url, hts)
mtype_df1 = measurement_list(base_url, hts, site)

tsdata1 = get_data(base_url, hts, site, measurement, from_date=from_date, to_date=to_date, agg_method=agg_method, agg_interval=agg_interval)

test_url = build_url(base_url, hts, 'GetData', site, measurement, from_date=from_date, to_date=to_date, agg_method='Total', agg_interval='1 day')


sites = site_list(base_url, hts)
sites1 = set(i for i in sites if not re.search('\d+\.\d\d\d', i))



id1 = '2222.222'





