
import eclabfiles as ecf
from bokeh.palettes import small_palettes
from pathlib import Path
from bokeh.plotting import figure, output_notebook, show
from bokeh.layouts import row
from src.eclabvisual.utils import Grapher

class DataFrameEmpty(Exception):
    pass

class PEISGrapher(Grapher):
    def __init__(self, data):
        super().__init__()
        self.data_peis = data.data_peis

    def nyquist_plot(self, items):

        if len(items) == 1:
            plot_title = f"Nyquist plot of {list(self.data_peis)[items[0]]}"
        else: 
            plot_title = "Nyquist plot"

        output_notebook()

    
        pe = figure(
            title= plot_title,
            x_axis_label="Real values Z' (Ω)",
            y_axis_label="Imaginary values Z'' (Ω)",
            width=800,
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

            zReal = df["Re(Z)"]
            zImagine = df["-Im(Z)"]

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
            x_axis_label="Log(Frequency) (Hz)",
            y_axis_label="Magnitude of impedance (Ω)",
            width=400,
            height=400,
        )

        phase_plot = figure(
            title= "Phase bode plot " + plot_title,
            x_axis_label="Log(Frequency) (Hz)",
            y_axis_label="Phase (degree)",
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

            Zmag = df["|Z|"]
            phase = df["Phase(Z)"]
            freq = df["freq"] # Need to add log here

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

        mag_plot.legend.location = "bottom_right"
    
        show(row(mag_plot, phase_plot))


