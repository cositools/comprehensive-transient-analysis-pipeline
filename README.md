# comprehensive-transient-analysis-pipeline
The repository for the COSI comprehensive pipeline.

# INSTALLATION
Install in the same way as the fast pipeline. Substitute only "fast" -> "comprehensive" whenever needed.
Uses official cosipy now.

# AFTER THE INSTALLATION IS SUCCESSFUL.

How to test this first version:

1) create under 
	../cosiflow/data/
	the ICD directory structure (as of Nov. 2026):

	Go to comprehensive-transient-analysis-pipeline/ 
	directory and run:

	./setup_directory.sh YYYY MM DD DD_FR directoryName

	where the parameters are year month day day_fraction (000 to 999) and the directory where you want to add the new directory structure
	The baseline you should choose is ../cosiflow/data/.

2) Copy the test files with the devoted script:
        Go to comprehensive-transient-analysis-pipeline/ 
        directory and run (for example):

        ./copy_data.sh examplesForTest/evt1002/ ../cosiflow/data/obs/2028_01/280101/gct/ data_grbdc3_full.fits
	
	This will copy all the data and config files you need from the example evt1002. Use as destination directory the gct/ directory...

	Rember: now the pipeline will automatically update all the configurations inside the yaml files depending on the names of the data structure.
        By-hand name configurations change should not be needed anymore.
	Provide a baseline config (as the ones from the examples) and the pipeline should do everything is needed.

3) Put  
	FullSet_gamma_50ms.fits
	and
	FullSet_proton_50ms.fits
	../cosiflow/data/obs/YYYY_MM/YYMMDD/acs/

	Fits files converted from E. Neights simulations.

4) Put:

	-Total_BG_without_SAAcomponent_3months_unbinned_data_filtered_with_SAAcut.fits

	-ResponseContinuum.o3.e100_10000.b10log.s10396905069491.m2284.filtered.nonsparse.binnedimaging.imagingresponse.h5

	-DC3_final_530km_3_month_with_slew_1sbins_GalacticEarth_SAA.ori

	(I don't upload these three files since they belong to the DC files. In case, for whatever reason,  you need to test with my files just ask...)

	under
	../cosiflow/data/obs/YYYY_MM/YYMMDD/auxil/

	You shold still copy these files by hand since I don't want to cp too many times ~20 GB files.

	I provided several examples for testing purposes.
	Check at the bottom what such events are...
        Still, if you wish you can run the transient search on the full data set.
	We also have a set of external triggers (that are obviously specific for each event).

6) And finally run through the interface of cosiflow. For any problem/comment feedback is appreciated.

*) What the test files are:

	-evt 100: GRB_bn090424592 from DC4

		I put this file in three versions:

		*full data

		*downsampled0.1 (1 photon out of 10)

		*downsampled0.01 (1 photon out of 100)

	-bn110605183 from DC4

	-evt 3: is bn110605183 with a shift in time, position and some rescaled luminosity.

	-evt 14: is bn110605183 with a shift in time, position and some rescaled luminosity.

	-evt 1002: this is the first example of a transient source of 1.5 ks duration. Only for testing purposes.

	-BGO: these are the gamma and proton channels of 3 hours of E. Neights BGO simulations. 
	      A conversion to fits file is done with a modified version of N. Parmiggiani tool.
