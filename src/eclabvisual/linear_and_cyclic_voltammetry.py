import os
from pathlib import Path
from bokeh.palettes import small_palettes
from bokeh.plotting import figure, output_notebook, show
from src.eclabvisual.utils import Grapher
import eclabfiles as ecf
import pandas as pd

# Linear Sweep Voltammetry function

class DataFrameEmpty(Exception):
    pass

class VoltammetryGrapher(Grapher):
    
    def __init__(self, data):
        super().__init__()
        self.SCE = 0.241
        self.el_surface_area = 2.48
        self.data_cv = data.data_cv
        self.data_lsv = data.data_lsv

    def cv_plot(self, items):
        output_notebook()
        if len(items) == 1:
            plot_title = f"Cyclic Voltammetry of {list(self.data_cv)[items[0]]}"
        else: 
            plot_title = "Cyclic Voltammetry"

        cv = figure(
            title="Cyclic Voltammetry",
            x_axis_label="Potential (V vs Zn)",
            y_axis_label="Current density (mA/cm^2)",
            width=800,
            height=400,
            background_fill_color = self.plot_color,
            border_fill_color = self.background_color,
            #tools="box_select,box_zoom,lasso_select,reset",
        )

        ## Constrain axes
        # cv.x_range.start = -0.5
        # cv.x_range.end = 4
        # cv.y_range.start = -20
        # cv.y_range.end = 20


        for e, i in enumerate(items):
            key = list(self.data_cv)[i]
            file_path = list(self.data_cv.values())[i][0]
            df = ecf.to_df(file_path)     

            potential = df["Ewe"]  # - SCE
            current = df["<I>"] / self.el_surface_area

            # Plot
            colors = self.get_colors(items)
            cv.line(
                potential,
                current,
                legend_label=key,
                line_color=colors[e],
                line_width=2,
            )

        cv.legend.location = "top_left"

        show(cv)


    def lsv_plot(self, items, electrodePotential=0):

        if len(items) == 1:
            plot_title = f"Linear Sweep Voltammetry of {list(self.data_lsv)[items[0]]}"
        else: 
            plot_title = "Linear Sweep Voltammetry"

        output_notebook()

        lsv = figure(
            title=plot_title,
            x_axis_label="Potential (V vs Zn)",
            y_axis_label="Current density (mA/cm^2)",
            width=800,
            height=400,
            #tools="box_select,box_zoom,lasso_select,reset",
        )

        # Constrain axes
        #lsv.x_range.start = -0.5
        #lsv.x_range.end = 4
        #lsv.y_range.start = -20
        #lsv.y_range.end = 20

        for e, i in enumerate(items):
            key = list(self.data_lsv)[i]
            file_path = list(self.data_lsv.values())[i][0]
            df = ecf.to_df(file_path)    

            potential = df["Ewe"] + electrodePotential
            current = df["<I>"] / self.el_surface_area
            # Plot
            colors = self.get_colors(items)
            
            lsv.line(
                potential,
                current,
                legend_label=key,
                line_color=colors[e],
                line_width=2,
            )
   
        lsv.legend.location = "bottom_right"
   
        show(lsv)

    def lst_plot_split(self, items, threshold=0.5, electrodePotential=0):

        if len(items) == 1:
            plot_title = "Threshold Linear Sweep Voltammetry"
        else: 
            plot_title = "Threshold Linear Sweep Voltammetry"

        output_notebook()

        lsv = figure(
            title= plot_title,
            x_axis_label="Potential (V vs Zn)",
            y_axis_label="Current density (mA/cm^2)",
            width=800,
            height=400,
            #tools="box_select,box_zoom,lasso_select,reset",
            background_fill_color = self.plot_color,
            border_fill_color = self.background_color,

        )
                
        # Constrain axes
        #lsv.x_range.start = -0.5
        #lsv.x_range.end = 4
        #lsv.y_range.start = -20
        #lsv.y_range.end = 20

        for count, pair in enumerate(items):
            print("Pair: ",pair)
            for e, i in enumerate(pair):
                key = list(self.data_lsv)[i]
                file_path = list(self.data_lsv.values())[i][0]
                df = ecf.to_df(file_path)    
                
                if e == 0:
                    df0 = df[df["Ewe"] < threshold].iloc[::-1]
                if e == 1:
                    df1 = df[df["Ewe"] > threshold]

            
            
            dfcombined = pd.concat([df0, df1])

            #print("combined", dfcombined)

            potential = dfcombined["Ewe"] + electrodePotential
            current = dfcombined["<I>"] / self.el_surface_area

            # Plot
            colors = self.get_colors(items)
            lsv.line(
                potential,
                current,
                legend_label=key,
                line_color=colors[count],
                line_width=2,
            )

        lsv.legend.location = "bottom_right"
        #lsv.legend.title = "ZnSO4 Concentrations"
    
        lsv.vspan(
            x=[threshold + electrodePotential],
            line_width=[1],
            line_color="black",
            line_dash="dashed",
            legend_label="Threshold",
        )

        show(lsv)