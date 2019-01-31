How to use hilltop-py
=====================

This section will describe how to use the hilltop-py package. The functions depend heavily on the Pandas package. Nearly all outputs are either as Pandas Series or DataFrames.

Some of this documentation comes from the "Scripting.doc" file. Please look at that doc for more details about the internals.

COM module
------------
The following documentation describes how to set up and use the COM module functions.

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
The following documentation describes how to set up and use the module functions built upon the native python module.

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


Web service
-----------
The web service calls are simpler and more straightforward. No extra setup is needed other than already having a Hilltop server to query. See the doc called "server.doc" for more details about the web service calls.

Data access
~~~~~~~~~~~
The function names are the same, although the input parameters are slightly different. There is also an additional function specific to water quality samples. Below is an actual working example!

.. code:: python

    from hilltoppy import web_service as ws

    base_url = 'http://wateruse.ecan.govt.nz'
    hts = 'WQAll.hts'
    site = 'SQ31045'
    measurement = 'Total Phosphorus'
    from_date = '1983-11-22'
    to_date = '2018-04-13'
    dtl_method = 'trend'

.. ipython:: python
   :suppress:

   from hilltoppy import web_service as ws
   import pandas as pd

   pd.options.display.max_columns = 5

   base_url = 'http://wateruse.ecan.govt.nz'
   hts = 'WQAll.hts'
   site = 'SQ31045'
   measurement = 'Total Phosphorus'
   from_date = '1983-11-22'
   to_date = '2018-04-13'
   dtl_method = 'trend'

.. ipython:: python

  sites_out1 = ws.site_list(base_url, hts)
  sites_out1.head()

  sites_out2 = ws.site_list(base_url, hts, location=True)
  sites_out2.head()

  meas_df = ws.measurement_list(base_url, hts, site)
  meas_df.head()

  tsdata = ws.get_data(base_url, hts, site, measurement, from_date=from_date, to_date=to_date)
  tsdata.head()

  tsdata1 = ws.get_data(base_url, hts, site, measurement, from_date=from_date, to_date=to_date,
                        dtl_method=dtl_method)
  tsdata1.head()

  tsdata2, extra2 = ws.get_data(base_url, hts, site, measurement, parameters=True)
  tsdata2.head()
  extra2.head()

  tsdata3 = ws.get_data(base_url, hts, site, 'WQ Sample')
  tsdata3.head()

  wq_sample_df = ws.wq_sample_parameter_list(base_url, hts, site)
  wq_sample_df.head()

  # For debugging purposes - copy-paste output into internet browser
  url = ws.build_url(base_url, hts, 'MeasurementList', site)
  print(url)
