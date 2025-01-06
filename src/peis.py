
import eclabfiles as ecf
from bokeh.palettes import small_palettes
from pathlib import Path
from bokeh.plotting import figure, output_notebook, show

class DataFrameEmpty(Exception):
    pass


def PEIS(dict):

    output_notebook()
    pe = figure(
        title="Nyquist plot",
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
            continue


        zReal = df["Re(Z)"]
        zImagine = df["-Im(Z)"]

        # Plot
        colors = small_palettes["Viridis"][4]
        pe.line(
            zReal,
            zImagine,
            legend_label=key,
            line_color=colors[color % len(colors)],
            line_width=1,
        )

        color += 1

    pe.legend.location = "bottom_right"
    #pe.legend.title = "ZnSO4 Concentrations"
    show(pe)






def PEIS_dictionary(path):
    folder_path = Path(path)
    data_dict = {}


    # Iterate over all .mpr files that contain "LSV"
    for file_path in folder_path.iterdir():
        if (
            file_path.is_file()
            and file_path.suffix == ".mpr"
            and "PEIS" in file_path.name
        ):
            # Find the position of "GCLP"
            file_name = file_path.name
            peis_index = file_name.find("PEIS")

            # Extract 4 characters before "LSV"
            if peis_index > 1:  # Ensure there are at least 4 characters before
                prefix = file_name[: peis_index - 1]
                # print(f"Prefix before 'LSV': {prefix}")
            else:
                print(f"Not enough characters before 'CV' in {file_name}")
                prefix = "InvalidPrefix"

            # Add the file name to the dictionary under the appropriate prefix
            if prefix not in data_dict:
                data_dict[prefix] = [str(file_path)]

    return data_dict