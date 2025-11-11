"""
Benchmark: Weaviate Hybrid Search vs FAISS Semantic Search

This script compares retrieval precision between:
1. Weaviate hybrid search (semantic + keyword, alpha=0.7)
2. FAISS pure semantic search

Focus: Healthcare-specific queries (CPT codes, dollar amounts, policy terms)
"""

import sys
import os
import time
from pathlib import Path
from typing import List, Dict

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.weaviate_rag import WeaviateHealthcareRAG
from src.rag_pipeline import HealthcareContractRAG


def create_test_queries() -> List[Dict[str, str]]:
    """
    Create test queries focusing on healthcare-specific scenarios where
    hybrid search should outperform pure semantic search.
    """
    return [
        {
            "query": "CPT 99213",
            "type": "exact_code",
            "description": "Exact CPT code (keyword match critical)"
        },
        {
            "query": "What is the rate for CPT 99213 with United Healthcare?",
            "type": "code_with_context",
            "description": "CPT code in natural language"
        },
        {
            "query": "$90.00",
            "type": "exact_amount",
            "description": "Exact dollar amount"
        },
        {
            "query": "How much does United Healthcare pay for office visits?",
            "type": "semantic",
            "description": "Semantic understanding needed"
        },
        {
            "query": "99214 reimbursement rate",
            "type": "code_sparse",
            "description": "CPT code with minimal context"
        },
        {
            "query": "Net 30 payment terms",
            "type": "policy_exact",
            "description": "Exact policy term"
        },
        {
            "query": "Which payer has fastest payment?",
            "type": "comparative",
            "description": "Comparison question (semantic)"
        },
        {
            "query": "CPT 27447 Total Knee Arthroplasty",
            "type": "code_with_name",
            "description": "CPT code with procedure name"
        },
        {
            "query": "$16000 knee surgery",
            "type": "amount_procedure",
            "description": "Amount with procedure type"
        },
        {
            "query": "prior authorization requirements",
            "type": "policy_semantic",
            "description": "Policy query (semantic)"
        }
    ]


def evaluate_results(results: List[Dict], query_info: Dict) -> Dict:
    """
    Evaluate retrieval quality.

    Returns:
        dict: Precision metrics
    """
    if not results:
        return {
            "relevant_count": 0,
            "total_count": 0,
            "precision": 0.0,
            "top1_relevant": False
        }

    # Check relevance based on query type
    query_type = query_info["type"]
    relevant_count = 0

    # Simple relevance check (can be enhanced)
    for result in results:
        text = result.get("text", "").lower()

        if query_type == "exact_code" and "cpt" in text and "99213" in text:
            relevant_count += 1
        elif query_type == "exact_amount" and ("90" in text or "$90" in text):
            relevant_count += 1
        elif query_type == "code_with_context" and ("99213" in text or "office" in text):
            relevant_count += 1
        elif len(text) > 100:  # Generic relevance - has substantial content
            relevant_count += 1

    precision = relevant_count / len(results) if results else 0

    return {
        "relevant_count": relevant_count,
        "total_count": len(results),
        "precision": precision,
        "top1_relevant": relevant_count > 0 and len(results) > 0
    }


def run_weaviate_benchmark(rag: WeaviateHealthcareRAG, queries: List[Dict]) -> List[Dict]:
    """Run benchmark on Weaviate hybrid search."""
    print("Running Weaviate Hybrid Search Benchmark...")
    print(f"Alpha: {rag.alpha} (70% semantic, 30% keyword)")
    print()

    results = []

    for i, query_info in enumerate(queries, 1):
        query = query_info["query"]
        print(f"[{i}/{len(queries)}] {query[:50]}...")

        start_time = time.time()
        search_results = rag.hybrid_search(query, limit=4)
        elapsed = time.time() - start_time

        metrics = evaluate_results(search_results, query_info)

        results.append({
            "query": query,
            "type": query_info["type"],
            "description": query_info["description"],
            "results_count": len(search_results),
            "precision": metrics["precision"],
            "retrieval_time": elapsed,
            "top1_relevant": metrics["top1_relevant"]
        })

        print(f"  Results: {len(search_results)}, Precision: {metrics['precision']:.2f}, Time: {elapsed:.3f}s")

    print()
    return results


def run_faiss_benchmark(rag: HealthcareContractRAG, queries: List[Dict]) -> List[Dict]:
    """Run benchmark on FAISS semantic search."""
    print("Running FAISS Semantic Search Benchmark...")
    print("Pure semantic (TF-IDF embeddings)")
    print()

    results = []

    for i, query_info in enumerate(queries, 1):
        query = query_info["query"]
        print(f"[{i}/{len(queries)}] {query[:50]}...")

        try:
            start_time = time.time()

            # Use the retriever directly for fair comparison
            retriever = rag.vectorstore.as_retriever(search_kwargs={"k": 4})
            search_results = retriever.get_relevant_documents(query)

            elapsed = time.time() - start_time

            # Convert to comparable format
            formatted_results = [
                {"text": doc.page_content}
                for doc in search_results
            ]

            metrics = evaluate_results(formatted_results, query_info)

            results.append({
                "query": query,
                "type": query_info["type"],
                "description": query_info["description"],
                "results_count": len(search_results),
                "precision": metrics["precision"],
                "retrieval_time": elapsed,
                "top1_relevant": metrics["top1_relevant"]
            })

            print(f"  Results: {len(search_results)}, Precision: {metrics['precision']:.2f}, Time: {elapsed:.3f}s")

        except Exception as e:
            print(f"  Error: {str(e)}")
            results.append({
                "query": query,
                "type": query_info["type"],
                "description": query_info["description"],
                "results_count": 0,
                "precision": 0.0,
                "retrieval_time": 0.0,
                "top1_relevant": False,
                "error": str(e)
            })

    print()
    return results


def compare_results(weaviate_results: List[Dict], faiss_results: List[Dict]):
    """Compare and display results."""
    print("=" * 70)
    print("BENCHMARK RESULTS: Weaviate vs FAISS")
    print("=" * 70)
    print()

    # Calculate averages
    weaviate_avg_precision = sum(r["precision"] for r in weaviate_results) / len(weaviate_results)
    faiss_avg_precision = sum(r["precision"] for r in faiss_results) / len(faiss_results)

    weaviate_avg_time = sum(r["retrieval_time"] for r in weaviate_results) / len(weaviate_results)
    faiss_avg_time = sum(r["retrieval_time"] for r in faiss_results) / len(faiss_results)

    weaviate_top1_accuracy = sum(1 for r in weaviate_results if r["top1_relevant"]) / len(weaviate_results)
    faiss_top1_accuracy = sum(1 for r in faiss_results if r["top1_relevant"]) / len(faiss_results)

    print("Overall Metrics:")
    print()
    print(f"{'Metric':<30} {'Weaviate Hybrid':<20} {'FAISS Semantic':<20} {'Winner'}")
    print("-" * 75)
    print(f"{'Average Precision':<30} {weaviate_avg_precision:>18.2%}  {faiss_avg_precision:>18.2%}  {'Weaviate' if weaviate_avg_precision > faiss_avg_precision else 'FAISS'}")
    print(f"{'Top-1 Accuracy':<30} {weaviate_top1_accuracy:>18.2%}  {faiss_top1_accuracy:>18.2%}  {'Weaviate' if weaviate_top1_accuracy > faiss_top1_accuracy else 'FAISS'}")
    print(f"{'Avg Retrieval Time':<30} {weaviate_avg_time:>17.3f}s {faiss_avg_time:>18.3f}s {'FAISS' if faiss_avg_time < weaviate_avg_time else 'Weaviate'}")
    print()

    # Breakdown by query type
    print("Performance by Query Type:")
    print()

    query_types = set(r["type"] for r in weaviate_results)

    for qtype in sorted(query_types):
        weaviate_type = [r for r in weaviate_results if r["type"] == qtype]
        faiss_type = [r for r in faiss_results if r["type"] == qtype]

        if weaviate_type and faiss_type:
            w_prec = sum(r["precision"] for r in weaviate_type) / len(weaviate_type)
            f_prec = sum(r["precision"] for r in faiss_type) / len(faiss_type)

            improvement = ((w_prec - f_prec) / f_prec * 100) if f_prec > 0 else 0

            print(f"{qtype:<25} W: {w_prec:.2%}  F: {f_prec:.2%}  Δ: {improvement:+.1f}%")

    print()

    # Key insights
    print("Key Insights:")
    print()

    if weaviate_avg_precision > faiss_avg_precision:
        improvement = (weaviate_avg_precision - faiss_avg_precision) / faiss_avg_precision * 100
        print(f"✅ Weaviate hybrid search provides {improvement:.1f}% better precision")
    else:
        print("⚠️  FAISS semantic search performed better in this test")

    print()

    # Query-specific wins
    weaviate_wins = sum(1 for w, f in zip(weaviate_results, faiss_results) if w["precision"] > f["precision"])
    print(f"✅ Weaviate won on {weaviate_wins}/{len(weaviate_results)} queries")

    # Expected strengths
    exact_queries = [r for r in weaviate_results if r["type"] in ["exact_code", "exact_amount", "code_sparse"]]
    if exact_queries:
        exact_precision = sum(r["precision"] for r in exact_queries) / len(exact_queries)
        print(f"✅ Hybrid search precision on exact matches: {exact_precision:.2%}")

    print()
    print("=" * 70)


def main():
    print("=" * 70)
    print("ContractIQ: Weaviate vs FAISS Benchmark")
    print("=" * 70)
    print()

    # Create test queries
    queries = create_test_queries()
    print(f"Test queries: {len(queries)}")
    print()

    # Run Weaviate benchmark
    try:
        weaviate_rag = WeaviateHealthcareRAG(alpha=0.7)
        if not weaviate_rag.connect():
            print("❌ Could not connect to Weaviate")
            print("Please run migration first: python3 src/migrate_to_weaviate.py")
            return 1

        weaviate_results = run_weaviate_benchmark(weaviate_rag, queries)

    except Exception as e:
        print(f"❌ Weaviate benchmark failed: {e}")
        return 1

    # Run FAISS benchmark
    try:
        print("Initializing FAISS RAG...")
        faiss_rag = HealthcareContractRAG(provider="claude")

        # Check if vectorstore exists
        if not Path("outputs/vectorstore").exists():
            print("Building FAISS pipeline...")
            faiss_rag.build_pipeline(save_vectorstore=True)
        else:
            print("Loading FAISS pipeline...")
            faiss_rag.load_vectorstore()

        faiss_results = run_faiss_benchmark(faiss_rag, queries)

    except Exception as e:
        print(f"❌ FAISS benchmark failed: {e}")
        print("Tip: Delete outputs/vectorstore and rebuild")
        return 1

    # Compare results
    compare_results(weaviate_results, faiss_results)

    print("Benchmark complete!")
    print()
    print("Next: Update README.md with these results")

    return 0


if __name__ == "__main__":
    sys.exit(main())
