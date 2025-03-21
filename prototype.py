import getpass
import os

os.environ["OPENAI_API_KEY"] = ""

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

os.environ["OPENAI_API_KEY"] = "sk-proj-Xivkve2M61eZ5JFApFaoT3BlbkFJLApMnH3bAr9DeP0Ff4t0"

# Load, chunk and index the contents of the PDFs in the /data_sources folder.
data_source_folder = "data_sources"
pdf_files = [file for file in os.listdir(data_source_folder) if file.endswith(".pdf")]

docs = []
for pdf_file in pdf_files:
    pdf_path = os.path.join(data_source_folder, pdf_file)
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

print("Welcome to the Disney Corporation Information Retrieval System!")
print("You can ask questions about Disney Corporation and John Doe's records.")
print("Type 'exit' to quit the program.")

chat_history = []

while True:
    query = input("\nEnter your question: ")

    if query.lower() == 'exit':
        print("Thank you for using the Disney Corporation Information Retrieval System. Goodbye!")
        break

    prompt = generate_prompt(chat_history, query)
    response = llm([prompt])

    print("\nAnswer:", response.content)

    chat_history.append((HumanMessage(content=query), AIMessage(content=response.content)))