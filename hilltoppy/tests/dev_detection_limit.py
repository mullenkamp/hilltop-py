# -*- coding: utf-8 -*-
"""
Created on Wed May 30 12:05:46 2018

@author: MichaelEK
"""
from hilltoppy.web_service import measurement_list, site_list, get_data, wq_sample_parameter_list

### Parameters
base_url = 'http://wateruse.ecan.govt.nz'
hts = 'WQAll.hts'
site = 'SQ31045'
measurement = 'Total Phosphorus'
from_date = '1983-11-22 10:50'
to_date = '2018-04-13 14:05'
dtl_method = 'trend'

### Tests

sites = site_list(base_url, hts)

mtype_df1 = measurement_list(base_url, hts, site)

tsdata1 = get_data(base_url, hts, site, measurement, from_date=from_date, to_date=to_date)

tsdata2, extra2 = get_data(base_url, hts, site, measurement, from_date=from_date, to_date=to_date, parameters=True)

tsdata3 = get_data(base_url, hts, site, measurement, from_date=from_date, to_date=to_date, dtl_method=dtl_method)

tsdata4, extra4 = get_data(base_url, hts, site, measurement, from_date=from_date, to_date=to_date, parameters=True, dtl_method=dtl_method)
