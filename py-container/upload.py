import os
import re
import pysolr

# Define the path to your text file
text_file_path = "./file.txt"

# Read the entire text file
with open(text_file_path, "r") as file:
    content = file.read()

# Split the content into chunks based on two consecutive newlines
chunks = content.split("\n\n\n")

# Initialize the Solr client
solr_url = "http://localhost:8983/solr/lasso_quickstart"
solr = pysolr.Solr(solr_url, always_commit=True)

# Regular expression pattern to match content within parentheses
pattern = r"\((.*?)\)"

# Upload each eligible chunk to Solr
for i, chunk in enumerate(chunks, start=1):
    # Check if the chunk starts with "def"
    if chunk.strip().startswith("def"):
        # Extract the first line as the signature
        # Extract the content within parentheses
        match = re.search(pattern, chunk)
        if match:
            input_value = match.group(1)
        # Extract the name before the opening parenthesis
        name = chunk.split("(")[0].strip()
        first_line = chunk.split("\n", 1)[0]
        # Create a Solr document for each eligible chunk
        doc = {"id": f"chunk_{i}", "raw": chunk, "signature": first_line[4:], "input": input_value, "name": name[4:]}
        solr.add([doc])

print(f"Uploaded {len(chunks)} chunks to Solr core 'lasso_quickstart'.")