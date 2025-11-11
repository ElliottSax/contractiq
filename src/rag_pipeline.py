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
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Import offline embeddings as fallback
try:
    from src.offline_embeddings import OfflineTfidfEmbeddings
except ImportError:
    from offline_embeddings import OfflineTfidfEmbeddings

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
        model_name: str = "claude-3-haiku-20240307",
        temperature: float = 0,
        provider: str = "claude"  # "claude", "gemini", or "openai"
    ):
        """
        Initialize the Healthcare Contract RAG system.

        Args:
            data_dir: Directory containing PDF documents
            chunk_size: Size of text chunks for splitting
            chunk_overlap: Overlap between consecutive chunks
            model_name: Model to use for QA (claude-3-haiku-20240307, gemini-pro, gpt-3.5-turbo)
            temperature: Temperature for LLM responses (0 = deterministic)
            provider: LLM provider - "claude", "gemini", or "openai"
        """
        # Load environment variables
        load_dotenv()

        self.provider = provider.lower()

        # Validate API key based on provider
        if self.provider == "claude":
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY not found in environment variables. "
                    "Please create a .env file with your Anthropic API key. "
                    "Get one at: https://console.anthropic.com/"
                )
        elif self.provider == "gemini":
            self.api_key = os.getenv("GOOGLE_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "GOOGLE_API_KEY not found in environment variables. "
                    "Please create a .env file with your Google API key. "
                    "Get one free at: https://makersuite.google.com/app/apikey"
                )
        elif self.provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "OPENAI_API_KEY not found in environment variables. "
                    "Please create a .env file with your OpenAI API key."
                )
        else:
            raise ValueError(f"Unsupported provider: {provider}. Use 'claude', 'gemini', or 'openai'.")

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
            logger.info(f"Creating embeddings using {self.provider} and building FAISS vector store")

            # Try to initialize embeddings based on provider
            use_offline = False
            try:
                if self.provider == "gemini":
                    self.embeddings = GoogleGenerativeAIEmbeddings(
                        model="models/embedding-001",
                        google_api_key=self.api_key
                    )
                elif self.provider == "claude":
                    # Claude uses Gemini embeddings (avoids SSL/network issues)
                    gemini_key = os.getenv("GOOGLE_API_KEY")
                    if gemini_key:
                        logger.info("Using Gemini embeddings for Claude provider")
                        self.embeddings = GoogleGenerativeAIEmbeddings(
                            model="models/embedding-001",
                            google_api_key=gemini_key
                        )
                    else:
                        # Fallback to OpenAI if Gemini key not available
                        openai_key = os.getenv("OPENAI_API_KEY")
                        if not openai_key:
                            raise ValueError(
                                "When using Claude, you need either GOOGLE_API_KEY or OPENAI_API_KEY for embeddings. "
                                "Add one to your .env file."
                            )
                        logger.info("Using OpenAI embeddings for Claude provider")
                        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_key)
                else:  # openai
                    self.embeddings = OpenAIEmbeddings(
                        openai_api_key=self.api_key
                    )

                # Try creating vector store with external API embeddings
                self.vectorstore = FAISS.from_documents(
                    documents=chunks,
                    embedding=self.embeddings
                )

            except Exception as api_error:
                error_str = str(api_error).lower()
                # Check if it's an SSL or network error
                if any(keyword in error_str for keyword in ['ssl', 'certificate', 'handshake', 'timeout', '503', 'unavailable']):
                    logger.warning(f"External API embeddings failed due to network/SSL issues: {api_error}")
                    logger.warning("Falling back to offline TF-IDF embeddings")
                    use_offline = True
                else:
                    # If it's not a network error, re-raise
                    raise

            # If external APIs failed, use offline embeddings
            if use_offline:
                self.embeddings = OfflineTfidfEmbeddings()
                self.vectorstore = FAISS.from_documents(
                    documents=chunks,
                    embedding=self.embeddings
                )
                logger.info("Vector store created successfully with offline TF-IDF embeddings")
            else:
                logger.info("Vector store created successfully with external API embeddings")

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
            # Use offline TF-IDF embeddings as they work in all environments
            if self.embeddings is None:
                logger.info("Using offline TF-IDF embeddings for loading vector store")
                self.embeddings = OfflineTfidfEmbeddings()

            # Try loading with the parameter first (newer versions)
            try:
                self.vectorstore = FAISS.load_local(
                    str(load_path),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            except TypeError:
                # Fall back to loading without the parameter (older versions)
                self.vectorstore = FAISS.load_local(
                    str(load_path),
                    self.embeddings
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

            # Initialize the language model based on provider
            if self.provider == "gemini":
                llm = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    temperature=self.temperature,
                    google_api_key=self.api_key,
                    convert_system_message_to_human=True
                )
            elif self.provider == "claude":
                llm = ChatAnthropic(
                    model=self.model_name,
                    temperature=self.temperature,
                    anthropic_api_key=self.api_key
                )
            else:  # openai
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
