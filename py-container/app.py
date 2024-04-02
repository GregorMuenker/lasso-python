# app.py
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    from upload import test_docs
    test_docs()
    return jsonify({'message': 'File uploaded successfully'})

@app.route('/docs', methods=['GET'])
def get_document():
    name = request.args.get('name')
    from getdoc import get_solr_documents_by_name
    return jsonify({'documents': get_solr_documents_by_name(name)})

@app.route('/fetch', methods=['GET'])
def fetch_data():
    # Handle data fetching logic here
    # Example: Fetch data from a database
    return jsonify({'data': 'Some fetched data'})

if __name__ == '__main__':
    app.run(debug=True, port=8000)
