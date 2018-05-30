# -*- coding: utf-8 -*-
"""
Created on Wed May 30 12:05:46 2018

@author: MichaelEK
"""
from hilltoppy.web_service import measurement_list, measurement_list_all, site_list, get_data, wq_sample_parameter_list
import pandas as pd


base_url = 'http://wateruse.ecan.govt.nz'
hts = 'BathingAll.hts'
request = 'SiteList'
site = 'BV24/0024'
measurement = 'Nitrate Nitrogen'
from_date = '2015-01-01'
to_date = '2017-01-01'

sites = site_list(base_url, hts)
mtype_df1 = measurement_list(base_url, hts, site)
mtype_df2 = wq_sample_parameter_list(base_url, hts, site)
tsdata1 = get_data(base_url, hts, site, measurement, from_date=from_date, to_date=to_date)
tsdata2, extra2 = get_data(base_url, hts, site, measurement, parameters=True)
tsdata3 = get_data(base_url, hts, site, 'WQ Sample')


sample_param_list = []
for s in sites:
    site_sample_param = wq_sample_parameter_list(base_url, hts, s)
    sample_param_list.append(site_sample_param)

sample_param_df = pd.concat(sample_param_list)


mtype_df_all = measurement_list_all(base_url, hts)














