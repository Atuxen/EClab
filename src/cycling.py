from pathlib import Path
import eclabfiles as ecf
from bokeh.palettes import small_palettes
from bokeh.plotting import figure, output_notebook, show
import numpy as np

# Color scheme
backgrund_color = "white"
plot_color = "whitesmoke"

class DataFrameEmpty(Exception):
    pass

def GCPL(GCPL_paths):

    output_notebook()
    GCPL = figure(
        title="Galvanostatic Cycling with Potential Limitation",
        x_axis_label="Time (h)",
        y_axis_label="Ewe (V vs Zn)",
        width=800,
        height=300,
        tools = "hover",
    )
    GCPL.background_fill_color = plot_color
    GCPL.border_fill_color = backgrund_color

    # Load data
    color = 0
    for key, value in GCPL_paths.items():
        try:
            df = ecf.to_df(value[0])
            if df.empty:
                raise DataFrameEmpty(f"Data frame is empty for {key}")

        except DataFrameEmpty as eD:
            print(f"Error processing frame: {eD}")
            continue
        except Exception as e:
            print(f"Error processing {key}: {e}")
            continue

        #df = ecf.to_df(value[0])

        df["Hours"] = df["time"]/3600 # From seconds to hours
        time = df["Hours"]
        potential = df["Ewe"]

  
        colors = small_palettes["Viridis"][4]
        GCPL.line(
            time,
            potential,
            legend_label=key,
            line_color=colors[color % len(colors)],
            line_width=1,
            
        )
        color += 1
    GCPL.legend.location = "bottom_right"

    show(GCPL)

def CEplot(dict):

    output_notebook()
    CE = figure(
        title="Coulombic Effeciency",
        x_axis_label="Cycle number",
        y_axis_label="Coulombic Effeciency (%)",
        width=800,
        height=400,
        tools = "hover",
    )

    ## Constrain axes
    # CE.x_range.start = -0.5  # Set x-axis range from 0 to 3V
    # CE.x_range.end = 4
    # CE.y_range.start = -20  # Set y-axis range from 0 to 20 mA/cm^2
    # CE.y_range.end = 20

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
        CE.line(
            cycle,
            coleff,
            legend_label=key,
            line_color=colors[color % len(colors)],
            line_width=1,
        )

        color += 1

    CE.legend.location = "bottom_right"
    #CE.legend.title = "ZnSO4 Concentrations"
    show(CE)


def cap_retention(dict):
    output_notebook()
    CR = figure(
        title="Capacity retention",
        x_axis_label="Cycle number",
        y_axis_label="Capacity retention (%)",
        width=800,
        height=400,
        tools = "hover",
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



def cycling_dictionary(path):
    folder_path = Path(path)
    data_dict = {}

    # Iterate over all .mpr files that contain "LSV"
    for file_path in folder_path.iterdir():
        if (
            file_path.is_file()
            and file_path.suffix == ".mpr"
            and "GCPL" in file_path.name
        ):
            # Find the position of "GCLP"
            file_name = file_path.name
            lsv_index = file_name.find("GCPL")

            # Extract 4 characters before "LSV"
            if lsv_index > 1:  # Ensure there are at least 4 characters before
                prefix = file_name[: lsv_index - 1]
                # print(f"Prefix before 'LSV': {prefix}")
            else:
                print(f"Not enough characters before 'CV' in {file_name}")
                prefix = "InvalidPrefix"

            # Add the file name to the dictionary under the appropriate prefix
            if prefix not in data_dict:
                data_dict[prefix] = [str(file_path)]

  

    #print(f"Check if these are your files of interest {data_dict}")

    return data_dict





