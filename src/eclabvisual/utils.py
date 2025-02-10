import pandas as pd
from IPython.display import HTML, display
from bokeh.palettes import viridis, magma
from pathlib import Path
import pandas as pd
from IPython.display import HTML, display
import eclabfiles as ecf
import eclabfiles as ecf


class DataFrameEmpty(Exception):
    pass

class DataDictionary:
    """Collects file paths from a directory based on a given filetype."""

    def __init__(self):
        self.path = "./data/"
        self.data_gcpl = self._build_data_dict("GCPL")
        self.data_lsv = self._build_data_dict("LSV")
        self.data_cv = self._build_data_dict("CV")
        self.data_peis = self._build_data_dict("PEIS")

    def _build_data_dict(self, filetype: str) -> dict:
        folder_path = Path(self.path)
        data_dict = {}

        print(f"Checking {filetype} files in {folder_path} ...")

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
                    print(f"File name Error: {file_name} has a filetype as name. Remove that.")
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
                    print(f"Empty data Error: {eD}")
                    continue
                except Exception as e:
                    print(f"Error processing {prefix}: {e}")
                    continue
                    
        print(f"Found the following {filetype} files: ")
        self.tabulate(data_dict)
                
        return data_dict

    def tabulate(self, dictionary: dict):
        # Flatten the dictionary into rows
        flattened_data = [{'Sample': key, 'File path': value[0]} for key, value in dictionary.items()]
        df = pd.DataFrame(flattened_data)
        display(HTML(df.to_html()))

    def viewData(self, path):
        df = ecf.to_df(path)    
        print(df)
        return df



class Grapher():
    def __init__(self):
     # Colors for plots
        self.background_color = "white"
        self.plot_color = "whitesmoke"
    
    def get_colors(self, items):
        n = len(items)
        return viridis(n)
    
