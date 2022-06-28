hilltop-py - Hilltop Python tools
==================================
This package contains a variety of Python functions for accessing data contained in `Hilltop <http://www.hilltop.co.nz/>`_.
You must have the Hilltop software to use this package.

There are three different modules to access Hilltop data:
  - Windows COM objects
  - Native Hilltop Python package
  - Hilltop web service

The recommended module is the web service as it is much easier to debug than the other two. The web service module is currently the only module that is maintained as I do not have access to a running instance of Hilltop. Only use one of the other two if your organisation has not installed/configured the Hilltop web service and you're very ambitious. Try them out and provide feedback on the `GitHub page <https://github.com/mullenkamp/hilltop-py>`_ to improve the package!

A major rewrite of the web service functions has occurred for version 2, which makes the code much simpler as well as the user requests themselves. Also, there is more consistency with the terminology between Hilltop and hilltop-py as well as within the hilltop-py functions. Consequently, there are some differences that the user will need to pay attention to and update in their scripts when making requests.

Not all Data Types are currently supported. These include for example HydSection and HydFacecard. The response from the Hilltop server is very different as compared to other Data Types (and I don't really understand what they mean). If there is enough demand (or support), then I might add them.

For further information about the Hilltop server, please look through the `official Hilltop server doc <https://github.com/mullenkamp/hilltop-py/raw/master/sphinx/source/docs/Hilltop_Server_Manual.doc>`_.

The GitHub repository is found `here <https://github.com/mullenkamp/hilltop-py>`_.

.. toctree::
   :maxdepth: 2
   :caption: Sections

   installation
   usage_v2
   package_references
   license-terms
