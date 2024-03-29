import pysolr
import os

if 'DOCKER' not in os.environ:
    from dotenv import load_dotenv
    load_dotenv()

# Create a client instance.
solr_path = os.getenv("SOLR_PATH")

solr = pysolr.Solr(solr_path + 'lasso_quickstart', timeout=10)

docs = [
    {
        "id": "doc_1",
        "title": "A test document",
    },
    {
        "id": "doc_2",
        "title": "The Banana: Tasty or Dangerous?",
    },
]

solr.add(docs)
