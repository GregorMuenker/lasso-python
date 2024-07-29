import os
import pysolr

solr_url = "http://localhost:8983/solr/lasso_quickstart"

def get_solr_documents_by_name(document_name):
    """
    Retrieves Solr documents based on their name.

    Args:
        document_name (str): Name of the document to search for.

    Returns:
        list: List of matching documents.
    """
    try:
        # Initialize the Solr client
        solr = pysolr.Solr(solr_url)

        # Query for documents with the specified name
        query = f'name:"{document_name}"'
        results = solr.search(query)

        # Extract relevant information from the results
        matching_documents = []
        for result in results:
            matching_documents.append(result)

        return matching_documents

    except Exception as e:
        print(f"Error retrieving Solr documents: {e}")
        return []

# Example usage
if __name__ == "__main__":
    document_name = "process"
    matching_docs = get_solr_documents_by_name(document_name)
    if matching_docs:
        print(f"Found {len(matching_docs)} documents with name '{document_name}':")
        for doc in matching_docs:
            print(f"Document ID: {doc['id']}")
            print(f"Raw content: {doc['raw']}")
    else:
        print(f"No documents found with name '{document_name}'.")
