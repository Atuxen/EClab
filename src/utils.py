from IPython.display import Markdown, display, HTML
import pandas as pd

def tabulate(dictionary):
    # Flatten the dictionary into rows
    print("Check if this is your intended data:")
    flattened_data = [{'Key': key, 'File': value[0]} for key, value in dictionary.items()]
    df = pd.DataFrame(flattened_data)

    display(HTML(df.to_html()))