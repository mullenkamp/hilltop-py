How to use hilltop-py
=====================

This section will describe how to use the hilltop-py package. The functions depend heavily on the Pandas package. Nearly all outputs are Pandas DataFrames.

Some of this documentation comes from the "Scripting.doc" file in the Hilltop installation folder. Please look at that doc for more details about the internals.


Web service
-----------
The web service calls are simpler and more straightforward than the other two options. No extra setup is needed other than already having a Hilltop server to query. See the doc called "server.doc" for more details about the web service calls.

Data access
~~~~~~~~~~~
The function names are based on the associated Hilltop function names from the COM module. There is also an additional function specific to water quality samples. Below are an actual working examples!

Import the module and set the appropriate parameters.


.. code:: python

    from hilltoppy import web_service as ws

    base_url = 'http://hilltop.gw.govt.nz/'
    hts = 'data.hts'
    site = 'Akatarawa River at Hutt Confluence'
    collection = 'WQ / Rivers and Streams'
    measurement = 'Total Phosphorus'
    from_date = '2012-01-22 10:50'
    to_date = '2018-04-13 14:05'

.. ipython:: python
   :suppress:

   from hilltoppy import web_service as ws
   import pandas as pd

   pd.options.display.max_columns = 5

   base_url = 'http://hilltop.gw.govt.nz/'
   hts = 'data.hts'
   site = 'Akatarawa River at Hutt Confluence'
   collection = 'WQ / Rivers and Streams'
   measurement = 'Total Phosphorus'
   from_date = '2012-01-22 10:50'
   to_date = '2018-04-13 14:05'


All data in Hilltop are stored in hts files. The top level objects in Hilltop are Sites, which can be queried by calling the site_list function. Calling it with only the base_url and hts will return all of the sites in an hts file. Adding the parameter location=True will return the Easting and Northing geographic coordinates (EPSG 2193), or location='LatLong' will return the Latitude and Longitude. There are other optional input parameters to site_list as well.


.. ipython:: python

  sites_out1 = ws.site_list(base_url, hts)
  sites_out1.head()

  sites_out2 = ws.site_list(base_url, hts, location=True)
  sites_out2.head()

  sites_out3 = ws.site_list(base_url, hts, location='LatLong',
                            measurement=measurement)
  sites_out3.head()


A Collection groups one or many Sites together and has its own function to return a dataframe of all the Sites and associated Collections. Note that not all hts files (and organisations) have collections.


.. ipython:: python

  collection1 = ws.collection_list(base_url, hts)
  collection1.head()

  sites_out4 = ws.site_list(base_url, hts, collection=collection)
  sites_out4.head()


The next step is to determine what types of Measurements are associated with the Sites. In Hilltop, a Measurement is also associated to a Data Source. Conceptually, the Data Source represents the actual observation or measurement from the source, while the Measurement is a value derived from the Data Source. In many cases, the Measurement Name and the Data Source Name are the same, but there are instances where there are multiple Measurements per Data Source. For example, a Data Source Name of "Water Level" (which normally represents a surface water level) may have a Measurement Name of both Water Level and Flow (since flow can be derived from water level). Hilltop also has the concept of Virtual Measurements. Virtual Measurements do not have data directly stored in the hts files. Rather, Hilltop simply stores the equation to convert an existing Measurement (that does contain data) into a Virtual Measurement when the user requests the data. This reduces data storage with a very minor overhead computational cost.

In Hilltop, you must make a measurement_list function request to get all of the Data Sources and the associated Measurements.

.. ipython:: python


  meas_df = ws.measurement_list(base_url, hts, site)
  meas_df.head()


Once you know the Site Name and Measurement Name you want time series data for, then you make a request via the get_data function. The get_data function has a variety of parameters. Check the doc strings or package references for more details.

.. ipython:: python


  tsdata = ws.get_data(base_url, hts, site, measurement, from_date=from_date,
                        to_date=to_date)
  tsdata.head()


If you run into an issue with your Hilltop server, you can debug via the browser by using the build_url function.

.. ipython:: python


  url = ws.build_url(base_url, hts, 'MeasurementList', site)
  print(url)


COM module
------------
The following documentation describes how to set up and use the COM module functions. The COM module is no longer maintained!

Install pywin32
~~~~~~~~~~~~~~~
pywin32 does not come installed by default. Install it like any other python package before continuing.

.. code::

  conda install pywin32


Register Hydrolib
~~~~~~~~~~~~~~~~~
Hilltop Manager needs to be added into the Windows registry. This can be done for either the 32bit or the 64bit versions of Hilltop Manager, but if you have the choice pick the 64bit version in case you need to handle very large datasets. Find either version of Hilltop Manager,  and open the program (called Manager.exe) as administrator. Load in an hts file (this allows you to access the configuration menus). Go to the tab called ‘Configure’ then go to ‘installation’. It will ask you if you want Hilltop registered, and of course say yes.

Run makepy_hilltop
~~~~~~~~~~~~~~~~~~
The COM utility must be built for hilltop to access it's functions. This is all wrapped in a single function. Once Hydrolib is properly registered, run makepy_hilltop without any parameters and you should be ready to use the COM functions.

.. code-block:: python

  from hilltoppy import com

  com.makepy_hilltop()


Data access
~~~~~~~~~~~
The function names are based on the associated Hilltop function names. Since functionally, accessing quantity data is quite different (from the COM) as compared to the quality data, there are two functions accessing the time series data.

.. code-block:: python

  from hilltoppy import com

  hts = r'\\path\to\file.hts'
  sites = ['site1', 'site2']
  mtypes = ['Total Suspended Solids']

  meas_df = com.measurement_list(hts, sites)

  tsdata = com.get_data_quality(hts, sites, mtypes)
  print(tsdata)

Native Python module
--------------------
The following documentation describes how to set up and use the module functions built upon the native python module. The Native Hilltop Python module is no longer maintained!

Python path to Hilltop.pyd
~~~~~~~~~~~~~~~~~~~~~~~~~~
First, make sure that the Hilltop.pyd exists in either the root directory of the Hilltop directory or in the x64 directory (depending on your python installation). Open manager.exe, go to configure, and click on Python. It simply adds the Python path to the windows environment variables so that Python knows where to load the Hilltop.pyd from. This can also be modified from within Spyder or the sys module.

Data access
~~~~~~~~~~~
The function names are similar to the COM module except that one function covers both quantity and quality data.

.. code-block:: python

  from hilltoppy import hilltop

  hts = r'\\path\to\file.hts'
  sites = ['site1', 'site2']
  mtypes = ['Total Suspended Solids']

  sites_out = hilltop.site_list(hts)

  meas_df = hilltop.measurement_list(hts, sites)

  tsdata = hilltop.get_data(hts, sites, mtypes)
  print(tsdata)
