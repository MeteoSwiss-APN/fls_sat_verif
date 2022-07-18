#!/bin/bash -l
set -euo pipefail

# Script for running fls_sat_verif scripts, also see GitHub
testrunid=$(date +%Y%m%d_%H%M%S)_$$

# Parameters
satstart=202112312345 # What a terrible line to read! Why no sat files at XX:00 UTC... ?
satend=202201020045
start=22010100
end=22010100
testwdir=/scratch/${LOGNAME}/tmp/wd_fls_sat_verif_${testrunid}/
expid="560"
initime="0"

# Derived parameters
yy=${start:0:2}

# Create testwdir
mkdir -p testwdir

# Prepare sat input
rbrun ~osm/bin/extract_satdata.rb -P LSCL -m c2e -p ${satstart}..${satend},1h -o ${testwdir}/sat/ -v

# Next line is commented out because symlinks are already there.
#ln -s /store/s83/bcrezee/EXP_TST/${expid}/ /store/s83/bcrezee/EXP_TST/${expid}/FCST${yy}
fls_sat_verif --retrieve_cosmo --wd ${testwdir} --start ${start} --end ${end} --interval 6 --exp_model_dir /store/s83/bcrezee/EXP_TST/${expid}/ --exp ${expid} -vvv --model c2e
fls_sat_verif --calc_fractions --wd ${testwdir} --start ${start} --end ${end} --interval 6 --max_lt 24 --exp ${expid} --extend_previous --model c2e
fls_sat_verif --plot_median_day_cycle --wd ${testwdir} --start ${start} --end ${end} --init $initime --exp ${expid}

rm -r ${testwdir}
# Any error will make the script stop execution, so if we reach this line, we can celebrate!
echo "Test was successful."
