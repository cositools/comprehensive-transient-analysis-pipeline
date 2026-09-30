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

def convert_fits_to_hdf5(cosipy_yaml_input,lib_dir):
    import cosipy
    import sys

    import numpy as np
    sys.path.append(lib_dir)
    from yayc import Configurator
    from histpy import Histogram
    import matplotlib.pyplot as plt
    from funzioni_comuni import read_trigger_file,save_output_hdf5
    
    full_config = Configurator.open(cosipy_yaml_input)
    fits_file_input_gamma = full_config["fits_to_hdf5"]["fits_data_file_gamma"]
    hdf5_file_output_gamma = full_config["fits_to_hdf5"]["hdf5_data_file_gamma"]
    fits_file_input_proton = full_config["fits_to_hdf5"]["fits_data_file_proton"]
    hdf5_file_output_proton = full_config["fits_to_hdf5"]["hdf5_data_file_proton"]

    directory_output =full_config["general_pipeline_config"]["directory_output"]

    save_output_hdf5(fits_file_input_gamma,hdf5_file_output_gamma)
    save_output_hdf5(fits_file_input_proton,hdf5_file_output_proton)


def basic_light_curve(cosipy_yaml_input,lib_dir):
    import cosipy
    import sys
    import h5py
    import numpy as np
    sys.path.append(lib_dir)
    from yayc import Configurator
    from histpy import Histogram
    import matplotlib.pyplot as plt
    from funzioni_comuni import read_trigger_file,print_basic_light_curve
    
    full_config = Configurator.open(cosipy_yaml_input)
    directory_output =full_config["general_pipeline_config"]["directory_output"]
    input_file_test_gamma =full_config["general_pipeline_config"]["test_bgo_file_gamma"]
    input_file_test_proton =full_config["general_pipeline_config"]["test_bgo_file_proton"]
    t_start = full_config["general_pipeline_config"]["t_scan_start_source"]
    t_stop  = full_config["general_pipeline_config"]["t_scan_stop_source"]
    
    create_arr_plot_x0_0,create_arr_content_x0_0=read_trigger_file(directory_output+'points_x0_0.txt')
    create_arr_plot_x0_1,create_arr_content_x0_1=read_trigger_file(directory_output+'points_x0_1.txt')
    create_arr_plot_x1_0,create_arr_content_x1_0=read_trigger_file(directory_output+'points_x1_0.txt')
    create_arr_plot_x1_1,create_arr_content_x1_1=read_trigger_file(directory_output+'points_x1_1.txt')

    create_arr_plot_y0_0,create_arr_content_y0_0=read_trigger_file(directory_output+'points_y0_0.txt')
    create_arr_plot_y0_1,create_arr_content_y0_1=read_trigger_file(directory_output+'points_y0_1.txt')
    create_arr_plot_y1_0,create_arr_content_y1_0=read_trigger_file(directory_output+'points_y1_0.txt')
    create_arr_plot_y1_1,create_arr_content_y1_1=read_trigger_file(directory_output+'points_y1_1.txt')

    create_arr_plot_z0_0,create_arr_content_z0_0=read_trigger_file(directory_output+'points_z0_0.txt')
    create_arr_plot_z0_1,create_arr_content_z0_1=read_trigger_file(directory_output+'points_z0_1.txt')
    create_arr_plot_z1_0,create_arr_content_z1_0=read_trigger_file(directory_output+'points_z1_0.txt')
    create_arr_plot_z1_1,create_arr_content_z1_1=read_trigger_file(directory_output+'points_z1_1.txt')
    
    arr_0 = np.zeros(12)
    arr_1 = np.zeros(12)
    arr_0 = [create_arr_plot_x0_0,create_arr_content_x0_0,create_arr_plot_x1_0,create_arr_content_x1_0,create_arr_plot_y0_0,create_arr_content_y0_0,create_arr_plot_y1_0,create_arr_content_y1_0,create_arr_plot_z0_0,create_arr_content_z0_0,create_arr_plot_z1_0,create_arr_content_z1_0]
    arr_1 = [create_arr_plot_x0_1,create_arr_content_x0_1,create_arr_plot_x1_1,create_arr_content_x1_1,create_arr_plot_y0_1,create_arr_content_y0_1,create_arr_plot_y1_1,create_arr_content_y1_1,create_arr_plot_z0_1,create_arr_content_z0_1,create_arr_plot_z1_1,create_arr_content_z1_1]
    
    print_basic_light_curve(input_file_test_gamma,t_start,t_stop,directory_output,"BGO_totcurve_gamma.png",arr_0,0)
    print_basic_light_curve(input_file_test_proton,t_start,t_stop,directory_output,"BGO_totcurve_proton.png",arr_1,1)

def moving_average_scan(cosipy_yaml_input,lib_dir):
    import cosipy
    import sys
    import h5py
    import numpy as np
    sys.path.append(lib_dir)
    from yayc import Configurator
    from histpy import Histogram
    import matplotlib.pyplot as plt
    from funzioni_comuni import calculate_moving_average,save_trigger_file

    full_config = Configurator.open(cosipy_yaml_input)
    directory_output =full_config["general_pipeline_config"]["directory_output"]
    input_file_test_gamma =full_config["general_pipeline_config"]["test_bgo_file_gamma"]
    input_file_test_proton =full_config["general_pipeline_config"]["test_bgo_file_proton"]

    t_start = full_config["general_pipeline_config"]["t_scan_start_source"]
    t_stop  = full_config["general_pipeline_config"]["t_scan_stop_source"]
    delta_integral = full_config["general_pipeline_config"]["delta_integral"]
    k_sigma_thr = full_config["general_pipeline_config"]["k_sigma_thr"]
    
    f = h5py.File(input_file_test_gamma,"r")
    f2 = h5py.File(input_file_test_proton,"r")
    
    d = f["time bins (s)"][:]
    dx0 = f["x0"][:]
    dx1 = f["x1"][:]
    dy0 = f["y0"][:]
    dy1 = f["y1"][:]
    dz0 = f["z0"][:]
    dz1 = f["z1"][:]

    d_2 = f2["time bins (s)"][:]
    dx0_2 = f2["x0"][:]
    dx1_2 = f2["x1"][:]
    dy0_2 = f2["y0"][:]
    dy1_2 = f2["y1"][:]
    dz0_2 = f2["z0"][:]
    dz1_2 = f2["z1"][:]

    index=np.where((d>t_start) & (d<t_stop))
    d_select = d[index]
    dx0_select = dx0[index]
    dx1_select = dx1[index]
    dy0_select = dy0[index]
    dy1_select = dy1[index]
    dz0_select = dz0[index]
    dz1_select = dz1[index]

    index_2=np.where((d_2>t_start) & (d_2<t_stop))
    d_select_2 = d_2[index_2]
    dx0_select_2 = dx0_2[index_2]
    dx1_select_2 = dx1_2[index_2]
    dy0_select_2 = dy0_2[index_2]
    dy1_select_2 = dy1_2[index_2]
    dz0_select_2 = dz0_2[index_2]
    dz1_select_2 = dz1_2[index_2]
    
    avg_x0_0 = np.zeros(len(index))
    stdev_x0_0 = np.zeros(len(index))
    
    sum=0.
    sum_2=0.
    sum_norm=0
    frames=0
    average=0.
    std_dev=0.

    time_tensor_x0_0,avg_tensorx0_0, std_dev_tensorx0_0,num_bin_x0_0,values_Peak_x0_0 = calculate_moving_average(dx0_select,d_select,k_sigma_thr,delta_integral)
    time_tensor_x0_1,avg_tensorx0_1, std_dev_tensorx0_1,num_bin_x0_1,values_Peak_x0_1 = calculate_moving_average(dx0_select_2,d_select_2,k_sigma_thr,delta_integral)
    time_tensor_x1_0,avg_tensorx1_0, std_dev_tensorx1_0,num_bin_x1_0,values_Peak_x1_0 = calculate_moving_average(dx1_select,d_select,k_sigma_thr,delta_integral)
    time_tensor_x1_1,avg_tensorx1_1, std_dev_tensorx1_1,num_bin_x1_1,values_Peak_x1_1 = calculate_moving_average(dx1_select_2,d_select_2,k_sigma_thr,delta_integral)
    print('time_tensor_x0_0 ', time_tensor_x0_0.shape)
    print('time_tensor_x1_0 ', time_tensor_x1_0.shape)
    print('time_tensor_x0_1 ', time_tensor_x0_1.shape)
    print('time_tensor_x1_1 ', time_tensor_x1_1.shape)

    time_tensor_y0_0,avg_tensory0_0, std_dev_tensory0_0,num_bin_y0_0,values_Peak_y0_0 = calculate_moving_average(dy0_select,d_select,k_sigma_thr,delta_integral)
    time_tensor_y0_1,avg_tensory0_1, std_dev_tensory0_1,num_bin_y0_1,values_Peak_y0_1 = calculate_moving_average(dy0_select_2,d_select_2,k_sigma_thr,delta_integral)
    time_tensor_y1_0,avg_tensory1_0, std_dev_tensory1_0,num_bin_y1_0,values_Peak_y1_0 = calculate_moving_average(dy1_select,d_select,k_sigma_thr,delta_integral)
    time_tensor_y1_1,avg_tensory1_1, std_dev_tensory1_1,num_bin_y1_1,values_Peak_y1_1 = calculate_moving_average(dy1_select_2,d_select_2,k_sigma_thr,delta_integral)
    print('time_tensor_y0_0 ', time_tensor_y0_0.shape)
    print('time_tensor_y1_0 ', time_tensor_y1_0.shape)
    print('time_tensor_y0_1 ', time_tensor_y0_1.shape)
    print('time_tensor_y1_1 ', time_tensor_y1_1.shape)

    time_tensor_z0_0,avg_tensorz0_0, std_dev_tensorz0_0,num_bin_z0_0,values_Peak_z0_0 = calculate_moving_average(dz0_select,d_select,k_sigma_thr,delta_integral)
    time_tensor_z0_1,avg_tensorz0_1, std_dev_tensorz0_1,num_bin_z0_1,values_Peak_z0_1 = calculate_moving_average(dz0_select_2,d_select_2,k_sigma_thr,delta_integral)
    time_tensor_z1_0,avg_tensorz1_0, std_dev_tensorz1_0,num_bin_z1_0,values_Peak_z1_0 = calculate_moving_average(dz1_select,d_select,k_sigma_thr,delta_integral)
    time_tensor_z1_1,avg_tensorz1_1, std_dev_tensorz1_1,num_bin_z1_1,values_Peak_z1_1 = calculate_moving_average(dz1_select_2,d_select_2,k_sigma_thr,delta_integral)
    print('time_tensor_z0_0 ', time_tensor_z0_0.shape)
    print('time_tensor_z1_0 ', time_tensor_z1_0.shape)
    print('time_tensor_z0_1 ', time_tensor_z0_1.shape)
    print('time_tensor_z1_1 ', time_tensor_z1_1.shape)

    save_trigger_file(num_bin_x0_0,time_tensor_x0_0,avg_tensorx0_0, std_dev_tensorx0_0,values_Peak_x0_0,directory_output+"points_x0_0.txt")
    save_trigger_file(num_bin_x0_1,time_tensor_x0_1,avg_tensorx0_1, std_dev_tensorx0_1,values_Peak_x0_1,directory_output+"points_x0_1.txt")
    save_trigger_file(num_bin_x1_0,time_tensor_x1_0,avg_tensorx1_0, std_dev_tensorx1_0,values_Peak_x1_0,directory_output+"points_x1_0.txt")
    save_trigger_file(num_bin_x1_1,time_tensor_x1_1,avg_tensorx1_1, std_dev_tensorx1_1,values_Peak_x1_1,directory_output+"points_x1_1.txt")

    save_trigger_file(num_bin_y0_0,time_tensor_y0_0,avg_tensory0_0, std_dev_tensory0_0,values_Peak_y0_0,directory_output+"points_y0_0.txt")
    save_trigger_file(num_bin_y0_1,time_tensor_y0_1,avg_tensory0_1, std_dev_tensory0_1,values_Peak_y0_1,directory_output+"points_y0_1.txt")
    save_trigger_file(num_bin_y1_0,time_tensor_y1_0,avg_tensory1_0, std_dev_tensory1_0,values_Peak_y1_0,directory_output+"points_y1_0.txt")
    save_trigger_file(num_bin_y1_1,time_tensor_y1_1,avg_tensory1_1, std_dev_tensory1_1,values_Peak_y1_1,directory_output+"points_y1_1.txt")

    save_trigger_file(num_bin_z0_0,time_tensor_z0_0,avg_tensorz0_0, std_dev_tensorz0_0,values_Peak_z0_0,directory_output+"points_z0_0.txt")
    save_trigger_file(num_bin_z0_1,time_tensor_z0_1,avg_tensorz0_1, std_dev_tensorz0_1,values_Peak_z0_1,directory_output+"points_z0_1.txt")
    save_trigger_file(num_bin_z1_0,time_tensor_z1_0,avg_tensorz1_0, std_dev_tensorz1_0,values_Peak_z1_0,directory_output+"points_z1_0.txt")
    save_trigger_file(num_bin_z1_1,time_tensor_z1_1,avg_tensorz1_1, std_dev_tensorz1_1,values_Peak_z1_1,directory_output+"points_z1_1.txt")
    
