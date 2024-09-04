import pysolr
import re

class LassoSolrConnector:
    def __init__(self, solr_url):
        self.solr = pysolr.Solr(solr_url)

    def search_matching_methods(self, interface_spec):
        queries = []
        for method in interface_spec.methods:
            query = []
            param_types = method.parameterTypes
            param_count = len(param_types)

            method_name_query = f"method:{method.methodName}"
            param_count_query = f"methodSignatureParamsOrderedNodefault:{param_count}*"
            name_count_query = f"({method_name_query}) AND ({param_count_query})"

            query.append(f"({param_count_query})")
            if len(param_types) == 0:
                query.append(f"({name_count_query})^3")
            else:
                param_type_query = "methodSignatureParamsOrderedNodefault:*" + '*'.join(
                    [f"pt_{ptype}" for ptype in param_types]) + "*"
                name_type_query = f"({method_name_query}) AND ({param_type_query})"
                name_type_count_query = f"({method_name_query}) AND ({param_type_query}) AND ({param_count_query})"
                query.append(f"({param_type_query})")
                query.append(f"({name_count_query})^2")
                query.append(f"({name_type_query})^2")
                query.append(f"({name_type_count_query})^3")
            queries.append(" OR ".join(query))
        response = []
        for query in queries:
            response += self.solr.search(query)
        return response

    def search_matching_constructors(self, response):
        needed_constructors = set(f"{x['name'][0]}@{x['packagename'][0]}" for x in response if "name" in x.keys())
        for needed_constructor in needed_constructors:
            class_name, package_name = needed_constructor.split("@")
            response += self.solr.search(f"((method:__init__) OR (method:__new__)) AND (packagename:{package_name}) AND (name:{class_name})")
        return response

    def parse_solr_response(self, response):
        """
        Parses the Solr response and extracts relevant information to create FunctionSignature and ModuleUnderTest objects.
        As of now, only the first module is considered.
        """
        from backend.arena.adaptation import FunctionSignature, ModuleUnderTest

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

            # Extracting only the first possible datatype of a parameter
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
                classDict[moduleName][parentClass].append(functionSignature)
            else:
                functionSignatureDict[moduleName].append(functionSignature)

        allModulesUnderTest = []
        for moduleName in functionSignatureDict:
            print(moduleName)
            moduleUnderTest = ModuleUnderTest(
                moduleName, functionSignatureDict[moduleName], classDict[moduleName]
            )
            allModulesUnderTest.append(moduleUnderTest)

        print(f"Generated {len(allModulesUnderTest)} ModuleUnderTest objects.")

        return allModulesUnderTest

    def generate_modules_under_test(self, interface_spec):
        response = self.search_matching_methods(interface_spec)
        response += self.search_matching_constructors(response)
        modules_under_test = self.parse_solr_response(response)
        return modules_under_test

if __name__ == "__main__":
    from backend.lql.antlr_parser import parse_interface_spec

    lql_string = """
        Array {
            Array(list)->None
            mean()->float
            sum()->float
        }
        """
    interface_spec = parse_interface_spec(lql_string)
    solr_url = "http://localhost:8983/solr/lasso_quickstart"
    solr_conn = LassoSolrConnector(solr_url)
    modules_under_test = solr_conn.generate_modules_under_test(interface_spec)
    print(modules_under_test)