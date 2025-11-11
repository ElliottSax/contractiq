"""
Test Weaviate Connection

Simple script to verify Weaviate Cloud/local connection is working.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.weaviate_rag import WeaviateHealthcareRAG


def main():
    print("=" * 70)
    print("Weaviate Connection Test")
    print("=" * 70)
    print()

    # Initialize RAG system
    try:
        rag = WeaviateHealthcareRAG(alpha=0.7)
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print()
        print("Please ensure you have set up Weaviate credentials in .env:")
        print("  WEAVIATE_URL=https://your-cluster.weaviate.network")
        print("  WEAVIATE_API_KEY=your-api-key")
        print()
        print("See WEAVIATE_SETUP.md for detailed instructions.")
        return 1

    # Test connection
    print("Testing connection...")
    if rag.connect():
        print()
        print("✅ SUCCESS!")
        print()
        print("Weaviate cluster is ready for use.")
        print()

        # Get stats if schema exists
        try:
            stats = rag.get_stats()
            if "total_chunks" in stats:
                print(f"📊 Database Stats:")
                print(f"   Total chunks: {stats['total_chunks']}")
                print(f"   Alpha (hybrid): {stats['alpha']}")
            else:
                print("📊 Database is empty. Run migration to populate.")
        except Exception as e:
            print(f"📊 Database is empty. Run migration to populate.")

        print()
        print("Next steps:")
        print("  1. Run migration: python3 src/migrate_to_weaviate.py")
        print("  2. Test queries: python3 src/weaviate_rag.py")
        print()
        return 0

    else:
        print()
        print("❌ FAILED")
        print()
        print("Could not connect to Weaviate cluster.")
        print()
        print("Troubleshooting:")
        print("  1. Check WEAVIATE_URL is correct (include https://)")
        print("  2. Verify WEAVIATE_API_KEY is valid")
        print("  3. Ensure cluster status is 'Ready' in Weaviate Console")
        print("  4. Check firewall/SSL settings")
        print()
        print("See WEAVIATE_SETUP.md for detailed troubleshooting.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
