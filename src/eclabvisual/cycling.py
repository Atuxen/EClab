from pathlib import Path
import eclabfiles as ecf
from bokeh.palettes import small_palettes
from bokeh.plotting import figure, output_notebook, show
import numpy as np
from bokeh.io import export_png
import pandas as pd
from IPython.display import HTML, display


# Color scheme
backgrund_color = "white"
plot_color = "whitesmoke"

class DataFrameEmpty(Exception):
    pass

class DataDictionary:
    """Collects file paths from a directory based on a given filetype."""

    def __init__(self, path: str, filetype: str):
        self.background_color = "white"
        self.plot_color = "whitesmoke"
        self.path = path
        self.data_dict = self._build_data_dict(filetype)
        self.tabulate()

    def _build_data_dict(self, filetype: str) -> dict:
        folder_path = Path(self.path)
        data_dict = {}

        
        

        for file_path in folder_path.glob('**/*'):
            if (
                file_path.is_file()
                and file_path.suffix == ".mpr"
                and filetype in file_path.name
            ):
                file_name = file_path.name
                filetype_index = file_name.find(filetype)

                if filetype_index > 1:
                    prefix = file_name[: filetype_index - 1]
                else:
                    print(f"Not enough characters before filetype in {file_name}")
                    prefix = "InvalidPrefix"

                # Add the file name to the dictionary under the appropriate prefix

                try:
                    df = ecf.to_df(file_path)
                    if df.empty:
                        raise DataFrameEmpty(f"Data frame is empty for {prefix}")
                    if prefix not in data_dict:
                    
                        data_dict[prefix] = []
                    data_dict[prefix].append(str(file_path))

                except DataFrameEmpty as eD:
                    print(f"Error processing frame: {eD}")
                    continue
                except Exception as e:
                    print(f"Error processing {prefix}: {e}")
                    continue
                

        return data_dict

    def tabulate(self):
        # Flatten the dictionary into rows
        print("Check if this is your intended data:")
        flattened_data = [{'Sample': key, 'File path': value[0]} for key, value in self.data_dict.items()]
        df = pd.DataFrame(flattened_data)
        display(HTML(df.to_html()))


class CyclingData(DataDictionary):
    """Specialized DataDictionary that always looks for 'GCPL'."""

    def __init__(self, path: str):
        super().__init__(path, "GCPL")

    def gcpl_plot(self, items):
        """
        Plots galvanostatic cycling data for the given dictionary prefix.
        """

        if len(items) == 1:
            plot_title = list(self.data_dict)[0]
        else: 
            plot_title = "Galvanostatic Cycling"

        output_notebook()
        fig = figure(
            title = plot_title,
            x_axis_label="Time (h)",
            y_axis_label="Ewe (V vs Zn)",
            width=800,
            height=300,
            background_fill_color = self.background_color,
            border_fill_color = self.plot_color  # or background_fill_color if desired
        )

        for i in items:
            key = list(self.data_dict)[i]
            file_path = list(self.data_dict.values())[i][0]

            df = ecf.to_df(file_path)
            df["Hours"] = df["time"] / 3600  # from seconds to hours

            time = df["Hours"]
            potential = df["Ewe"]

            colors = small_palettes["Viridis"][4]

            fig.line(
                time,
                potential,
                legend_label=key,
                line_color=colors[i],  # or however you want to pick colors
                line_width=1
            )

        fig.legend.location = "bottom_right"
        show(fig)



def CEplot(dict):

    output_notebook()
    CE = figure(
        title="Coulombic Effeciency",
        x_axis_label="Cycle number",
        y_axis_label="Coulombic Effeciency (%)",
        width=800,
        height=400,
        tools="box_zoom,lasso_select,reset, save",
    )

    ## Constrain axes
    # CE.x_range.start = -0.5  # Set x-axis range from 0 to 3V
    # CE.x_range.end = 4
    CE.y_range.start = 0  # Set y-axis range from 0 to 20 mA/cm^2
    CE.y_range.end = 100

    color = 0
    for key, value in dict.items():
        try:
            df = ecf.to_df(value[0])
            if df.empty:
                raise DataFrameEmpty(f"Data frame is empty for {key}")

        except DataFrameEmpty as eD:
            print(f"Error processing frame: {eD}")
            continue
        except Exception as e:
            print(f"Error processing {key}: {e}")

        # The CE function
        cycle, coleff, _ = columbicEf(df)

        CE.background_fill_color = plot_color
        CE.border_fill_color = backgrund_color

        # Plot
        colors = small_palettes["Viridis"][4]
        #CE.line(
        #    cycle,
        #    coleff,
        #    legend_label=key,
        #    line_color=colors[color % len(colors)],
        #    line_width=1,
        #)

        CE.scatter(
            cycle,
            coleff,
            legend_label=key,
            color=colors[color % len(colors)],
        )

        color += 1

    CE.legend.location = "bottom_right"
    #CE.legend.title = "ZnSO4 Concentrations"

    # save the results to a file
    #export_png(CE, filename=f"./{key}.png")
    show(CE)


def cap_retention(dict):
    output_notebook()
    CR = figure(
        title="Capacity retention",
        x_axis_label="Cycle number",
        y_axis_label="Capacity retention (%)",
        width=800,
        height=400,
        tools="box_select,box_zoom,lasso_select,reset",
    )

    ## Constrain axes
    #CR.x_range.start = -0.5  # Set x-axis range from 0 to 3V
    #CR.x_range.end = 500
    #CR.y_range.start = 0  # Set y-axis range from 0 to 20 mA/cm^2
    #CR.y_range.end = 100

    CR.background_fill_color = plot_color
    CR.border_fill_color = backgrund_color

    color = 0
    for key, value in dict.items():
        try:
            df = ecf.to_df(value[0])
            if df.empty:
                raise DataFrameEmpty(f"Data frame is empty for {key}")

        except DataFrameEmpty as eD:
            print(f"Error processing frame: {eD}")
            continue
        except Exception as e:
            print(f"Error processing {key}: {e}")

        # The CE function
        cycle, _, capacity_retention = columbicEf(df)

        # Plot
        colors = small_palettes["Viridis"][4]
        CR.scatter(
            cycle,
            capacity_retention,
            legend_label=key,
            color=colors[color % len(colors)],
        )


        color += 1

    CR.legend.location = "bottom_right"
    #CR.legend.title = "ZnSO4 Concentrations"
    show(CR)


def columbicEf(df):

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
    intial_discharge_retention = np.ones(len(discharge_cycles)) * discharge_cycles[3] # I am choosing 3 here cause the first cycles are often a littel voltaile
    # print("Discharge retetntion", intial_discharge_retention)
    # print("Discharge cycle", discharge_cycles)
    capacity_retention = (discharge_cycles / intial_discharge_retention) * 100

    coleff = coulombic_efficiency
    cycle = np.array(range(0, len(coulombic_efficiency)))

    # print("capacity_retention", capacity_retention)

    return cycle, coleff, capacity_retention









def function(x):
    
    y = x+2
    print(y)

    return

