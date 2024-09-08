from mbpp_query import query_solr_for_methods


def create_sequence_sheet(method_names):
    sequence_sheet = {"methods": []}

    for method_name in method_names:
        result = query_solr_for_methods(method_name)
        if "response" in result and "docs" in result["response"]:
            for doc in result["response"]["docs"]:
                sequence_sheet["methods"].append(
                    {"method": doc["code"], "test_cases": doc["test_cases"]}
                )

    return sequence_sheet


if __name__ == "__main__":
    method_names = ["add_numbers", "multiply_numbers"]
    sheet = create_sequence_sheet(method_names)
    print(sheet)
    print(sheet)
