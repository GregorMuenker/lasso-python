from adaptation_identification import FunctionSignature, ModuleUnderTest
import re

def parse_solr_response(response):
    """
    Parses the Solr response and extracts relevant information to create FunctionSignature and ModuleUnderTest objects.
    As of now, only the first module is considered.
    """
    

    functionSignatureDict = (
        {}
    )  # key: module name, value: list of FunctionSignature objects
    classDict = (
        {}
    )  # key: module name, value: dict with key: class name, value: list of FunctionSignature objects

    for doc in response:
        moduleName = doc.get("packagename", [None])[0]

        if moduleName not in functionSignatureDict:
            functionSignatureDict[moduleName] = []
            classDict[moduleName] = {}

        functionName = doc.get("method", None)[0]
        returnType = doc.get("return_types", ["Any"])[0]
        parameters = doc.get("methodSignatureParamsOrderedNodefault", [""])[0].split("|")[1:]
        parameters = [x.split("_", 1) for x in parameters]

        #Extracting only the first possible datatype of a parameter
        parameterTypes = [re.sub("pt_", '', x[1][1:-1]).split(",")[0] for x in parameters]
        firstDefault = -1

        parentClass = doc.get("name", [None])[0]
        if parentClass == "None":
            parentClass = None
        else:
            if parentClass not in classDict[moduleName]:
                classDict[moduleName][parentClass] = []



        functionSignature = FunctionSignature(
            functionName, returnType, parameterTypes, parentClass, firstDefault
        )

        if functionName == "__init__" or functionName == "__new__":
            classDict[moduleName][parentClass] = functionSignature
        else:
            functionSignatureDict[moduleName].append(functionSignature)

    allModulesUnderTest = []
    for moduleName in functionSignatureDict:
        print(moduleName)
        moduleUnderTest = ModuleUnderTest(
            moduleName, functionSignatureDict[moduleName], classDict[moduleName]
        )
        moduleUnderTest.classConstructors = classDict[moduleName]
        allModulesUnderTest.append(moduleUnderTest)

    print(f"Generated {len(allModulesUnderTest)} ModuleUnderTest objects.")

    return allModulesUnderTest


if __name__ == "__main__":
    import json

    path = "./numpy_query.json"
    with open(path, "r") as file:
        file_content = json.load(file)

    moduleUnderTest = parse_solr_response(file_content)
    print(moduleUnderTest)
