# Healthcare Contract Analysis System

A production-ready RAG (Retrieval-Augmented Generation) system for analyzing healthcare payer contracts. This system uses LangChain, OpenAI embeddings, and FAISS vector storage to provide intelligent question-answering capabilities about reimbursement rates, payment terms, and contract clauses.

## Features

- **PDF Document Processing**: Automatically loads and processes healthcare contract PDFs
- **Intelligent Chunking**: Splits documents into optimally sized chunks (500 characters with 50 character overlap)
- **Vector Search**: Uses FAISS for fast and accurate semantic search
- **OpenAI Integration**: Leverages OpenAI embeddings and GPT models for high-quality answers
- **Persistent Storage**: Saves vector stores to disk for quick reloading
- **Interactive CLI**: User-friendly command-line interface for asking questions
- **Source Citations**: Provides references to source documents and page numbers
- **Production-Ready**: Comprehensive error handling and logging

## Project Structure

```
contractiq/
├── data/               # Place your healthcare contract PDFs here
├── src/               # Source code
│   ├── rag_pipeline.py    # Core RAG pipeline implementation
│   └── cli.py             # Command-line interface
├── outputs/           # Generated outputs (vector stores, etc.)
├── requirements.txt   # Python dependencies
├── .env.example      # Environment variable template
└── README.md         # This file
```

## Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Healthcare contract PDFs in PDF format

## Installation

### 1. Clone or Download the Repository

```bash
cd contractiq
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 5. Add Healthcare Contract PDFs

Place your healthcare payer contract PDF files in the `data/` directory:

```bash
# Example:
cp /path/to/your/contracts/*.pdf data/
```

## Usage

### Interactive Mode (Recommended)

Start an interactive session to ask multiple questions:

```bash
python src/cli.py
```

Example session:
```
╔══════════════════════════════════════════════════════════════╗
║     Healthcare Contract Analysis System                     ║
║     RAG-Powered Contract Intelligence                       ║
╚══════════════════════════════════════════════════════════════╝

Interactive Mode: Ask questions about your healthcare contracts.
Type 'quit', 'exit', or 'q' to end the session.

Your Question: What is the reimbursement rate for office visits?

Analyzing contracts...

────────────────────────────────────────────────────────────────
ANSWER:
Based on the contract, office visits are reimbursed at 110% of Medicare
rates for CPT codes 99213-99215...
```

### Single Question Mode

Ask a single question and exit:

```bash
python src/cli.py -q "What are the payment terms for urgent care?"
```

### Command-Line Options

```bash
# Rebuild the vector store from scratch
python src/cli.py --rebuild

# Use a specific data directory
python src/cli.py --data-dir /path/to/pdfs

# Use a different OpenAI model
python src/cli.py --model gpt-4

# Combine options
python src/cli.py --rebuild --model gpt-4 -q "What is the claim submission deadline?"
```

## How It Works

### 1. Document Loading
The system uses LangChain's `PyPDFLoader` to extract text from PDF files in the `data/` directory.

### 2. Text Chunking
Documents are split into 500-character chunks with 50-character overlap using `RecursiveCharacterTextSplitter`, preserving context across chunks.

### 3. Embedding Generation
Each chunk is converted to a vector embedding using OpenAI's `text-embedding-ada-002` model.

### 4. Vector Storage
Embeddings are stored in a FAISS vector database for efficient similarity search.

### 5. Question Answering
When you ask a question:
1. Your question is converted to an embedding
2. The top 4 most relevant chunks are retrieved from FAISS
3. These chunks are sent to GPT-3.5-turbo as context
4. The model generates an answer based on the contract information

### 6. Persistent Storage
The vector store is saved to `outputs/vectorstore/` so subsequent runs load instantly without reprocessing PDFs.

## Example Questions

Here are some example questions you can ask about healthcare contracts:

- "What is the reimbursement rate for CPT code 99213?"
- "What are the payment terms and timelines?"
- "Are there any claim submission deadlines?"
- "What is the termination notice period?"
- "What services require prior authorization?"
- "What is the fee schedule for emergency services?"
- "Are there any performance bonuses or incentives?"
- "What is the credentialing process?"

## Architecture

### Core Components

**HealthcareContractRAG** (`src/rag_pipeline.py`)
- Main RAG pipeline class
- Handles document loading, chunking, embedding, and QA
- Provides methods for building, saving, and loading pipelines

**CLI** (`src/cli.py`)
- Interactive and single-question modes
- User-friendly output formatting
- Comprehensive error handling

### Technology Stack

- **LangChain**: Framework for building LLM applications
- **OpenAI**: Embeddings (text-embedding-ada-002) and LLM (GPT-3.5-turbo)
- **FAISS**: Vector similarity search
- **PyPDF**: PDF text extraction
- **Python-dotenv**: Environment variable management

## Development

### Running Tests

```bash
# Run with a test question
python src/cli.py -q "Test question"
```

### Rebuilding the Index

If you add new PDFs to the `data/` directory:

```bash
python src/cli.py --rebuild
```

### Troubleshooting

**Issue**: `OPENAI_API_KEY not found`
- **Solution**: Ensure you've created a `.env` file with your API key

**Issue**: `No PDF files found in data`
- **Solution**: Add PDF files to the `data/` directory

**Issue**: `Error loading vector store`
- **Solution**: Run with `--rebuild` flag to recreate the vector store

**Issue**: Slow first run
- **Solution**: First run processes all PDFs and creates embeddings. Subsequent runs are much faster.

## Performance Considerations

- **First Run**: Takes several minutes to process PDFs and create embeddings
- **Subsequent Runs**: Loads in seconds using saved vector store
- **API Costs**: ~$0.0001 per 1K tokens for embeddings, ~$0.002 per 1K tokens for GPT-3.5-turbo
- **Chunk Size**: 500 characters balances context and granularity

## Future Enhancements

Potential improvements for production deployment:

- [ ] Streamlit web interface
- [ ] Support for multiple contract versions
- [ ] Comparison between different payer contracts
- [ ] Export answers to PDF reports
- [ ] Integration with contract management systems
- [ ] Fine-tuned model for healthcare terminology
- [ ] Support for additional document formats (DOCX, HTML)
- [ ] Advanced filtering (by payer, date, contract type)

## License

This project is provided as-is for educational and professional portfolio purposes.

## Contact

For questions or feedback about this project, please contact the developer.

## Acknowledgments

- Built with [LangChain](https://www.langchain.com/)
- Powered by [OpenAI](https://openai.com/)
- Vector search by [FAISS](https://github.com/facebookresearch/faiss)
