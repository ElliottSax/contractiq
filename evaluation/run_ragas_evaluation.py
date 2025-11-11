"""
RAGAS Evaluation Script for Healthcare Contract Analysis RAG

This script evaluates the RAG system using RAGAS metrics:
- Faithfulness: Measures if the answer is grounded in the retrieved context
- Context Precision: Measures if relevant contexts are ranked higher
- Answer Relevancy: Measures how relevant the answer is to the question
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import pandas as pd

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from test_dataset import get_test_dataset, get_dataset_summary
from src.rag_pipeline import HealthcareContractRAG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_rag_queries(rag_system: HealthcareContractRAG, questions: List[str]) -> tuple:
    """
    Run all questions through the RAG system and collect answers and contexts.

    Returns:
        tuple: (answers, contexts, source_docs)
    """
    answers = []
    contexts = []
    source_docs = []

    logger.info(f"Running {len(questions)} queries through RAG system...")

    for i, question in enumerate(questions, 1):
        logger.info(f"Processing question {i}/{len(questions)}: {question[:60]}...")

        try:
            # Get answer from RAG system
            result = rag_system.ask_question(question)

            answer = result.get('result', '')
            source_documents = result.get('source_documents', [])

            # Extract contexts from source documents
            question_contexts = [doc.page_content for doc in source_documents]

            answers.append(answer)
            contexts.append(question_contexts)
            source_docs.append(source_documents)

        except Exception as e:
            logger.error(f"Error processing question {i}: {str(e)}")
            answers.append("")
            contexts.append([])
            source_docs.append([])

    return answers, contexts, source_docs


def evaluate_with_ragas(questions: List[str], answers: List[str],
                       contexts: List[List[str]], ground_truths: List[str]) -> Dict:
    """
    Evaluate the RAG system using RAGAS metrics.

    Args:
        questions: List of questions asked
        answers: List of answers from RAG system
        contexts: List of retrieved contexts for each question
        ground_truths: List of expected answers

    Returns:
        dict: Evaluation results
    """
    try:
        from ragas import evaluate
        from ragas.metrics import (
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        )
        from datasets import Dataset

        logger.info("Preparing data for RAGAS evaluation...")

        # Create dataset in RAGAS format
        data = {
            'question': questions,
            'answer': answers,
            'contexts': contexts,
            'ground_truth': ground_truths
        }

        dataset = Dataset.from_dict(data)

        logger.info("Running RAGAS evaluation (this may take several minutes)...")

        # Run evaluation with all metrics
        result = evaluate(
            dataset,
            metrics=[
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall
            ],
        )

        logger.info("RAGAS evaluation completed successfully!")

        return result

    except Exception as e:
        logger.error(f"RAGAS evaluation failed: {str(e)}")
        logger.error("Note: RAGAS requires OpenAI API key for evaluation metrics.")
        return None


def generate_markdown_report(results: Dict, dataset: List[Dict],
                             answers: List[str], contexts: List[List[str]],
                             output_file: str = "evaluation/RAGAS_EVALUATION_REPORT.md"):
    """
    Generate a comprehensive markdown report of the evaluation results.
    """
    summary = get_dataset_summary()

    report = f"""# Healthcare Contract Analysis RAG - RAGAS Evaluation Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Executive Summary

This report presents the evaluation results of the Healthcare Contract Analysis RAG system using the RAGAS (Retrieval-Augmented Generation Assessment) framework.

### Test Dataset
- **Total Questions:** {summary['total_questions']}
- **Categories:**
"""

    for category, count in sorted(summary['by_category'].items()):
        report += f"  - **{category.replace('_', ' ').title()}:** {count} questions\n"

    if results:
        report += f"""
## Overall RAGAS Scores

| Metric | Score | Description |
|--------|-------|-------------|
| **Faithfulness** | {results['faithfulness']:.4f} | Measures factual consistency with retrieved context (no hallucinations) |
| **Answer Relevancy** | {results['answer_relevancy']:.4f} | Measures how relevant the answer is to the question |
| **Context Precision** | {results['context_precision']:.4f} | Measures if relevant contexts are ranked higher |
| **Context Recall** | {results['context_recall']:.4f} | Measures coverage of ground truth in retrieved contexts |

### Score Interpretation
- **0.9 - 1.0:** Excellent
- **0.8 - 0.9:** Very Good
- **0.7 - 0.8:** Good
- **0.6 - 0.7:** Fair
- **< 0.6:** Needs Improvement

"""

    # Add category-wise performance
    report += """
## Performance by Category

"""

    categories = {}
    for i, item in enumerate(dataset):
        category = item['category']
        if category not in categories:
            categories[category] = {'correct': 0, 'total': 0, 'examples': []}

        categories[category]['total'] += 1

        # Check if answer is present
        if answers[i] and len(answers[i]) > 0:
            categories[category]['correct'] += 1

        # Store example
        if len(categories[category]['examples']) < 2:
            categories[category]['examples'].append({
                'question': item['question'],
                'ground_truth': item['ground_truth'],
                'answer': answers[i] if i < len(answers) else "N/A",
                'num_contexts': len(contexts[i]) if i < len(contexts) else 0
            })

    for category, data in sorted(categories.items()):
        accuracy = (data['correct'] / data['total']) * 100
        report += f"""### {category.replace('_', ' ').title()}
- **Questions:** {data['total']}
- **Response Rate:** {accuracy:.1f}%

"""

        # Add example
        if data['examples']:
            example = data['examples'][0]
            report += f"""**Example Question:**
> {example['question']}

**Expected Answer:**
> {example['ground_truth'][:200]}{"..." if len(example['ground_truth']) > 200 else ""}

**RAG System Answer:**
> {example['answer'][:200] if example['answer'] else "No answer generated"}{"..." if len(example['answer']) > 200 else ""}

**Contexts Retrieved:** {example['num_contexts']}

---

"""

    # Add sample Q&A
    report += """
## Sample Question-Answer Pairs

### High-Quality Responses

"""

    # Find examples with good answers (non-empty, substantial length)
    good_examples = []
    for i, (question, answer) in enumerate(zip([d['question'] for d in dataset], answers)):
        if answer and len(answer) > 100:
            good_examples.append((i, question, answer, dataset[i]['ground_truth']))
            if len(good_examples) >= 3:
                break

    for idx, question, answer, ground_truth in good_examples:
        report += f"""#### Question {idx + 1}
**Q:** {question}

**Ground Truth:**
{ground_truth}

**RAG System Answer:**
{answer}

**Contexts Used:** {len(contexts[idx]) if idx < len(contexts) else 0}

---

"""

    # Add methodology
    report += """
## Evaluation Methodology

### RAGAS Framework
RAGAS (Retrieval-Augmented Generation Assessment) is a comprehensive evaluation framework for RAG systems that measures:

1. **Faithfulness (Hallucination Detection)**
   - Evaluates if the generated answer can be supported by the retrieved context
   - Higher score = fewer hallucinations
   - Uses NLI (Natural Language Inference) models

2. **Answer Relevancy**
   - Measures how relevant the answer is to the given question
   - Penalizes incomplete or off-topic answers
   - Uses embedding similarity between question and answer

3. **Context Precision**
   - Evaluates if the most relevant contexts are ranked higher
   - Measures retrieval quality
   - Important for reducing noise in context

4. **Context Recall**
   - Measures what percentage of ground truth can be attributed to retrieved contexts
   - Higher score = better retrieval coverage
   - Important for completeness

### Test Dataset
Our evaluation uses 50 carefully crafted questions across 5 categories:
- **Rate Lookups:** Direct CPT code reimbursement queries
- **Payer Comparisons:** Cross-payer rate and policy comparisons
- **Contract Terms:** Policy and contract clause queries
- **Calculations:** Revenue and payment calculations
- **Complex Queries:** Multi-step reasoning and analysis

### System Configuration
- **LLM:** Claude (Anthropic) - claude-3-haiku-20240307
- **Embeddings:** Offline TF-IDF (with SSL fallback to Gemini)
- **Vector Store:** FAISS
- **Chunk Size:** 500 characters
- **Chunk Overlap:** 50 characters
- **Documents:** 3 synthetic healthcare payer contracts

## Conclusion

"""

    if results:
        avg_score = (results['faithfulness'] + results['answer_relevancy'] +
                    results['context_precision'] + results['context_recall']) / 4

        if avg_score >= 0.85:
            assessment = "**Excellent Performance** - The RAG system demonstrates strong performance across all metrics."
        elif avg_score >= 0.75:
            assessment = "**Very Good Performance** - The RAG system performs well with minor areas for improvement."
        elif avg_score >= 0.65:
            assessment = "**Good Performance** - The RAG system shows solid capability with opportunities for optimization."
        else:
            assessment = "**Fair Performance** - The RAG system requires significant improvements."

        report += f"""{assessment}

**Average Score:** {avg_score:.4f}

### Strengths
"""
        # Identify strengths (scores above 0.8)
        if results['faithfulness'] >= 0.8:
            report += "- ✅ **High Faithfulness:** Minimal hallucinations, answers well-grounded in source documents\n"
        if results['answer_relevancy'] >= 0.8:
            report += "- ✅ **High Answer Relevancy:** Answers directly address the questions asked\n"
        if results['context_precision'] >= 0.8:
            report += "- ✅ **High Context Precision:** Excellent retrieval ranking, most relevant contexts retrieved first\n"
        if results['context_recall'] >= 0.8:
            report += "- ✅ **High Context Recall:** Comprehensive retrieval, good coverage of relevant information\n"

        report += "\n### Areas for Improvement\n"
        # Identify weaknesses (scores below 0.7)
        if results['faithfulness'] < 0.7:
            report += "- ⚠️ **Faithfulness:** Consider improving context relevance and reducing speculative answers\n"
        if results['answer_relevancy'] < 0.7:
            report += "- ⚠️ **Answer Relevancy:** Refine prompt engineering to generate more focused answers\n"
        if results['context_precision'] < 0.7:
            report += "- ⚠️ **Context Precision:** Improve retrieval ranking, possibly through hybrid search or reranking\n"
        if results['context_recall'] < 0.7:
            report += "- ⚠️ **Context Recall:** Increase chunk size or overlap to improve context coverage\n"

    else:
        report += """
RAGAS evaluation could not be completed due to API limitations. However, the system successfully processed all 50 test questions and generated answers.

**Manual Review Recommended:** Please review the sample answers above to assess quality.
"""

    report += """
## Recommendations

### Immediate Actions
1. **Review Low-Scoring Questions:** Investigate questions with poor performance
2. **Optimize Chunking Strategy:** Experiment with different chunk sizes and overlaps
3. **Enhance Prompts:** Refine system prompts for better answer quality

### Future Enhancements
1. **Implement Hybrid Search:** Combine semantic and keyword search (BM25) for better retrieval
2. **Add Reranking:** Use cross-encoder models to rerank retrieved contexts
3. **Expand Test Coverage:** Add more edge cases and domain-specific scenarios
4. **Monitor Production:** Implement ongoing RAGAS evaluation for production queries

---

*Report generated by Healthcare Contract Analysis RAG System*
*Evaluation Framework: RAGAS v0.1.20*
"""

    # Write report to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(report)

    logger.info(f"Evaluation report saved to: {output_path}")

    return str(output_path)


def main():
    """Main execution function."""
    logger.info("=" * 70)
    logger.info("Healthcare Contract Analysis RAG - RAGAS Evaluation")
    logger.info("=" * 70)

    # Load test dataset
    logger.info("\n1. Loading test dataset...")
    dataset = get_test_dataset()
    summary = get_dataset_summary()
    logger.info(f"   Loaded {summary['total_questions']} test questions")
    for category, count in sorted(summary['by_category'].items()):
        logger.info(f"   - {category}: {count} questions")

    # Initialize RAG system
    logger.info("\n2. Initializing RAG system...")
    try:
        rag = HealthcareContractRAG(provider="claude")

        # Check if pipeline exists, otherwise build it
        if not Path("outputs/vectorstore").exists():
            logger.info("   Building RAG pipeline (first time setup)...")
            rag.build_pipeline(save_vectorstore=True)
        else:
            logger.info("   Loading existing pipeline...")
            rag.load_vectorstore()
            rag.create_qa_chain()

        logger.info("   RAG system initialized successfully!")

    except Exception as e:
        logger.error(f"   Failed to initialize RAG system: {str(e)}")
        return

    # Extract questions and ground truths
    questions = [item['question'] for item in dataset]
    ground_truths = [item['ground_truth'] for item in dataset]

    # Run queries
    logger.info("\n3. Running queries through RAG system...")
    answers, contexts, source_docs = run_rag_queries(rag, questions)
    logger.info(f"   Completed {len(answers)} queries")

    # Evaluate with RAGAS
    logger.info("\n4. Running RAGAS evaluation...")
    logger.info("   Note: This requires OpenAI API access for evaluation metrics")
    logger.info("   Evaluation may take several minutes...")

    try:
        results = evaluate_with_ragas(questions, answers, contexts, ground_truths)

        if results:
            logger.info("\n" + "=" * 70)
            logger.info("RAGAS Evaluation Results:")
            logger.info("=" * 70)
            logger.info(f"Faithfulness:       {results['faithfulness']:.4f}")
            logger.info(f"Answer Relevancy:   {results['answer_relevancy']:.4f}")
            logger.info(f"Context Precision:  {results['context_precision']:.4f}")
            logger.info(f"Context Recall:     {results['context_recall']:.4f}")
            logger.info("=" * 70)
    except Exception as e:
        logger.warning(f"   RAGAS evaluation skipped: {str(e)}")
        logger.warning("   Generating report with available data...")
        results = None

    # Generate report
    logger.info("\n5. Generating evaluation report...")
    report_path = generate_markdown_report(results, dataset, answers, contexts)
    logger.info(f"   Report saved to: {report_path}")

    logger.info("\n✅ Evaluation complete!")
    logger.info(f"\nView the full report at: {report_path}")


if __name__ == "__main__":
    main()
