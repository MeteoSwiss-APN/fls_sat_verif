=============
fls_sat_verif
=============

Satellite-based verification of fog and low stratus forecasts

Installation
------------
1. Clone this repo
2. ``cd fls_sat_verif``
3. ``make venv install``

Usage
-----
1. Prepare SAT input data: Retrieve with rubyscript
    1. Make input dir on scratch, e.g. ``$SCRATCH/input_sat_verif/sat``
    2. Run: ``rbrun ~osm/bin/extract_satdata.rb -P LSCL -m c1e -p <start>..<end>,1h -v``
        - start: e.g. 202108302345
        - end: e.g. 202112312345
        - intervall: 1h, 3h
        ! The satellite files are available at :45 only!
    3. Manually check whether files are available, if many files are missing, get in contact with Uli Hamann & Daniel Leuenberger
        
2. Prepare COSMO input data: Retrieve from archive, extract TQC

``conda activate fls_sat_verif``

``fls_sat_verif --retrieve_cosmo --start YYMMDDHH --end YYMMDDHH --interval HH --model_dir $SCRATCH/input_sat_verif/tqc``

3. Calculate FLS fractions

``fls_sat_verif --calc_fractions --start YYMMDDHH --end YYMMDDHH --interval HH --max_lt HH
--obs_dir $SCRATCH/input_sat_verif/sat
--model_dir $SCRATCH/input_sat_verif/tqc
--fls_dir $SCRATCH/input_sat_verif/fls
--extend_previous``



Credits
-------

This package was created with `Cookiecutter`_ and the `MeteoSwiss-APN/mch-python-blueprint`_ project template.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`MeteoSwiss-APN/mch-python-blueprint`: https://github.com/MeteoSwiss-APN/mch-python-blueprint
