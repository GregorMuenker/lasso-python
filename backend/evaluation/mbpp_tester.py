def run_test_cases(data):
    for problem in data:
        method_name = problem["code"].split("(")[0].split()[1]
        exec(problem["code"])

        for test_case in problem["test_cases"]:
            try:
                result = eval(f"{method_name}(*{test_case['input']})")
                if result == test_case["output"]:
                    print(
                        f"Test passed for {method_name} with input {test_case['input']}"
                    )
                else:
                    print(
                        f"Test failed for {method_name} with input {test_case['input']}. Expected {test_case['output']} but got {result}"
                    )
            except Exception as e:
                print(f"Error in method {method_name}: {e}")


if __name__ == "__main__":
    from mbpp_loader import load_mbpp_data

    mbpp_data = load_mbpp_data("mbpp.jsonl")
    run_test_cases(mbpp_data)
