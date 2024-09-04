from backend.arena.adaptation import InterfaceSpecification


def translate_to_solr_queries(interface_spec):
    queries = []

    for constructor in interface_spec.constructors:
        query = []
        param_types = constructor.parameterTypes
        param_count = len(param_types)

        method_name_query = f"(method:__init__)^3 or (method:__new__)"
        param_count_query = f"methodSignatureParamsOrderedNodefault:{param_count}*"

        query.append(f"({param_count_query})")
        if len(param_types) != 0:
            param_type_query = "methodSignatureParamsOrderedNodefault:*" + '*'.join(
                [f"pt_{ptype}" for ptype in param_types]) + "*"
            type_count_query = f"({param_type_query}) AND ({param_count_query})"
            query.append(f"({param_type_query})")
            query.append(f"({type_count_query})^2")
        queries.append(f"({method_name_query}) AND ({' OR '.join(query)})")

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
    return queries

if __name__ == "__main__":
    from adaptation import MethodSignature
    import pysolr
    
    solr_url = "http://localhost:8983/solr/lasso_quickstart"
    solr = pysolr.Solr(solr_url)
    
    icubed = MethodSignature("convert_from_string", "str", ["int"])
    iminus = MethodSignature("asmatrix", "str", ["float", "int"])

    interfaceSpecification = InterfaceSpecification("Calculator", [], [icubed, iminus])

    solr_query = translate_to_solr_queries(interfaceSpecification)
    print("QUERY:", solr_query)
    results = solr.search(solr_query)
    for result in results:
        print(result)
