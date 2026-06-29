import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import os
import subprocess
import time
import warnings
import yaml
from typing import Any

from matplotlib.lines import Line2D

EXTERNAL_PYTHON = "/home/gamma/envs/cosipy_laura/bin/python"
def execute_bindata_grb(cosipy_yaml_input,lib_dir):
    import cosipy
    from cosipy.pipeline.task.task import cosi_bindata
    import subprocess
    from yayc import Configurator    
    print('Binning source')
    
    full_config = Configurator.open(cosipy_yaml_input)
    t_scan_start_source=full_config["general_pipeline_config"]["t_scan_start_source"]
    t_scan_stop_source=full_config["general_pipeline_config"]["t_scan_stop_source"]
    directory_output =full_config["general_pipeline_config"]["directory_output"]
     
    args=['--config',cosipy_yaml_input,'--config_group','bindata_soubk','--overwrite', '--suffix','galbk_grbdc3','--output-dir',directory_output,'--tmin', str(t_scan_start_source), '--tmax', str(t_scan_stop_source)]
    cosi_bindata (argv=args)
    
def execute_bindata_background(cosipy_yaml_input,lib_dir):
    import cosipy
    from cosipy.pipeline.task.task import cosi_bindata
    import subprocess
    from yayc import Configurator
    print('Binning background ')
    
    full_config = Configurator.open(cosipy_yaml_input)
    t_scan_start_back=full_config["general_pipeline_config"]["t_scan_start_back"]
    t_scan_stop_back=full_config["general_pipeline_config"]["t_scan_stop_back"]
    directory_output =full_config["general_pipeline_config"]["directory_output"]
     
    args=['--config',cosipy_yaml_input,'--config_group','bindata_bk','--overwrite', '--suffix','Background_Model','--output-dir',directory_output,'--tmin', str(t_scan_start_back), '--tmax', str(t_scan_stop_back)]
    cosi_bindata (argv=args)


def execute_tsmap_scan(cosipy_yaml_input,lib_dir):
    import cosipy
    import subprocess
    from contextlib import redirect_stdout
    from cosipy.pipeline.task.task import cosi_tsdetect
    from yayc import Configurator
    full_config = Configurator.open(cosipy_yaml_input)

    t_scan_start_source=full_config["general_pipeline_config"]["t_scan_start_source"]
    t_scan_stop_source=full_config["general_pipeline_config"]["t_scan_stop_source"]
    t_scan_delta=full_config["general_pipeline_config"]["t_scan_delta"]
    directory_output =full_config["general_pipeline_config"]["directory_output"]

    subprocess.run('mkdir '+directory_output+'timescan', shell=True)

    fileNum=0
    print('|||||||||||||||||||||||||||||||||||||||||||||||',t_scan_start_source,t_scan_stop_source,t_scan_delta)
    for time in range(t_scan_start_source,t_scan_stop_source,t_scan_delta):
        outputFile=directory_output+'timescan/cosi-tsdetect_' + str(time) + '.txt'
        newpngFileName=directory_output+'timescan/raw_ts_' + str(time) + '.png'
        tstart=time
        tstop=time+t_scan_delta
        print('################ ',time)
        args=['--config',cosipy_yaml_input,'--output-dir',directory_output+'timescan','--overwrite','--tstart', str(tstart), '--tstop', str(tstop)]
        with open(outputFile, "w") as f:
            with redirect_stdout(f):
                print('cosi_tsdetect begin')
                cosi_tsdetect (argv=args)
                print('cosi_tsdetect end')
                subprocess.run('mv '+directory_output+'timescan/raw_ts.png '+newpngFileName, shell=True)
        fileNum+=1


def execute_tsmap_external(cosipy_yaml_input,lib_dir):
    import cosipy
    from contextlib import redirect_stdout
    from cosipy.pipeline.task.task import cosi_tsdetect
    import subprocess
    
    import sys
    sys.path.append(lib_dir)

    from funzioni_comuni import read_trigger_content_multiple_yaml
    
    from yayc import Configurator
    full_config = Configurator.open(cosipy_yaml_input)
    trigger_list=full_config["general_pipeline_config"]["external_trigger_list"]
    directory_output =full_config["general_pipeline_config"]["directory_output"]

    externalTrigger_start,externalTrigger_stop,flag_trigger = read_trigger_content_multiple_yaml(lib_dir,trigger_list)

    for numFileTrigg in range(flag_trigger):
        externalTrigger_start_tmp=int(externalTrigger_start[numFileTrigg])
        externalTrigger_stop_tmp=int(externalTrigger_stop[numFileTrigg])
        print(externalTrigger_start_tmp,externalTrigger_stop_tmp)
        
        outputFile=directory_output+'cosi-tsdetect_' + str(externalTrigger_start_tmp) + '.txt'
        newpngFileName=directory_output+'raw_ts_' + str(externalTrigger_start_tmp) + '.png'
    
        args=['--config',cosipy_yaml_input,'--output-dir',directory_output,'--overwrite','--tstart', str(externalTrigger_start_tmp), '--tstop', str(externalTrigger_stop_tmp)]
        with open(outputFile, "w") as f:
            with redirect_stdout(f):
                cosi_tsdetect (argv=args)
                subprocess.run('mv '+directory_output+'raw_ts.png '+newpngFileName, shell=True)

def anomaly_detection_autoencoder(cosipy_yaml_input,lib_dir):
    import cosipy
    import torch
    import torch.nn as nn
    import subprocess
    from contextlib import redirect_stdout
    import matplotlib.pyplot as plt
    import numpy as np
    from cosipy.pipeline.task.task import cosi_tsdetect
    from cosipy.pipeline.src.io import load_ori
    import sys
    sys.path.append(lib_dir)
    import healpy as hp
    from funzioni_comuni import read_base_pipeline_params,read_file_histo,read_anomaly_detection_config
    from models import Autoencoder
    from astropy.time import Time
    from histpy import Histogram
    from mhealpy import HealpixMap
    from scoords import SpacecraftFrame

    from yayc import Configurator
    full_config = Configurator.open(cosipy_yaml_input)
    t_scan_start_source=full_config["general_pipeline_config"]["t_scan_start_source"]
    t_scan_stop_source=full_config["general_pipeline_config"]["t_scan_stop_source"]
    t_scan_delta=full_config["general_pipeline_config"]["t_scan_delta"]
    directory_output =full_config["general_pipeline_config"]["directory_output"]
    anomaly_config =full_config["general_pipeline_config"]["anomaly_config"]
    ori_file2 = full_config["general_pipeline_config"]["ori_file"]

    criterion = nn.CrossEntropyLoss()

    input_file_name,model_file,resolutionImage,timeBin,plotting_window,ori_file,true_b,true_l,threshold_loss,out_file=read_anomaly_detection_config(anomaly_config)
    
    FileName=directory_output+"FileOut_test_back_full_backgr"
    numberEventstest=1
    t0_test=0
    
    data_full     = Histogram.open(str(input_file_name))
    binNumTime = int(data_full.project('Time').nbins)
    imagePlotX_Z_t_test = read_file_histo(data_full,t0_test,t0_test+binNumTime,resolutionImage,binNumTime,FileName,binNumTime,numberEventstest)

    model = Autoencoder()
    state = torch.load(lib_dir+str(model_file))
    model.load_state_dict(state)

    lossTensor = torch.zeros(int(binNumTime))
    frameNum = torch.zeros(int(binNumTime))
    
    lossMap_3D_tmp = torch.zeros((numberEventstest,resolutionImage,resolutionImage,resolutionImage,int(binNumTime)))
    signalMap_3D_tmp = torch.zeros((numberEventstest,resolutionImage,resolutionImage,resolutionImage,int(binNumTime)))
    modelMap_3D_tmp = torch.zeros((numberEventstest,resolutionImage,resolutionImage,resolutionImage,int(binNumTime)))

    max_loss=0
    max_loss_time=-1
    time_detection_first=-1
    time_detection_last=-1

    for t in range(0,binNumTime):
        image_for_input = imagePlotX_Z_t_test[:,:,:,:,int(t)]
        outTEST=model(image_for_input)
        lossPlot = criterion(outTEST,image_for_input)
        frameNum[int(t)]=int(t)
        lossTensor[int(t)]=float(lossPlot)
        outClone=outTEST.clone()
        imageClone=image_for_input.clone()
        lossMap_3D_tmp[0:1,:,:,:,int(t)] += (outClone - imageClone)**2
        signalMap_3D_tmp[0:1,:,:,:,int(t)] += imageClone
        modelMap_3D_tmp[0:1,:,:,:,int(t)] += outClone
        if lossPlot>threshold_loss:
            time_detection_last=t
            if time_detection_first==-1:
                time_detection_first=t
        
        if lossPlot>max_loss:
            max_loss=lossPlot
            max_loss_time = int(t)

    # save the timing of the transient
    fout_trigg= open(directory_output+out_file,'w')
    if time_detection_first>=0:
        transientstart=int(t_scan_start_source)+time_detection_first
        transientstop=int(t_scan_start_source)+time_detection_last
        maximum_time=int(t_scan_start_source)+max_loss_time
        print('t_start, t_max, t_stop ',transientstart,maximum_time,transientstop,file=fout_trigg)
        print('max_loss ',float(max_loss),file=fout_trigg)
    fout_trigg.close()
    
    print('NumBinsTime ######################################### ',binNumTime)
    skymaptoplot = torch.t(lossMap_3D_tmp[0,:,:,0:10,int(max_loss_time-plotting_window):int(max_loss_time+plotting_window)].sum(dim=3).sum(dim=2))
    
    skymaptoplot_data = torch.t(signalMap_3D_tmp[0,:,:,0:10,int(max_loss_time-plotting_window):int(max_loss_time+plotting_window)].sum(dim=3).sum(dim=2))
    skymaptoplot_data2 = torch.t(signalMap_3D_tmp[0,:,:,0:10,int(max_loss_time+20):int(max_loss_time+30)].sum(dim=3).sum(dim=2))

    skymaptoplot_model = torch.t(modelMap_3D_tmp[0,:,:,0:10,int(max_loss_time-plotting_window):int(max_loss_time+plotting_window)].sum(dim=3).sum(dim=2))
    skymaptoplot_model2 = torch.t(modelMap_3D_tmp[0,:,:,0:10,int(max_loss_time+20):int(max_loss_time+30)].sum(dim=3).sum(dim=2))
    
    
    arrTest_2 = np.zeros(data_full.project('PsiChi').nbins)
    for i in range(skymaptoplot.shape[0]):
        for ii in range(skymaptoplot.shape[1]):
            ang1=np.deg2rad(float(ii*(180. / resolutionImage)))
            ang2=np.deg2rad(float(i*(360. / resolutionImage)))
            pixel_2=hp.ang2pix(8,ang1,ang2)
            arrTest_2[pixel_2]+=skymaptoplot[i][ii]
            
    
    plt.figure(figsize=(16.03, 10.41) ) 
    plt.plot(frameNum,lossTensor)
    plt.title('Anomaly detection - Loss curve')
    plt.xlabel("Frame number")
    plt.ylabel('Loss curve')
    plt.savefig(directory_output+'loss_curve.png')
    
    plt.figure(figsize=(16.03, 10.41) ) 
    plt.imshow(skymaptoplot.detach().numpy())
    plt.gca().invert_yaxis() 
    plt.title('LossMap - example; Test set')
    plt.xlabel('Bin X')
    plt.ylabel('Bin Y')
    plt.colorbar()
    plt.savefig(directory_output+'imageLoss_2DPLot.png')

    plt.figure(figsize=(16.03, 10.41) ) 
    plt.imshow(skymaptoplot_data.detach().numpy())
    plt.gca().invert_yaxis() 
    plt.title('DataMap - example; Test set')
    plt.xlabel('Bin X')
    plt.ylabel('Bin Y')
    plt.clim(0,10)
    plt.colorbar()
    plt.savefig(directory_output+'imageData_2DPLot.png')

    plt.figure(figsize=(16.03, 10.41) ) 
    plt.imshow(skymaptoplot_data2.detach().numpy())
    plt.gca().invert_yaxis() 
    plt.title('DataMap - example backg; Test set')
    plt.xlabel('Bin X')
    plt.ylabel('Bin Y')
    plt.clim(0,10)
    plt.colorbar()
    plt.savefig(directory_output+'imageData_2DPLot_2.png')

    plt.figure(figsize=(16.03, 10.41) ) 
    plt.imshow(skymaptoplot_model.detach().numpy())
    plt.gca().invert_yaxis() 
    plt.title('ModelMap - example; Test set')
    plt.xlabel('Bin X')
    plt.ylabel('Bin Y')
    plt.clim(0,10)
    plt.colorbar()
    plt.savefig(directory_output+'imageModel_2DPLot.png')

    plt.figure(figsize=(16.03, 10.41) ) 
    plt.imshow(skymaptoplot_model2.detach().numpy())
    plt.gca().invert_yaxis() 
    plt.title('ModelMap background- example; Test set')
    plt.xlabel('Bin X')
    plt.ylabel('Bin Y')
    plt.clim(0,10)
    plt.colorbar()
    plt.savefig(directory_output+'imageModel_2DPLot_2.png')
    
    ori = load_ori(str(ori_file2))
    tstart=Time(t_scan_start_source, format='unix')
    tstop=Time(t_scan_stop_source, format='unix')
    tmiddle=(t_scan_start_source+t_scan_stop_source)/2.
    m = HealpixMap(nside = 8, coordsys=SpacecraftFrame( attitude = ori.interp_attitude(Time(tmiddle, format='unix')   )))

    for i in range(data_full.project('PsiChi').nbins):
        content =arrTest_2[i]
        m[i]+=content
        
    fig,ax = plt.subplots(subplot_kw = {'projection':'mollview', 'coord':'G'})
    m.plot(ax=ax,vmin=10)
    ax.scatter(true_l, true_b, marker='*', color='red', s=50, zorder=5, transform=ax.get_transform('world'))
    plt.savefig(directory_output+'imageLoss_GalCoord_rot.png')

def cnn_locate(cosipy_yaml_input,lib_dir):
    import cosipy
    import torch
    import torch.nn as nn
    import subprocess
    from contextlib import redirect_stdout
    import matplotlib.pyplot as plt
    import numpy as np
    from cosipy.pipeline.task.task import cosi_tsdetect
    from cosipy.pipeline.src.io import load_ori
    import sys
    sys.path.append(lib_dir)
    import healpy as hp
    from funzioni_comuni import read_base_pipeline_params,read_file_histo2,read_anomaly_detection_config,read_file_histo_second
    from models import CNN3D
    from astropy.time import Time
    from histpy import Histogram
    from mhealpy import HealpixMap
    import mhealpy
    from scoords import SpacecraftFrame
    from astropy.coordinates import SkyCoord
    import astropy.units as u

    from yayc import Configurator
    full_config = Configurator.open(cosipy_yaml_input)
    t_scan_start_source=full_config["general_pipeline_config"]["t_scan_start_source"]
    t_scan_stop_source=full_config["general_pipeline_config"]["t_scan_stop_source"]
    t_scan_delta=full_config["general_pipeline_config"]["t_scan_delta"]
    directory_output =full_config["general_pipeline_config"]["directory_output"]
    trigger_list=full_config["general_pipeline_config"]["external_trigger_list"]
    threshold_TS=full_config["general_pipeline_config"]["ts_threshold"]
    anomaly_config =full_config["general_pipeline_config"]["anomaly_config"]
    ori_file2 = full_config["general_pipeline_config"]["ori_file"]

    input_file_name,model_file,resolutionImage,timeBin,plotting_window,ori_file,true_b,true_l,threshold_loss,out_file=read_anomaly_detection_config(anomaly_config)
    
    FileName=directory_output+"FileOut_test_3DCNN_"
    numberEventstest=1
    t0_test=0
    
    data_full     = Histogram.open(str(input_file_name))
    binNumTime = int(data_full.project('Time').nbins)
    imagePlotX_Z_t_test = read_file_histo2(data_full,t0_test,t0_test+binNumTime,resolutionImage,binNumTime,FileName,binNumTime,numberEventstest)
    print('########################### ',imagePlotX_Z_t_test.shape,binNumTime)
    
    model = CNN3D()
    state = torch.load(lib_dir+'Model_3DCNN_newTarget.pth')
    model.load_state_dict(state)

    lightCurveMax=0
    latMax=0
    longMax=0
    tmax=0
    
    for t in range(0,binNumTime,20):
        image_for_input = imagePlotX_Z_t_test[0:1,:,:,:,int(t):int(t)+20].sum(dim=4)
        outTEST=model(image_for_input)
        lightCurveVal=image_for_input[0,0:50,0:100,0:50].sum(dim=2).sum(dim=1).sum(dim=0)
        print(np.rad2deg(outTEST[0,0].detach().numpy()),outTEST[0,1].detach().numpy(),outTEST[0,2].detach().numpy(),lightCurveVal)
        if lightCurveVal>lightCurveMax:
            lightCurveMax=lightCurveVal
            latMax=np.rad2deg(outTEST[0,0].detach().numpy())
            longMax_cos=outTEST[0,1].detach().numpy()
            longMax_sin=outTEST[0,2].detach().numpy()
            longMax=np.rad2deg(np.atan2(longMax_sin,longMax_cos))

            tmax=t

    print(tmax,latMax,longMax)
    if longMax<0:
        longMax+=360
    
    print(tmax,latMax,longMax)

    skymaptoplot = imagePlotX_Z_t_test[0,:,:,0:10,tmax:tmax+20].sum(dim=3).sum(dim=2)
    
    #####################################
    ori = load_ori(str(ori_file2))
    tmiddle=t_scan_start_source+tmax
    attitude = ori.interp_attitude(Time(tmiddle, format='unix') )
    m = HealpixMap(nside = 8, coordsys=SpacecraftFrame( attitude = attitude))
    #####################################

    ellypseOr = np.deg2rad(0)

    # punti dell'ellisse
    ang = np.linspace(0, 2*np.pi, 400)
    xang = 20 * np.cos(ang)
    yang = 10 * np.sin(ang)

    # rotazione
    xr_ang = xang*np.cos(ellypseOr) - yang*np.sin(ellypseOr)
    yr_ang = xang*np.sin(ellypseOr) + yang*np.cos(ellypseOr)

    arrTest_2 = np.zeros(data_full.project('PsiChi').nbins)
    for i in range(skymaptoplot.shape[0]):
        for ii in range(skymaptoplot.shape[1]):
            ang1=np.deg2rad(float(i*(180. / resolutionImage))+1e-4)
            ang2=np.deg2rad(float(ii*(360. / (2 * resolutionImage)))+1e-4)
            m[m.ang2pix(ang1, ang2)]+=skymaptoplot[i][ii]
    
    print("latMax,longMax ",latMax,longMax)

    fig,ax = plt.subplots(subplot_kw = {'projection':'mollview', 'coord':'G'})
    m.plot(ax=ax,vmin=0)
    ax.scatter(true_l,true_b, marker='*',  color='pink', s=50, zorder=5, transform=ax.get_transform('world'))
    
    c = SkyCoord(lon = longMax*u.deg, lat = (90 - latMax)*u.deg, frame = SpacecraftFrame(attitude = attitude) )
    coordin_new=c.transform_to('galactic')
    ax.scatter(coordin_new.l,coordin_new.b, marker='o', color='red', s=10, zorder=5 ,transform=ax.get_transform('world'))

    lon_ell = float(coordin_new.l.value) + xr_ang
    lat_ell = float(coordin_new.b.value) + yr_ang

    ax.scatter(
        lon_ell*u.deg,
        lat_ell*u.deg,
        color='red',
        marker='o',
        s=0.05,
        transform=ax.get_transform('world'),
        zorder=4
    )

    plt.savefig(directory_output+'CNNSignal.png')
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~',longMax, latMax)

    
def execute_threemlfit(cosipy_yaml_input,lib_dir,fitmodel,scanvar):
    import cosipy
    from cosipy.pipeline.task.task import cosi_threemlfit
    import sys
    sys.path.append(lib_dir)
    from funzioni_comuni import read_cosi_ts_detect,read_base_pipeline_params,format_override_val,read_trigger_content_multiple_yaml
    from PIL import Image, ImageDraw, ImageFont
    from threeML import JointLikelihood,DataList,XYLike,Model,PointSource,Constant
    import numpy as np
    import torch
            
    from yayc import Configurator
    full_config = Configurator.open(cosipy_yaml_input)
    t_scan_start_source=full_config["general_pipeline_config"]["t_scan_start_source"]
    t_scan_stop_source=full_config["general_pipeline_config"]["t_scan_stop_source"]
    t_scan_delta=full_config["general_pipeline_config"]["t_scan_delta"]
    directory_output =full_config["general_pipeline_config"]["directory_output"]
    trigger_list=full_config["general_pipeline_config"]["external_trigger_list"]
    threshold_TS=full_config["general_pipeline_config"]["ts_threshold"]
    
    externalTrigger_start,externalTrigger_stop,flag_trigger = read_trigger_content_multiple_yaml(lib_dir,trigger_list)
    
    measured_l=float(0.)
    measured_b=float(0.)
    error_coo=float(0.)
    maxumumTS=float(0.)

    var_override1,var_override2,var_override3,var_override4,var_override5,var_override6,var_override7,var_override8,modelname = format_override_val(fitmodel,measured_l,measured_b,error_coo)

    array_range_start = torch.zeros(0,dtype=torch.int64)
    array_range_stop = torch.zeros(0,dtype=torch.int64)

    if scanvar==1:
        directory_output+="timescan/"
        for time in range(t_scan_start_source,t_scan_stop_source,t_scan_delta):
            array_range_start = torch.cat([array_range_start,torch.tensor([time])])
            time_stop = time + t_scan_delta
            array_range_stop = torch.cat([array_range_stop,torch.tensor([time_stop])])
    else:
        for n_t in range(externalTrigger_start.size(0)):
            t_init=externalTrigger_start[n_t]
            t_stop=externalTrigger_stop[n_t]
            array_range_start=torch.cat([array_range_start,torch.tensor([t_init])])
            array_range_stop=torch.cat([array_range_stop,torch.tensor([t_stop])])
    
    for n_t in range(array_range_start.shape[0]):
        time      =int(array_range_start[n_t])
        time_stop =int(array_range_stop[n_t])
        print('##################################### ',str(time))
        print('##################################### ',str(time_stop))

        measured_l,measured_b,error_coo,maxumumTS=read_cosi_ts_detect(directory_output+'cosi-tsdetect_'+str(time)+'.txt')
        
        args=['--config',cosipy_yaml_input, '--config_group', 'threemlfit_'+modelname,'--override',var_override1,var_override2,var_override3,var_override4,var_override5,var_override6,var_override7,var_override8,'--overwrite', '--suffix',modelname+'_'+str(time),'--output-dir',directory_output,'--tstart',str(time),'--tstop',str(time_stop)]
        if maxumumTS>float(threshold_TS):
            print("READY cosi_threemlfit "+modelname)
            cosi_threemlfit(argv=args)
        else:            
            img = Image.new("RGBA",size=(1000,1000),color=(255,255,255,255))
            txt = Image.new("RGBA",size=(1000,1000),)
            font = ImageFont.truetype("DejaVuSans.ttf", 40)
            draw = ImageDraw.Draw(txt)
            draw.text((100, 400),"Under threshold!" ,font=font,fill=(0, 0, 0, 255))
            draw.text((100, 500),"Time "+str(time)+' s; model= '+str(modelname),font=font,fill=(0, 0, 0, 255))
            out = Image.alpha_composite(img, txt)
            out.save(str(directory_output)+"raw_spectrum_"+str(modelname)+"_"+str(time)+".png")
            
            ###################
            x = np.array([1.0])
            y = np.array([0.0])
            yerr = np.array([1.0])
            plugin = XYLike("single_point", x, y, yerr)
            plugins = DataList(plugin)
            model = Model(
                PointSource(
                    "src",
                    0, 0,
                    spectral_shape=Constant()
                )
            )
            model.src.spectrum.main.value = 0.0
            
            like = JointLikelihood(model, plugins, verbose=False)
            like.fit()
            results=like.results
            results.write_to(str(directory_output)+"results_"+str(modelname)+"_"+str(time)+".h5",as_hdf=True)


def build_pdf_file(cosipy_yaml_input,lib_dir):
    import cosipy
    from cosipy.pipeline.task.task import cosi_bindata
    from PIL import Image,ImageDraw,ImageFont
    import os
    import re
    import math
    import sys
    sys.path.append(lib_dir)
    from funzioni_comuni import read_cosi_ts_detect,read_base_pipeline_params,read_trigger_content_multiple_yaml,read_anomaly_detection_config
    
    from yayc import Configurator
    full_config = Configurator.open(cosipy_yaml_input)
    t_scan_start_source=full_config["general_pipeline_config"]["t_scan_start_source"]
    t_scan_stop_source=full_config["general_pipeline_config"]["t_scan_stop_source"]
    t_scan_delta=full_config["general_pipeline_config"]["t_scan_delta"]
    directory_output =full_config["general_pipeline_config"]["directory_output"]
    trigger_list=full_config["general_pipeline_config"]["external_trigger_list"]
    threshold_TS=full_config["general_pipeline_config"]["ts_threshold"]
    anomaly_config =full_config["general_pipeline_config"]["anomaly_config"]

    input_file_name,model_file,resolutionImage,timeBin,plotting_window,ori_file,true_b,true_l,threshold_loss,out_file=read_anomaly_detection_config(anomaly_config)

    
    externalTrigger_start,externalTrigger_stop,flag_trigger = read_trigger_content_multiple_yaml(lib_dir,trigger_list)
    
    # read max TS on single scan intervals 
    maxumumTS_all = []
    maxumum_l = []
    maxumum_b = []
    nameFiles_TS = []
    timeFiles = []
    for f in os.listdir(directory_output+'timescan/'):
        if f.lower().endswith(".txt"):
            fileName=directory_output+'timescan/'+ f
            nameFiles_TS.append(fileName)
            print(f)

    nameFiles_TS_sorted = sorted(
        nameFiles_TS,
        key=lambda f: int(re.findall(r'\d+', f)[-1])
    )
    
    for name in nameFiles_TS_sorted:
        num = re.findall(r"\d+", name)[0]
        measured_l_tmp,measured_b_tmp,error_coo_tmp,maxumumTS_tmp=read_cosi_ts_detect(name)
        maxumumTS_all.append(maxumumTS_tmp)
        timeFiles.append(num)
        maxumum_l.append(measured_l_tmp)
        maxumum_b.append(measured_b_tmp)
    
    pages = []
    pngs = []
    # read png for scan 
    for f in os.listdir(directory_output+'timescan/'):
        if f.lower().endswith(".png") and "raw_ts" in f:
            pngs.append(directory_output+'timescan/'+ f)
            print(f)

    pngs_sorted = sorted(
        pngs,
        key=lambda f: int(re.findall(r'\d+', f)[-1])
    )
    # read png for external trigger
    for t in range(len(externalTrigger_start)):
        time_start=str(int(externalTrigger_start[t]))
        pngs_sorted.append(directory_output+'raw_ts_'+time_start+'.png')
    
    frame_numtot=len(pngs_sorted)
    frame_numtot_external=len(externalTrigger_start)
    print(frame_numtot,frame_numtot_external)
    
    imgsize=0
    frameNum=0
    for path in pngs_sorted:
        img = Image.open(path)
        txt = Image.new("RGBA", img.size)
        imgsize=img.size
        
        font = ImageFont.truetype("DejaVuSans.ttf", 40)
        font2 = ImageFont.truetype("DejaVuSans.ttf", 30)
        font3 = ImageFont.truetype("DejaVuSans.ttf", 60)

        draw = ImageDraw.Draw(txt)
        if frameNum<frame_numtot-frame_numtot_external:

            draw.text((20, 0),'Frame '+str(frameNum) ,font=font,fill=(0, 0, 0, 255))
            draw.text((20, 40),'Time start= ' + str(timeFiles[frameNum]) + ' s' ,font=font2,fill=(0, 0, 0, 255))
            draw.text((20, 80),'Max TS='+str(math.trunc(maxumumTS_all[frameNum]*10)/10),font=font2,fill=(0, 0, 0, 255))
            draw.text((20, 120),'Max l='+str(math.trunc(maxumum_l[frameNum]*10)/10)+' deg',font=font2,fill=(0, 0, 0, 255))
            draw.text((20, 160),'Max b='+str(math.trunc(maxumum_b[frameNum]*10)/10)+' deg',font=font2,fill=(0, 0, 0, 255))
            
        else:
            numIndex=int(frameNum-(frame_numtot-frame_numtot_external))
            print(numIndex)
            measured_l,measured_b,error_coo,maxumumTS=read_cosi_ts_detect(directory_output+'cosi-tsdetect_'+str(int(externalTrigger_start[numIndex]))+'.txt')
            draw.text((20, 0),'External trigger',font=font3,fill=(255, 0, 0, 255))# TRUE????????????????????? Existing?
            draw.text((20, 80),'Max TS='+str(math.trunc(maxumumTS*10)/10),font=font2,fill=(0, 0, 0, 255))
            draw.text((20, 120),'Max l='+str(math.trunc(measured_l*10)/10)+' deg',font=font2,fill=(0, 0, 0, 255))
            draw.text((20, 160),'Max b='+str(math.trunc(measured_b*10)/10)+' deg',font=font2,fill=(0, 0, 0, 255))
            draw.text((1100, 60),'External start='+str(int(externalTrigger_start[numIndex]))+' s',font=font2,fill=(255, 0, 0, 255))
            draw.text((1100, 100),'External stop='+str(int(externalTrigger_stop[numIndex]))+' s',font=font2,fill=(255, 0, 0, 255))

        out = Image.alpha_composite(img, txt)
        pages.append(out.convert("RGB"))
        frameNum+=1
    
    ## read anomaly detection trigg
    # Add anomaly detection info to output
    startAnomaly=-1
    stopAnomaly=-1
    maxAnomaly=-1
    
    f_anomaly_trigg=open(directory_output+out_file)
    content_anomaly = f_anomaly_trigg.read().splitlines()
    for line_anomaly_tot in content_anomaly:
        line_anomaly=line_anomaly_tot.split()
        if line_anomaly[0]=="t_start,":
            startAnomaly=int(line_anomaly[3])
            maxAnomaly=int(line_anomaly[4])
            stopAnomaly=int(line_anomaly[5])
            
    font_anomaly = ImageFont.truetype("DejaVuSans.ttf", 20)
    img_anomaly = Image.open(directory_output+'loss_curve.png')
    txt_anomaly = Image.new("RGBA", img_anomaly.size)
    draw_anomaly = ImageDraw.Draw(txt_anomaly)
    if startAnomaly>0:
        draw_anomaly.text((50, 50),'Start anomaly '+str(startAnomaly)+' s',font=font_anomaly,fill=(255, 0, 0, 255))
        draw_anomaly.text((50, 100),'Stop anomaly '+str(stopAnomaly)+' s',font=font_anomaly,fill=(255, 0, 0, 255))
    else:
        draw_anomaly.text((40, 50),'No anomaly detected! ',font=font_anomaly,fill=(255, 0, 0, 255))

    out_anomaly = Image.alpha_composite(img_anomaly, txt_anomaly)
    out_anomaly=out_anomaly.resize(imgsize)
    pages.append(out_anomaly.convert("RGB"))

    img_anomaly4 = Image.open(directory_output+'imageLoss_GalCoord_rot.png')
    txt_anomaly4 = Image.new("RGBA", img_anomaly4.size)
    out_anomaly4 = Image.alpha_composite(img_anomaly4, txt_anomaly4)
    out_anomaly4=out_anomaly4.resize(imgsize)
    draw_anomaly4 = ImageDraw.Draw(txt_anomaly4)
    draw_anomaly4.text((0, 0),'Anomaly detection loss projected',font=font_anomaly,fill=(255, 0, 0, 255))
    pages.append(out_anomaly4.convert("RGB"))
    
    
    img_anomaly5 = Image.open(directory_output+'CNNSignal.png')
    txt_anomaly5 = Image.new("RGBA", img_anomaly5.size)
    out_anomaly5 = Image.alpha_composite(img_anomaly5, txt_anomaly5)
    out_anomaly5=out_anomaly5.resize(imgsize)
    draw_anomaly5 = ImageDraw.Draw(txt_anomaly5)
    draw_anomaly5.text((0, 0),'CNN output',font=font_anomaly,fill=(255, 0, 0, 255))

    pages.append(out_anomaly5.convert("RGB"))

    pages[0].save(
        directory_output+'raw_ts_sequence.pdf',
        save_all=True,
        resolution=200.0,
        format="PDF",
        append_images=pages[1:])

   

def build_spectral_fit(cosipy_yaml_input,lib_dir,modeltoplot):
    import cosipy
    from cosipy.pipeline.task.task import cosi_bindata
    from PIL import Image,ImageDraw,ImageFont
    import os
    import re
    import math
    import sys
    import h5py

    sys.path.append(lib_dir)
    from funzioni_comuni import read_cosi_ts_detect,read_base_pipeline_params,read_spectral_fit_info,read_trigger_content_multiple_yaml
    
    from yayc import Configurator
    full_config = Configurator.open(cosipy_yaml_input)
    t_scan_start_source=full_config["general_pipeline_config"]["t_scan_start_source"]
    t_scan_stop_source=full_config["general_pipeline_config"]["t_scan_stop_source"]
    t_scan_delta=full_config["general_pipeline_config"]["t_scan_delta"]
    directory_output =full_config["general_pipeline_config"]["directory_output"]
    trigger_list=full_config["general_pipeline_config"]["external_trigger_list"]
    threshold_TS=full_config["general_pipeline_config"]["ts_threshold"]
  
    externalTrigger_start,externalTrigger_stop,flag_trigger = read_trigger_content_multiple_yaml(lib_dir,trigger_list)
    
    nameFiles_fit = []
    for f in os.listdir(directory_output+'timescan/'):
        if f.lower().endswith(".h5") and str(modeltoplot) in f:
            fileName=directory_output+'timescan/'+ f
            nameFiles_fit.append(fileName)
            print(f)
            
    nameFiles_fit_sorted = sorted(
        nameFiles_fit,
        key=lambda f: int(re.findall(r'\d+', f)[-2])
    )
        
    nameFiles_fit_external = []
    for f in os.listdir(directory_output):
        if f.lower().endswith(".h5") and str(modeltoplot) in f:
            fileName=directory_output+ f
            nameFiles_fit_external.append(fileName)
            print(f)
            
    nameFiles_fit_external_sorted = sorted(
        nameFiles_fit_external,
        key=lambda f: int(re.findall(r'\d+', f)[-2])
    )

    for list_tmp in nameFiles_fit_external_sorted:
        nameFiles_fit_sorted.append(list_tmp)
    
    pages = []
    pngs1 = []
    timeFiles = []
    # read png for scan 
    for f in os.listdir(directory_output+'timescan/'):
        if f.lower().endswith(".png") and "raw_spectrum_"+str(modeltoplot) in f:
            pngs1.append(directory_output+'timescan/'+ f)
            print(f)

    pngs_sorted = sorted(
        pngs1,
        key=lambda f: int(re.findall(r'\d+', f)[-1])
    )
    # read png for external trigger
    for t in range(len(externalTrigger_start)):
        time_start=str(int(externalTrigger_start[t]))
        pngs_sorted.append(directory_output+'raw_spectrum_'+modeltoplot+'_'+str(time_start)+'.png')

    for name in nameFiles_fit_sorted:
        num = re.findall(r"\d+", name)[0]
        timeFiles.append(num)
  
    frame_numtot=len(pngs_sorted)
    frame_numtot_external=len(externalTrigger_start)
    num_fitmodels=len(nameFiles_fit_external_sorted)

    frameNum=0
    
    for path in pngs_sorted:
        img = Image.open(path)
        txt = Image.new("RGBA", img.size)
        
        font = ImageFont.truetype("DejaVuSans.ttf", 10)
        font2 = ImageFont.truetype("DejaVuSans.ttf", 9)
        font3 = ImageFont.truetype("DejaVuSans.ttf", 20)

        draw = ImageDraw.Draw(txt)
        draw.text((600, 30),str(modeltoplot) ,font=font3,fill=(255, 0, 0, 255))

        if frameNum<frame_numtot-frame_numtot_external:

            name_var,value_var,errneg_var,errpos_var,unit_var = read_spectral_fit_info(frameNum,directory_output+'timescan/',modeltoplot)

            draw.text((90, 70),'Time start= ' + str(timeFiles[frameNum]) + ' s' ,font=font2,fill=(0, 0, 0, 255))
            if len(value_var)==1:
                draw.text((90, 200),'Fit not converging! ',font=font2,fill=(255, 0, 0, 255))
                
            for uu in range(len(value_var)):
                draw.text((90, 100+uu*20),str(name_var[uu].decode("utf-8")[-15:]) + ' = ' ,font=font2,fill=(0, 0, 0, 255))
                draw.text((200, 100+uu*20),str(math.trunc(value_var[uu]*1000)/1000) + ' (' + str(math.trunc(errneg_var[uu]*10000)/10000) + ',' + str(math.trunc(errpos_var[uu]*10000)/10000) + ')' ,font=font2,fill=(0, 0, 0, 255))
                draw.text((320, 100+uu*20),str(unit_var[uu].decode("utf-8")) ,font=font2,fill=(0, 0, 0, 255))

        else:
            numIndex=int(frameNum-(frame_numtot-frame_numtot_external))
            print(numIndex)

            name_var,value_var,errneg_var,errpos_var,unit_var = read_spectral_fit_info(0,directory_output,modeltoplot)
            draw.text((100, 80),'External trigger',font=font3,fill=(255, 0, 0, 255))# TRUE????????????????????? Existing?
            draw.text((100, 110),'External start='+str(externalTrigger_start[numIndex])+' s',font=font2,fill=(255, 0, 0, 255))
            draw.text((100, 130),'External stop='+str(externalTrigger_stop[numIndex])+' s',font=font2,fill=(255, 0, 0, 255))
            if len(value_var)==1:
                draw.text((90, 200),'Fit not converging! ',font=font2,fill=(255, 0, 0, 255))

            for uu in range(len(value_var)):
                draw.text((90, 150+uu*20),str(name_var[uu].decode("utf-8")[-15:]) + ' = ' ,font=font2,fill=(0, 0, 0, 255))
                draw.text((200, 150+uu*20),str(math.trunc(value_var[uu]*1000)/1000) + ' (' + str(math.trunc(errneg_var[uu]*10000)/10000) + ',' + str(math.trunc(errpos_var[uu]*10000)/10000) + ')' ,font=font2,fill=(0, 0, 0, 255))
                draw.text((320, 150+uu*20),str(unit_var[uu].decode("utf-8")) ,font=font2,fill=(0, 0, 0, 255))

        out = Image.alpha_composite(img, txt)

        pages.append(out.convert("RGB"))
        frameNum+=1

    pages[0].save(
        directory_output+'raw_spectrum_'+modeltoplot+'_sequence.pdf',
        save_all=True,
        resolution=200.0,
        format="PDF",
        append_images=pages[1:])


def prepare_alert_external(cosipy_yaml_input,lib_dir):
    import sys
    import os
    import re
    import json
    from astropy.time import Time
    from astropy.coordinates import SkyCoord
    import astropy.units as u

    sys.path.append(lib_dir)
    from funzioni_comuni import read_cosi_ts_detect,read_base_pipeline_params,read_trigger_content_multiple_yaml
    from yayc import Configurator
    full_config = Configurator.open(cosipy_yaml_input)
    t_scan_start_source=full_config["general_pipeline_config"]["t_scan_start_source"]
    t_scan_stop_source=full_config["general_pipeline_config"]["t_scan_stop_source"]
    t_scan_delta=full_config["general_pipeline_config"]["t_scan_delta"]
    directory_output =full_config["general_pipeline_config"]["directory_output"]
    trigger_list=full_config["general_pipeline_config"]["external_trigger_list"]
    threshold_TS=full_config["general_pipeline_config"]["ts_threshold"]

    externalTrigger_start,externalTrigger_stop,flag_trigger = read_trigger_content_multiple_yaml(lib_dir,trigger_list)
    
    nameFiles_TS = []
    trigger_TS = []
    trigger_l = []
    trigger_b = []

    for f in os.listdir(directory_output+'timescan/'):
        if f.lower().endswith(".txt"):
            fileName=directory_output+'timescan/'+ f
            nameFiles_TS.append(fileName)
            print(f)

    nameFiles_TS_sorted = sorted(
        nameFiles_TS,
        key=lambda f: int(re.findall(r'\d+', f)[-1])
    )

    triggertype="NONE"
    first_time=1e20
    first_latitude=0
    first_longitude=0

    with open(directory_output+"Pseudo_alert.txt", "w") as f:
        print('Alert from external trigger ',file=f)
        print('Origin XYZ (Fast pipeline, GCN...)',file=f)

        for i in range(len(externalTrigger_start)):
            time_start=str(int(externalTrigger_start[i]))
            time_stop=str(int(externalTrigger_stop[i]))
            
            measured_l,measured_b,error_coo,maxumumTS=read_cosi_ts_detect(directory_output+'cosi-tsdetect_'+time_start+'.txt')
            if maxumumTS>float(threshold_TS):
                triggertype="EXTERNAL"
                if first_time>int(time_start):
                    first_time=int(time_start)
                    first_latitude=measured_l
                    first_longitude=measured_b
                    
                print('Confirmed_ext ',1,file=f)
                print('timeStart ',time_start,file=f)
                print('timeStart ',time_stop,file=f)
                print('Galactic_lat ', measured_l,file=f)
                print('Galactic_long ',measured_b,file=f)
                print('Resolution ',error_coo,file=f)
                print('Max_TS= ',maxumumTS,file=f)
            else:
                print('Confirmed_ext ',0,file=f)
                print('timeStart ',time_start,file=f)
                print('timeStart ',time_stop,file=f)

        print('',file=f)
        print('#############################',file=f)
        print('Alert from TSmap scan ',file=f)
        time_frame=0
        number_trigger_frames=0
        for file in nameFiles_TS_sorted:
            measured_l_tmp,measured_b_tmp,error_coo_tmp,maxumumTS_tmp=read_cosi_ts_detect(file)
            timestart=t_scan_start_source + (time_frame*t_scan_delta)
            timestop= timestart + t_scan_delta
            if maxumumTS_tmp>float(threshold_TS):
                if triggertype=="EXTERNAL" or triggertype=="SCAN+EXTERNAL":
                    triggertype="SCAN+EXTERNAL"
                else:
                    triggertype="SCAN"

                if first_time>int(timestart):
                    first_time=int(timestart)
                    first_latitude=measured_l
                    first_longitude=measured_b

                print('Independent ',1,file=f)
                print('timeStart ',timestart,file=f)
                print('timeStart ',timestop,file=f)
                print('Galactic_lat ', measured_l_tmp,file=f)
                print('Galactic_long ',measured_b_tmp,file=f)
                print('Resolution ',error_coo_tmp,file=f)
                print('Max_TS= ',maxumumTS_tmp,file=f)
                print('',file=f)
                number_trigger_frames+=1
                
            time_frame+=1
        if number_trigger_frames==0:
            print('Independent ',0,file=f)

    ####################################################################
    # save json ########################################################
    ####################################################################
    t = Time(first_time, format="unix", scale="utc")
    dt = t.to_datetime()
    l =  first_latitude * u.deg
    b =  first_longitude * u.deg

    c = SkyCoord(l=l, b=b, frame="galactic")
    ra  = c.icrs.ra.deg
    dec = c.icrs.dec.deg

    
    data = {
        "$schema": "https://gcn.nasa.gov/schema/XXXXXXXXXXXXXXXXX.json",
        "mission": "COSI",
        "instrument": "GeD",
        "pipeline": "Comprehensive pipeline",
        "messenger": "EM",
        "alert_datetime": str(dt),
        "alert_type": triggertype,
        "event_name": "GRBXYZ",
        "trigger_time": str(dt),
        "ra": ra,
        "dec": dec,
        "ra_dec_error": 0.0,
        "algorithm": "TSMap",
        "trigger_date": str(dt),
    }
            
    with open(directory_output+"XXXXXXX.json", "w") as f:
        json.dump(data, f, indent=2)


    ####################################################################
    # save txt  ########################################################
    ####################################################################
    with open(directory_output+"XXXXXXX.cosi.txt", "w") as f:
        print('//////////////////////////////////////////////////////////////////////',file=f)
        print('TITLE: GCN COSI NOTICE ',file=f)
        print('NOTICE_DATE: '+str(dt),file=f)
        print('NOTICE_TYPE: '+triggertype,file=f)
        print('SOURCE_OBJ: XXXXXX.png',file=f)
        print('REF_NUM: XXXXXX',file=f)
        print('RA: '+str(ra),file=f)
        print('DEC: '+str(dec),file=f)
        print('GAL_COORDS: '+str(first_latitude)+' '+str(first_longitude),file=f)
        print('TRIGGER_DATE: '+str(dt),file=f)


def cleanup_and_format(cosipy_yaml_input,lib_dir):
    # some cleanup and some service directory creation

    from PIL import Image,ImageDraw,ImageFont
    import numpy as np
    import cosipy
    from contextlib import redirect_stdout
    import sys
    import subprocess
    sys.path.append(lib_dir)
    from funzioni_comuni import read_base_pipeline_params,read_trigger_content_multiple_yaml
    from threeML import JointLikelihood,DataList,XYLike,Model,PointSource,Constant
    
    from yayc import Configurator
    full_config = Configurator.open(cosipy_yaml_input)
    t_scan_start_source=full_config["general_pipeline_config"]["t_scan_start_source"]
    t_scan_stop_source=full_config["general_pipeline_config"]["t_scan_stop_source"]
    t_scan_delta=full_config["general_pipeline_config"]["t_scan_delta"]
    directory_output =full_config["general_pipeline_config"]["directory_output"]
    trigger_list=full_config["general_pipeline_config"]["external_trigger_list"]
    threshold_TS=full_config["general_pipeline_config"]["ts_threshold"]
    
    externalTrigger_start,externalTrigger_stop,flag_trigger = read_trigger_content_multiple_yaml(lib_dir,trigger_list)
    
    # clean up old files
    subprocess.run('mkdir '+directory_output+'timescan', shell=True)
    subprocess.run('mkdir '+directory_output+'../garbagebin', shell=True)

    subprocess.run('mv ~/tmp_trigger_list '+directory_output+'../garbagebin', shell=True)
    subprocess.run('mv '+directory_output+'tsel_* '+directory_output+'../garbagebin', shell=True)
    subprocess.run('mv '+directory_output+'bin* '+directory_output+'../garbagebin', shell=True)
    subprocess.run('mv '+directory_output+'*png '+directory_output+'../garbagebin', shell=True)
    subprocess.run('mv '+directory_output+'timescan/*png '+directory_output+'../garbagebin', shell=True)
    subprocess.run('mv '+directory_output+'timescan/*h5 '+directory_output+'../garbagebin', shell=True)
    subprocess.run('mv '+directory_output+'timescan/*txt '+directory_output+'../garbagebin', shell=True)
    subprocess.run('mv '+directory_output+'*pdf '+directory_output+'../garbagebin', shell=True)
    subprocess.run('mv '+directory_output+'results*h5 '+directory_output+'../garbagebin', shell=True)
    subprocess.run('mv '+directory_output+'Pseudo_alert.txt '+directory_output+'../garbagebin', shell=True)

    fileName_toClean = directory_output+"cosi-tsdetect_*.txt"
    subprocess.run('mv ' + fileName_toClean + ' '+directory_output+'../garbagebin',shell=True)

    # since I cannot include the python_callable in the branch I need a tmp file with the list of external triggers
    subprocess.run('cat '+trigger_list+' > /home/gamma/tmp_trigger_list',shell=True)


