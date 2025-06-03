"""
Main entry point for the R&D Simulation OEE application.

This module provides the main functions to run the application either 
in GUI mode or from the command line.
"""

import argparse
import datetime
import json
import os
import sys
from typing import Dict, Any

from .oee_calculator import OEECalculator
from .data_handler import SimulationDataHandler
from .gui import run_dashboard


def run_gui():
    """Run the OEE application in GUI mode."""
    run_dashboard()


def run_cli(args):
    """
    Run the OEE application in command-line mode.
    
    Args:
        args: Command line arguments
    """
    data_handler = SimulationDataHandler()
    oee_calculator = OEECalculator()
    
    if args.command == "calculate":
        # Calculate OEE from command line arguments
        oee_data = oee_calculator.calculate_complete_oee(
            planned_time=args.planned_time,
            downtime=args.downtime,
            actual_cycle_time=args.actual_cycle_time,
            ideal_cycle_time=args.ideal_cycle_time,
            total_simulations=args.total_simulations,
            failed_simulations=args.failed_simulations
        )
        
        # Generate and print report
        report = oee_calculator.generate_report(oee_data, args.model_name)
        print(report)
        
        # Save data if requested
        if args.save:
            simulation_data = {
                "planned_time": args.planned_time,
                "downtime": args.downtime,
                "actual_cycle_time": args.actual_cycle_time,
                "ideal_cycle_time": args.ideal_cycle_time,
                "total_simulations": args.total_simulations,
                "failed_simulations": args.failed_simulations,
                "availability": oee_data["availability"],
                "performance": oee_data["performance"],
                "quality": oee_data["quality"],
                "oee": oee_data["oee"],
                "notes": args.notes
            }
            
            file_path = data_handler.save_simulation_run(simulation_data, args.model_name)
            print(f"Data saved to {file_path}")
    
    elif args.command == "report":
        # Generate report for a specific model
        model_name = args.model_name
        days = args.days
        
        # Get recent data
        data_list = data_handler.get_recent_simulations(model_name, days=days)
        
        if not data_list:
            print(f"No data found for model '{model_name}' in the last {days} days.")
            return
        
        # Calculate average metrics
        avg_metrics = data_handler.calculate_average_metrics(data_list)
        
        # Print summary report
        print(f"OEE REPORT - {model_name}")
        print(f"Data from the last {days} days")
        print(f"Number of simulation runs: {len(data_list)}")
        print("=" * 50)
        print(f"Average Availability: {avg_metrics.get('availability', 0):.2%}")
        print(f"Average Performance: {avg_metrics.get('performance', 0):.2%}")
        print(f"Average Quality: {avg_metrics.get('quality', 0):.2%}")
        print("=" * 30)
        print(f"Average OEE: {avg_metrics.get('oee', 0):.2%}")
        
    elif args.command == "list":
        # List recent simulations
        model_name = args.model_name if args.model_name != "all" else None
        days = args.days
        
        # Get recent data
        data_list = data_handler.get_recent_simulations(model_name, days=days)
        
        if not data_list:
            print(f"No simulation data found" + 
                  (f" for model '{model_name}'" if model_name else "") + 
                  f" in the last {days} days.")
            return
        
        # Print list of simulations
        print(f"Recent Simulations" + 
              (f" for model '{model_name}'" if model_name else "") + 
              f" in the last {days} days:")
        print("=" * 80)
        print(f"{'Timestamp':<20} {'Model':<25} {'Availability':<12} {'Performance':<12} {'Quality':<12} {'OEE':<12}")
        print("-" * 80)
        
        for item in data_list:
            timestamp = item.get('timestamp', '')
            try:
                dt = datetime.datetime.fromisoformat(timestamp)
                timestamp_str = dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                timestamp_str = timestamp
                
            model = item.get('model_name', 'Unknown')
            availability = item.get('availability', 0)
            performance = item.get('performance', 0)
            quality = item.get('quality', 0)
            oee = item.get('oee', 0)
            
            print(f"{timestamp_str:<20} {model:<25} {availability:.2%:<12} {performance:.2%:<12} {quality:.2%:<12} {oee:.2%:<12}")


def setup_parser():
    """Set up the command line argument parser."""
    parser = argparse.ArgumentParser(description='R&D Simulation OEE Calculator')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # GUI command
    gui_parser = subparsers.add_parser('gui', help='Run the GUI dashboard')
    
    # Calculate command
    calc_parser = subparsers.add_parser('calculate', help='Calculate OEE from command line')
    calc_parser.add_argument('--model-name', type=str, default='Simulation Model',
                           help='Name of the simulation model')
    calc_parser.add_argument('--planned-time', type=float, required=True,
                           help='Planned simulation time in minutes')
    calc_parser.add_argument('--downtime', type=float, required=True,
                           help='Downtime in minutes')
    calc_parser.add_argument('--actual-cycle-time', type=float, required=True,
                           help='Actual cycle time in minutes')
    calc_parser.add_argument('--ideal-cycle-time', type=float, required=True,
                           help='Ideal cycle time in minutes')
    calc_parser.add_argument('--total-simulations', type=int, required=True,
                           help='Total number of simulations')
    calc_parser.add_argument('--failed-simulations', type=int, required=True,
                           help='Number of failed simulations')
    calc_parser.add_argument('--notes', type=str, default='',
                           help='Notes about this simulation run')
    calc_parser.add_argument('--save', action='store_true',
                           help='Save the calculation results')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate a summary report')
    report_parser.add_argument('--model-name', type=str, required=True,
                             help='Name of the simulation model')
    report_parser.add_argument('--days', type=int, default=30,
                             help='Number of days to include in the report')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List recent simulations')
    list_parser.add_argument('--model-name', type=str, default='all',
                           help='Name of the simulation model, or "all" for all models')
    list_parser.add_argument('--days', type=int, default=30,
                           help='Number of days to look back')
    
    return parser


def main():
    """Main entry point for the application."""
    parser = setup_parser()
    args = parser.parse_args()
    
    if not args.command or args.command == 'gui':
        run_gui()
    else:
        run_cli(args)


if __name__ == "__main__":
    main() 