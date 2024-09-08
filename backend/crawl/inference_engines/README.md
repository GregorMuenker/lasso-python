# Type Inferencing Schema
To create a modular type inferencing module with different type inference engines, the inferred datatypes should be stored with the following JSON format:

Name of the json file: *\<full module path\>+_INFERREDTYPES.json*
```json
{
  "function_name@dependent_class": {
    "name_of_parameter": ["datatypes"],
    "return": ["return datatypes"]
  }
}
```