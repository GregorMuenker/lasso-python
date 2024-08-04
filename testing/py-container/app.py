# app.py
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/testupload', methods=['POST'])
def upload_file():
    from upload import test_docs
    test_docs()
    return jsonify({'message': 'File uploaded successfully'})

@app.route('/testdocs', methods=['GET'])
def get_document():
    name = request.args.get('name')
    from getdoc import get_solr_documents_by_name
    return jsonify({'documents': get_solr_documents_by_name(name)})

@app.route('/docs', methods=['GET'])
def get_document():
    name = request.args.get('name')
    if name is not None:
        from solr_api import get_solr_documents_by_name
        return jsonify({'documents': get_solr_documents_by_name(name)})
    ret = request.args.get('return')
    if ret is not None:
        from solr_api import get_solr_documents_by_return
        return jsonify({'documents': get_solr_documents_by_return(ret)})

@app.route('/add', methods=['POST'])
def upload_file():
    doc = request.json
    from solr_api import upload_doc_obj
    upload_doc_obj(doc)
    return jsonify({'message': 'Doc uploaded successfully'})

@app.route('/fetch', methods=['GET'])
def fetch_data():
    # Handle data fetching logic here
    # Example: Fetch data from a database
    return jsonify({'data': 'Some fetched data'})

if __name__ == '__main__':
    app.run(debug=True, port=8000)
