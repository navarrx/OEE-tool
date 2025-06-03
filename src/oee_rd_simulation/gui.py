"""
GUI Dashboard for OEE in R&D Department

This module provides a graphical user interface for monitoring and analyzing
OEE metrics for computational processes and model training.

OEE = Availability (A) × Efficiency (B) × Quality (C) = Effectiveness (Z)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import datetime
import json
from typing import Dict, List, Any, Optional
import logging

from .oee_calculator import OEECalculator
from .data_handler import SimulationDataHandler


class OEEDashboard:
    """
    GUI Dashboard for OEE visualization and management.
    """
    
    def __init__(self, root):
        """
        Initialize the OEE Dashboard GUI.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("R&D Department OEE Dashboard")
        self.root.geometry("1000x700")
        
        # Initialize data handler and calculator
        self.data_handler = SimulationDataHandler()
        self.oee_calculator = OEECalculator()
        
        # Config file path
        self.config_file = os.path.join("data", "dashboard_config.json")
        
        # Initialize empty state
        self.models = []
        self.current_model = tk.StringVar()
        
        # Load saved state if exists
        self.load_state()
        
        self.setup_ui()
        
        # Add save state button to menu
        self.setup_menu()
    
    def setup_menu(self):
        """Set up the application menu."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save State", command=self.save_state)
        file_menu.add_command(label="Load State", command=self.load_state)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
    
    def save_state(self):
        """Save the current dashboard state to a configuration file."""
        try:
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # Prepare state data
            state = {
                "models": self.models,
                "last_selected_model": self.current_model.get(),
                "window_geometry": self.root.geometry(),
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Save to file
            with open(self.config_file, 'w') as f:
                json.dump(state, f, indent=4)
            
            messagebox.showinfo("Success", "Dashboard state saved successfully!")
            logging.info(f"Dashboard state saved to {self.config_file}")
            
        except Exception as e:
            logging.error(f"Error saving dashboard state: {str(e)}")
            messagebox.showerror("Error", f"Failed to save dashboard state: {str(e)}")
    
    def load_state(self):
        """Load the dashboard state from configuration file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    state = json.load(f)
                
                # Load models list
                self.models = state.get("models", [])
                
                # Set last selected model
                last_model = state.get("last_selected_model")
                if last_model and last_model in self.models:
                    self.current_model.set(last_model)
                elif self.models:
                    self.current_model.set(self.models[0])
                
                # Restore window geometry
                if "window_geometry" in state:
                    self.root.geometry(state["window_geometry"])
                
                logging.info(f"Dashboard state loaded from {self.config_file}")
            else:
                # Start with empty state if no config file exists
                self.models = []
                self.current_model.set("")
                logging.info("No saved state found, starting with empty state")
                
        except Exception as e:
            logging.error(f"Error loading dashboard state: {str(e)}")
            # Start with empty state if loading fails
            self.models = []
            self.current_model.set("")
            messagebox.showerror("Error", f"Failed to load dashboard state: {str(e)}\nStarting with empty state.")
    
    def setup_ui(self):
        """Set up the user interface components."""
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create tab control
        tab_control = ttk.Notebook(main_frame)
        
        # Create tabs
        dashboard_tab = ttk.Frame(tab_control)
        input_tab = ttk.Frame(tab_control)
        history_tab = ttk.Frame(tab_control)
        
        tab_control.add(dashboard_tab, text="Dashboard")
        tab_control.add(input_tab, text="Input Data")
        tab_control.add(history_tab, text="History")
        
        tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Set up each tab
        self.setup_dashboard_tab(dashboard_tab)
        self.setup_input_tab(input_tab)
        self.setup_history_tab(history_tab)
    
    def setup_dashboard_tab(self, parent):
        """Set up the dashboard tab with charts and metrics."""
        # Create header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(header_frame, text="R&D Department OEE Dashboard", 
                 font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Model selection
        model_frame = ttk.Frame(header_frame)
        model_frame.pack(side=tk.RIGHT)
        
        ttk.Label(model_frame, text="Process:").pack(side=tk.LEFT)
        self.dashboard_model_dropdown = ttk.Combobox(model_frame, textvariable=self.current_model, 
                                    values=self.models, state="readonly", width=25)
        self.dashboard_model_dropdown.pack(side=tk.LEFT, padx=5)
        self.dashboard_model_dropdown.bind("<<ComboboxSelected>>", self.update_dashboard)
        
        # Add Process button
        ttk.Button(model_frame, text="Add Process", command=self.add_new_process).pack(side=tk.LEFT, padx=5)
        
        # Delete Process button
        ttk.Button(model_frame, text="Delete Process", command=self.delete_process).pack(side=tk.LEFT, padx=5)
        
        # Create metrics frame
        metrics_frame = ttk.LabelFrame(parent, text="OEE Metrics")
        metrics_frame.pack(fill=tk.X, pady=10, padx=5)
        
        # Create placeholders for metric values
        self.availability_var = tk.StringVar(value="N/A")
        self.efficiency_var = tk.StringVar(value="N/A")
        self.quality_var = tk.StringVar(value="N/A")
        self.effectiveness_var = tk.StringVar(value="N/A")
        
        # Create grid for metrics
        metrics_grid = ttk.Frame(metrics_frame)
        metrics_grid.pack(fill=tk.X, pady=10, padx=10)
        
        # Row 0: Headers
        ttk.Label(metrics_grid, text="Availability (A)", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10)
        ttk.Label(metrics_grid, text="Efficiency (B)", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=10)
        ttk.Label(metrics_grid, text="Quality (C)", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=10)
        ttk.Label(metrics_grid, text="Effectiveness (Z)", font=("Arial", 10, "bold")).grid(row=0, column=3, padx=10)
        
        # Row 1: Values
        ttk.Label(metrics_grid, textvariable=self.availability_var, font=("Arial", 14)).grid(row=1, column=0, padx=10)
        ttk.Label(metrics_grid, textvariable=self.efficiency_var, font=("Arial", 14)).grid(row=1, column=1, padx=10)
        ttk.Label(metrics_grid, textvariable=self.quality_var, font=("Arial", 14)).grid(row=1, column=2, padx=10)
        ttk.Label(metrics_grid, textvariable=self.effectiveness_var, font=("Arial", 14)).grid(row=1, column=3, padx=10)
        
        # Create charts frame
        charts_frame = ttk.LabelFrame(parent, text="OEE Trends")
        charts_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)
        
        # Set up matplotlib figure
        self.fig = plt.Figure(figsize=(10, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, charts_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Update the dashboard with initial data
        self.update_dashboard()
    
    def setup_input_tab(self, parent):
        """Set up the input tab for entering computational metrics."""
        # Create form frame
        form_frame = ttk.Frame(parent, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Process selection
        model_frame = ttk.Frame(form_frame)
        model_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(model_frame, text="Process Name:").pack(side=tk.LEFT)
        self.input_model = ttk.Combobox(model_frame, values=self.models, state="readonly", width=30)
        self.input_model.current(0)
        self.input_model.pack(side=tk.LEFT, padx=5)
        
        # Create input fields
        fields_frame = ttk.Frame(form_frame)
        fields_frame.pack(fill=tk.X, pady=10)
        
        # Two-column layout
        left_col = ttk.Frame(fields_frame)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_col = ttk.Frame(fields_frame)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Availability metrics (A)
        avail_frame = ttk.LabelFrame(left_col, text="Availability Metrics (A)")
        avail_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Label(avail_frame, text="Total Time (minutes):").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.total_time_var = tk.DoubleVar(value=480.0)  # 8 hours default
        ttk.Entry(avail_frame, textvariable=self.total_time_var, width=15).grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(avail_frame, text="Downtime (minutes):").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.downtime_var = tk.DoubleVar(value=48.0)  # 10% of inactividad
        ttk.Entry(avail_frame, textvariable=self.downtime_var, width=15).grid(row=1, column=1, pady=5, padx=5)
        
        # Efficiency metrics (B)
        eff_frame = ttk.LabelFrame(left_col, text="Efficiency Metrics (B)")
        eff_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Label(eff_frame, text="Completed Simulations:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.completed_sims_var = tk.IntVar(value=102)  # Más simulaciones completadas
        ttk.Entry(eff_frame, textvariable=self.completed_sims_var, width=15).grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(eff_frame, text="Ideal Time per Simulation (minutes):").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.ideal_time_var = tk.DoubleVar(value=4.0)  # Tiempo ideal por simulación
        ttk.Entry(eff_frame, textvariable=self.ideal_time_var, width=15).grid(row=1, column=1, pady=5, padx=5)
        
        # Quality metrics (C)
        qual_frame = ttk.LabelFrame(right_col, text="Quality Metrics (C)")
        qual_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Label(qual_frame, text="Total Simulations:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.total_sims_var = tk.IntVar(value=102)  # Total de simulaciones
        ttk.Entry(qual_frame, textvariable=self.total_sims_var, width=15).grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(qual_frame, text="Valid Simulations:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.valid_sims_var = tk.IntVar(value=97)  # 95% de simulaciones válidas
        ttk.Entry(qual_frame, textvariable=self.valid_sims_var, width=15).grid(row=1, column=1, pady=5, padx=5)
        
        # Notes field
        notes_frame = ttk.LabelFrame(form_frame, text="Process Notes")
        notes_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        self.notes_text = tk.Text(notes_frame, height=5, width=50)
        self.notes_text.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Calculate OEE", command=self.calculate_and_display).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Data", command=self.save_simulation_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset Form", command=self.reset_form).pack(side=tk.LEFT, padx=5)
        
        # Results display
        self.results_frame = ttk.LabelFrame(form_frame, text="Results")
        self.results_frame.pack(fill=tk.X, pady=10, padx=5)
        
        self.results_text = tk.Text(self.results_frame, height=8, width=50, state=tk.DISABLED)
        self.results_text.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
    
    def setup_history_tab(self, parent):
        """Set up the history tab for viewing past computational data."""
        # Create top control frame
        control_frame = ttk.Frame(parent, padding="10")
        control_frame.pack(fill=tk.X)
        
        # Filter by process
        ttk.Label(control_frame, text="Process:").pack(side=tk.LEFT)
        self.history_model_var = tk.StringVar(value="All Processes")
        models_with_all = ["All Processes"] + self.models
        model_dropdown = ttk.Combobox(control_frame, textvariable=self.history_model_var, 
                                     values=models_with_all, state="readonly", width=25)
        model_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Date range
        ttk.Label(control_frame, text="Time Range:").pack(side=tk.LEFT, padx=(20, 0))
        self.history_range_var = tk.StringVar(value="Last 30 Days")
        ranges = ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"]
        range_dropdown = ttk.Combobox(control_frame, textvariable=self.history_range_var, 
                                     values=ranges, state="readonly", width=15)
        range_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Refresh button
        ttk.Button(control_frame, text="Refresh", command=self.load_history_data).pack(side=tk.RIGHT, padx=5)
        
        # Create table for history data
        table_frame = ttk.Frame(parent, padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("timestamp", "process", "availability", "efficiency", "quality", "effectiveness")
        self.history_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Set column headings
        self.history_tree.heading("timestamp", text="Date/Time")
        self.history_tree.heading("process", text="Process")
        self.history_tree.heading("availability", text="Availability (A)")
        self.history_tree.heading("efficiency", text="Efficiency (B)")
        self.history_tree.heading("quality", text="Quality (C)")
        self.history_tree.heading("effectiveness", text="Effectiveness (Z)")
        
        # Set column widths
        self.history_tree.column("timestamp", width=150)
        self.history_tree.column("process", width=150)
        self.history_tree.column("availability", width=100)
        self.history_tree.column("efficiency", width=100)
        self.history_tree.column("quality", width=100)
        self.history_tree.column("effectiveness", width=100)
        
        # Add vertical scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the tree and scrollbar
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind select event
        self.history_tree.bind("<<TreeviewSelect>>", self.display_selected_record)
        
        # Create details frame
        self.details_frame = ttk.LabelFrame(parent, text="Process Details", padding="10")
        self.details_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.details_text = tk.Text(self.details_frame, height=8, width=50, state=tk.DISABLED)
        self.details_text.pack(fill=tk.BOTH, expand=True)
        
        # Load initial history data
        self.load_history_data()
    
    def update_dashboard(self, event=None):
        """Update dashboard with latest data"""
        try:
            # Get selected process
            process = self.current_model.get()
            if not process:
                # No process selected, show empty state
                self.availability_var.set("N/A")
                self.efficiency_var.set("N/A")
                self.quality_var.set("N/A")
                self.effectiveness_var.set("N/A")
                self.update_charts([])
                return
                
            # Get latest data
            latest_data = self.data_handler.get_latest_data(process)
            
            # Si no hay datos, mostrar ceros
            if not latest_data:
                self.availability_var.set("0.0%")
                self.efficiency_var.set("0.0%")
                self.quality_var.set("0.0%")
                self.effectiveness_var.set("0.0%")
                self.update_charts([])
                return
                
            # Get average metrics
            avg_metrics = self.data_handler.calculate_average_metrics([latest_data])
            
            # Update metrics display - multiply by 100 to show as percentage
            self.availability_var.set(f"{avg_metrics.get('availability', 0) * 100:.1f}%")
            self.efficiency_var.set(f"{avg_metrics.get('efficiency', 0) * 100:.1f}%")
            self.quality_var.set(f"{avg_metrics.get('quality', 0) * 100:.1f}%")
            self.effectiveness_var.set(f"{avg_metrics.get('effectiveness', 0) * 100:.1f}%")
            
            # Update charts with recent data
            recent_data = self.data_handler.get_recent_simulations(process, days=30)
            self.update_charts(recent_data)
            
            # Log the update for debugging
            logging.info(f"Dashboard updated for process: {process}")
            logging.info(f"Metrics: {avg_metrics}")
                
        except Exception as e:
            logging.error(f"Error updating dashboard: {str(e)}")
            messagebox.showerror("Error", f"Error updating dashboard: {str(e)}")
    
    def update_charts(self, data_list: List[Dict[str, Any]]):
        """Update the charts with the given data."""
        self.fig.clear()
        
        if not data_list:
            # No data to display
            self.canvas.draw()
            return
            
        # Sort data by timestamp
        data_list.sort(key=lambda x: x.get('timestamp', ''))
        
        # Extract dates and metrics
        dates = []
        availability_values = []
        efficiency_values = []
        quality_values = []
        effectiveness_values = []
        
        for item in data_list:
            if 'timestamp' in item:
                try:
                    dt = datetime.datetime.fromisoformat(item['timestamp'])
                    dates.append(dt)
                    
                    availability_values.append(item.get('availability', 0))
                    efficiency_values.append(item.get('efficiency', 0))
                    quality_values.append(item.get('quality', 0))
                    effectiveness_values.append(item.get('effectiveness', 0))
                except Exception:
                    continue
        
        if not dates:
            # No valid dates found
            self.canvas.draw()
            return
            
        # Create subplots
        ax1 = self.fig.add_subplot(111)
        
        # Plot metrics
        ax1.plot(dates, availability_values, 'b-', label='Availability (A)')
        ax1.plot(dates, efficiency_values, 'g-', label='Efficiency (B)')
        ax1.plot(dates, quality_values, 'y-', label='Quality (C)')
        ax1.plot(dates, effectiveness_values, 'r-', linewidth=2, label='Effectiveness (Z)')
        
        # Format chart
        ax1.set_ylabel('Percentage')
        ax1.set_ylim(0, 1.0)
        ax1.legend(loc='upper left')
        ax1.grid(True)
        
        # Format x-axis dates
        self.fig.autofmt_xdate()
        
        # Update the canvas
        self.canvas.draw()
    
    def calculate_and_display(self):
        """Calculate OEE from form inputs and display results."""
        try:
            # Get input values
            total_time = self.total_time_var.get()
            downtime = self.downtime_var.get()
            completed_sims = self.completed_sims_var.get()
            ideal_time = self.ideal_time_var.get()
            total_sims = self.total_sims_var.get()
            valid_sims = self.valid_sims_var.get()
            
            # Check input validity
            if total_time <= 0 or ideal_time <= 0 or total_sims <= 0:
                messagebox.showerror("Invalid Input", "Please enter valid positive values for time and simulations.")
                return
                
            if downtime > total_time:
                messagebox.showerror("Invalid Input", "Downtime cannot exceed total time.")
                return
                
            if valid_sims > total_sims:
                messagebox.showerror("Invalid Input", "Valid simulations cannot exceed total simulations.")
                return
            
            # Calculate OEE
            oee_data = self.oee_calculator.calculate_complete_oee(
                total_time=total_time,
                downtime=downtime,
                completed_simulations=completed_sims,
                ideal_time_per_simulation=ideal_time,
                total_simulations=total_sims,
                valid_simulations=valid_sims
            )
            
            # Generate report
            model_name = self.input_model.get()
            report = self.oee_calculator.generate_report(oee_data, model_name)
            
            # Display results
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, report)
            self.results_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to calculate OEE: {e}")
    
    def save_simulation_data(self):
        """Save the current computational data to storage."""
        try:
            # Get input values
            total_time = self.total_time_var.get()
            downtime = self.downtime_var.get()
            completed_sims = self.completed_sims_var.get()
            ideal_time = self.ideal_time_var.get()
            total_sims = self.total_sims_var.get()
            valid_sims = self.valid_sims_var.get()
            notes = self.notes_text.get(1.0, tk.END).strip()
            model_name = self.input_model.get()
            
            # Calculate OEE
            oee_data = self.oee_calculator.calculate_complete_oee(
                total_time=total_time,
                downtime=downtime,
                completed_simulations=completed_sims,
                ideal_time_per_simulation=ideal_time,
                total_simulations=total_sims,
                valid_simulations=valid_sims
            )
            
            # Create data dictionary
            simulation_data = {
                "total_time": total_time,
                "downtime": downtime,
                "completed_simulations": completed_sims,
                "ideal_time_per_simulation": ideal_time,
                "total_simulations": total_sims,
                "valid_simulations": valid_sims,
                "availability": oee_data["availability"],
                "efficiency": oee_data["efficiency"],
                "quality": oee_data["quality"],
                "effectiveness": oee_data["effectiveness"],
                "notes": notes
            }
            
            # Save data
            file_path = self.data_handler.save_simulation_run(simulation_data, model_name)
            
            messagebox.showinfo("Success", f"Data saved to {file_path}")
            
            # Update dashboard
            if self.current_model.get() == model_name:
                self.update_dashboard()
                
            # Update history
            self.load_history_data()
            
            # Reset form
            self.reset_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")
    
    def reset_form(self):
        """Reset the input form to default values."""
        # Valores optimistas para mejoras
        self.total_time_var.set(480.0)  # 8 horas
        self.downtime_var.set(48.0)     # 10% de inactividad
        self.completed_sims_var.set(102) # Más simulaciones completadas
        self.ideal_time_var.set(4.0)    # Tiempo ideal por simulación
        self.total_sims_var.set(102)    # Total de simulaciones
        self.valid_sims_var.set(97)     # 95% de simulaciones válidas
        self.notes_text.delete(1.0, tk.END)
        
        # Clear results
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
    
    def load_history_data(self):
        """Load and display historical computational data."""
        # Clear current data
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        try:
            # Get filter parameters
            model_filter = self.history_model_var.get()
            if model_filter == "All Processes":
                model_filter = None
                
            days_filter = 30  # Default
            time_range = self.history_range_var.get()
            if time_range == "Last 7 Days":
                days_filter = 7
            elif time_range == "Last 30 Days":
                days_filter = 30
            elif time_range == "Last 90 Days":
                days_filter = 90
            elif time_range == "All Time":
                days_filter = 3650  # ~10 years
            
            # Get data
            data_list = self.data_handler.get_recent_simulations(model_filter, days=days_filter)
            
            # Add data to tree
            for item in data_list:
                timestamp = item.get('timestamp', '')
                model = item.get('model_name', 'Unknown')
                
                # Get metrics and multiply by 100 to show as percentage
                availability = item.get('availability', 0) * 100
                efficiency = item.get('efficiency', 0) * 100
                quality = item.get('quality', 0) * 100
                effectiveness = item.get('effectiveness', 0) * 100
                
                # Format values as percentages
                availability_str = f"{availability:.1f}%"
                efficiency_str = f"{efficiency:.1f}%"
                quality_str = f"{quality:.1f}%"
                effectiveness_str = f"{effectiveness:.1f}%"
                
                # Format timestamp
                try:
                    dt = datetime.datetime.fromisoformat(timestamp)
                    timestamp_str = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    timestamp_str = timestamp
                
                # Insert into tree
                self.history_tree.insert("", tk.END, values=(
                    timestamp_str, model, availability_str, efficiency_str, quality_str, effectiveness_str
                ), tags=(str(timestamp),))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load history data: {e}")
    
    def display_selected_record(self, event):
        """Display details of the selected history record."""
        selected_items = self.history_tree.selection()
        if not selected_items:
            return
            
        item = selected_items[0]
        item_values = self.history_tree.item(item, "values")
        
        if not item_values:
            return
            
        # Get the timestamp value from the tree
        timestamp_str = item_values[0]
        model_name = item_values[1]
        
        try:
            # Find the corresponding record in data
            data_list = self.data_handler.get_recent_simulations(days=3650)  # Get all data
            record = None
            
            for data in data_list:
                if data.get('model_name') == model_name:
                    try:
                        dt = datetime.datetime.fromisoformat(data.get('timestamp', ''))
                        if dt.strftime("%Y-%m-%d %H:%M") == timestamp_str:
                            record = data
                            break
                    except Exception:
                        continue
            
            if record:
                # Display record details
                details = f"Process: {record.get('model_name', 'Unknown')}\n"
                details += f"Date/Time: {timestamp_str}\n\n"
                
                details += f"Total Time: {record.get('total_time', 0)} minutes\n"
                details += f"Downtime: {record.get('downtime', 0)} minutes\n"
                details += f"Completed Simulations: {record.get('completed_simulations', 0)}\n"
                details += f"Ideal Time per Simulation: {record.get('ideal_time_per_simulation', 0)} minutes\n"
                details += f"Total Simulations: {record.get('total_simulations', 0)}\n"
                details += f"Valid Simulations: {record.get('valid_simulations', 0)}\n\n"
                
                details += f"Notes: {record.get('notes', 'None')}"
                
                self.details_text.config(state=tk.NORMAL)
                self.details_text.delete(1.0, tk.END)
                self.details_text.insert(tk.END, details)
                self.details_text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display record details: {e}")
    
    def add_new_process(self):
        """Open dialog to add a new process."""
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Process")
        dialog.geometry("400x150")
        dialog.transient(self.root)  # Make dialog modal
        dialog.grab_set()  # Make dialog modal
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create form
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Process Name:").pack(anchor=tk.W, pady=(0, 5))
        process_name = ttk.Entry(form_frame, width=40)
        process_name.pack(fill=tk.X, pady=(0, 20))
        process_name.focus()
        
        def save_process():
            new_process = process_name.get().strip()
            if new_process:
                if new_process not in self.models:
                    self.models.append(new_process)
                    # Update all comboboxes
                    self.current_model.set(new_process)
                    self.input_model['values'] = self.models
                    self.history_model_var.set(new_process)
                    # Update dashboard
                    self.update_dashboard()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Process name already exists!")
            else:
                messagebox.showerror("Error", "Please enter a process name!")
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Save", command=save_process).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
        
        # Bind Enter key to save
        process_name.bind('<Return>', lambda e: save_process())
        
        # Make dialog modal
        dialog.wait_window()
    
    def delete_process(self):
        """Delete the currently selected process."""
        try:
            # Obtener el proceso seleccionado directamente del combobox
            current_process = self.dashboard_model_dropdown.get()
            logging.info(f"Attempting to delete process: {current_process}")
            
            # No permitir eliminar si es el último proceso
            if len(self.models) <= 1:
                logging.warning("Cannot delete the last process")
                messagebox.showerror("Error", "Cannot delete the last process!")
                return
                
            # Confirmar eliminación
            if messagebox.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete the process '{current_process}'?\n\n"
                                 "This will also delete all associated data."):
                logging.info(f"User confirmed deletion of process: {current_process}")
                
                # Eliminar el proceso de la lista
                if current_process in self.models:
                    # Eliminar los archivos de datos asociados primero
                    try:
                        self.delete_process_data(current_process)
                        logging.info("Process data files deleted successfully")
                    except Exception as e:
                        logging.error(f"Error deleting process data: {str(e)}")
                        raise
                    
                    # Eliminar el proceso de la lista
                    self.models.remove(current_process)
                    logging.info(f"Process removed from models list. Remaining processes: {self.models}")
                    
                    # Actualizar los comboboxes y UI
                    try:
                        # Actualizar el combobox del dashboard
                        self.dashboard_model_dropdown['values'] = list(self.models)
                        self.dashboard_model_dropdown.set(self.models[0])
                        self.current_model.set(self.models[0])
                        logging.info(f"Dashboard combobox updated to: {self.models[0]}")
                        
                        # Actualizar el combobox de input
                        self.input_model['values'] = list(self.models)
                        self.input_model.set(self.models[0])
                        logging.info("Input combobox values updated")
                        
                        # Actualizar el combobox de history
                        self.history_model_var.set(self.models[0])
                        for widget in self.root.winfo_children():
                            if isinstance(widget, ttk.Frame):
                                for child in widget.winfo_children():
                                    if isinstance(child, ttk.Notebook):
                                        for tab in child.winfo_children():
                                            if isinstance(tab, ttk.Frame):
                                                for frame in tab.winfo_children():
                                                    if isinstance(frame, ttk.Frame):
                                                        for widget in frame.winfo_children():
                                                            if isinstance(widget, ttk.Combobox) and widget.cget('textvariable') == str(self.history_model_var):
                                                                widget['values'] = ["All Processes"] + list(self.models)
                        logging.info("History combobox updated")
                        
                        # Forzar actualización de los widgets
                        self.root.update_idletasks()
                        
                    except Exception as e:
                        logging.error(f"Error updating comboboxes: {str(e)}")
                        raise
                    
                    # Actualizar el dashboard y la historia
                    self.update_dashboard()
                    self.load_history_data()
                    logging.info("Dashboard and history updated after process deletion")
                    
                    messagebox.showinfo("Success", f"Process '{current_process}' has been deleted.")
                else:
                    logging.error(f"Process {current_process} not found in models list")
                    messagebox.showerror("Error", f"Process '{current_process}' not found in the list!")
                    return
                
        except Exception as e:
            logging.error(f"Error in delete_process: {str(e)}")
            messagebox.showerror("Error", f"Failed to delete process: {str(e)}")
    
    def delete_process_data(self, process_name: str):
        """Delete all data files associated with a process."""
        try:
            logging.info(f"Starting deletion of data files for process: {process_name}")
            deleted_files = 0
            
            # Obtener la lista de archivos en el directorio de datos
            if not os.path.exists(self.data_handler.storage_dir):
                logging.error(f"Storage directory does not exist: {self.data_handler.storage_dir}")
                return
                
            for filename in os.listdir(self.data_handler.storage_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.data_handler.storage_dir, filename)
                    try:
                        # Leer el archivo para verificar si pertenece al proceso
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            if data.get('model_name') == process_name:
                                # Eliminar el archivo si pertenece al proceso
                                os.remove(file_path)
                                deleted_files += 1
                                logging.info(f"Deleted data file: {filename}")
                    except Exception as e:
                        logging.error(f"Error processing file {filename}: {str(e)}")
            
            logging.info(f"Deleted {deleted_files} files for process {process_name}")
            
        except Exception as e:
            logging.error(f"Error in delete_process_data: {str(e)}")
            raise


def run_dashboard():
    """Run the OEE Dashboard application."""
    root = tk.Tk()
    app = OEEDashboard(root)
    root.mainloop() 