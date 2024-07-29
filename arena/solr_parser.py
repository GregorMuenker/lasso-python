def parse_solr_response(response):
    """
    Parses the Solr response and extracts relevant information to create FunctionSignature and ModuleUnderTest objects.
    As of now, only the first module is considered.
    """
    from adaptation import FunctionSignature, ModuleUnderTest
    functionSignatureDict = {} # key: module name, value: list of FunctionSignature objects
    classDict = {} # key: module name, value: dict with key: class name, value: list of FunctionSignature objects
    
    for doc in response:
        moduleName = doc.get('module', [None])[0]

        if moduleName not in functionSignatureDict:
            functionSignatureDict[moduleName] = []
            classDict[moduleName] = {}

        functionName = doc.get('name', None)[0]
        returnType = doc.get('return_types', ['Any'])[0]
        parameterTypes = doc.get('arguments.datatype', [])
        firstDefault = doc.get('default_index', [len(parameterTypes)])[0]

        parentClass = doc.get('dependend_class', [None])[0]
        if parentClass == "None":
            parentClass = None
        else:
            if parentClass not in classDict[moduleName]:
                classDict[moduleName][parentClass]= []
        
        parameterNames = doc.get('arguments.name', [])
        if len(parameterNames) > 0:
            if parameterNames[0] == "self":
                parameterTypes = parameterTypes[1:]
                firstDefault -= 1

        functionSignature = FunctionSignature(functionName, returnType, parameterTypes, parentClass, firstDefault)

        if functionName == "__init__" or functionName == "__new__":
                classDict[moduleName][parentClass].append(functionSignature)
        else:
            functionSignatureDict[moduleName].append(functionSignature)
    
    allModulesUnderTest = []
    for moduleName in functionSignatureDict:
        print(moduleName)
        moduleUnderTest = ModuleUnderTest(moduleName, functionSignatureDict[moduleName], classDict[moduleName])
        allModulesUnderTest.append(moduleUnderTest)
    
    print(f"Generated {len(allModulesUnderTest)} ModuleUnderTest objects.")

    return allModulesUnderTest

if __name__  == "__main__":
    import json

    path = "./numpy_query.json"
    with open(path, 'r') as file:
        file_content = json.load(file)

    moduleUnderTest = parse_solr_response(file_content)