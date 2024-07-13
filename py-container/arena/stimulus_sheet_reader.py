import os
import pandas as pd

# read in excel/csv and return stimulus sheet in DataFrame format
def get_stimulus_sheet(path) -> pd.DataFrame:
    _, file_extension = os.path.splitext(path)
    
    # read in file based on its extension
    if file_extension in ['.xls', '.xlsx', '.xlsm', '.xlsb']:
        df = pd.read_excel(path, header=None)
    elif file_extension in ['.csv']:
        df = pd.read_csv(path, header=None, sep=';')
    else:
        raise ValueError("Unsupported file type")
    
    if df.iloc[0].astype(str).str.contains("create").any():
        # Drop the first row if it contains the create statement
        df = df.drop(df.index[0])

    # combine all input param columns into one list and drop null entries
    input_params = pd.DataFrame(df.apply(lambda row: [x for x in row[3:] if pd.notnull(x)], axis=1))

    # drop all separate input_param columns and concat remaining df with combined input_param column
    df = df.drop(df.columns[3:], axis=1)
    df = pd.concat([df, input_params], axis=1)

    # create headers/column labels
    df.columns = ['output_param', 'method_name', 'instance_param', 'input_params']

    return df