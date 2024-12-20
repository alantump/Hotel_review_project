import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.load import dumps, loads
from operator import itemgetter
from langchain_community.vectorstores import FAISS





import os
import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings

from langchain_community.vectorstores import FAISS



def save_vectorstore(hotel_reviews, data_name, local=True):
    # Merge the columns using string concatenation
    file_name = "Data/used_data.txt"
    index_path = f"Data/faiss_index/{data_name}/"

    hotel_reviews['MergedColumn'] = hotel_reviews.apply(
        lambda row: (
            f"Hotel: {row['Hotel_Name']}. "
            f"Positive Guest Review: {row['Positive_Review'] or 'No review available'}\n\n"
            f"Hotel: {row['Hotel_Name']}. "
            f"Negative Guest Review: {row['Negative_Review'] or 'No review available'}\n\n"
        ),
        axis=1
    )
    # Select the first 100 rows of the merged column
    used_data = hotel_reviews['MergedColumn'].dropna()
    
    # Save the data to a text file
    with open(file_name, 'w') as f:
        for line in used_data:
            f.write(line + '\n')
    
    # Load raw documents
    raw_documents = TextLoader(file_name).load()
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        separators=["\n\n"],
        chunk_size=400, 
        chunk_overlap=0
    )
    splits = text_splitter.split_documents(raw_documents)
    print(f"Make embeddings. Found splits:{len(splits)}")
    # Initialize embeddings
    if local:
        embeddings = OllamaEmbeddings(model="llama3")
    else:
        embeddings = OpenAIEmbeddings()


    # Check if the FAISS index already exists
    if not os.path.exists(index_path):
        # Create a new FAISS index from documents
        vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
        # Save the index to disk
        vectorstore.save_local(index_path)
    else:
        # Load the existing FAISS index
        vectorstore = FAISS.load_local(index_path, embeddings=embeddings, allow_dangerous_deserialization=True)
    
    # Use the vectorstore as a retriever
    retriever = vectorstore.as_retriever()
    
    return retriever










def get_retriever_faiss(index_path,local=True):
    if local:
        embeddings = OllamaEmbeddings(model="llama3")
    else:
        embeddings = OpenAIEmbeddings()

    vectorstore = FAISS.load_local(index_path, embeddings=embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever()
    print("Running retriever")
    return retriever


####


# Define a function to get unique union of documents
def get_unique_union(documents: list[list]):
    """ Unique union of retrieved docs """
    # Flatten list of lists, and convert each Document to string
    flattened_docs = [dumps(doc) for sublist in documents for doc in sublist]
    # Get unique documents
    print("Running get_unique_union")
    unique_docs = list(set(flattened_docs))
    # Return
    return [loads(doc) for doc in unique_docs]


def process_question(question,retriever):



    # Multi Query: Different Perspectives
    template = """You are an AI language model assistant. Your task is to generate five 
    different versions of the given user question to retrieve relevant documents from a vector 
    database. By generating multiple perspectives on the user question, your goal is to help
    the user overcome some of the limitations of the distance-based similarity search. 
    Provide these alternative questions separated by newlines. Please answer the question and provide a summary of the review your answer is based on. Original question: {question}"""
    prompt_perspectives = ChatPromptTemplate.from_template(template)

    # Generate queries
    generate_queries = (
        prompt_perspectives 
        | ChatOpenAI(temperature=0) 
        | StrOutputParser() 
        | (lambda x: x.split("\n"))
    )


    # Retrieve documents
    retrieval_chain = generate_queries | retriever.map() | get_unique_union

    # RAG
    template = """Answer the following question based on this context:

    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOpenAI(temperature=0)

    final_rag_chain = (
        {"context": retrieval_chain, 
         "question": itemgetter("question")} 
        | prompt
        | llm
        | StrOutputParser()
    )

    # Invoke the final chain and return the result
    return final_rag_chain.invoke({"question": question})


