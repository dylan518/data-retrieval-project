import os
from flask import Flask, request, jsonify, request, render_template
from werkzeug.utils import secure_filename
from langchain import hub
from langchain_chroma import Chroma
from langchain.document_loaders import PyPDFLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage
import logging
logging.basicConfig(level=logging.DEBUG)

os.environ["OPENAI_API_KEY"] = "sk-proj-Xivkve2M61eZ5JFApFaoT3BlbkFJLApMnH3bAr9DeP0Ff4t0"

app = Flask(__name__)
app = Flask(__name__)

# Configure the upload directory
UPLOAD_FOLDER = 'data_sources'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Load, chunk and index the contents of the PDFs in the /data_sources folder.

pdf_files = [file for file in os.listdir(UPLOAD_FOLDER) if file.endswith(".pdf")]

docs = []
for pdf_file in pdf_files:
    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_file)
    loader = PyPDFLoader(file_path=pdf_path)
    docs.extend(loader.load())

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)
vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

# Retrieve and generate using the relevant snippets of the PDFs.
retriever = vectorstore.as_retriever()

def generate_prompt(chat_history, question):
    context = retriever.get_relevant_documents(question)
    formatted_context = "\n".join([doc.page_content for doc in context])

    chat_history_str = "\n".join([f"John Doe: {q.content}\nAI Assistant: {a.content}" for q, a in chat_history])

    template = f"""
You are an AI assistant trained to provide detailed and informative answers to questions from John Doe about Disney Corporation and the company's records on John Doe. Use the following retrieved information and the previous chat history to answer the question thoroughly. If the context doesn't contain enough information to answer the question, indicate that more information is needed.

Chat History:
{chat_history_str}

Current Question: {question}

Context:
{formatted_context}

Answer:
"""

    return HumanMessage(content=template)

llm = ChatOpenAI(model="gpt-4o")

chat_history = []

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    global chat_history
    chat_history = []
    return jsonify({"message": "Chat history cleared"})

@app.route('/query', methods=['POST'])
def query_llm():
    global chat_history
    query = request.json['query']

    prompt = generate_prompt(chat_history, query)
    response = llm([prompt])

    chat_history.append((HumanMessage(content=query), AIMessage(content=response.content)))

    return jsonify({"response": response.content})

@app.route('/get_chat', methods=['GET'])
def get_chat():
    global chat_history
    chat_data = [
        {
            "role": "user",
            "content": message.content
        } if isinstance(message, HumanMessage) else {
            "role": "assistant",
            "content": message.content
        }
        for message, _ in chat_history
    ]

    return jsonify({"chat_history": chat_data})



# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({"message": "File uploaded successfully"}), 200
    else:
        return jsonify({"message": "Invalid file type"}), 400

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)