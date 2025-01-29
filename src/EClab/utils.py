import pandas as pd
from IPython.display import HTML, display


def tabulate(dictionary):
    # Flatten the dictionary into rows
    print("Check if this is your intended data:")
    flattened_data = [{'Sample': key, 'File path': value[0]} for key, value in dictionary.items()]
    df = pd.DataFrame(flattened_data)

    display(HTML(df.to_html()))




# Plot settings

# Color scheme
backgrund_color = "white"
plot_color = "whitesmoke"

# Tools
tools="box_zoom,lasso_select,reset, save"
