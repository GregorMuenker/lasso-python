from adaptation import MethodSignature, InterfaceSpecification, AdaptationHandler, execute_test, create_adapted_module
from stimulus_sheet_reader import get_stimulus_sheet
from solr_parser import parse_solr_response
from solr_query import translate_to_solr_query
import pysolr

if __name__ == "__main__":
    icubed = MethodSignature("log", "float", ["int", "int"])
    iminus = MethodSignature("sqrd", "str", ["int"])
    interfaceSpecification = InterfaceSpecification("Calculator", [], [icubed, iminus])

    solr_url = "http://localhost:8983/solr/lasso_quickstart"
    solr = pysolr.Solr(solr_url)
    solr_query = translate_to_solr_query(interfaceSpecification)
    print("QUERY:", solr_query)
    results = solr.search(solr_query)
    print(f"Found {len(results)} results")

    moduleUnderTest = parse_solr_response(results)

    adaptationHandler = AdaptationHandler(interfaceSpecification, moduleUnderTest, excludeClasses=False, useFunctionDefaultValues=False)
    adaptationHandler.identifyAdaptations(maxParamPermutationTries=2)
    adaptationHandler.visualizeAdaptations()
    adaptationHandler.generateMappings(onlyKeepTopN=10)

    (adapted_module, number_of_submodules, submodules_metadata)  = create_adapted_module(adaptationHandler, moduleUnderTest.moduleName, use_constructor_default_values=True)

    stimulus_sheet = get_stimulus_sheet("calc4.csv")
    execute_test(stimulus_sheet, adapted_module, number_of_submodules, submodules_metadata)