import pandas as pd
from IPython.display import HTML, display
from bokeh.palettes import viridis, magma
from pathlib import Path
import pandas as pd
import eclabfiles as ecf



class DataFrameEmpty(Exception):
    pass

class DataDictionary:
    """Collects file paths from a directory based on a given filetype."""
    
    def __init__(self, path="./data/"):
        self.path = path
        # Initialize empty dictionaries for each file type
        self.data_gcpl = {}
        self.data_lsv = {}
        self.data_cv = {}
        self.data_peis = {}
        
        # Build the data dictionaries in a single pass.
        self._build_data_dict()

    def _build_data_dict(self) -> None:
        folder_path = Path(self.path)
        print(f"Loading data from {folder_path} folder")
        print("_______________________________________________")
        
        # Define candidate file types here:
        candidate_types = ["CV", "GCPL", "LSV", "PEIS"]

        for file_path in folder_path.glob('**/*'):
            if file_path.is_file() and file_path.suffix == ".mpr":
                file_name = file_path.name
                
                # Call detect_filetype with the list of candidate types.
                detected_ft = self.detect_filetype(file_name, candidate_types)
                
                if not detected_ft:
                    print(f"Could not detect a valid file type in: {file_name}")
                    continue

                # Find the index of the detected file type (closest to the end).
                filetype_index = file_name.rfind(detected_ft)
                
                if filetype_index > 1:
                    prefix = file_name[: filetype_index - 1]
                else:
                    print(f"File name Error: {file_name} has the filetype as name. Remove that.")
                    prefix = "InvalidPrefix"
                
                # Process the file: this example assumes you want to convert the file into a DataFrame.
                try:
                    df = ecf.to_df(file_path)  # Replace with your actual file processing logic.
                    if df.empty:
                        raise DataFrameEmpty(f"Data frame is empty for {file_name}")
                    
                    #print("File type inside loop:", detected_ft)
                    
                    # Use a match-case block to assign the file to the correct dictionary.
                    if detected_ft == "CV":
                        data_dict = self.data_cv
                    elif detected_ft == "LSV":
                        data_dict = self.data_lsv
                    elif detected_ft == "PEIS":
                        data_dict = self.data_peis
                    elif detected_ft == "GCPL":
                        data_dict = self.data_gcpl
                    else:
                        print(f"Unknown file type detected: {detected_ft}")
                        continue
                    
                    if prefix not in data_dict:
                        data_dict[prefix] = []
                    data_dict[prefix].append(str(file_path))
                
                except DataFrameEmpty as eD:
                    print(eD)
                    continue
                except Exception as e:
                    print(f"Error processing {prefix}: {e}")
                    continue
        print("_______________________________________________")

        print("LSV data")
        self.tabulate(self.data_lsv)

        print("PEIS data")
        self.tabulate(self.data_peis)

        print("CV data")
        self.tabulate(self.data_cv)

        print("GCPL data")
        self.tabulate(self.data_gcpl)





    @staticmethod
    def detect_filetype(file_name: str, candidate_types: list) -> str:
        """
        Given a file_name and a list of candidate file types,
        returns the file type that occurs closest to the end of the file name.
        If none of the candidate types is found, returns None.
        """
        last_occurrence = -1
        detected_type = None
        for ft in candidate_types:
            pos = file_name.rfind(ft)
            # Only update if the candidate is found and its position is later than any seen so far.
            if pos > last_occurrence:
                last_occurrence = pos
                detected_type = ft
        return detected_type


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
    
