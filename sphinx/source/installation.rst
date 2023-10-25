Installation
============
Install via pip::

  pip install hilltop-py

Or conda::

  conda install -c conda-forge hilltop-py

Requirements
------------
The main dependencies are `pandas <https://pandas.pydata.org/docs/>`_, `pydantic <https://pydantic-docs.helpmanual.io/>`_, `requests <https://docs.python-requests.org>`_, and `orjson <https://github.com/ijl/orjson>`_. `pywin32 <https://github.com/mhammond/pywin32>`_ is a dependency if the user wishes to use the COM module, but it is not installed by default. pywin32 is only for a Windows OS, so the COM module requires the user to be running a Windows OS. This is also likely the case for the native python module.
