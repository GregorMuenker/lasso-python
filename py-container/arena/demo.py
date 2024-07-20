from adaptation import MethodSignature, InterfaceSpecification, AdaptationHandler, execute_test, create_adapted_module
from stimulus_sheet_reader import get_stimulus_sheet
import json
from solr_parser import parse_solr_response

if __name__ == "__main__":
    icubed = MethodSignature("icubed", "str", ["int"])
    iminus = MethodSignature("iminus", "str", ["float", "int"])

    interfaceSpecification = InterfaceSpecification("Calculator", [], [icubed, iminus])

    path = "./numpy_query.json"
    with open(path, 'r') as file:
        file_content = json.load(file)
        moduleUnderTest = parse_solr_response(file_content)

    adaptationHandler = AdaptationHandler(interfaceSpecification, moduleUnderTest, excludeClasses=False, useFunctionDefaultValues=False)
    adaptationHandler.identifyAdaptations(maxParamPermutationTries=1)
    adaptationHandler.visualizeAdaptations()
    adaptationHandler.generateMappings(onlyKeepTopN=10)

    (adapted_module, number_of_submodules, submodules_metadata)  = create_adapted_module(adaptationHandler, moduleUnderTest.moduleName, use_constructor_default_values=True)

    stimulus_sheet = get_stimulus_sheet("calc3.csv")
    execute_test(stimulus_sheet, adapted_module, number_of_submodules, submodules_metadata)