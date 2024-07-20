def parse_solr_response(response):
    from adaptation import FunctionSignature, ModuleUnderTest
    functionSignatures = []
    classes = {}
    moduleName = None
    
    for doc in response:
        if not moduleName:
            moduleName = doc.get('module', [None])[0]
        
        functionName = doc.get('name', None)[0]
        returnType = 'Any'  # TODO
        parameterTypes = doc.get('arguments.datatype', [])
        parentClass = doc.get('dependend_class', [None])[0]
        firstDefault = doc.get('default_index', [len(parameterTypes)])[0]

        if parentClass == "None":
            parentClass = None
        
        if parentClass:
            if parentClass not in classes:
                classes[parentClass] = []
        parameterNames = doc.get('arguments.name', [])
        if parameterNames[0] == "self":
            parameterTypes = parameterTypes[1:]
            firstDefault -= 1

        functionSignature = FunctionSignature(functionName, returnType, parameterTypes, parentClass, firstDefault)

        if functionName == "__init__" or functionName == "__new__":
                classes[parentClass].append(functionSignature)
        else:
            functionSignatures.append(functionSignature)

        print(functionSignature)
    
    moduleUnderTest = ModuleUnderTest(moduleName, functionSignatures)
    moduleUnderTest.classes = classes
    print(classes)
    return moduleUnderTest

if __name__  == "__main__":
    import json

    path = "./numpy_query.json"
    with open(path, 'r') as file:
        file_content = json.load(file)

    moduleUnderTest = parse_solr_response(file_content)