"""
Command-Line Interface for Healthcare Contract Analysis

This script provides an interactive CLI for asking questions about
healthcare payer contracts using the RAG pipeline.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from rag_pipeline import HealthcareContractRAG


def print_banner():
    """Print a welcome banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║     Healthcare Contract Analysis System                     ║
║     RAG-Powered Contract Intelligence                       ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_separator():
    """Print a visual separator."""
    print("\n" + "─" * 64 + "\n")


def display_answer(result: dict):
    """
    Display the answer with source information.

    Args:
        result: Dictionary containing answer and source documents
    """
    print_separator()
    print("ANSWER:")
    print(result["answer"])

    if result.get("source_documents"):
        print("\n" + "─" * 64)
        print("SOURCES:")
        for i, doc in enumerate(result["source_documents"], 1):
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "Unknown")
            print(f"\n  [{i}] File: {Path(source).name}")
            print(f"      Page: {page}")
            print(f"      Preview: {doc.page_content[:150]}...")

    print_separator()


def interactive_mode(rag: HealthcareContractRAG):
    """
    Run interactive question-answering mode.

    Args:
        rag: Initialized HealthcareContractRAG instance
    """
    print("Interactive Mode: Ask questions about your healthcare contracts.")
    print("Type 'quit', 'exit', or 'q' to end the session.\n")

    while True:
        try:
            # Get user input
            question = input("Your Question: ").strip()

            # Check for exit commands
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nThank you for using Healthcare Contract Analysis System!")
                break

            # Skip empty questions
            if not question:
                print("Please enter a question.\n")
                continue

            # Process question
            print("\nAnalyzing contracts...")
            result = rag.ask_question(question)

            # Display answer
            display_answer(result)

        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}\n")


def single_question_mode(rag: HealthcareContractRAG, question: str):
    """
    Answer a single question and exit.

    Args:
        rag: Initialized HealthcareContractRAG instance
        question: Question to answer
    """
    try:
        print(f"\nQuestion: {question}")
        print("Analyzing contracts...")

        result = rag.ask_question(question)
        display_answer(result)

    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Healthcare Contract Analysis System - Ask questions about your contracts"
    )
    parser.add_argument(
        "-q", "--question",
        type=str,
        help="Ask a single question and exit"
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild the vector store from scratch"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data",
        help="Directory containing PDF contracts (default: data)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="claude-3-haiku-20240307",
        help="Model to use (default: claude-3-haiku-20240307 for Claude, gemini-pro for Gemini, gpt-3.5-turbo for OpenAI)"
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="claude",
        choices=["claude", "gemini", "openai"],
        help="LLM provider to use (default: claude)"
    )

    args = parser.parse_args()

    # Print banner
    print_banner()

    try:
        # Initialize RAG system
        print(f"Initializing Healthcare Contract Analysis System with {args.provider.upper()}...")
        rag = HealthcareContractRAG(
            data_dir=args.data_dir,
            model_name=args.model,
            provider=args.provider
        )

        # Build or load pipeline
        vectorstore_path = Path("outputs/vectorstore")

        if args.rebuild or not vectorstore_path.exists():
            print("Building RAG pipeline (this may take a few minutes)...")
            rag.build_pipeline(save_vectorstore=True)
            print("Pipeline built successfully!\n")
        else:
            print("Loading existing vector store...")
            rag.load_vectorstore()
            rag.create_qa_chain()
            print("Pipeline loaded successfully!\n")

        # Run appropriate mode
        if args.question:
            single_question_mode(rag, args.question)
        else:
            interactive_mode(rag)

    except FileNotFoundError as e:
        print(f"\nError: {str(e)}")
        print("\nPlease ensure:")
        print(f"  1. The '{args.data_dir}' directory exists")
        print("  2. You have added PDF contract files to this directory")
        sys.exit(1)

    except ValueError as e:
        print(f"\nConfiguration Error: {str(e)}")
        print("\nPlease ensure:")
        print("  1. You have created a .env file in the project root")
        print("  2. For Claude (default): Add ANTHROPIC_API_KEY=sk-ant-your_key_here")
        print("     Get a key at: https://console.anthropic.com/")
        print("     Note: When using Claude, you also need OPENAI_API_KEY for embeddings")
        print("  3. For Gemini: Add GOOGLE_API_KEY=your_api_key_here")
        print("     Get a FREE key at: https://makersuite.google.com/app/apikey")
        print("  4. For OpenAI: Add OPENAI_API_KEY=your_api_key_here")
        print("     Get a key at: https://platform.openai.com/api-keys")
        sys.exit(1)

    except Exception as e:
        print(f"\nUnexpected Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
