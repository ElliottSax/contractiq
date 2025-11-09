"""
Healthcare Contract Analysis RAG Pipeline

This module provides a complete RAG (Retrieval-Augmented Generation) pipeline
for analyzing healthcare payer contracts. It loads PDF documents, processes them
into chunks, creates embeddings, and enables question-answering capabilities.
"""

import os
import logging
from typing import List, Optional
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HealthcareContractRAG:
    """
    A RAG system specialized for healthcare contract analysis.

    This class handles the complete pipeline from document loading to
    question answering about healthcare payer contracts.
    """

    def __init__(
        self,
        data_dir: str = "data",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0
    ):
        """
        Initialize the Healthcare Contract RAG system.

        Args:
            data_dir: Directory containing PDF documents
            chunk_size: Size of text chunks for splitting
            chunk_overlap: Overlap between consecutive chunks
            model_name: OpenAI model to use for QA
            temperature: Temperature for LLM responses (0 = deterministic)
        """
        # Load environment variables
        load_dotenv()

        # Validate OpenAI API key
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables. "
                "Please create a .env file with your OpenAI API key."
            )

        self.data_dir = Path(data_dir)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.model_name = model_name
        self.temperature = temperature

        # Initialize components
        self.embeddings = None
        self.vectorstore = None
        self.qa_chain = None

        logger.info("HealthcareContractRAG initialized")

    def load_documents(self) -> List:
        """
        Load PDF documents from the data directory.

        Returns:
            List of loaded documents

        Raises:
            FileNotFoundError: If data directory doesn't exist
            ValueError: If no PDF files are found
        """
        try:
            if not self.data_dir.exists():
                raise FileNotFoundError(
                    f"Data directory '{self.data_dir}' not found. "
                    f"Please create it and add PDF files."
                )

            logger.info(f"Loading PDF documents from {self.data_dir}")

            # Use DirectoryLoader for batch PDF loading
            loader = DirectoryLoader(
                str(self.data_dir),
                glob="**/*.pdf",
                loader_cls=PyPDFLoader,
                show_progress=True
            )

            documents = loader.load()

            if not documents:
                raise ValueError(
                    f"No PDF files found in {self.data_dir}. "
                    f"Please add healthcare contract PDFs to this directory."
                )

            logger.info(f"Successfully loaded {len(documents)} document pages")
            return documents

        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
            raise

    def split_documents(self, documents: List) -> List:
        """
        Split documents into chunks for processing.

        Args:
            documents: List of documents to split

        Returns:
            List of document chunks
        """
        try:
            logger.info(
                f"Splitting documents into chunks "
                f"(size={self.chunk_size}, overlap={self.chunk_overlap})"
            )

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )

            chunks = text_splitter.split_documents(documents)
            logger.info(f"Created {len(chunks)} text chunks")

            return chunks

        except Exception as e:
            logger.error(f"Error splitting documents: {str(e)}")
            raise

    def create_vectorstore(self, chunks: List) -> FAISS:
        """
        Create a FAISS vector store from document chunks.

        Args:
            chunks: List of document chunks

        Returns:
            FAISS vector store
        """
        try:
            logger.info("Creating embeddings and building FAISS vector store")

            # Initialize OpenAI embeddings
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=self.api_key
            )

            # Create FAISS vector store
            self.vectorstore = FAISS.from_documents(
                documents=chunks,
                embedding=self.embeddings
            )

            logger.info("Vector store created successfully")
            return self.vectorstore

        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            raise

    def save_vectorstore(self, save_path: str = "outputs/vectorstore") -> None:
        """
        Save the vector store to disk for reuse.

        Args:
            save_path: Path to save the vector store
        """
        try:
            if self.vectorstore is None:
                raise ValueError("No vector store to save. Please build the pipeline first.")

            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)

            self.vectorstore.save_local(str(save_path))
            logger.info(f"Vector store saved to {save_path}")

        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}")
            raise

    def load_vectorstore(self, load_path: str = "outputs/vectorstore") -> None:
        """
        Load a previously saved vector store.

        Args:
            load_path: Path to the saved vector store
        """
        try:
            load_path = Path(load_path)

            if not load_path.exists():
                raise FileNotFoundError(f"Vector store not found at {load_path}")

            # Initialize embeddings if not already done
            if self.embeddings is None:
                self.embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)

            self.vectorstore = FAISS.load_local(
                str(load_path),
                self.embeddings,
                allow_dangerous_deserialization=True
            )

            logger.info(f"Vector store loaded from {load_path}")

        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            raise

    def create_qa_chain(self) -> RetrievalQA:
        """
        Create a question-answering chain using the vector store.

        Returns:
            RetrievalQA chain
        """
        try:
            if self.vectorstore is None:
                raise ValueError(
                    "No vector store available. Please build or load the pipeline first."
                )

            logger.info("Creating QA chain")

            # Create custom prompt for healthcare contracts
            template = """You are a healthcare contract analysis expert. Use the following pieces of context from healthcare payer contracts to answer the question. Focus on specific details about reimbursement rates, payment terms, and contract clauses.

If you don't know the answer based on the context, say so clearly. Do not make up information.

Context: {context}

Question: {question}

Answer: Let me analyze the contract information:"""

            QA_PROMPT = PromptTemplate(
                template=template,
                input_variables=["context", "question"]
            )

            # Initialize the language model
            llm = ChatOpenAI(
                model_name=self.model_name,
                temperature=self.temperature,
                openai_api_key=self.api_key
            )

            # Create retrieval QA chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(
                    search_kwargs={"k": 4}  # Retrieve top 4 relevant chunks
                ),
                return_source_documents=True,
                chain_type_kwargs={"prompt": QA_PROMPT}
            )

            logger.info("QA chain created successfully")
            return self.qa_chain

        except Exception as e:
            logger.error(f"Error creating QA chain: {str(e)}")
            raise

    def ask_question(self, question: str) -> dict:
        """
        Ask a question about the healthcare contracts.

        Args:
            question: Question to ask

        Returns:
            Dictionary with answer and source documents
        """
        try:
            if self.qa_chain is None:
                raise ValueError(
                    "QA chain not initialized. Please build the pipeline first."
                )

            logger.info(f"Processing question: {question}")

            response = self.qa_chain.invoke({"query": question})

            return {
                "question": question,
                "answer": response["result"],
                "source_documents": response["source_documents"]
            }

        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            raise

    def build_pipeline(self, save_vectorstore: bool = True) -> None:
        """
        Build the complete RAG pipeline from scratch.

        Args:
            save_vectorstore: Whether to save the vector store to disk
        """
        try:
            logger.info("Building RAG pipeline...")

            # Step 1: Load documents
            documents = self.load_documents()

            # Step 2: Split into chunks
            chunks = self.split_documents(documents)

            # Step 3: Create vector store
            self.create_vectorstore(chunks)

            # Step 4: Save vector store if requested
            if save_vectorstore:
                self.save_vectorstore()

            # Step 5: Create QA chain
            self.create_qa_chain()

            logger.info("RAG pipeline built successfully!")

        except Exception as e:
            logger.error(f"Error building pipeline: {str(e)}")
            raise
