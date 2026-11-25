import sys
sys.path.append("/home/gamma/airflow/modules")
from datetime import datetime
from cosidag import COSIDAG
from cosidag import cfg
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import ExternalPythonOperator,BranchPythonOperator
from numpy import ndarray
from airflow.utils.trigger_rule import TriggerRule

def monitor_data():
    directory_monitor = "/home/gamma/workspace/data/obs/"
    return directory_monitor

def build_custom(dag):
    # ==============================================
    # 1. External interpreters + library dirs (same conventions as other DAGs)
    # ==============================================
    EXTERNAL_PYTHON_COSIPY = cfg("EXTERNAL_PYTHON_COSIPY", "/home/gamma/envs/cosipy/bin/python")
    LIB_DIR_COMPREHENSIVE_TRANSIENT_PIPELINE = cfg(
        "COMPREHENSIVE_LIB_DIR",
        "/home/gamma/airflow/pipeline/comprehensive-transient-analysis-pipeline.cfmodule/comprehensive_transient_pipeline/",
    )

    cosipy_yaml_input_file_first = "/home/gamma/workspace/data/pipeline_Comprehensive_GeD_2.yaml"
    
    #######################################
    # full-sky light curve
    def light_curve(config_path: str, lib_dir: str):
        import os
        import sys
        import yaml
        sys.path.append(lib_dir)

        from pipeline_functions import basic_light_curve
        basic_light_curve(config_path,lib_dir)

    ged_light_curve = ExternalPythonOperator(
        task_id="basic_light_curve",
        python=EXTERNAL_PYTHON_COSIPY,
        python_callable=light_curve,
        op_kwargs={
            "config_path": "{{ ti.xcom_pull(task_ids='define_day_config')[0] }}",
            "lib_dir": LIB_DIR_COMPREHENSIVE_TRANSIENT_PIPELINE,
        },
        dag=dag,
    )

    #######################################
    # bin source file
    def binning_data(config_path: str, lib_dir: str,t_start: int,t_stop: int):
        import os
        import sys
        import yaml
        sys.path.append(lib_dir)

        from pipeline_functions import execute_bindata_grb
        execute_bindata_grb(config_path,lib_dir,t_start,t_stop)

    ged_data_binning = ExternalPythonOperator(
        task_id="Data_Binning",
        python=EXTERNAL_PYTHON_COSIPY,
        python_callable=binning_data,
        op_kwargs={
            "config_path": "{{ ti.xcom_pull(task_ids='define_day_config')[0] }}",
            "lib_dir": LIB_DIR_COMPREHENSIVE_TRANSIENT_PIPELINE,
            "t_start": "{{ ti.xcom_pull(task_ids='define_day_config')[1] }}",
            "t_stop": "{{ ti.xcom_pull(task_ids='define_day_config')[2] }}",
        },
        dag=dag,
    )
    #######################################
    
    #######################################
    # bin background file
    def binning_data_bk(config_path: str, lib_dir: str,t_start: int,t_stop: int):
        import os
        import sys
        import yaml
        sys.path.append(lib_dir)

        from pipeline_functions import execute_bindata_background
        execute_bindata_background(config_path,lib_dir,t_start,t_stop)

    ged_data_binning_bk = ExternalPythonOperator(
        task_id="Background_Binning",
        python=EXTERNAL_PYTHON_COSIPY,
        python_callable=binning_data_bk,
        op_kwargs={
            "config_path": "{{ ti.xcom_pull(task_ids='define_day_config')[0] }}",
            "lib_dir": LIB_DIR_COMPREHENSIVE_TRANSIENT_PIPELINE,
            "t_start": "{{ ti.xcom_pull(task_ids='define_day_config')[1] }}",
            "t_stop": "{{ ti.xcom_pull(task_ids='define_day_config')[2] }}",

        },
        dag=dag,
    )
    #######################################
    
    #######################################
    # TS map scan
    def ts_map_scan(config_path: str, lib_dir: str,t_start: int,t_stop: int):
        import os
        import sys
        import yaml
        sys.path.append(lib_dir)

        from pipeline_functions import execute_tsmap_scan
        execute_tsmap_scan(config_path,lib_dir,t_start,t_stop)

    ged_ts_map_scan = ExternalPythonOperator(
        task_id="TSMap_scan",
        python=EXTERNAL_PYTHON_COSIPY,
        python_callable=ts_map_scan,
        op_kwargs={
            "config_path": "{{ ti.xcom_pull(task_ids='define_day_config')[0] }}",
            "lib_dir": LIB_DIR_COMPREHENSIVE_TRANSIENT_PIPELINE,
            "t_start": "{{ ti.xcom_pull(task_ids='define_day_config')[1] }}",
            "t_stop": "{{ ti.xcom_pull(task_ids='define_day_config')[2] }}",

        },
        dag=dag,
    )
    #######################################
    
    #######################################
    # TS map external
    def ts_map_external(config_path: str, lib_dir: str):
        import os
        import sys
        import yaml
        sys.path.append(lib_dir)

        from pipeline_functions import execute_tsmap_external
        execute_tsmap_external(config_path,lib_dir)

    ged_ts_map_external = ExternalPythonOperator(
        task_id="TSMap_external",
        python=EXTERNAL_PYTHON_COSIPY,
        python_callable=ts_map_external,
        op_kwargs={
            "config_path": "{{ ti.xcom_pull(task_ids='define_day_config')[0] }}",
            "lib_dir": LIB_DIR_COMPREHENSIVE_TRANSIENT_PIPELINE,
        },
        dag=dag,
    )
    #######################################
    
    #######################################
    # Check for external triggers
         
    def check_external_task(config_path: str, lib_dir: str,ext_trigg_list_num: int):
        import os
        import sys
        import yaml
        sys.path.append(lib_dir)
        from funzioni_comuni import count_trigger_num
        print('External trigger number ',ext_trigg_list_num)
        # if num_trigger>0:
        if int(ext_trigg_list_num)>0:
            return "TSMap_external"
        else:
            return None
    
    check_external_funct = BranchPythonOperator(
        task_id="check_external_trigg",
        python_callable=check_external_task,
        op_kwargs={
            "config_path": "{{ ti.xcom_pull(task_ids='define_day_config')[0] }}",
            "lib_dir": LIB_DIR_COMPREHENSIVE_TRANSIENT_PIPELINE,
            "ext_trigg_list_num": "{{ ti.xcom_pull(task_ids='define_day_config')[4] }}",

        },
    )
        
    #######################################
    
    #######################################
    # Spectral fit 
    def execute_spectral_fit(config_path: str, lib_dir: str,model_fit: int, scan_flag: int, flag_CNN_in: int,t_start: int,t_stop: int):
        import sys
        sys.path.append(lib_dir)
        from pipeline_functions import execute_threemlfit
        execute_threemlfit(config_path,lib_dir,model_fit,scan_flag,flag_CNN_in,t_start,t_stop)
    
    fittask_externaltrigger = []
    for i in range(2):
        modelname=""
        if i==0:
            modelname="fit_spectrum_pw_externaltrigger"
        if i==1:
            modelname="fit_spectrum_band_externaltrigger"

        t = ExternalPythonOperator(
        task_id=modelname,
        python=EXTERNAL_PYTHON_COSIPY,  # Specifica l'interprete dell'ambiente cosipy
        python_callable=execute_spectral_fit,
        op_kwargs={
            "config_path": "{{ ti.xcom_pull(task_ids='define_day_config')[0] }}",
            "lib_dir": LIB_DIR_COMPREHENSIVE_TRANSIENT_PIPELINE,
            "model_fit": i,
            "scan_flag": 0,
            "flag_CNN_in": 0,
            "t_start": "{{ ti.xcom_pull(task_ids='define_day_config')[1] }}",
            "t_stop": "{{ ti.xcom_pull(task_ids='define_day_config')[2] }}",

        },

        )
        fittask_externaltrigger.append(t)
        
    
    fittask_CNN = []
    for i in range(2):
        modelname=""
        if i==0:
            modelname="fit_spectrum_pw_CNN"
        if i==1:
            modelname="fit_spectrum_band_CNN"

        t = ExternalPythonOperator(
        task_id=modelname,
        python=EXTERNAL_PYTHON_COSIPY,  # Specifica l'interprete dell'ambiente cosipy
        python_callable=execute_spectral_fit,
        op_kwargs={
            "config_path": "{{ ti.xcom_pull(task_ids='define_day_config')[0] }}",
            "lib_dir": LIB_DIR_COMPREHENSIVE_TRANSIENT_PIPELINE,
            "model_fit": i,
            "scan_flag": 0,
            "flag_CNN_in": 1,
            "t_start": "{{ ti.xcom_pull(task_ids='define_day_config')[1] }}",
            "t_stop": "{{ ti.xcom_pull(task_ids='define_day_config')[2] }}",
        },

        )
        fittask_CNN.append(t)
    
    fittask_scan = []
    for i in range(2):
        modelname=""
        if i==0:
            modelname="fit_spectrum_pw_scan"
        if i==1:
            modelname="fit_spectrum_band_scan"

        t = ExternalPythonOperator(
        task_id=modelname,
        python=EXTERNAL_PYTHON_COSIPY,  # Specifica l'interprete dell'ambiente cosipy
        python_callable=execute_spectral_fit,
        op_kwargs={
            "config_path": "{{ ti.xcom_pull(task_ids='define_day_config')[0] }}",
            "lib_dir": LIB_DIR_COMPREHENSIVE_TRANSIENT_PIPELINE,
            "model_fit": i,
            "scan_flag": 1,
            "flag_CNN_in": 0,
            "t_start": "{{ ti.xcom_pull(task_ids='define_day_config')[1] }}",
            "t_stop": "{{ ti.xcom_pull(task_ids='define_day_config')[2] }}",
        },

        )
        fittask_scan.append(t)
        
    #######################################
    
    #######################################
    # Build imaging pdf
    def build_pdf(config_path: str, lib_dir: str):
        import os
        import sys
        import yaml
        sys.path.append(lib_dir)

        from pipeline_functions import build_pdf_file
        build_pdf_file(config_path,lib_dir)

    build_pdf_task = ExternalPythonOperator(
        task_id="Build_pdf",
        python=EXTERNAL_PYTHON_COSIPY,
        python_callable=build_pdf,
        op_kwargs={
            "config_path": "{{ ti.xcom_pull(task_ids='define_day_config')[0] }}",
            "lib_dir": LIB_DIR_COMPREHENSIVE_TRANSIENT_PIPELINE,
        },
        dag=dag,
    )
    #######################################
    
    #######################################
    # Build spectral fit pdf
    def build_spectral_pdf(config_path: str, lib_dir: str,model_merge: str):
        import os
        import sys
        import yaml
        sys.path.append(lib_dir)

        from pipeline_functions import build_spectral_fit
        build_spectral_fit(config_path,lib_dir,model_merge)

    merge_spectral_fit_multiple = []
    for i in range(2):
        modelname=""
        if i==0:
            modelname="pw"
        if i==1:
            modelname="band"

        t = ExternalPythonOperator(
        task_id='merge_spectral_fit_plots_'+modelname,
        python=EXTERNAL_PYTHON_COSIPY,
        python_callable=build_spectral_pdf,
        op_kwargs={
            "config_path": "{{ ti.xcom_pull(task_ids='define_day_config')[0] }}",
            "lib_dir": LIB_DIR_COMPREHENSIVE_TRANSIENT_PIPELINE,
            "model_merge": modelname
        },
        )
        merge_spectral_fit_multiple.append(t)

    #######################################
    
    #######################################
    # Build alert file
    def build_alert_file(config_path: str, lib_dir: str):
        import os
        import sys
        import yaml
        sys.path.append(lib_dir)

        from pipeline_functions import prepare_alert_external
        prepare_alert_external(config_path,lib_dir)

    build_alert_task = ExternalPythonOperator(
        task_id="Build_alert",
        python=EXTERNAL_PYTHON_COSIPY,
        python_callable=build_alert_file,
        op_kwargs={
            "config_path": "{{ ti.xcom_pull(task_ids='define_day_config')[0] }}",
            "lib_dir": LIB_DIR_COMPREHENSIVE_TRANSIENT_PIPELINE,
        },
        dag=dag,
    )
    #######################################
    
    # redefine config for specific data download
    def redefine_config(config_path: str, lib_dir: str,dir_mon: str):
        import os
        import sys
        import yaml
        sys.path.append(lib_dir)

        from pipeline_functions import define_day_config
        return define_day_config(config_path,lib_dir,dir_mon)
        
    define_config = ExternalPythonOperator(
        task_id="define_day_config",
        python=EXTERNAL_PYTHON_COSIPY,
        python_callable=redefine_config,
        op_kwargs={
            "config_path": cosipy_yaml_input_file_first,
            "lib_dir": LIB_DIR_COMPREHENSIVE_TRANSIENT_PIPELINE,
            "dir_mon": monitor_data(),
        },
        dag=dag,
    )
    
    #######################################
    # Clean up and format
    def cleanup_funct(config_path: str, lib_dir: str):
        import os
        import sys
        import yaml
        sys.path.append(lib_dir)

        from pipeline_functions import cleanup_and_format
        cleanup_and_format(config_path,lib_dir)

    cleanup_task = ExternalPythonOperator(
        task_id="Cleanup_function",
        python=EXTERNAL_PYTHON_COSIPY,
        python_callable=cleanup_funct,
        op_kwargs={
            #"config_path": cosipy_yaml_input_file_first,
            "config_path": "{{ ti.xcom_pull(task_ids='define_day_config')[0] }}",
            "lib_dir": LIB_DIR_COMPREHENSIVE_TRANSIENT_PIPELINE,
        },
        dag=dag,
    )
    #######################################
    
    #######################################
    # Anomaly detection
    def transient_id_anomaly(config_path: str, lib_dir: str,t_start: int,t_stop: int):
        import os
        import sys
        import yaml
        sys.path.append(lib_dir)

        from pipeline_functions import anomaly_detection_autoencoder
        anomaly_detection_autoencoder(config_path,lib_dir,t_start,t_stop)

    transient_id_anomaly_task = ExternalPythonOperator(
        task_id="AnomalyDetection",
        python=EXTERNAL_PYTHON_COSIPY,
        python_callable=transient_id_anomaly,
        op_kwargs={
            "config_path": "{{ ti.xcom_pull(task_ids='define_day_config')[0] }}",
            "lib_dir": LIB_DIR_COMPREHENSIVE_TRANSIENT_PIPELINE,
            "t_start": "{{ ti.xcom_pull(task_ids='define_day_config')[1] }}",
            "t_stop": "{{ ti.xcom_pull(task_ids='define_day_config')[2] }}",

        },
        dag=dag,
    )
    #######################################
    
    #######################################
    # CNN localization
    def localization_cnn(config_path: str, lib_dir: str,t_start: int,t_stop: int):
        import os
        import sys
        import yaml
        sys.path.append(lib_dir)

        from pipeline_functions import cnn_locate
        cnn_locate(config_path,lib_dir,t_start,t_stop)

    localization_cnn_task = ExternalPythonOperator(
        task_id="CNN_localization",
        python=EXTERNAL_PYTHON_COSIPY,
        python_callable=localization_cnn,
        op_kwargs={
            "config_path": "{{ ti.xcom_pull(task_ids='define_day_config')[0] }}",
            "lib_dir": LIB_DIR_COMPREHENSIVE_TRANSIENT_PIPELINE,
            "t_start": "{{ ti.xcom_pull(task_ids='define_day_config')[1] }}",
            "t_stop": "{{ ti.xcom_pull(task_ids='define_day_config')[2] }}",

        },
        dag=dag,
    )
    
    #######################################
    #  save transient fits files
    def transient_fits_save(config_path: str, lib_dir: str,time_tot_start: int,time_tot_stop: int):
        import os
        import sys
        import yaml
        sys.path.append(lib_dir)

        from pipeline_functions import create_output_files_transient
        create_output_files_transient(config_path,lib_dir,time_tot_start,time_tot_stop)
    
    save_fits = ExternalPythonOperator(
        task_id="save_transient_fits",
        python=EXTERNAL_PYTHON_COSIPY,
        python_callable=transient_fits_save,
        op_kwargs={
            "config_path": "{{ ti.xcom_pull(task_ids='define_day_config')[0] }}",
            "lib_dir": LIB_DIR_COMPREHENSIVE_TRANSIENT_PIPELINE,
            "time_tot_start": "{{ ti.xcom_pull(task_ids='define_day_config')[1] }}",
            "time_tot_stop": "{{ ti.xcom_pull(task_ids='define_day_config')[2] }}",
        },
        dag=dag,
    )
    
    #######################################
    
    #######################################

    join = EmptyOperator(task_id="join")
    join2 = EmptyOperator(task_id="join2")
    
    ######### wiring definition #####
    
    define_config>>cleanup_task>>[ged_data_binning,ged_data_binning_bk]>>join
    join>>[ged_ts_map_scan,transient_id_anomaly_task,check_external_funct]
    check_external_funct>>ged_ts_map_external>>fittask_externaltrigger>>join2
    ged_ts_map_scan>>fittask_scan>>join2
    transient_id_anomaly_task>>localization_cnn_task>>fittask_CNN>>join2
    join2>>ged_light_curve>>build_pdf_task>>merge_spectral_fit_multiple>>save_fits>>build_alert_task
    
    #define_config>>save_fits
    ################################


with COSIDAG(
    dag_id="Comprehensive_GeD_v6",
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    monitoring_folders=[monitor_data()],
    file_patterns={
        "grb_file": "data_grbdc3_full.fits"
    },
    select_policy="latest_mtime",
    only_basename="gct",
    prefer_deepest=True,
    idle_seconds=5,
    level=3,
    build_custom=build_custom,
    tags=["example"],

):
    pass
