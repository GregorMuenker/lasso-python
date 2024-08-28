import os
import pandas as pd

import sys

sys.path.insert(1, "../../backend")
from constants import RED, RESET


class SequenceSpecification:
    def __init__(self, filePath) -> None:
        self.name = os.path.basename(filePath)
        self.sequenceSheet = get_sequence_sheet(filePath)

        self.statements = {}
        for index, row in self.sequenceSheet.iterrows():
            statement = Statement(
                index,
                row["output_param"],
                row["method_name"],
                row["instance_param"],
                row["input_params"],
            )
            self.statements[index] = statement
    
    def printInputParamTypes(self):
        for index, statement in self.statements.items():
            print(f"Row: {index}")
            for param in statement.inputParams:
                print(f"{param}, {type(param)}")


class Statement:
    def __init__(self, position, oracleValue, methodName, instanceParam, inputParams) -> None:
        self.position = position
        self.oracleValue = oracleValue
        self.methodName = methodName
        self.instanceParam = instanceParam
        self.inputParams = inputParams
    
    def __repr__(self) -> str:
        return f"{self.position}: Oracle Value: {self.oracleValue} | Method Name: {self.methodName} | Instance Param: {self.instanceParam} | Input Params: {self.inputParams}"


def get_sequence_sheet(path) -> pd.DataFrame:
    """
    Read in excel/csv file and return sequence sheet in DataFrame format
    """
    _, file_extension = os.path.splitext(path)

    if file_extension in [".xls", ".xlsx", ".xlsm", ".xlsb"]:
        # dtype=object prevents that integers are automatically converted to floats
        df = pd.read_excel(path, header=None, dtype=object)
    elif file_extension in [".csv"]:
        # dtype=object would not work here as every value would become a string
        df = pd.read_csv(path, header=None, sep=";")
        print(f"{RED}Warning:{RESET} Due to Pandas, int values in CSV files are automatically converted to floats. Use Excel files instead.")
    else:
        raise ValueError("Unsupported file type")

    if not df.iloc[0].astype(str).str.contains("create").any():
        raise ValueError("Sequence sheet must contain a create statement")

    # Apply reference resolution across the DataFrame TODO uncomment if this works
    # df = df.applymap(lambda x: resolve_references(x, df))

    # combine all input param columns into one list and drop null entries
    input_params = pd.DataFrame(
        df.apply(lambda row: [x for x in row[3:] if pd.notnull(x)], axis=1)
    )

    # drop all separate input_param columns and concat remaining df with combined input_param column
    df = df.drop(df.columns[3:], axis=1)
    df = pd.concat([df, input_params], axis=1)

    # create headers/column labels
    df.columns = ["output_param", "method_name", "instance_param", "input_params"]

    return df


def resolve_references(cell, df):
    """
    Resolve cell references like A1, B2, etc.
    NOTE: Currently, cell references are realized by prepending >>, e.g., ">>A1"
    """
    if isinstance(cell, str) and cell.startswith(">>"):
        try:
            # Get the referenced cell position, e.g., ">>A1"
            ref = cell[2:]
            # Parse the column and row
            col = ord(ref[0].upper()) - 65
            row = int(ref[1:]) - 1

            value = df.iloc[row, col]
            # Ensure integer values remain as integers
            if isinstance(value, float) and value.is_integer():
                return int(value)
            return value
        except Exception as e:
            # Return the original value if parsing fails
            return cell 
    return cell


if __name__ == "__main__":
    sequenceSpecification = SequenceSpecification("calc3_adaptation.xlsx")
    print(sequenceSpecification.sequenceSheet)
    
    sequenceSpecification.printInputParamTypes()