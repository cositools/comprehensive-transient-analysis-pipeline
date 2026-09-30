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
    EXTERNAL_PYTHON_COSIPY = cfg("EXTERNAL_PYTHON_COSIPY", "/home/gamma/envs/cosipy_laura/bin/python")
    LIB_DIR_COMPREHENSIVE_TRANSIENT_PIPELINE = cfg(
        "COMPREHENSIVE_LIB_DIR",
        "/home/gamma/airflow/pipeline/comprehensive-transient-analysis-pipeline.cfmodule/comprehensive_transient_pipeline/",
    )

    cosipy_yaml_input_file = "/home/gamma/workspace/data/pipeline_Comprehensive_BGO.yaml"

    #######################################
    # fits file conversion
    def fits_to_hdf5(config_path: str, lib_dir: str):
        import os
        import sys
        import yaml
        sys.path.append(lib_dir)

        from pipeline_functions_BGO import convert_fits_to_hdf5
        convert_fits_to_hdf5(config_path,lib_dir)

    fits_to_hdf5_funct = ExternalPythonOperator(
        task_id="fits_to_hdf5",
        python=EXTERNAL_PYTHON_COSIPY,
        python_callable=fits_to_hdf5,
        op_kwargs={
            "config_path": cosipy_yaml_input_file,
            "lib_dir": LIB_DIR_COMPREHENSIVE_TRANSIENT_PIPELINE,
        },
        dag=dag,
    )
    
    #######################################
    # full-sky light curve
    def light_curve(config_path: str, lib_dir: str):
        import os
        import sys
        import yaml
        sys.path.append(lib_dir)

        from pipeline_functions_BGO import basic_light_curve
        basic_light_curve(config_path,lib_dir)

    bgo_light_curve = ExternalPythonOperator(
        task_id="basic_light_curve",
        python=EXTERNAL_PYTHON_COSIPY,
        python_callable=light_curve,
        op_kwargs={
            "config_path": cosipy_yaml_input_file,
            "lib_dir": LIB_DIR_COMPREHENSIVE_TRANSIENT_PIPELINE,
        },
        dag=dag,
    )

    #######################################
    # moving average detection
    def moving_average(config_path: str, lib_dir: str):
        import os
        import sys
        import yaml
        sys.path.append(lib_dir)

        from pipeline_functions_BGO import moving_average_scan
        moving_average_scan(config_path,lib_dir)

    moving_average_task = ExternalPythonOperator(
        task_id="moving_average",
        python=EXTERNAL_PYTHON_COSIPY,
        python_callable=moving_average,
        op_kwargs={
            "config_path": cosipy_yaml_input_file,
            "lib_dir": LIB_DIR_COMPREHENSIVE_TRANSIENT_PIPELINE,
        },
        dag=dag,
    )
    
    #######################################
    
    join = EmptyOperator(task_id="join")
    join2 = EmptyOperator(task_id="join2")
    
    ######### wiring definition #####  
    fits_to_hdf5_funct>>moving_average_task>>bgo_light_curve
    ################################


with COSIDAG(
    dag_id="Comprehensive_BGO_v1",
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    monitoring_folders=[monitor_data()],
    file_patterns={
        "grb_file": "FullSet_gamma_50ms.fits"
    },
    select_policy="latest_mtime",
    only_basename="bgo",
    prefer_deepest=True,
    idle_seconds=5,
    level=3,
    build_custom=build_custom,
    tags=["example"],
):
    pass
