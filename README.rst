=============
fls_sat_verif
=============

Satellite-based verification of fog and low stratus forecasts

Installation
------------
1. Clone this repo
2. ``cd fls_sat_dir``
3. ``make venv install

Usage
-----
1. Prepare SAT input data: Retrieve with rubyscript
    1. Make input dir on scratch, e.g. `input_sat_verif`
    2. Run: ``rbrun ~osm/bin/extract_satdata.rb -P LSCL -m c1e -p <start>..<end>,1h -v``
        - start: e.g. 202108302345
        - end: e.g. 202112312345
        - intervall: 1h, 3h
        
2. Prepare COSMO input data: Retrieve from archive, extract TQC

* TODO

Credits
-------

This package was created with `Cookiecutter`_ and the `MeteoSwiss-APN/mch-python-blueprint`_ project template.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`MeteoSwiss-APN/mch-python-blueprint`: https://github.com/MeteoSwiss-APN/mch-python-blueprint
