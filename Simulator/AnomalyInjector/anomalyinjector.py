import pandas as pd
import numpy as np
from typing import Union, List, Optional, Dict
from DBAPI import utils as ut
from DBAPI.talk_to_backend import AnomalySetting
import datetime as dt

class TimeSeriesAnomalyInjector:
    def __init__(self, seed: int = 42):
        """
        Initialize the Anomaly Injector with a configurable random seed

        Args:
            seed (int, optional): Random seed for reproducibility. Defaults to 42.
        """
        self.rng = np.random.default_rng(seed)
    
    def inject_anomaly(
        self, 
        data: Union[pd.DataFrame, pd.Series],
        anomaly_settings: Optional[Union[AnomalySetting, List[AnomalySetting]]] = None,
    ) -> Union[pd.DataFrame, pd.Series]:
        if isinstance(anomaly_settings, AnomalySetting):
            anomaly_settings = [anomaly_settings]

        if not anomaly_settings:
            return data

        modified_data = data.copy()
        timestamp_col = modified_data.columns[0]

        for setting in anomaly_settings:
            start_time = setting.timestamp
            duration = ut.parse_duration_seconds(setting.duration)
            columns = setting.columns
            anomaly_type = setting.anomaly_type
            percentage = setting.percentage
            magnitude = setting.magnitude

            # Convert timestamp column to datetime
            modified_data[timestamp_col] = pd.to_datetime(modified_data[timestamp_col])
            
            # Convert start_time to datetime
            start_time = pd.to_datetime(start_time) if isinstance(start_time, str) else start_time

            # Calculate end time 
            end_time = start_time + pd.Timedelta(seconds=duration) if duration else start_time

            # Create span mask
            span_mask = (modified_data[timestamp_col] >= start_time) & \
                        (modified_data[timestamp_col] < end_time)

            # Select data within the span
            span_data = modified_data[span_mask]

            # If no columns specified, use all numeric columns
            if not columns:
                columns = list(span_data.select_dtypes(include=[np.number]).columns)
            
            # Inject anomalies for each specified column
            for column in columns:
                if column in span_data.columns:
                    data_range = modified_data[column].max() - modified_data[column].min()
                    mean = modified_data[column].mean()
                    
                    # Calculate number of anomalies to inject
                    num_anomalies = min(len(span_data), max(1, int(len(span_data) * percentage)))
                    
                    print(f"Num_anomalies: {num_anomalies}")

                    if num_anomalies > 0:
                        # Select random indices to modify within the span
                        anomaly_indices = self.rng.choice(
                            span_data.index, 
                            size=num_anomalies, 
                            replace=False
                        )
                        
                        # Apply anomaly
                        modified_data.loc[anomaly_indices, column] = self._apply_anomaly( 
                            modified_data.loc[anomaly_indices, column],
                            data_range,
                            mean,
                            anomaly_type,
                            magnitude,
                        )

        print(modified_data['load-1m'])

        return modified_data

    def _apply_anomaly(self, data, data_range, mean, anomaly_type, magnitude):
        """
        Apply a specific type of anomaly to the data.

        Args:
            data (pd.Series): Data to modify
            anomaly_type (str): Type of anomaly to apply
            magnitude (float): Intensity of the anomaly

        Returns:
            pd.Series: Modified data
        """
        print("______________________")
        if anomaly_type == 'lowered':
            print("Injecting lowerd anomaly!")
            random_factors = self.rng.uniform(0.3, 0.4)
            step_value = -data_range * random_factors
            print(f"Step: {step_value} = -datarange: -{data_range} * random: {random_factors} = {-data_range * random_factors}")
            print(f"OLD: {data}. NEW: {np.maximum(data + step_value, 0)}")
            print(f"return: {np.maximum(data + step_value, 0)}")

            return np.maximum(data + step_value, 0)
        
        elif anomaly_type == 'spike':
            print("Injecting spike anomaly!")
            std_dev = data.std()
            modifications = self.rng.normal(
                loc=0, 
                scale=std_dev * (magnitude * 2)
            )
            return data + modifications
        
        elif anomaly_type == 'step':
            print("Injecting step anomaly!")
            step_value = mean * magnitude
            return data + step_value
        
        elif anomaly_type == 'custom':
            print("Injecting custom anomaly!")
            return data * magnitude
        
        else:
            return data