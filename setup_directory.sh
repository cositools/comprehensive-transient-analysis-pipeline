# Only for the developmenta phase...
# Creates the HEASARC data structure as defined in
# ICD Nov 2026
# run as ./setup_directory.sh year month day day_fraction directory
# Creates the structure of directories for the acquisition.
# For the source directory, for the moment, adds only the Crab Nebula...
# year, month, day refer to the time you put your data (arbitrary choice for the moment)
# It works from the comprehensive-transient-analysis-pipeline/ directory...

year=$1
month=$2
day=$3
day_fraction=$4
base_dir=$5

year_short=`echo $year | cut -c 3-4`
echo $year_short

mkdir -p $base_dir
# obs #############################
obs_dir=$base_dir/obs
mkdir -p $obs_dir

month_dir=$obs_dir/$year\_$month
mkdir -p $month_dir

month_dir_2=$month_dir/$year_short$month$day
mkdir -p $month_dir_2
mkdir -p $month_dir_2/auxil
mkdir -p $month_dir_2/gct
mkdir -p $month_dir_2/acs
mkdir -p $month_dir_2/bto

# trigger ##############################
obs_dir=$base_dir/trigger
mkdir -p $obs_dir

month_dir=$obs_dir/$year\_$month
mkdir -p $month_dir

month_dir_2=$month_dir/$year_short$month$day$day_fraction
mkdir -p $month_dir_2

current_dir=$month_dir_2/current
previous_dir=$month_dir_2/previous
mkdir -p $current_dir
mkdir -p $previous_dir
mkdir -p $current_dir/products
mkdir -p $current_dir/plots
mkdir -p $previous_dir/products
mkdir -p $previous_dir/plots


# transient ###############################
obs_dir=$base_dir/transient
mkdir -p $obs_dir

month_dir=$obs_dir/$year\_$month
mkdir -p $month_dir

month_dir_2=$month_dir/$year_short$month$day$day_fraction\t
mkdir -p $month_dir_2

current_dir=$month_dir_2/current
previous_dir=$month_dir_2/previous
mkdir -p $current_dir
mkdir -p $previous_dir
mkdir -p $current_dir/products
mkdir -p $current_dir/plots
mkdir -p $previous_dir/products
mkdir -p $previous_dir/plots

month_dir_2=$month_dir/$year_short$month$day$day_fraction\u
mkdir -p $month_dir_2

current_dir=$month_dir_2/current
previous_dir=$month_dir_2/previous
mkdir -p $current_dir
mkdir -p $previous_dir
mkdir -p $current_dir/products
mkdir -p $current_dir/plots
mkdir -p $previous_dir/products
mkdir -p $previous_dir/plots

# source ##############################
obs_dir=$base_dir/source
mkdir -p $obs_dir

# add coordinates for Crab pulsar (just for testing the structure)
source_dir=$obs_dir/0534S2200
mkdir -p $source_dir

mkdir -p $source_dir/current
mkdir -p $source_dir/previous
mkdir -p $source_dir/$year\_$month

# maps ##############################
obs_dir=$base_dir/maps
mkdir -p $obs_dir

# add some map...
mkdir -p $obs_dir/511
mkdir -p $obs_dir/al_26
mkdir -p $obs_dir/fe_60
mkdir -p $obs_dir/ti_44
mkdir -p $obs_dir/continuum



