import eclabfiles as ecf
from bokeh.plotting import figure, show, output_notebook
from bokeh.palettes import small_palettes, mpl
from bokeh.models import Range1d, LinearAxis
import math
import pandas as pd
from pathlib import Path
import os

# Define the folder path
cwd = Path(os.getcwd()).parents[0]
print(f"Current working directory: {cwd}")



# Linear Sweep Voltammetry function

from bokeh.plotting import figure, output_notebook, show
from bokeh.palettes import small_palettes


class DataFrameEmpty(Exception):
    pass


def LSV_plot(data_dict, threshold=None, electrodePotential=0):
    output_notebook()
    lsv = figure(
        title="Linear Sweep Voltammetry",
        x_axis_label="Potential (V vs Zn)",
        y_axis_label="Current density (mA/cm^2)",
        width=800,
        height=400,
    )

    # Constrain axes
    lsv.x_range.start = -0.5
    lsv.x_range.end = 4
    lsv.y_range.start = -20
    lsv.y_range.end = 20

    color = 0
    for key, value in data_dict.items():
        for i, path in enumerate(value):
            try:
                # Load data
                df = ecf.to_df(path)
                if df.empty:
                    raise DataFrameEmpty(f"Data frame is empty for {key}")

                # Apply threshold filter
                if threshold:
                    if "01_LSV" in path:
                        df = df[df["Ewe"] >= threshold]
                    if "02_LSV" in path:
                        df = df[df["Ewe"] <= threshold]

                # Adjust potential and current density
                # SCE = 0.241
                el_surface_area = 2.48
                potential = df["Ewe"] + electrodePotential
                current = df["<I>"] / el_surface_area

                # Plot
                colors = small_palettes["Viridis"][4]
                lsv.line(
                    potential,
                    current,
                    legend_label=key,
                    line_color=colors[color % len(colors)],
                    line_width=2,
                )
            except DataFrameEmpty as eD:
                print(f"{eD}")
                continue
            except Exception as e:
                print(f"Error processing {key}: {e}")

        color += 1

    lsv.legend.location = "top_left"
    lsv.legend.title = "ZnSO4 Concentrations"
    if threshold:
        lsv.vspan(
            x=[threshold + electrodePotential],
            line_width=[1],
            line_color="black",
            line_dash="dashed",
            legend_label="Threshold",
        )

    show(lsv)

# Cyclic voltammetry function


class DataFrameEmpty(Exception):
    pass


def cv_plot(data_dict):
    output_notebook()
    cv = figure(
        title="Cyclic Voltammetry",
        x_axis_label="Potential (V vs Zn)",
        y_axis_label="Current density (mA/cm^2)",
        width=800,
        height=400,
    )

    ## Constrain axes
    # cv.x_range.start = -0.5
    # cv.x_range.end = 4
    # cv.y_range.start = -20
    # cv.y_range.end = 20

    color = 0
    for key, value in data_dict.items():
        try:
            # Load data
            df = ecf.to_df(value[0])
            if df.empty:
                raise DataFrameEmpty(f"Data frame is empty for {key}")

            # Adjust potential and current density
            SCE = 0.241
            el_surface_area = 2.48

            potential = df["Ewe"]  # - SCE
            current = df["<I>"] / el_surface_area

            # Plot
            colors = small_palettes["Viridis"][4]
            cv.line(
                potential,
                current,
                legend_label=key,
                line_color=colors[color % len(colors)],
                line_width=2,
            )
        except DataFrameEmpty as eD:
            print(f"{eD}")
        except Exception as e:
            print(f"Error processing {key}: {e}")

        color += 1

    cv.legend.location = "top_left"
    cv.legend.title = "ZnSO4 Concentrations"

    show(cv)

# LSV dictionary maker


def lsv_dictionary(path):
    folder_path = Path(path)

    print(folder_path.name)

    data_dict = {}

    # Iterate over all .mpr files that contain "LSV"
    for file_path in folder_path.iterdir():
        if (
            file_path.is_file()
            and file_path.suffix == ".mpr"
            and "LSV" in file_path.name
        ):
            # Find the position of "LSV"
            file_name = file_path.name
            lsv_index = file_name.find("LSV")

            # Extract 4 characters before "LSV"
            if lsv_index > 4:  # Ensure there are at least 4 characters before
                prefix = file_name[: lsv_index - 4]
                # print(f"Prefix before 'LSV': {prefix}")
            else:
                print(f"Not enough characters before 'LSV' in {file_name}")
                prefix = "InvalidPrefix"

            # Add the file name to the dictionary under the appropriate prefix
            if prefix not in data_dict:
                data_dict[prefix] = [str(file_path)]
            else:
                data_dict[prefix].append(str(file_path))

    print(f"Check if these are your files of interest {data_dict}")

    return data_dict


# CV dictionary maker
def cv_dictionary(path):
    folder_path = Path(path)
    data_dict = {}

    # Iterate over all .mpr files that contain "LSV"
    for file_path in folder_path.iterdir():
        if (
            file_path.is_file()
            and file_path.suffix == ".mpr"
            and "CV" in file_path.name
        ):
            # Find the position of "CV"
            file_name = file_path.name
            lsv_index = file_name.find("CV")

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

    print(f"Check if these are your files of interest {data_dict}")

    return data_dict