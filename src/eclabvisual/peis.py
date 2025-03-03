
import eclabfiles as ecf
from bokeh.palettes import small_palettes
from pathlib import Path
from bokeh.plotting import figure, output_notebook, show
from bokeh.layouts import row
from .utils import Grapher
import numpy as np

class DataFrameEmpty(Exception):
    pass

class cellConf():
    def __init__(self):
        self.cell_length = 0.1
        self.cell_area = 1.31
        self.cell_constant = self.cell_length/self.cell_area
        pass

class PEISGrapher(Grapher):
    def __init__(self, data):
        super().__init__()

        self.cell = cellConf()
        
        self.data_peis = data.data_peis
        
    def nyquist_plot(self, items, plot_title=None, names=None):

        if not plot_title:
            if len(items) == 1:
                plot_title = f"Nyquist plot of {list(self.data_peis)[items[0]]}"
            else: 
                plot_title = "Nyquist plot"

        output_notebook()

        TOOLTIPS = [("(x, y)", "($x, $y)")]
        pe = figure(
            title= plot_title,
            x_axis_label="Real values Z' (Ω), normalised by cell constant",
            y_axis_label="Imaginary values -Z'' (Ω), normalised by cell constant",
            width=800,
            height=400,
            background_fill_color = self.plot_color,
            border_fill_color = self.background_color,
            tools="box_zoom,wheel_zoom,reset, hover",
            tooltips = TOOLTIPS
        )

        ## Constrain axes
        # pe.x_range.start = -0.5  # Set x-axis range from 0 to 3V
        # pe.x_range.end = 4
        # pe.y_range.start = -20  # Set y-axis range from 0 to 20 mA/cm^2
        # pe.y_range.end = 20


        
    
    

        for e, i in enumerate(items):
            if not names:
                key = list(self.data_peis)[i]
            else: 
                key = names[e]
            file_path = list(self.data_peis.values())[i][0]
            df = ecf.to_df(file_path)    

            zReal = df["Re(Z)"] #/ self.cell.cell_constant
            zImagine = df["-Im(Z)"] #// self.cell.cell_constant

            # Plot
            colors = self.get_colors(items)
            pe.line(
            zReal,
            zImagine,
            legend_label=key,
            line_color=colors[e],
            line_width=1,
            
        )

        pe.legend.location = "bottom_right"
    
        show(pe)

    def bode_plots(self, items):

        if len(items) == 1:
            plot_title = f"{list(self.data_peis)[items[0]]}"
        else: 
            plot_title = ""

        output_notebook()

    ######## TIll here
    ## One plot is log(freq) and log(Z=impedance), and the other is log(freq) and log phase shift
        mag_plot = figure(
            title= "Magnitude bode plot " + plot_title,
            x_axis_label="Log10 Frequency (Hz)",
            y_axis_label="Magnitude of impedance (Ω), normalised by cell constant",
            width=400,
            height=400,
        )

        phase_plot = figure(
            title= "Phase bode plot " + plot_title,
            x_axis_label="Log10 Frequency (Hz)",
            y_axis_label="Phase (°), normalised by cell constant",
            width=400,
            height=400,
        )



        ## Constrain axes
        # pe.x_range.start = -0.5  # Set x-axis range from 0 to 3V
        # pe.x_range.end = 4
        # pe.y_range.start = -20  # Set y-axis range from 0 to 20 mA/cm^2
        # pe.y_range.end = 20



        for e, i in enumerate(items):
            key = list(self.data_peis)[i]
            file_path = list(self.data_peis.values())[i][0]
            df = ecf.to_df(file_path)    

            Zmag = df["|Z|"] / self.cell.cell_constant
            phase = df["Phase(Z)"] / self.cell.cell_constant
            freq = np.log10(df["freq"]) # Need to add log here

            # Mag Plot
            colors = self.get_colors(items)
            mag_plot.line(
            freq,
            Zmag,
            legend_label=key,
            line_color=colors[e],
            line_width=1,
            )


            # Phase Plot
            colors = self.get_colors(items)
            phase_plot.line(
            freq,
            phase,
            legend_label=key,
            line_color=colors[e],
            line_width=1,
            )

    
    
        show(row(mag_plot, phase_plot))


