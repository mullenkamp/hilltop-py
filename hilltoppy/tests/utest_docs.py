#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 12:56:09 2023

@author: mike
"""
from hilltoppy import Hilltop
import pandas as pd

pd.options.display.max_columns = 5

base_url = 'http://hilltop.gw.govt.nz/'
hts = 'data.hts'
site = 'Akatarawa River at Hutt Confluence'
collection = 'WQ / Rivers and Streams'
measurement = 'Total Phosphorus'
from_date = '2012-01-22 10:50'
to_date = '2018-04-13 14:05'


ht = Hilltop(base_url, hts)
sites_out1 = ht.get_site_list()
sites_out1.head()

sites_out2 = ht.get_site_list(location=True)
sites_out2.head()

sites_out3 = ht.get_site_list(location='LatLong',
                          measurement=measurement)
sites_out3.head()

collection1 = ht.get_collection_list()
collection1.head()

sites_out4 = ht.get_site_list(collection=collection)
sites_out4.head()

site_meas = ht.get_measurement_list(site)
site_meas.head()

meas = ht.get_measurement_names()
meas.head()

tsdata = ht.get_data(site, measurement, from_date=from_date,
                      to_date=to_date)
tsdata.head()














































