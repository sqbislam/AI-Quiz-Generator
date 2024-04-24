import sys
import os
import streamlit as st
import chromadb

from app.embedding_client import EmbeddingClient
sys.path.append(os.path.abspath('../../'))
from app.document_processor import DocumentProcessor
from constants import CONFIG


# Import Task libraries
from langchain_core.documents import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma

class ChromaCollectionCreator:
    def __init__(self, processor, embed_model):
        """
        Initializes the ChromaCollectionCreator with a DocumentProcessor instance and embeddings configuration.
        :param processor: An instance of DocumentProcessor that has processed documents.
        :param embeddings_config: An embedding client for embedding documents.
        """
        self.processor = processor      
        self.embed_model = embed_model  
        self.db = None                 
    def as_retriever(self):
        if(self.db is None):
            raise ValueError("No DB initialized")
        
        return self.db.as_retriever()
    def create_chroma_collection(self):
        """
        Task: Create a Chroma collection from the documents processed by the DocumentProcessor instance.
        
        Steps:
        1. Check if any documents have been processed by the DocumentProcessor instance. If not, display an error message using streamlit's error widget.
        
        2. Split the processed documents into text chunks suitable for embedding and indexing. Use the CharacterTextSplitter from Langchain to achieve
        
        3. Create a Chroma collection in memory with the text chunks obtained from step 2 and the embeddings model initialized in the class.
   
        """
        
        # Step 1: Check for processed documents
        if len(self.processor.pages) == 0:
            st.error("No documents found!", icon="🚨")
            return

        # Step 2: Split documents into text chunks
        text_splitter = CharacterTextSplitter(
            separator=" ",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )
        texts=text_splitter.split_documents(self.processor.pages)
        if texts is not None:
            st.success(f"Successfully split pages to {len(texts)} documents!", icon="✅")

        # Step 3: Create the Chroma Collection
   
        # Add persistent client to use stored db
        client = chromadb.PersistentClient(path="../../cache/.chroma")
        self.db = Chroma.from_documents(texts, self.embed_model, client=client, persist_directory='../../cache/.chroma')
        
        if self.db:
            st.success("Successfully created Chroma Collection!", icon="✅")
        else:
            st.error("Failed to create Chroma Collection!", icon="🚨")
    
    def query_chroma_collection(self, query) -> Document:
        """
        Queries the created Chroma collection for documents similar to the query.
        :param query: The query string to search for in the Chroma collection.
        
        Returns the first matching document from the collection with similarity score.
        """
        if self.db:
            docs = self.db.similarity_search_with_relevance_scores(query)
            if docs:
                return docs[0]
            else:
                st.error("No matching documents found!", icon="🚨")
        else:
            st.error("Chroma Collection has not been created!", icon="🚨")

