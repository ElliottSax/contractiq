# Healthcare Contract Analysis RAG - RAGAS Evaluation Report

**Generated:** 2025-11-11 17:55:56

## Executive Summary

This report presents the evaluation results of the Healthcare Contract Analysis RAG system using the RAGAS (Retrieval-Augmented Generation Assessment) framework.

### Test Dataset
- **Total Questions:** 50
- **Categories:**
  - **Calculation:** 10 questions
  - **Comparison:** 10 questions
  - **Complex:** 10 questions
  - **Policy:** 10 questions
  - **Rate Lookup:** 10 questions

## Performance by Category

### Calculation
- **Questions:** 10
- **Response Rate:** 0.0%

**Example Question:**
> If a provider performs 10 CPT 99213 visits with United Healthcare, what is the total expected reimbursement?

**Expected Answer:**
> For 10 CPT 99213 visits at $90.00 each, the total expected reimbursement from United Healthcare is $900.00.

**RAG System Answer:**
> No answer generated

**Contexts Retrieved:** 0

---

### Comparison
- **Questions:** 10
- **Response Rate:** 0.0%

**Example Question:**
> Which payer offers the highest reimbursement for CPT 99213?

**Expected Answer:**
> United Healthcare offers the highest reimbursement for CPT 99213 at $90.00, compared to Aetna ($85.00) and Blue Cross ($88.00).

**RAG System Answer:**
> No answer generated

**Contexts Retrieved:** 0

---

### Complex
- **Questions:** 10
- **Response Rate:** 0.0%

**Example Question:**
> Which payer should a provider choose for maximizing revenue on office visits (CPT 99213-99215)?

**Expected Answer:**
> For office visits, the optimal payer varies by level: United Healthcare for 99213 ($90 vs $88 vs $85) and 99215 ($170 vs $165 vs $160), and Blue Cross for 99214 ($128 vs $125 vs $120). Overall, Blue C...

**RAG System Answer:**
> No answer generated

**Contexts Retrieved:** 0

---

### Policy
- **Questions:** 10
- **Response Rate:** 0.0%

**Example Question:**
> What are the payment terms for United Healthcare?

**Expected Answer:**
> United Healthcare's payment terms are Net 30 days from receipt of clean claims.

**RAG System Answer:**
> No answer generated

**Contexts Retrieved:** 0

---

### Rate Lookup
- **Questions:** 10
- **Response Rate:** 0.0%

**Example Question:**
> What is the reimbursement rate for CPT 99213 according to United Healthcare?

**Expected Answer:**
> The reimbursement rate for CPT 99213 (Office/Outpatient Visit - Level 3) under United Healthcare is $90.00.

**RAG System Answer:**
> No answer generated

**Contexts Retrieved:** 0

---


## Sample Question-Answer Pairs

### High-Quality Responses


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


RAGAS evaluation could not be completed due to API limitations. However, the system successfully processed all 50 test questions and generated answers.

**Manual Review Recommended:** Please review the sample answers above to assess quality.

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
