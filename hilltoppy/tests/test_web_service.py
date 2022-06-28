# -*- coding: utf-8 -*-
"""
Created on Wed May 30 12:05:46 2018

@author: MichaelEK
"""
import pytest
import numpy as np
from hilltoppy.web_service import measurement_list, site_list, collection_list, get_data, site_info

### Parameters

# test_data1 = dict(
#     base_url = 'http://data.ecan.govt.nz/',
#     hts = 'WQAll.hts',
#     site = 'SQ31045',
#     collection = 'LWRPLakes',
#     measurement = 'Total Phosphorus',
#     from_date = '1983-11-22 10:50',
#     to_date = '2018-04-13 14:05',
#     dtl_method = 'trend'
#     )

# test_data2 = dict(
#     base_url = 'https://data.hbrc.govt.nz/Envirodata',
#     hts = 'ContinuousArchive.hts',
#     site = 'Well.16772 Ngatarawa Rd',
#     collection = 'Stage',
#     measurement = 'Elevation Above Sea Level[Recorder Water Level]',
#     from_date = '2018-10-13',
#     to_date = '2018-11-01'
#     )

# test_data2 = dict(
#     base_url = 'https://data.hbrc.govt.nz/Envirodata',
#     hts = 'data.hts',
#     site = 'Akatarawa River at Cemetery',
#     measurement = 'Flow',
#     from_date = '2018-10-13',
#     to_date = '2018-11-01'
#     )

test_data1 = dict(
    base_url = 'http://hilltop.gw.govt.nz/',
    hts = 'data.hts',
    site = 'Akatarawa River at Hutt Confluence',
    collection = 'WQ / Rivers and Streams',
    measurement = 'Total Phosphorus',
    from_date = '2012-01-22 10:50',
    to_date = '2018-04-13 14:05',
    )

### Tests

@pytest.mark.parametrize('data', [test_data1])
def test_site_list(data):
    sites = site_list(data['base_url'], data['hts'], True)
    assert len(sites) > 1000


@pytest.mark.parametrize('data', [test_data1])
def test_site_info(data):
    site_data = site_info(data['base_url'], data['hts'], data['site'])
    assert len(site_data.columns) > 10


@pytest.mark.parametrize('data', [test_data1])
def test_measurement_list(data):
    mtype_df1 = measurement_list(data['base_url'], data['hts'], data['site'])
    assert len(mtype_df1) > 6


@pytest.mark.parametrize('data', [test_data1])
def test_site_list_with_collection(data):
    sites = site_list(data['base_url'], data['hts'], collection=data['collection'])
    assert len(sites) > 40


@pytest.mark.parametrize('data', [test_data1])
def test_collection_list(data):
    cl = collection_list(data['base_url'], data['hts'])
    assert len(cl) > 180


@pytest.mark.parametrize('data', [test_data1])
def test_get_data1(data):
    tsdata1 = get_data(data['base_url'], data['hts'], data['site'], data['measurement'], from_date=data['from_date'], to_date=data['to_date'])
    assert len(tsdata1) > 70
