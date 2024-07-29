import os
import pysolr

solr_url = "http://lasso_solr_quickstart:8983/solr/lasso_quickstart"

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
    
def get_solr_documents_by_return(document_return):
    """
    Retrieves Solr documents based on their return type.

    Args:
        document_return (str): Return type of the document to search for.

    Returns:
        list: List of matching documents.
    """
    try:
        # Initialize the Solr client
        solr = pysolr.Solr(solr_url)

        # Query for documents with the specified name
        query = f'retrun:"{document_return}"'
        results = solr.search(query)

        # Extract relevant information from the results
        matching_documents = []
        for result in results:
            matching_documents.append(result)

        return matching_documents

    except Exception as e:
        print(f"Error retrieving Solr documents: {e}")
        return []
    
def upload_doc_obj(doc):
    
    # Initialize the Solr client
    solr = pysolr.Solr(solr_url, always_commit=True)
    solr.add([doc])
    
    print(f"Uploaded doc to Solr core 'lasso_quickstart'.")
    
def upload_docs_arr(docs):
    
    # Initialize the Solr client
    solr = pysolr.Solr(solr_url, always_commit=True)
    solr.add(docs)
    
    print(f"Uploaded docs to Solr core 'lasso_quickstart'.")