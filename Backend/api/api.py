import os
import socket
import json
from time import sleep
from datetime import datetime

class BackendAPI:
    # Constructor setting host adress and port for the the backend container
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    # Sends a request to the backend to start a batch job
    def run_batch(self, model: str, dataset: str, name: str, debug=False, inj_params: dict=None) -> None:
        data = {
            "METHOD": "run-batch",
            "model": model,
            "dataset": dataset,
            "name": name,
            "debug": debug
        }
        if inj_params:
            data["inj_params"] = inj_params

        self.__send_data(data, response=False)

    # Sends a request to the backend to start a stream job
    def run_stream(self, model: str,dataset: str, name: str, speedup: int, debug=False, inj_params: dict=None) -> None:
        data = {
            "METHOD": "run-stream",
            "model": model,
            "dataset": dataset,
            "name": name,
            "speedup": speedup,
            "debug" : debug
        }
        if inj_params:
            data["inj_params"] = inj_params
            
        self.__send_data(data, response=False)

    # Requests each row of data of a running job from timestamp and forward
    def get_data(self, from_timestamp: str, name: str, to_timestamp: str=None) -> str:
        data = {
                "METHOD": "get-data",
                "from_timestamp": from_timestamp,
                "to_timestamp": to_timestamp,
                "job_name": name
            }
        return self.__send_data(data)

    # Get all running jobs
    def get_running(self) -> str:
        data = {
            "METHOD": "get-running"
        }
        return self.__send_data(data)
    
    # Cancels a running job, deletes the data and stops the anomaly detection
    def cancel_job(self, name: str) -> None:
        data = {
            "METHOD": "cancel-job",
            "job_name": name
        }
        self.__send_data(data, response=False)
    
    # Get all available models for anomaly detection
    def get_models(self) -> str:
        data = {
            "METHOD": "get-models"
        }
        return self.__send_data(data)
    
    # Get all available anomaly injection methods
    def get_injection_methods(self) -> str:
        data = {
            "METHOD": "get-injection-methods"
        }
        return self.__send_data(data)
    
    # Get all available datasets
    def get_datasets(self) -> str:
        data = {
            "METHOD": "get-datasets"
        }
        return self.__send_data(data)
    
    # Uploads a complete dataset to the backend
    def import_dataset(self, file_path: str, timestamp_column: str) -> None:
        if not os.path.isfile(file_path):
            return handle_error(2, "File not found")

        file = open(file_path, "r")
        file_content = file.read()
        data = {
            "METHOD": "import-dataset",
            "name": os.path.basename(file_path),
            "timestamp_column": timestamp_column,
            "file_content": file_content
        }
        
        self.__send_data(data, response=False)

    # Get all started and running jobs from the backend
    def get_all_jobs(self) -> str:
        data = {
            "METHOD": "get-all-jobs"
        }
        return self.__send_data(data)

    # Get columns of a running job
    def get_columns(self, name: str) -> str:
        data = {
            "METHOD": "get-columns",
            "name": name
        }
        return self.__send_data(data)

    def get_dataset_columns(self, dataset: str) -> str:
        data = {
            "METHOD": "get-dataset-columns",
            "dataset": dataset
        }
        return self.__send_data(data)

    # Initates connection to backend and sends json data through the socket
    def __send_data(self, data: str, response: bool=True) -> str:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))

            # Send two messages through the same connection if the method is import-dataset
            if data["METHOD"] == "import-dataset":
                file_content = data["file_content"]
                del data["file_content"]
                data = json.dumps(data)
                sock.sendall(bytes(data, encoding="utf-8"))
                sleep(0.5)
                sock.sendall(bytes(file_content, encoding="utf-8"))
            elif data["METHOD"] == "get-data":       
                data = json.dumps(data)
                sock.sendall(bytes(data, encoding="utf-8"))

                recv_data = sock.recv(1024).decode("utf-8")
                json_data = recv_data
                while recv_data:
                    sock.settimeout(1)
                    recv_data = sock.recv(1024).decode("utf-8")
                    if recv_data:
                        json_data += recv_data
                
                data = json.loads(json_data)
                return data
            else:
                data = json.dumps(data)
                sock.sendall(bytes(data, encoding="utf-8"))
            if response:
                data = sock.recv(1024)
                data = data.decode("utf-8")
                return data
        except Exception as e:
            print(e)