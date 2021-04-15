# -*- coding: utf-8 -*-
"""
Created on Wed May 30 12:05:46 2018

@author: MichaelEK
"""
from hilltoppy.web_service import measurement_list, site_list, get_data, wq_sample_parameter_list

### Parameters
base_url = 'http://data.ecan.govt.nz/'
hts = 'WQAll.hts'
site = 'SQ31045'
measurement = 'Total Phosphorus'
from_date = '1983-11-22 10:50'
to_date = '2018-04-13 14:05'
dtl_method = 'trend'

### Tests


def test_site_list():
    sites = site_list(base_url, hts, True)
    assert len(sites) > 9000


def test_measurement_list():
    mtype_df1 = measurement_list(base_url, hts, site)
    assert len(mtype_df1) > 30


def test_wq_sample_parameter_list():
    mtype_df2 = wq_sample_parameter_list(base_url, hts, site)
    assert len(mtype_df2) > 10


def test_get_data1():
    tsdata1 = get_data(base_url, hts, site, measurement, from_date=from_date, to_date=to_date)
    assert len(tsdata1) > 80


def test_get_data2():
    tsdata2, extra2 = get_data(base_url, hts, site, measurement, from_date=from_date, to_date=to_date, parameters=True)
    assert (len(tsdata2) > 80) & (len(extra2) > 300)


def test_get_data3():
    tsdata3 = get_data(base_url, hts, site, 'WQ Sample', from_date=from_date, to_date=to_date)
    assert len(tsdata3) > 800


def test_get_data4():
    tsdata4, extra4 = get_data(base_url, hts, site, measurement, from_date=from_date, to_date=to_date, parameters=True, dtl_method=dtl_method)
    assert (len(tsdata4) > 80) & (len(extra4) > 300) & (tsdata4.Value.dtype.name == 'float32')

