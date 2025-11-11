"""
Weaviate-based RAG with Hybrid Search

This module provides a RAG implementation using Weaviate for hybrid search,
combining semantic vector search with keyword (BM25) search for better
retrieval accuracy on healthcare contracts.
"""

import os
import logging
from typing import List, Dict, Optional
from pathlib import Path
import weaviate
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeaviateHealthcareRAG:
    """
    Healthcare Contract RAG system using Weaviate for hybrid search.

    Features:
    - Hybrid search (semantic + BM25 keyword matching)
    - Metadata filtering by payer name
    - Alpha parameter tuning for search balance
    - Optimized for healthcare domain (CPT codes, rates, policies)
    """

    def __init__(
        self,
        weaviate_url: Optional[str] = None,
        weaviate_api_key: Optional[str] = None,
        llm_provider: str = "claude",
        llm_model: str = "claude-3-haiku-20240307",
        alpha: float = 0.7,  # Hybrid search balance (0.7 = 70% semantic, 30% keyword)
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        """
        Initialize Weaviate Healthcare RAG system.

        Args:
            weaviate_url: Weaviate cluster URL (defaults to env var)
            weaviate_api_key: Weaviate API key (defaults to env var)
            llm_provider: LLM provider ("claude", "openai", "gemini")
            llm_model: Model name
            alpha: Hybrid search balance (0.0=keyword, 1.0=semantic, 0.7=recommended)
            chunk_size: Document chunk size
            chunk_overlap: Overlap between chunks
        """
        load_dotenv()

        # Weaviate configuration
        self.weaviate_url = weaviate_url or os.getenv("WEAVIATE_URL")
        self.weaviate_api_key = weaviate_api_key or os.getenv("WEAVIATE_API_KEY")

        if not self.weaviate_url:
            raise ValueError(
                "WEAVIATE_URL not found. Please set it in .env or pass as parameter.\n"
                "Get your URL from: https://console.weaviate.cloud/"
            )

        # LLM configuration
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        # Search configuration
        self.alpha = alpha  # 0.7 = 70% semantic, 30% keyword
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Initialize components
        self.client = None
        self.llm = None
        self.qa_chain = None
        self.class_name = "HealthcareContract"

        logger.info(f"WeaviateHealthcareRAG initialized with alpha={alpha}")

    def connect(self) -> bool:
        """
        Connect to Weaviate cluster.

        Returns:
            bool: True if connected successfully
        """
        try:
            logger.info(f"Connecting to Weaviate at {self.weaviate_url}...")

            # Connect with or without API key
            if self.weaviate_api_key:
                self.client = weaviate.Client(
                    url=self.weaviate_url,
                    auth_client_secret=weaviate.AuthApiKey(api_key=self.weaviate_api_key)
                )
            else:
                # Local Weaviate without auth
                self.client = weaviate.Client(url=self.weaviate_url)

            # Test connection
            if self.client.is_ready():
                logger.info("✅ Successfully connected to Weaviate!")
                return True
            else:
                logger.error("❌ Weaviate cluster is not ready")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to connect to Weaviate: {str(e)}")
            return False

    def create_schema(self) -> bool:
        """
        Create Weaviate schema for healthcare contracts.

        Schema includes:
        - text: Document content
        - payer: Payer name (United Healthcare, Aetna, Blue Cross)
        - source: Source file name
        - page: Page number
        """
        try:
            # Check if schema already exists
            existing_schema = self.client.schema.get()
            existing_classes = [c['class'] for c in existing_schema.get('classes', [])]

            if self.class_name in existing_classes:
                logger.info(f"Schema '{self.class_name}' already exists")
                return True

            logger.info(f"Creating schema '{self.class_name}'...")

            schema = {
                "class": self.class_name,
                "description": "Healthcare payer contract documents",
                "vectorizer": "none",  # We'll provide vectors or use text2vec module
                "properties": [
                    {
                        "name": "text",
                        "dataType": ["text"],
                        "description": "Contract text content",
                        "moduleConfig": {
                            "text2vec-transformers": {
                                "skip": False,
                                "vectorizePropertyName": False
                            }
                        }
                    },
                    {
                        "name": "payer",
                        "dataType": ["string"],
                        "description": "Payer name (United Healthcare, Aetna, Blue Cross)",
                        "moduleConfig": {
                            "text2vec-transformers": {
                                "skip": True
                            }
                        }
                    },
                    {
                        "name": "source",
                        "dataType": ["string"],
                        "description": "Source PDF file name"
                    },
                    {
                        "name": "page",
                        "dataType": ["int"],
                        "description": "Page number in source document"
                    }
                ]
            }

            self.client.schema.create_class(schema)
            logger.info(f"✅ Schema '{self.class_name}' created successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to create schema: {str(e)}")
            return False

    def load_and_chunk_documents(self, data_dir: str = "data") -> List[Dict]:
        """
        Load PDF documents and split into chunks with metadata.

        Returns:
            List of document chunks with metadata
        """
        try:
            logger.info(f"Loading documents from {data_dir}...")

            # Load PDFs
            loader = DirectoryLoader(
                data_dir,
                glob="**/*.pdf",
                loader_cls=PyPDFLoader,
                show_progress=True
            )
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} document pages")

            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len
            )
            chunks = text_splitter.split_documents(documents)
            logger.info(f"Created {len(chunks)} chunks")

            # Add metadata (extract payer from filename)
            processed_chunks = []
            for chunk in chunks:
                source = chunk.metadata.get('source', '')
                filename = Path(source).stem

                # Extract payer name from filename
                payer = "Unknown"
                if "united_healthcare" in filename.lower():
                    payer = "United Healthcare"
                elif "aetna" in filename.lower():
                    payer = "Aetna"
                elif "blue_cross" in filename.lower():
                    payer = "Blue Cross"

                processed_chunks.append({
                    "text": chunk.page_content,
                    "payer": payer,
                    "source": filename,
                    "page": chunk.metadata.get('page', 0)
                })

            return processed_chunks

        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
            raise

    def upload_documents(self, chunks: List[Dict]) -> bool:
        """
        Upload document chunks to Weaviate.

        Args:
            chunks: List of document chunks with metadata

        Returns:
            bool: True if upload successful
        """
        try:
            logger.info(f"Uploading {len(chunks)} chunks to Weaviate...")

            with self.client.batch as batch:
                batch.batch_size = 100

                for i, chunk in enumerate(chunks):
                    if (i + 1) % 10 == 0:
                        logger.info(f"  Uploaded {i + 1}/{len(chunks)} chunks...")

                    properties = {
                        "text": chunk["text"],
                        "payer": chunk["payer"],
                        "source": chunk["source"],
                        "page": chunk["page"]
                    }

                    batch.add_data_object(
                        data_object=properties,
                        class_name=self.class_name
                    )

            logger.info(f"✅ Successfully uploaded {len(chunks)} chunks!")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to upload documents: {str(e)}")
            return False

    def hybrid_search(
        self,
        query: str,
        alpha: Optional[float] = None,
        limit: int = 4,
        payer_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Perform hybrid search (semantic + keyword).

        Args:
            query: Search query
            alpha: Hybrid search balance (defaults to self.alpha)
            limit: Number of results
            payer_filter: Filter by payer name (e.g., "United Healthcare")

        Returns:
            List of search results with content and metadata
        """
        try:
            alpha = alpha if alpha is not None else self.alpha

            logger.info(f"Hybrid search (alpha={alpha}): {query[:60]}...")

            # Build query
            query_builder = (
                self.client.query
                .get(self.class_name, ["text", "payer", "source", "page"])
                .with_hybrid(
                    query=query,
                    alpha=alpha  # 0.7 = 70% semantic, 30% keyword
                )
                .with_limit(limit)
            )

            # Add payer filter if specified
            if payer_filter:
                where_filter = {
                    "path": ["payer"],
                    "operator": "Equal",
                    "valueString": payer_filter
                }
                query_builder = query_builder.with_where(where_filter)
                logger.info(f"  Filtering by payer: {payer_filter}")

            # Execute query
            result = query_builder.do()

            # Extract results
            objects = result.get("data", {}).get("Get", {}).get(self.class_name, [])

            logger.info(f"  Found {len(objects)} results")

            return objects

        except Exception as e:
            logger.error(f"Error in hybrid search: {str(e)}")
            return []

    def initialize_llm(self):
        """Initialize the LLM for question answering."""
        try:
            logger.info(f"Initializing {self.llm_provider} LLM...")

            if self.llm_provider == "claude":
                if not self.anthropic_api_key:
                    raise ValueError("ANTHROPIC_API_KEY not found in .env")

                self.llm = ChatAnthropic(
                    model=self.llm_model,
                    temperature=0,
                    anthropic_api_key=self.anthropic_api_key
                )

            logger.info("✅ LLM initialized successfully!")

        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            raise

    def ask_question(
        self,
        question: str,
        alpha: Optional[float] = None,
        payer_filter: Optional[str] = None
    ) -> Dict:
        """
        Ask a question and get an answer using hybrid search + LLM.

        Args:
            question: Question to ask
            alpha: Hybrid search balance (defaults to self.alpha)
            payer_filter: Filter by payer name

        Returns:
            dict: Answer and source documents
        """
        try:
            # Initialize LLM if not already done
            if not self.llm:
                self.initialize_llm()

            # Retrieve relevant contexts using hybrid search
            results = self.hybrid_search(
                query=question,
                alpha=alpha,
                limit=4,
                payer_filter=payer_filter
            )

            if not results:
                return {
                    "answer": "I couldn't find relevant information in the contracts to answer this question.",
                    "sources": []
                }

            # Prepare context from retrieved documents
            context = "\n\n".join([
                f"[{r['payer']} - {r['source']} p.{r['page']}]\n{r['text']}"
                for r in results
            ])

            # Create prompt
            prompt = f"""You are an expert healthcare contract analyst. Answer the question based on the provided contract excerpts.

Contract Information:
{context}

Question: {question}

Instructions:
- Answer based ONLY on the provided contract information
- Be specific with dollar amounts, CPT codes, and payer names
- If comparing payers, provide exact numbers
- If information is not in the contracts, say so
- Cite sources by payer name when possible

Answer:"""

            # Get answer from LLM
            response = self.llm.invoke(prompt)
            answer = response.content if hasattr(response, 'content') else str(response)

            return {
                "answer": answer,
                "sources": results,
                "context": context
            }

        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return {
                "answer": f"Error: {str(e)}",
                "sources": []
            }

    def get_stats(self) -> Dict:
        """Get statistics about the Weaviate database."""
        try:
            result = self.client.query.aggregate(self.class_name).with_meta_count().do()
            total_objects = result.get("data", {}).get("Aggregate", {}).get(self.class_name, [{}])[0].get("meta", {}).get("count", 0)

            # Get payer breakdown
            payer_result = self.client.query.aggregate(self.class_name).with_group_by_filter(["payer"]).with_meta_count().do()

            return {
                "total_chunks": total_objects,
                "class_name": self.class_name,
                "alpha": self.alpha,
                "status": "ready"
            }

        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {"error": str(e)}


if __name__ == "__main__":
    # Test Weaviate connection
    print("Testing Weaviate Healthcare RAG...")

    rag = WeaviateHealthcareRAG(alpha=0.7)

    if rag.connect():
        print("✅ Connection successful!")
        stats = rag.get_stats()
        print(f"Stats: {stats}")
    else:
        print("❌ Connection failed")
        print("Please check your WEAVIATE_URL and WEAVIATE_API_KEY in .env")
