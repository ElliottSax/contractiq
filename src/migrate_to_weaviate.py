"""
Migrate from FAISS to Weaviate

This script migrates your healthcare contract data from FAISS to Weaviate,
enabling hybrid search (semantic + keyword).
"""

import sys
import os
import time
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.weaviate_rag import WeaviateHealthcareRAG


def main():
    print("=" * 70)
    print("ContractIQ: FAISS → Weaviate Migration")
    print("=" * 70)
    print()

    print("This script will:")
    print("  1. Connect to your Weaviate cluster")
    print("  2. Create the healthcare contracts schema")
    print("  3. Load and chunk PDF documents")
    print("  4. Upload all chunks to Weaviate")
    print("  5. Test hybrid search functionality")
    print()

    input("Press Enter to continue (Ctrl+C to cancel)...")
    print()

    # Initialize Weaviate RAG
    print("Step 1: Initializing Weaviate RAG...")
    try:
        rag = WeaviateHealthcareRAG(alpha=0.7)
        print("✅ Initialized (alpha=0.7 for healthcare)")
    except ValueError as e:
        print(f"❌ Error: {e}")
        print()
        print("Please configure Weaviate credentials in .env")
        print("See WEAVIATE_SETUP.md for instructions.")
        return 1

    print()

    # Connect to Weaviate
    print("Step 2: Connecting to Weaviate cluster...")
    if not rag.connect():
        print("❌ Connection failed")
        return 1

    print()

    # Create schema
    print("Step 3: Creating schema...")
    if not rag.create_schema():
        print("❌ Schema creation failed")
        return 1

    print()

    # Load and chunk documents
    print("Step 4: Loading PDF documents...")
    try:
        chunks = rag.load_and_chunk_documents(data_dir="data")
        print(f"✅ Loaded and chunked {len(chunks)} document segments")

        # Show breakdown by payer
        payers = {}
        for chunk in chunks:
            payer = chunk['payer']
            payers[payer] = payers.get(payer, 0) + 1

        print()
        print("Breakdown by payer:")
        for payer, count in sorted(payers.items()):
            print(f"  - {payer}: {count} chunks")

    except Exception as e:
        print(f"❌ Error loading documents: {e}")
        return 1

    print()

    # Upload to Weaviate
    print("Step 5: Uploading to Weaviate...")
    print("(This may take 30-60 seconds)")
    print()

    start_time = time.time()

    if not rag.upload_documents(chunks):
        print("❌ Upload failed")
        return 1

    elapsed = time.time() - start_time
    print()
    print(f"✅ Upload complete in {elapsed:.1f} seconds!")
    print()

    # Get stats
    print("Step 6: Verifying database...")
    stats = rag.get_stats()
    if "total_chunks" in stats:
        print(f"✅ Database ready!")
        print(f"   Total chunks: {stats['total_chunks']}")
    else:
        print("⚠️  Warning: Could not verify stats")

    print()

    # Test hybrid search
    print("Step 7: Testing hybrid search...")
    print()

    test_queries = [
        "What is the reimbursement rate for CPT 99213?",
        "Compare United Healthcare and Aetna payment terms",
        "What is the highest rate for knee surgery?"
    ]

    for query in test_queries:
        print(f"Query: {query[:60]}...")
        results = rag.hybrid_search(query, limit=3)

        if results:
            print(f"✅ Found {len(results)} results")
            print(f"   Top result: {results[0]['payer']} - {results[0]['source']}")
        else:
            print("⚠️  No results found")

        print()

    # Success!
    print("=" * 70)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 70)
    print()
    print("Your healthcare contracts are now in Weaviate with hybrid search enabled.")
    print()
    print("Next steps:")
    print("  1. Test queries: python3 src/test_hybrid_search.py")
    print("  2. Run benchmarks: python3 src/benchmark_weaviate.py")
    print("  3. Update README with results")
    print()
    print("Hybrid Search Configuration:")
    print(f"  Alpha: {rag.alpha} (70% semantic, 30% keyword)")
    print("  Optimized for: CPT codes, dollar amounts, policy terms")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
