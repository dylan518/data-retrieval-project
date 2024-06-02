from flask import Flask, request, jsonify
import boto3
import os
import openai
import PyPDF2

app = Flask(__name__)

# Configure AWS S3
s3 = boto3.client('s3')
BUCKET_NAME = 'your-bucket-name'

# Configure OpenAI API
openai.api_key = 'your-openai-api-key'

# Route for uploading PDFs
@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Upload PDF to S3 bucket
    s3.upload_fileobj(file, BUCKET_NAME, file.filename)
    
    return jsonify({'message': 'PDF uploaded successfully'}), 200

# Route for listing uploaded PDFs
@app.route('/pdfs', methods=['GET'])
def list_pdfs():
    # Retrieve list of PDFs from S3 bucket
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    pdfs = [obj['Key'] for obj in response.get('Contents', [])]
    
    return jsonify({'pdfs': pdfs}), 200

# Route for processing search queries
@app.route('/search', methods=['POST'])
def search_pdfs():
    query = request.json['query']
    
    # Retrieve list of PDFs from S3 bucket
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    pdfs = [obj['Key'] for obj in response.get('Contents', [])]
    
    results = []
    for pdf_name in pdfs:
        # Download PDF from S3 bucket
        pdf_object = s3.get_object(Bucket=BUCKET_NAME, Key=pdf_name)
        pdf_content = pdf_object['Body'].read()
        
        # Extract text from PDF
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        # Generate embeddings using OpenAI API
        embeddings = openai.Embedding.create(
            input=text,
            model='text-embedding-ada-002'
        )
        
        # Perform similarity search using embeddings
        similarity = cosine_similarity(embeddings, query)
        
        if similarity > 0.8:  # Adjust the threshold as needed
            results.append({'pdf': pdf_name, 'similarity': similarity})
    
    # Sort results by similarity score
    results = sorted(results, key=lambda x: x['similarity'], reverse=True)
    
    return jsonify({'results': results}), 200

if __name__ == '__main__':
    app.run() 