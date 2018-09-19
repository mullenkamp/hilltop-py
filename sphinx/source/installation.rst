Installation
============
Install via pip::

  pip install hilltop-py

Or conda::

  conda install -c mullenkamp hilltop-py

Requirements
------------
The main dependencies are `Pandas <http://pandas.pydata.org/pandas-docs/stable/>`_, `requests <http://docs.python-requests.org>`_. `pywin32 <https://github.com/mhammond/pywin32>`_ is a dependency if the user wishes to use the COM module, but it is not installed by default. pywin32 is only for a Windows OS, so the COM module requires the user to be running a Windows OS. This is also likely the case for the native python module.

The three different access modules have their own sets of requirements to run properly. See the section "How to use Hilltop-py" on the specifics.
