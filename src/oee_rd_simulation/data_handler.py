"""
Data Handler for R&D and Simulation Department OEE

This module handles data collection, storage, and retrieval for
simulation metrics used in OEE calculations.
"""

import csv
import datetime
import json
import os
import sqlite3
from typing import Dict, List, Optional, Union, Any
import logging


class SimulationDataHandler:
    """
    Handles data operations for simulation metrics used in OEE calculations.
    """
    
    def __init__(self, storage_dir: str = "data"):
        """
        Initialize the data handler with storage directory.
        
        Args:
            storage_dir: Directory to store simulation data
        """
        self.storage_dir = storage_dir
        self._ensure_storage_dir()
        
    def _ensure_storage_dir(self):
        """Create the storage directory if it doesn't exist."""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
    
    def save_simulation_run(self, 
                          simulation_data: Dict[str, Any], 
                          model_name: str,
                          format: str = "json") -> str:
        """
        Save simulation run data to storage.
        
        Args:
            simulation_data: Dictionary with simulation metrics
            model_name: Name of the simulation model
            format: Storage format (json or csv)
            
        Returns:
            Path to the saved data file
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{model_name.replace(' ', '_')}_{timestamp}"
        
        # Add timestamp to data
        simulation_data["timestamp"] = datetime.datetime.now().isoformat()
        simulation_data["model_name"] = model_name
        
        if format.lower() == "json":
            file_path = os.path.join(self.storage_dir, f"{filename}.json")
            with open(file_path, 'w') as f:
                json.dump(simulation_data, f, indent=4)
        
        elif format.lower() == "csv":
            file_path = os.path.join(self.storage_dir, f"{filename}.csv")
            with open(file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=simulation_data.keys())
                writer.writeheader()
                writer.writerow(simulation_data)
        
        return file_path
    
    def load_simulation_run(self, file_path: str) -> Dict[str, Any]:
        """
        Load simulation run data from file.
        
        Args:
            file_path: Path to the simulation data file
            
        Returns:
            Dictionary with simulation data
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data file not found: {file_path}")
        
        if file_path.endswith('.json'):
            with open(file_path, 'r') as f:
                return json.load(f)
                
        elif file_path.endswith('.csv'):
            with open(file_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                return next(reader)  # Return the first row
        
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
    
    def get_recent_simulations(self, 
                              model_name: Optional[str] = None, 
                              days: int = 30,
                              limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent simulation runs from storage.
        
        Args:
            model_name: Filter by model name (optional)
            days: Number of days to look back
            limit: Maximum number of records to return
            
        Returns:
            List of simulation data dictionaries
        """
        results = []
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.storage_dir, filename)
                
                try:
                    data = self.load_simulation_run(file_path)
                    
                    # Filter by model name if provided
                    if model_name and data.get('model_name') != model_name:
                        continue
                    
                    # Parse timestamp and filter by date
                    if 'timestamp' in data:
                        timestamp = datetime.datetime.fromisoformat(data['timestamp'])
                        if timestamp < cutoff_date:
                            continue
                    
                    results.append(data)
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
        
        # Sort by timestamp (newest first) and apply limit
        results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return results[:limit]
    
    def calculate_average_metrics(self, 
                                simulation_data_list: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate average metrics from multiple simulation runs.
        
        Args:
            simulation_data_list: List of simulation data dictionaries
            
        Returns:
            Dictionary with average values for key metrics
        """
        if not simulation_data_list:
            return {}
        
        # Initialize counters
        totals = {
            "total_time": 0,
            "downtime": 0,
            "completed_simulations": 0,
            "ideal_time_per_simulation": 0,
            "total_simulations": 0,
            "valid_simulations": 0,
            "availability": 0,
            "efficiency": 0,
            "quality": 0,
            "effectiveness": 0
        }
        
        # Count valid entries for each metric
        counts = {key: 0 for key in totals.keys()}
        
        # Sum up all metrics
        for data in simulation_data_list:
            for key in totals:
                if key in data and isinstance(data[key], (int, float)):
                    totals[key] += data[key]
                    counts[key] += 1
        
        # Calculate averages
        averages = {}
        for key in totals:
            if counts[key] > 0:
                averages[key] = totals[key] / counts[key]
            else:
                averages[key] = 0
                
        return averages 
    
    def get_latest_data(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent simulation data for a specific model.
        
        Args:
            model_name: Name of the simulation model
            
        Returns:
            Dictionary with the latest simulation data or None if no data exists
        """
        try:
            # Get recent simulations for the model
            data_list = self.get_recent_simulations(model_name, days=30, limit=1)
            
            if not data_list:
                logging.info(f"No data found for model: {model_name}")
                return None
                
            latest_data = data_list[0]
            logging.info(f"Found latest data for {model_name}: {latest_data}")
            return latest_data
            
        except Exception as e:
            logging.error(f"Error getting latest data for {model_name}: {str(e)}")
            return None
            
    def get_process_history(self, model_name: str) -> List[Dict[str, Any]]:
        """
        Get historical data for a specific process.
        
        Args:
            model_name: Name of the simulation model
            
        Returns:
            List of simulation data dictionaries
        """
        try:
            # Get recent simulations for the model
            return self.get_recent_simulations(model_name, days=30)
            
        except Exception as e:
            logging.error(f"Error getting process history: {str(e)}")
            return [] 