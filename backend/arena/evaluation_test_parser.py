import json
import openpyxl
import re

import re

def parse_assert_line(line):
    # Remove 'assert' and strip whitespace
    line = line.replace('assert ', '').strip()

    # Split into left and right parts using '=='
    left_part, right_part = map(str.strip, line.split('=='))

    # Handle wrapped methods like set() on the left part
    if re.match(r"(\w+)\((.*)\)", left_part):
        while re.match(r"(\w+)\((.*)\)", left_part) and left_part.startswith("set("):
            left_part = re.sub(r"^set\((.*)\)$", r"\1", left_part)

    # Use regex to differentiate method call and parameters on the left
    match_left = re.match(r"(\w+)\((.*)\)", left_part)
    
    if match_left:
        method_name_left = match_left.group(1)  # Function/method name
        parameters_left = match_left.group(2)   # Parameters
        
        # Split parameters if they are wrapped in parentheses or multiple sets/lists (like (1,2,4))
        list_of_params = re.findall(r'\((.*?)\)', parameters_left)  # Extract all groups inside parentheses
        if list_of_params:
            # Generate a list of lists/sets for each group
            parameters_left = [[param.strip() for param in group.split(',')] for group in list_of_params]
        else:
            # If no list of params, split the parameters by commas
            parameters_left = [param.strip() for param in parameters_left.split(',')]
    else:
        raise ValueError("Invalid format for the left part of the assert.")

    # Handle wrapped methods or lists on the right part
    match_right = re.match(r"(\w+)\((.*)\)", right_part)

    # Check if the right part is a list (e.g., [4, 4, 3])
    list_match_right = re.match(r"\[(.*)\]", right_part)
    
    if match_right:
        # Case where there's a method wrapped on the right part (e.g., set((4, 5)))
        method_name_right = "create"
        instance_param_right = f"python.{str(match_right.group(1)).capitalize()}"  # Wrap the method name with 'python.'
        parameters_right = match_right.group(2)
        # Ensure parameters are a list
        parameters_right = re.sub(r'[\(\)]', '', parameters_right)  # Remove parentheses
        parameters_right = [param.strip() for param in parameters_right.split(',')]
    elif list_match_right:
        # Case where the right part is a list (e.g., [4, 4, 3])
        method_name_right = "create"
        instance_param_right = "python.List"
        parameters_right = list_match_right.group(1)
        # Ensure parameters are a list
        parameters_right = [param.strip() for param in parameters_right.split(',')]
    else:
        # Treat the right part as a simple value if not wrapped in a method or list
        method_name_right = None
        instance_param_right = None
        parameters_right = right_part

    # Return the parsed components
    result = {
        'method_name_left': method_name_left,
        'parameters_left': parameters_left,
        'expected_value': {
            'method_name_right': method_name_right,
            'instance_param_right': instance_param_right,
            'parameters_right': parameters_right
        } if method_name_right else {'value': parameters_right}
    }

    return result


file = open('evaluation_sanitized-mbpp.json', 'r')
data = json.load(file)  

for task in data:
    task_id = task["task_id"]
    class_name = f"Task{task_id}"
    # if task_id > 50:
    #     break
    wb = openpyxl.Workbook()
    sheet = wb.active  
    
    current_row = 2
    for test in task["test_list"]:
        
        sheet['B1'] = "create"
        sheet['C1'] = class_name

        parsed_result = parse_assert_line(test)
        method_name = parsed_result['method_name_left']   

        # Check if parameters are complex
        for parameter in parsed_result['parameters_left']:
            if isinstance(parameter, list):
                sheet[f'B{current_row}'] = "create"
                sheet[f'C{current_row}'] = "python.List"
                for i, arg in enumerate(parameter):
                    letter = chr(ord('D') + i)
                    sheet[f"{letter}{current_row}"] = arg
                current_row += 1
            else:
                for i, arg in enumerate(parsed_result['parameters_left']):
                    letter = chr(ord('D') + i)
                    sheet[f"{letter}{current_row}"] = arg

        if parsed_result['expected_value'].get('method_name_right'):
            # The oracle value is a complex value (list, set, etc.), add a create statement
            sheet[f'B{current_row}'] = "create"
            sheet[f'C{current_row}'] = parsed_result['expected_value']['instance_param_right']

            # Parameter values for create call
            for i, parameter in enumerate(parsed_result['expected_value']['parameters_right']):
                letter = chr(ord('D') + i)
                sheet[f"{letter}{current_row}"] = parameter
            
            current_row += 1
        else:
            # The oracle value is simple, no need to create a complex object
            sheet[f'B{current_row}'] = method_name            
            sheet[f'A{current_row}'] = parsed_result['expected_value']['value']
            sheet[f'C{current_row}'] = "A1"
            
        # Add the method call to the next row
        sheet[f'B{current_row}'] = method_name
        sheet[f'A{current_row}'] = f'A{current_row - 1}'
        sheet[f'C{current_row}'] = "A1"
        
        current_row += 1

    wb.save(f"./evaluation_sheets/{task_id}.xlsx")

