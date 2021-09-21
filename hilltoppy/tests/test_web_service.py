# -*- coding: utf-8 -*-
"""
Created on Wed May 30 12:05:46 2018

@author: MichaelEK
"""
import pytest
import numpy as np
from hilltoppy.web_service import measurement_list, site_list, get_data, wq_sample_parameter_list

### Parameters

test_data1 = dict(
    base_url = 'http://data.ecan.govt.nz/',
    hts = 'WQAll.hts',
    site = 'SQ31045',
    measurement = 'Total Phosphorus',
    from_date = '1983-11-22 10:50',
    to_date = '2018-04-13 14:05',
    dtl_method = 'trend'
    )

# test_data2 = dict(
#     base_url = 'https://data.hbrc.govt.nz/Envirodata',
#     hts = 'ContinuousArchive.hts',
#     site = 'Well.16772 Ngatarawa Rd',
#     measurement = 'Elevation Above Sea Level[Recorder Water Level]',
#     from_date = '2018-10-13',
#     to_date = '2018-11-01'
#     )


### Tests

@pytest.mark.parametrize('data', [test_data1])
def test_site_list(data):
    sites = site_list(data['base_url'], data['hts'], True)
    assert len(sites) > 1000


@pytest.mark.parametrize('data', [test_data1])
def test_measurement_list(data):
    mtype_df1 = measurement_list(data['base_url'], data['hts'], data['site'])
    assert len(mtype_df1) > 6


@pytest.mark.parametrize('data', [test_data1])
def test_wq_sample_parameter_list(data):
    mtype_df2 = wq_sample_parameter_list(data['base_url'], data['hts'], data['site'])
    assert len(mtype_df2) > 10


@pytest.mark.parametrize('data', [test_data1])
def test_get_data1(data):
    tsdata1 = get_data(data['base_url'], data['hts'], data['site'], data['measurement'], from_date=data['from_date'], to_date=data['to_date'])
    assert len(tsdata1) > 80


@pytest.mark.parametrize('data', [test_data1])
def test_get_data2(data):
    tsdata2, extra2 = get_data(data['base_url'], data['hts'], data['site'], data['measurement'], from_date=data['from_date'], to_date=data['to_date'], parameters=True)
    assert (len(tsdata2) > 80) & (len(extra2) > 300)


@pytest.mark.parametrize('data', [test_data1])
def test_get_data3(data):
    tsdata3 = get_data(data['base_url'], data['hts'], data['site'], 'WQ Sample', from_date=data['from_date'], to_date=data['to_date'])
    assert len(tsdata3) > 800


@pytest.mark.parametrize('data', [test_data1])
def test_get_data4(data):
    tsdata4, extra4 = get_data(data['base_url'], data['hts'], data['site'], data['measurement'], from_date=data['from_date'], to_date=data['to_date'], parameters=True, dtl_method=data['dtl_method'])
    assert (len(tsdata4) > 80) & (len(extra4) > 300) & (tsdata4.Value.dtype == np.number)
