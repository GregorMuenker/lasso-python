#import json


#from sequence_specification import SequenceSpecification

#sequenceSpecification = SequenceSpecification("calc4_demo.xlsx")
#print(sequenceSpecification.statements)
#print(sequenceSpecification.resolve_reference("A2"))

#sequence_spec = SequenceSpecification("calc6_greg.xlsx")
#print(sequence_spec.statements, flush=True)
#print(sequence_spec.resolve_reference("A2"), flush=True)

# Open the evaluation sanitized JSON file
# with open('./evaluation_sanitized-mbpp.json') as file:
#     data = json.load(file)

# Count the elements in the JSON file
# count = len(data)

# print(f"There are {count} elements in the evaluation sanitized JSON file.")

# element_with_max_product = None
# index = 0
# for element in data:
#     if 'max_Product' in element.get('code', ''):
#         element_with_max_product = element
#         print(f"Element with 'max_Product' found at index {index}.")
#         break
#     index += 1

# if element_with_max_product:
#     print("Element with 'max_Product' in code:", element_with_max_product)
# else:
#     print("No element with 'max_Product' found in code.")


from pyignite import Client

client = Client(compact_footer=False)
client.connect('localhost', 10800)