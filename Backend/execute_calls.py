import sys
from ML_models.lstm import LSTMModel
from ML_models.isolation_forest import IsolationForest
import pandas as pd
import numpy as np
import os
from socket import socket

# Third-Party
import threading
from pathlib import Path
import multiprocessing as mp
import pandas as pd
from typing import Union, List, Optional, Dict

# Custom
from Simulator.DBAPI.type_classes import Job
from Simulator.DBAPI.type_classes import AnomalySetting
from Simulator.SimulatorEngine import SimulatorEngine as se

MODEL_DIRECTORY = "./ML_models"
INJECTION_METHOD_DIRECTORY = "./Simulator/AnomalyInjector/InjectionMethods"
DATASET_DIRECTORY = "./Datasets"

# Starts processing of dataset in one batch
def run_batch(db_conn_params, model: str, path: str, name: str, inj_params: dict=None, debug=False) -> None:
    print("Starting Batch-job!")
    sys.stdout.flush()
    
    if inj_params is not None:
        anomaly = AnomalySetting(
        inj_params.get("anomaly_type", None),
        int(inj_params.get("timestamp", None)),
        int(inj_params.get("magnitude", None)),
        int(inj_params.get("percentage", None)),
        inj_params.get("columns", None),
        inj_params.get("duration", None)) 
        batch_job = Job(filepath=path, anomaly_settings=[anomaly], simulation_type="batch", speedup=None, table_name=name, debug=debug)
    else:
        batch_job = Job(filepath=path, simulation_type="batch", anomaly_settings=None, speedup=None, table_name=name, debug=debug)
    sim_engine = se()
    sim_engine.main(db_conn_params, batch_job)

"""
    #Removing the "is_injected" & "is_anomaly" columns
    feature_df = df.iloc[:, :-2]

    #Creating an instance of the model
    match model:
        case "lstm":
            time_steps=30
            lstm_instance = LSTMModel()
            lstm_instance.run(df.iloc[:, :-2], time_steps)
            anomalies = lstm_instance.detect(df.iloc[:, :-2])
            try: 
                df["is_anomaly"] = anomalies
            except Exception as e:
                print(f'ERROR: {e}')
        
        case "isolation_forest":
            if_instance = IsolationForest()
            if_instance.run(df.iloc[:, :-2])

            anomalies = if_instance.detect(df.iloc[:, :-2])
            df["is_anoamaly"] = anomalies
        
        case _:
            raise Exception("Model not found")
"""

# Starts processing of dataset as a stream
def run_stream(db_conn_params, model: str, path: str, name: str, speedup: int, inj_params: dict=None, debug=False) -> None:
    print("Starting Stream-job!")
    sys.stdout.flush()
    if inj_params is not None:
        anomaly = AnomalySetting(
        inj_params.get("anomaly_type", None),
        int(inj_params.get("timestamp", None)),
        int(inj_params.get("magnitude", None)),
        int(inj_params.get("percentage", None)),
        inj_params.get("columns", None),
        inj_params.get("duration", None)) 
        print("Should inject anomaly.")
        stream_job = Job(filepath=path, anomaly_settings=[anomaly], simulation_type="stream", speedup=speedup, table_name=name, debug=debug)
    else:
        print("Should not inject anomaly.")
        stream_job = Job(filepath=path, simulation_type="stream", speedup=speedup, table_name=name, debug=debug)

    sim_engine = se()
    sim_engine.main(db_conn_params, stream_job)

# Returns a list of models implemented in MODEL_DIRECTORY
def get_models() -> list:
    models = []
    for path in os.listdir(MODEL_DIRECTORY):
        file_path = MODEL_DIRECTORY + "/" + path
        if os.path.isfile(file_path):
            model_name = path.split(".")[0]
            models.append(model_name)

    # Removing the __init__, setup files and the .env file
    models.remove("")
    models.remove("model_interface")
    models.remove("__init__")
    models.remove("setup")
    
    return models

# Returns a list of injection methods implemented in INJECTION_METHOD_DIRECTORY
def get_injection_methods() -> list:
    injection_methods = []

    for path in os.listdir(INJECTION_METHOD_DIRECTORY):
        if os.path.isfile(os.path.join(INJECTION_METHOD_DIRECTORY, path)):
            method_name = path.split(".")[0]
            injection_methods.append(method_name)

    injection_methods.remove("__init__")
    return injection_methods

# Fetching datasets from the dataset directory
def get_datasets() -> list:
    datasets = []
    for path in os.listdir(DATASET_DIRECTORY):
        file_path = DATASET_DIRECTORY + "/" + path
        if os.path.isfile(file_path):
            dataset = path
            datasets.append(dataset)

    return datasets

