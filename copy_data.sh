# Copies data in the HEASARC-style directory
# origin: the directory where examples are
# destination: the gct directory (where you want the fits data file to go)
# name of file in the origin directory
# example ./copy_data.sh examplesForTest/evt1002/ ../cosiflow/data/obs/YYYY_MM/YYMMDD/gct/ data_grbdc3_full.fits

originDir=$1
destinationDir=$2
fitsFileName=$3
echo $originDir
echo $destinationDir

cp $originDir/pipeline_Comprehensive_GCT.yaml $destinationDir"/../../../../"
cp $originDir/$fitsFileName $destinationDir/data_grbdc3_full.fits
cp  $originDir"/ListOfTriggers.yaml" $destinationDir"/../auxil/"
cp  $originDir"/externalTriggerInfos"*".yaml" $destinationDir"/../auxil/"
cp  $originDir"/AnomalyDetectionConfig.yaml" $destinationDir"/../auxil/"
cp  $originDir"/CNNLocalizationConfig.yaml" $destinationDir"/../auxil/"

