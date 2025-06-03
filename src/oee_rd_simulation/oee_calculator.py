"""
OEE Calculator for R&D Department

This module calculates Overall Equipment Effectiveness (OEE) for R&D processes,
focusing on computational resources, model training, and simulation efficiency.

OEE = Availability (A) × Efficiency (B) × Quality (C) = Effectiveness (Z)
"""

import datetime
import json
import os
from typing import Dict, List, Tuple, Optional
import logging


class OEECalculator:
    """
    Calculates OEE metrics for R&D Department's computational processes and tools.
    """
    
    def __init__(self, data_source: Optional[str] = None):
        """
        Initialize OEE calculator with data source path.
        
        Args:
            data_source: Path to data source file or directory (optional)
        """
        self.data_source = data_source
        self.simulation_data = {}

    def load_data(self, data: Dict = None):
        """
        Load simulation data either from file or direct input.
        
        Args:
            data: Dictionary containing simulation data (optional)
        """
        if data:
            self.simulation_data = data
        elif self.data_source and os.path.exists(self.data_source):
            try:
                with open(self.data_source, 'r') as f:
                    self.simulation_data = json.load(f)
            except Exception as e:
                print(f"Error loading data: {e}")
                self.simulation_data = {}
    
    def calculate_availability(self, total_time: float, downtime: float) -> float:
        """
        Calculate Availability (A): (Total Time - Downtime) / Total Time
        
        Args:
            total_time: Total planned time in minutes
            downtime: Time when systems were unavailable in minutes
            
        Returns:
            Availability ratio as a float between 0 and 1
        """
        if total_time <= 0:
            return 0
        return max(0, min(1, (total_time - downtime) / total_time))
    
    def calculate_efficiency(self, 
                           completed_simulations: int,
                           total_time: float,
                           ideal_time_per_simulation: float) -> float:
        """
        Calculate Efficiency (B): (Completed Simulations / Total Time) / (Ideal Simulations / Total Time)
        
        Args:
            completed_simulations: Number of simulations completed
            total_time: Total time available in minutes
            ideal_time_per_simulation: Ideal time per simulation in minutes
            
        Returns:
            Efficiency ratio as a float between 0 and 1
        """
        if total_time <= 0 or ideal_time_per_simulation <= 0:
            return 0
            
        ideal_simulations = total_time / ideal_time_per_simulation
        actual_rate = completed_simulations / total_time
        ideal_rate = ideal_simulations / total_time
        
        if ideal_rate <= 0:
            return 0
            
        return max(0, min(1, actual_rate / ideal_rate))
    
    def calculate_quality(self, 
                         total_simulations: int, 
                         valid_simulations: int) -> float:
        """
        Calculate Quality (C): Valid Simulations / Total Simulations
        
        Args:
            total_simulations: Total number of simulations run
            valid_simulations: Number of simulations that meet validation criteria
            
        Returns:
            Quality ratio as a float between 0 and 1
        """
        if total_simulations <= 0:
            return 0
        return max(0, min(1, valid_simulations / total_simulations))
    
    def calculate_effectiveness(self, 
                              availability: float, 
                              efficiency: float, 
                              quality: float) -> float:
        """
        Calculate Overall Effectiveness (Z)
        
        Z = A × B × C
        
        Args:
            availability: Availability ratio (A)
            efficiency: Efficiency ratio (B)
            quality: Quality ratio (C)
            
        Returns:
            Effectiveness as a float between 0 and 1
        """
        return availability * efficiency * quality
    
    def calculate_metrics(self, 
                         total_time: float,
                         downtime: float,
                         completed_simulations: int,
                         ideal_time_per_simulation: float,
                         total_simulations: int,
                         valid_simulations: int) -> Dict[str, float]:
        """
        Calculate OEE metrics for R&D processes.
        
        Args:
            total_time: Total time available for simulations
            downtime: Time when system was unavailable
            completed_simulations: Number of simulations completed
            ideal_time_per_simulation: Ideal time per simulation
            total_simulations: Total number of simulations attempted
            valid_simulations: Number of simulations meeting quality criteria
            
        Returns:
            Dictionary containing calculated metrics
        """
        try:
            # Calculate availability
            availability = ((total_time - downtime) / total_time) * 100 if total_time > 0 else 0
            
            # Calculate efficiency
            actual_time_per_simulation = (total_time - downtime) / completed_simulations if completed_simulations > 0 else 0
            efficiency = (ideal_time_per_simulation / actual_time_per_simulation) * 100 if actual_time_per_simulation > 0 else 0
            
            # Calculate quality
            quality = (valid_simulations / total_simulations) * 100 if total_simulations > 0 else 0
            
            # Calculate overall effectiveness
            effectiveness = (availability * efficiency * quality) / 10000
            
            return {
                'availability': availability,
                'efficiency': efficiency,
                'quality': quality,
                'effectiveness': effectiveness
            }
            
        except Exception as e:
            logging.error(f"Error calculating metrics: {str(e)}")
            return {
                'availability': 0,
                'efficiency': 0,
                'quality': 0,
                'effectiveness': 0
            }
    
    def calculate_complete_oee(self, 
                              total_time: float,
                              downtime: float,
                              completed_simulations: int,
                              ideal_time_per_simulation: float,
                              total_simulations: int,
                              valid_simulations: int) -> Dict[str, float]:
        """
        Calculate all OEE metrics based on input parameters
        
        Args:
            total_time: Total planned time in minutes
            downtime: Time when systems were unavailable in minutes
            completed_simulations: Number of simulations completed
            ideal_time_per_simulation: Ideal time per simulation in minutes
            total_simulations: Total number of simulations run
            valid_simulations: Number of valid simulations
            
        Returns:
            Dictionary with availability (A), efficiency (B), quality (C), and effectiveness (Z)
        """
        availability = self.calculate_availability(total_time, downtime)
        efficiency = self.calculate_efficiency(completed_simulations, total_time, ideal_time_per_simulation)
        quality = self.calculate_quality(total_simulations, valid_simulations)
        effectiveness = self.calculate_effectiveness(availability, efficiency, quality)
        
        return {
            "availability": availability,
            "efficiency": efficiency,
            "quality": quality,
            "effectiveness": effectiveness
        }
    
    def generate_report(self, oee_data: Dict[str, float], model_name: str = "Computational Model") -> str:
        """
        Generate a text report for the OEE calculation
        
        Args:
            oee_data: Dictionary with OEE metrics
            model_name: Name of the model or computational process being evaluated
            
        Returns:
            Formatted report string
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"OEE REPORT - {model_name}\n"
        report += f"Generated: {timestamp}\n"
        report += "=" * 50 + "\n\n"
        
        report += f"Availability (A): {oee_data['availability']:.2%}\n"
        report += f"Efficiency (B): {oee_data['efficiency']:.2%}\n"
        report += f"Quality (C): {oee_data['quality']:.2%}\n"
        report += "=" * 30 + "\n"
        report += f"Overall Effectiveness (Z): {oee_data['effectiveness']:.2%}\n\n"
        
        # Interpretation
        if oee_data['effectiveness'] >= 0.85:
            report += "Status: EXCELLENT - World-class computational efficiency\n"
        elif oee_data['effectiveness'] >= 0.70:
            report += "Status: GOOD - Typical computational performance\n"
        elif oee_data['effectiveness'] >= 0.60:
            report += "Status: FAIR - Room for optimization\n"
        else:
            report += "Status: POOR - Significant optimization needed\n"
            
        # Suggestions for improvement
        report += "\nAreas for Improvement:\n"
        
        if oee_data['availability'] < 0.90:
            report += "- Availability: Optimize resource allocation and reduce system downtime\n"
        
        if oee_data['efficiency'] < 0.95:
            report += "- Efficiency: Optimize algorithms and computational efficiency\n"
        
        if oee_data['quality'] < 0.99:
            report += "- Quality: Improve model validation and error handling\n"
            
        return report 