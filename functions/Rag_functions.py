import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.load import dumps, loads
from operator import itemgetter
from langchain_community.vectorstores import FAISS

###### Preprcess
#import streamlit as st
#@st.cache_data
def get_retriever(folder_path):
    vectorstore = Chroma(persist_directory=folder_path, embedding_function=OpenAIEmbeddings())
    retriever = vectorstore.as_retriever()
    print("Running retriever")
    return retriever

#folder_path = "./Chroma/chroma_db_reviews_crete_merged3"
#retriever = get_retriever(folder_path)
####

def get_retriever_faiss(index_path):
    vectorstore = FAISS.load_local(index_path, embeddings=OpenAIEmbeddings(), allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever()
    print("Running retriever")
    return retriever

index_path = "./faiss_index"
retriever = get_retriever_faiss(index_path)
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


def process_question(question):



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
