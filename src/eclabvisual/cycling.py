
import eclabfiles as ecf
from bokeh.plotting import figure, output_notebook, show
import numpy as np
from bokeh.io import export_png

from .utils import DataDictionary, Grapher


class CyclingGrapher(Grapher):
    """Specialized DataDictionary that always looks for 'GCPL'."""

    def __init__(self, data):
        super().__init__()
        self.data_gcpl = data.data_gcpl

    def gcpl_plot(self, items, plot_title= None, names = None):
        """
        Plots galvanostatic cycling data for the given dictionary prefix.
        """
        TOOLTIPS = [("(Hours, mV)", "($x, $y)")]
        if not plot_title:
            if len(items) == 1:
                plot_title = f"Galvanostatic Cycling of {list(self.data_gcpl)[items[0]]}"
            else: 
                plot_title = "Galvanostatic Cycling"

        output_notebook()
        fig = figure(
            title = plot_title,
            x_axis_label="Time (h)",
            y_axis_label="Ewe (mV vs Zn/Zn²⁺)",
            width=800,
            height=300,
            background_fill_color = self.plot_color,
            border_fill_color = self.background_color,  # or background_fill_color if desired
            tools = "box_zoom,wheel_zoom,reset, hover",
            tooltips = TOOLTIPS,
        )


        fig.y_range.start = -100  # Set y-axis range from 0 to 20 mA/cm^2
        fig.y_range.end = 100

        for e, i in enumerate(items):

            if not names:
                key = list(self.data_gcpl)[i]
            else: 
                key = names[e]
            file_path = list(self.data_gcpl.values())[i][0]

            df = ecf.to_df(file_path)
            df["Hours"] = df["time"] / 3600  # from seconds to hours

            time = df["Hours"]
            potential = df["Ewe"] * 1000  # Convert V to mV

            colors = self.get_colors(items)

            if len(items) == 1:
                key = ""

            fig.line(
                time,
                potential,
                line_color=colors[e],  # or however you want to pick colors
                legend_label=key,
                line_width=1
            )

            
                
                #fig.legend.location = "bottom_right"

        show(fig)


    def CEplot(self, items, plot_title= None, names=None):
        output_notebook()
        TOOLTIPS = [("(x, y)", "($x, $y)")]

        if not plot_title:
            if len(items) == 1:
                plot_title = f"Coulombic Effeciency of {list(self.data_gcpl)[items[0]]}"
            else: 
                plot_title = "Coulombic Effeciency"

        CE = figure(
            title = plot_title,
            x_axis_label = "Cycle number",
            y_axis_label = "Coulombic Effeciency (%)",
            width=800,
            height=400,
            background_fill_color = self.plot_color,
            border_fill_color = self.background_color,
            tools = "box_zoom,wheel_zoom,reset, hover",
            tooltips = TOOLTIPS,
        )

        ## Constrain axes
        # CE.x_range.start = -0.5  # Set x-axis range from 0 to 3V
        # CE.x_range.end = 4
        CE.y_range.start = 0  # Set y-axis range from 0 to 20 mA/cm^2
        CE.y_range.end = 100


        for e, i in enumerate(items):
            if not names:
                key = list(self.data_gcpl)[i]
            else: key = names[e]
            file_path = list(self.data_gcpl.values())[i][0]
            # The CE function
            df = ecf.to_df(file_path)
        
            try:
                cycle, coleff, _ = self.columbicEf(df)
            except Exception as err:
                print(f"Not enough cycles in file {key}")
                continue

            # Plot
            colors = self.get_colors(items)
  
            CE.scatter(
                cycle,
                coleff,
                legend_label=key,
                color=colors[e],
            )


        CE.legend.location = "bottom_right"
   
        show(CE)

    def cap_retention(self, items, plot_title = None, names = None):

        if not plot_title:
            if len(items) == 1:
                plot_title = f"Capacity retention of {list(self.data_gcpl)[items[0]]}"
            else: 
                plot_title = "Capacity retention"

        output_notebook()

        CR = figure(
            title=plot_title,
            x_axis_label="Cycle number",
            y_axis_label="Capacity retention (%)",
            width=800,
            height=400,
            background_fill_color = self.plot_color,
            border_fill_color = self.background_color
            #tools="box_select,box_zoom,lasso_select,reset",
        )

        ## Constrain axes
        #CR.x_range.start = -0.5  # Set x-axis range from 0 to 3V
        #CR.x_range.end = 500
        #CR.y_range.start = 0  # Set y-axis range from 0 to 20 mA/cm^2
        #CR.y_range.end = 100

        for e, i in enumerate(items):
            if not names: 
                key = list(self.data_gcpl)[i]
            else: 
                key = names[e]
            file_path = list(self.data_gcpl.values())[i][0]
            df = ecf.to_df(file_path)

            # The CE function
            
            try:
                cycle, _, capacity_retention = self.columbicEf(df)
            except Exception as e:
                print(f"Not enough cycles in file {key}")
                continue

            # Plot
            colors = self.get_colors(items)
            CR.scatter(
                cycle,
                capacity_retention,
                legend_label=key,
                color=colors[e],
            )


        CR.legend.location = "bottom_right"
        #CR.legend.title = "ZnSO4 Concentrations"
        show(CR)


    def columbicEf(self, df):

        # Take the absolute values of `Q charge/discharge`
        df["Q charge/discharge"] = df["Q charge/discharge"].abs()

        # Find the maximum charge and discharge for each half cycle
        max_charge = df[df["ox/red"] == 1].groupby("half cycle")["Q charge/discharge"].max()
        max_discharge = (
            df[df["ox/red"] == 0].groupby("half cycle")["Q charge/discharge"].max()
        )

        # Align the indices of charge and discharge cycles for a full cycle comparison
        # Assuming that 'half cycle' pairs consecutive charge and discharge cycles (e.g., 0 and 1, 2 and 3)
        charge_cycles = max_charge.iloc[
            :-1
        ]  # Exclude the last half cycle if it's incomplete
        discharge_cycles = max_discharge.iloc[
            1:
        ]  # Exclude the first half cycle if it lacks a discharge

        # Reset indices for alignment
        charge_cycles = charge_cycles.reset_index(drop=True)
        discharge_cycles = discharge_cycles.reset_index(drop=True)

        # Calculate Coulombic Efficiency
        coulombic_efficiency = (discharge_cycles / charge_cycles) * 100

        # Capacity Retention
        ##
        
        skip_cycles = 3
        if len(discharge_cycles) <= skip_cycles:
        # not enough data to skip 3 cycles
        # either fallback or raise an error
            skip_cycles = 0  # or some fallback
    
        reference_cycle_val = discharge_cycles[skip_cycles]
        ##

        intial_discharge_retention = np.ones(len(discharge_cycles)) * reference_cycle_val # I am choosing 3 here cause the first cycles are often a littel voltaile
        # print("Discharge retetntion", intial_discharge_retention)
        # print("Discharge cycle", discharge_cycles)
        capacity_retention = (discharge_cycles / intial_discharge_retention) * 100

        coleff = coulombic_efficiency
        cycle = np.array(range(0, len(coulombic_efficiency)))

        # print("capacity_retention", capacity_retention)

        return cycle, coleff, capacity_retention



