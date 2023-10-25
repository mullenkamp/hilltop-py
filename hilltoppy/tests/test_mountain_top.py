# -*- coding: utf-8 -*-
"""
Created on Wed May 30 12:05:46 2018

@author: MichaelEK
"""
import pytest
import numpy as np
from hilltoppy import Hilltop

### Parameters

base_url = 'http://hilltop.gw.govt.nz/'
hts = 'data.hts'

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
#     site = '070649M1',
#     measurement = 'Flow',
#     from_date = '2012-10-13',
#     to_date = '2012-11-01'
#     )

test_data1 = dict(
    # base_url = 'http://hilltop.gw.govt.nz/',
    # hts = 'data.hts',
    site = 'Akatarawa River at Hutt Confluence',
    collection = 'WQ / Rivers and Streams',
    measurement = 'Total Phosphorus',
    from_date = '2012-01-22 10:50',
    to_date = '2018-04-13 14:05',
    )

### Tests

self = Hilltop(base_url, hts)

def test_available_sites():
    assert len(self.available_sites) > 1000


@pytest.mark.parametrize('data', [test_data1])
def test_site_list(data):
    sites = self.get_site_list(True)
    assert len(sites) > 1000


@pytest.mark.parametrize('data', [test_data1])
def test_site_info(data):
    site_data = self.get_site_info(data['site'])
    assert len(site_data.columns) > 4


@pytest.mark.parametrize('data', [test_data1])
def test_measurement_list(data):
    mtype_df1 = self.get_measurement_list(data['site'])
    assert len(mtype_df1) > 6


@pytest.mark.parametrize('data', [test_data1])
def test_site_list_with_collection(data):
    sites = self.get_site_list(collection=data['collection'])
    assert len(sites) > 40


@pytest.mark.parametrize('data', [test_data1])
def test_collection_list(data):
    cl = self.get_collection_list()
    assert len(cl) > 180


# @pytest.mark.parametrize('data', [test_data1])
# def test_measurement_names(data):
#     m_names1 = self.get_measurement_names()
#     m_names2 = self.get_measurement_names(True)
#     assert len(m_names1) > 100


@pytest.mark.parametrize('data', [test_data1])
def test_get_data1(data):
    tsdata1 = self.get_data(data['site'], data['measurement'], from_date=data['from_date'], to_date=data['to_date'])
    assert len(tsdata1) > 70

#################################################
### Other tests
















