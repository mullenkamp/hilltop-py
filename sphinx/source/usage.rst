How to use hilltop-py
=====================

This section will describe how to use the hilltop-py package. The functions depend heavily on the Pandas package. Nearly all outputs are either as Pandas Series or DataFrames.

COM module
------------
The package and general usage is via the main Hyd class with the parameters shown below.

.. code-block:: python

  from pyhydllp import hyd

  ini_path = r'\\fileservices02\ManagedShares\Data\Hydstra\prod\hyd'
  dll_path = r'\\fileservices02\ManagedShares\Data\Hydstra\prod\hyd\sys\run'
  username = ''
  password = ''
  hydllp_filename = 'hydllp.dll'
  hyaccess_filename = 'Hyaccess.ini'
  hyconfig_filename = 'HYCONFIG.INI'

  hyd1 = hyd(ini_path, dll_path, hydllp_filename=hydllp_filename,
             hyaccess_filename=hyaccess_filename, hyconfig_filename=hyconfig_filename,
             username=username, password=password)

Then all of the functions can be accessed via the newly initiated hyd1 object.
The following example won't work outside of ECan:

.. code-block:: python

  sites = [70105, 69607]
  datasource = 'A'
  varfrom = 100 # the 100 code is water level
  varto = 140 # the 140 code is flow
  qual_codes = [30, 20, 10 ,11, 21, 18] # It's best to specify as hydllp can
                                        # return bad values for a qual_code 255
  from_mod_date = '2018-01-01'
  to_mod_date = '2018-03-26'

  sites_var = hyd1.get_variable_list(sites)

  print(sites_var)

  ch1 = hyd1.ts_data_changes(varto=[varfrom], sites=sites, from_mod_date=from_mod_date,
                             to_mod_date=to_mod_date)
  print(ch1)

  tsdata = hyd1.get_ts_data(sites=sites, start=from_mod_date, end=to_mod_date,
                            varfrom=varfrom, varto=varto, datasource=datasource,
                            qual_codes=qual_codes)

  print(tsdata)
