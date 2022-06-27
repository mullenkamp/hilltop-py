hilltop-py - Hilltop Python tools
==================================
This package contains a variety of Python functions for accessing data contained in `Hilltop <http://www.hilltop.co.nz/>`_.
You must have the Hilltop software to use this package.

There are three different modules to access Hilltop data:
  - Windows COM objects
  - Native Hilltop Python package
  - Hilltop web service

The recommended module is the web service as it is much easier to debug than the other two. The web service module is currently the only module that is maintained as I do not currently have access to a running instance of Hilltop. Only use one of the other two if your organisation has not installed/configured the Hilltop web service. Try them out and provide feedback on the `GitHub page <https://github.com/mullenkamp/hilltop-py>`_ to improve the package!

For further information about the Hilltop server, please look through the `official Hilltop server doc <https://github.com/mullenkamp/hilltop-py/raw/master/sphinx/source/docs/Hilltop_Server_Manual.doc>`_.

The GitHub repository is found `here <https://github.com/mullenkamp/hilltop-py>`_.

.. toctree::
   :maxdepth: 2
   :caption: Sections

   installation
   usage_v1
   package_references
   license-terms
