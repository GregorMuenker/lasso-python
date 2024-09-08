import json


def load_mbpp_data(file_path):
    data = []
    with open(file_path, "r") as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data


if __name__ == "__main__":
    mbpp_data = load_mbpp_data("mbpp.jsonl")
    print(mbpp_data)
