import pandas as pd

# Solr search query results in JSON object of functions
solr_query_result = {
  "responseHeader":{
    "status":0,
    "QTime":1,
    "params":{
      "q":"*:*",
      "wt":"json"
    }
  },
  "response": {
    "numFound":2,
    "start":0,
    "docs":[
      {
        "id":"1",
        "class_name":"calculator",
        "method_name":"add",
        "parameters":["a int", "b int"],
        "return_type":"int",
        "code":"def add(a, b):\n    return a + b",
        "description":"Adds two numbers."
      },
      {
        "id":"2",
        "class_name":"calculator",
        "method_name":"subtract",
        "parameters":["a int", "b int"],
        "return_type":"int",
        "code":"def subtract(a, b):\n    return a - b",
        "description":"Subtracts second number from first."
      }
    ]
  }
}


def get_sequence_sheet(path):
    df = pd.read_excel(path, header=None)
    
    # combine all input params into one list
    #input_params = pd.DataFrame(df.apply(lambda row: row[3:].tolist(), axis=1)) # also include empty params here
    input_params = pd.DataFrame(df.apply(lambda row: [x for x in row[3:] if pd.notnull(x)], axis=1))

    df = df.drop(df.columns[3:], axis=1)
    df = pd.concat([df, input_params], axis=1)

    # create headers/column labels
    df.columns = ['output_param', 'method_name', 'instance_param', 'input_params']

    return df

def execute_sequence_sheet(solr_query_result, sequence_sheet):
    # Define the method globally and store a reference in 'methods'
    methods = {}
    for doc in solr_query_result["response"]["docs"]:
        exec(doc["code"])
        methods[doc["method_name"]] = eval(doc["code"].split('def ')[1].split('(')[0])
    print(methods)
    
    # apply methods and store results
    true_outputs = []
    for index, row in sequence_sheet.iterrows():        
        method_name = row['method_name']
        input_params = row['input_params']

        if method_name in methods:
            method = methods[method_name]
            try:
                # Call the method with unpacked input_params
                true_outputs.append(method(*input_params))
            except TypeError as e:
                print(f"Error calling method {method_name} with {input_params}: {e}")
                true_outputs.append("Error")
        else:
            print(f"Method {method_name} not found.")
            return None
    
    results = pd.DataFrame({
        'output_param': sequence_sheet['output_param'],
        'true_outputs': true_outputs
    })
    results['comparison'] = results['output_param'] == results['true_outputs']
    print(results)
        

sequence_sheet = get_sequence_sheet("calc.xlsx")
print(sequence_sheet.head())
execute_sequence_sheet(solr_query_result, sequence_sheet)