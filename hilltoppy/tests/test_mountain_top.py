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


@pytest.mark.skip(reason='MeasurementList without site is a heavy query that often times out')
@pytest.mark.parametrize('data', [test_data1])
def test_measurement_names(data):
    m_names1 = self.get_measurement_names()
    assert len(m_names1) > 100
    assert 'MeasurementName' in m_names1.columns


@pytest.mark.parametrize('data', [test_data1])
def test_get_data1(data):
    tsdata1 = self.get_data(data['site'], data['measurement'], from_date=data['from_date'], to_date=data['to_date'])
    assert len(tsdata1) > 70


@pytest.mark.parametrize('data', [test_data1])
def test_site_list_latlong(data):
    sites = self.get_site_list(location='LatLong')
    assert len(sites) > 1000
    assert 'Latitude' in sites.columns
    assert 'Longitude' in sites.columns


@pytest.mark.parametrize('data', [test_data1])
def test_site_list_with_measurement(data):
    sites = self.get_site_list(measurement=data['measurement'])
    assert len(sites) > 1
    assert 'SiteName' in sites.columns


@pytest.mark.parametrize('data', [test_data1])
def test_site_info_multiple(data):
    two_sites = [data['site'], data['site']]
    site_data = self.get_site_info(two_sites)
    assert len(site_data) == 2
    assert 'SiteName' in site_data.columns
    assert all(site_data['SiteName'] == data['site'])


@pytest.mark.parametrize('data', [test_data1])
def test_measurement_list_with_filter(data):
    mtype_df = self.get_measurement_list(data['site'], measurement=data['measurement'])
    assert len(mtype_df) >= 1
    assert all(mtype_df['MeasurementName'].str.lower() == data['measurement'].lower())


@pytest.mark.parametrize('data', [test_data1])
def test_measurement_list_columns(data):
    mtype_df = self.get_measurement_list(data['site'])
    for col in ['SiteName', 'MeasurementName', 'From', 'To', 'DataType']:
        assert col in mtype_df.columns


@pytest.mark.parametrize('data', [test_data1])
def test_measurement_cache(data):
    self._measurements = {}
    self.get_measurement_list(data['site'])
    assert data['site'] in self._measurements
    assert len(self._measurements[data['site']]) > 0


@pytest.mark.parametrize('data', [test_data1])
def test_get_data_columns(data):
    tsdata = self.get_data(data['site'], data['measurement'], from_date=data['from_date'], to_date=data['to_date'])
    for col in ['SiteName', 'MeasurementName', 'Time', 'Value']:
        assert col in tsdata.columns
    assert np.issubdtype(tsdata['Time'].dtype, np.datetime64)
    assert all(tsdata['SiteName'] == data['site'])
    assert all(tsdata['MeasurementName'] == data['measurement'])


@pytest.mark.parametrize('data', [test_data1])
def test_get_data_quality_codes(data):
    tsdata = self.get_data(data['site'], data['measurement'], from_date=data['from_date'], to_date=data['to_date'], quality_codes=True)
    assert len(tsdata) > 70
    for col in ['SiteName', 'MeasurementName', 'Time', 'Value']:
        assert col in tsdata.columns


def test_invalid_site_raises():
    with pytest.raises(ValueError, match='not in hts file'):
        self.get_site_info('This Site Does Not Exist 12345')


def test_invalid_site_measurement_raises():
    with pytest.raises(ValueError, match='not in hts file'):
        self.get_measurement_list('This Site Does Not Exist 12345')












