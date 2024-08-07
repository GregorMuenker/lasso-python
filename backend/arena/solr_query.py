from adaptation import InterfaceSpecification
def translate_to_solr_query(interface_spec):
    queries = []
    
    # TODO handle queries for methods/constructors without parameters

    for method in interface_spec.methods:
        param_types = method.parameterTypes
        param_count = len(param_types)
        
        # Building the Solr query for the method
        param_query = " AND ".join([f"arguments.datatype:('{ptype}')" for ptype in param_types])
        # Fuzzy search for method name with similarity factor 0.8
        query = f"name:{method.methodName}~0.1 AND ({param_query})"
        
        # Adding an alternative query that matches the parameter count
        alt_query = f"name:{method.methodName}~0.1 AND count_positional_args:({param_count})"
        
        queries.append(f"({query}) OR ({alt_query})")

    for constructor in interface_spec.constructors:
        param_types = constructor.parameterTypes
        param_count = len(param_types)
        
        # Building the Solr query for the constructor
        param_query = " AND ".join([f"arguments.datatype:('{ptype}')" for ptype in param_types])
        # Fuzzy search for method name with similarity factor 0.8
        query = f"name:__init__ OR name:__new__ AND ({param_query})"
        
        # Adding an alternative query that matches the parameter count
        alt_query = f"(name:__init__ OR name:__new) AND count_positional_args:({param_count})"
        
        queries.append(f"({query}) OR ({alt_query})")

    # Combining all queries into one
    combined_query = " OR ".join(queries)
    
    # Adding the group by module part
    solr_query = f"{combined_query}&group=true&group.field=module"
    
    return solr_query

if __name__ == "__main__":
    from adaptation import MethodSignature
    import pysolr
    
    solr_url = "http://localhost:8983/solr/lasso_quickstart"
    solr = pysolr.Solr(solr_url)
    
    icubed = MethodSignature("convert_from_string", "str", ["int"])
    iminus = MethodSignature("asmatrix", "str", ["float", "int"])

    interfaceSpecification = InterfaceSpecification("Calculator", [], [icubed, iminus])

    solr_query = translate_to_solr_query(interfaceSpecification)
    print("QUERY:", solr_query)
    results = solr.search(solr_query)
    for result in results:
        print(result)
