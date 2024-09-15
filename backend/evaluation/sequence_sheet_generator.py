import os
import uuid
import pandas as pd
import git
import sys
import re

repo = git.Repo(search_parent_directories=True)
sys.path.insert(0, repo.working_tree_dir)

import builtins
import ast
import json

cell_number = 1

def parse_value(source_code, element):
    try:
        if type(element) == ast.UnaryOp:
            constant_value = element.operand.value
        else:
            constant_value = element.value
        if type(constant_value) == int:
            return int(ast.get_source_segment(source_code, element))
        elif type(constant_value) == float:
            return float(ast.get_source_segment(source_code, element))
        elif type(constant_value) == str:
            constant_value = ast.get_source_segment(source_code, element)
            regex = r"[-+]?\b\d.?\d+\b"
            if re.match(regex, constant_value):
                return constant_value
            else:
                return constant_value[1:-1]
        elif type(constant_value) == bool:
            return constant_value
        elif constant_value is None:
            return None
        else:
            return ast.get_source_segment(source_code, element)
    except Exception as e:
        return ast.get_source_segment(source_code, element)

def create_sequence_sheet_entries(test, element, cell_type):
    global cell_number
    sequence_sheet = []
    if type(element) == ast.Call:
        args = []
        for arg in element.args:
            if type(arg) == ast.Call or type(arg) == ast.List or type(arg) == ast.Tuple or type(arg) == ast.Dict or type(arg) == ast.Set:
                sequence_sheet += create_sequence_sheet_entries(test, arg, cell_type)
                args.append(f"{cell_type}{cell_number - 1}")
            elif type(arg) != ast.Constant and type(arg) != ast.UnaryOp and type(arg) != ast.BinOp:
                print(f"Not supported: {parse_value(test, arg)}")
            else:
                args.append(parse_value(test, arg))
        function_name = element.func.id
        if function_name in dir(builtins):
            function_name = "python." + function_name.capitalize()
            sequence_sheet.append([f"{cell_type}{cell_number}", "create", function_name] + args)
        else:
            sequence_sheet.append([f"{cell_type}{cell_number}", function_name, "A1"] + args)
    elif type(element) == ast.List or type(element) == ast.Tuple or type(element) == ast.Set:
        elts = []
        for elt in element.elts:
            if type(elt) == ast.Call or type(elt) == ast.List or type(elt) == ast.Tuple or type(elt) == ast.Dict or type(elt) == ast.Set:
                sequence_sheet += create_sequence_sheet_entries(test, elt, cell_type)
                elts.append(f"{cell_type}{cell_number - 1}")
            elif type(elt) != ast.Constant and type(elt) != ast.UnaryOp and type(elt) != ast.BinOp:
                print(f"Not supported: {parse_value(test, elt)}")
            else:
                elts.append(parse_value(test, elt))
        if type(element) == ast.List:
            sequence_sheet.append([f"{cell_type}{cell_number}", "create", "python.List"] + elts)
        elif type(element) == ast.Set:
            sequence_sheet.append([f"{cell_type}{cell_number}", "create", "python.Set"] + elts)
        else:
            sequence_sheet.append([f"{cell_type}{cell_number}", "create", "python.Tuple"] + elts)
    elif type(element) == ast.Dict:
        key_value_list = [item for pair in zip(element.keys, element.values) for item in pair]
        for i, entry in enumerate(key_value_list):
            if type(entry) == ast.Call or type(entry) == ast.List or type(entry) == ast.Tuple or type(entry) == ast.Dict:
                sequence_sheet += create_sequence_sheet_entries(test, entry, cell_type)
                key_value_list[i] = f"{cell_type}{cell_number - 1}"
            elif type(entry) != ast.Constant and type(entry) != ast.UnaryOp:
                print(parse_value(test, entry))
            else:
                key_value_list[i] = parse_value(test, entry)
        sequence_sheet.append([f"{cell_type}{cell_number}", "create", "python.Dict"] + key_value_list)

    else:
        sequence_sheet.append([f"result{cell_number}", parse_value(test, element), ""])
    cell_number += 1
    return sequence_sheet


def generate_sequence_sheets(llm_file):
    global cell_number

    file = open(llm_file, 'r')
    tasks = json.load(file)
    sequence_sheets = {}
    for task in tasks:
        tests = task["test_list"]
        sequence_sheet = []
        cell_number = 1
        for test in tests:
            test_ast = ast.parse(test).body[0].test
            if type(test_ast) == ast.Compare:
                try:
                    right = create_sequence_sheet_entries(test, test_ast.comparators[0], "lasso_comp")
                    left = create_sequence_sheet_entries(test, test_ast.left, "lasso_test")
                    if "result" in right[-1][0]:
                        left[-1][0] = right[-1][1]
                        right.pop(-1)
                    else:
                        left[-1][0] = "res_" + right[-1][0]
                    sequence_sheet += (right + left)
                except AttributeError as e:
                    print(e)
                    pass
        print(sequence_sheet)
        first_row = [x[0] for x in sequence_sheet]
        for i, element in enumerate(first_row):
            if type(element) == str:
                if "res_" in element:
                    sequence_sheet[i][0] = f"A{first_row.index(element[4:]) + 2}"
                elif "lasso_comp" in element or "lasso_test" in element:
                    sequence_sheet[i][0] = ""
        for i_1, row in enumerate(sequence_sheet):
            for i_2, element in enumerate(row):
                if type(element) == str and ("lasso_test" in element or "lasso_comp" in element):
                    sequence_sheet[i_1][i_2] = f"A{first_row.index(element) + 2}"
        sequence_sheet = [["", "create", f"Task{task['task_id']}", ""]] + sequence_sheet
        sequence_sheets[task['task_id']] = sequence_sheet
    return sequence_sheets


if __name__ == "__main__":
    sequence_sheets = generate_sequence_sheets("evaluation_sanitized-mbpp.json")
    os.makedirs("evaluation_sheets/llm_sequence_sheets", exist_ok=True)
    for task_id in sequence_sheets.keys():
        pd.DataFrame(sequence_sheets[task_id]).to_excel(f"evaluation_sheets/llm_sequence_sheets/{task_id}.xlsx",
                                                        index=False, header=False)