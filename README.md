# comprehensive-transient-analysis-pipeline
The repository for the COSI comprehensive pipeline.

1) Install in the same way as the comprehensive pipeline. Substitute only "fast" -> "comprehensive" whenever needed.
Warning: for the moment I download a specific version of cosipy from a repostory of Laura.

AFTER INSTALLATION IS SUCCESSFUL.

How to test this first version:
2) create under 
../cosiflow/data/
the following structure
mkdir ../cosiflow/data/obs/2025_01/250101/auxil
mkdir ../cosiflow/data/obs/2025_01/250101/ged
mkdir ../cosiflow/data/transient/2025_01/250101001t/plots
mkdir ../cosiflow/data/transient/2025_01/250101001t/products
mkdir ../cosiflow/data/transient/2025_01/250101001u/plots 
mkdir ../cosiflow/data/transient/2025_01/250101001u/products

2) Put 
data_grbdc3_full.fits
under
../cosiflow/data/obs/2025_01/250101/ged/
I can provide any simulated GRB under request. 

3) Put
Total_BG_without_SAAcomponent_3months_unbinned_data_filtered_with_SAAcut.fits
ResponseContinuum.o3.e100_10000.b10log.s10396905069491.m2284.filtered.nonsparse.binnedimaging.imagingresponse.h5
DC3_final_530km_3_month_with_slew_1sbins_GalacticEarth_SAA.ori
(I don't upload these three files since they belong to the DC files. In case, for whatever reason,  you need to test with my files just ask...)
This yes...
ListOfTriggers.txt
externalTriggerInfos1.yaml
externalTriggerInfos2.yaml
externalTriggerInfos3.yaml
AnomalyDetectionConfig.txt

under
../cosiflow/data/obs/2025_01/250101/auxil/

4) put 
pipeline_Comprehensive_GeD_2.yaml

under 
../cosiflow/data/

5) And run through the interface of cosiflow.
For any problem/comment feedback is appreciated.

