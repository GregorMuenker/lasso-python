from adaptation import AdaptationHandler, create_adapted_module
from execution import execute_test
from stimulus_sheet_reader import get_stimulus_sheet
from solr_parser import parse_solr_response
from solr_query import translate_to_solr_query
from lql_parser import parse_interface_spec
import pysolr

if __name__ == "__main__":
    lql_string = """
    Calculator {
        Calculator(int)->None
        log(int, int)->float
        sqrd(int)->float
    }
    """

    interfaceSpecification = parse_interface_spec(lql_string)
    print(interfaceSpecification)

    solr_url = "http://localhost:8983/solr/lasso_quickstart"
    solr = pysolr.Solr(solr_url)
    solr_query = translate_to_solr_query(interfaceSpecification)
    print("QUERY:", solr_query)
    results = solr.search(solr_query)
    print(f"Found {len(results)} results")

    allModulesUnderTest = parse_solr_response(results)
    moduleUnderTest = allModulesUnderTest[0] # only take the first module for now

    adaptationHandler = AdaptationHandler(interfaceSpecification, moduleUnderTest, excludeClasses=False, useFunctionDefaultValues=False)
    adaptationHandler.identifyAdaptations(maxParamPermutationTries=2)
    adaptationHandler.visualizeAdaptations()
    adaptationHandler.generateMappings(onlyKeepTopN=10)

    (adapted_module, successful_mappings)  = create_adapted_module(adaptationHandler, moduleUnderTest.moduleName, use_constructor_default_values=True)

    stimulus_sheet = get_stimulus_sheet("calc4.csv")
    execute_test(stimulus_sheet, adapted_module, successful_mappings)