"""
Healthcare Contract Analysis RAG - Test Dataset

This module contains 50 carefully crafted test questions with ground truth answers
for evaluating the RAG system using RAGAS metrics.
"""

from typing import List, Dict

def get_test_dataset() -> List[Dict[str, str]]:
    """
    Returns a comprehensive test dataset for evaluating the RAG system.

    Each entry contains:
    - question: The query to ask the RAG system
    - ground_truth: The expected answer based on the contract PDFs
    - category: Type of query (rate_lookup, comparison, policy, calculation, etc.)
    """

    dataset = [
        # ===== CPT Code Rate Lookups (10 questions) =====
        {
            "question": "What is the reimbursement rate for CPT 99213 according to United Healthcare?",
            "ground_truth": "The reimbursement rate for CPT 99213 (Office/Outpatient Visit - Level 3) under United Healthcare is $90.00.",
            "category": "rate_lookup"
        },
        {
            "question": "How much does Aetna reimburse for CPT 99214?",
            "ground_truth": "Aetna reimburses $125.00 for CPT 99214 (Office/Outpatient Visit - Level 4 for Established Patient).",
            "category": "rate_lookup"
        },
        {
            "question": "What is Blue Cross's reimbursement rate for CPT 27447?",
            "ground_truth": "Blue Cross reimburses $16,000.00 for CPT 27447 (Total Knee Arthroplasty/Knee Replacement).",
            "category": "rate_lookup"
        },
        {
            "question": "What does United Healthcare pay for CPT 99215?",
            "ground_truth": "United Healthcare pays $170.00 for CPT 99215 (Office/Outpatient Visit - Level 5 for Established Patient).",
            "category": "rate_lookup"
        },
        {
            "question": "What is the reimbursement rate for CPT 29881 under Aetna?",
            "ground_truth": "Aetna reimburses $2,400.00 for CPT 29881 (Knee Arthroscopy with Meniscectomy).",
            "category": "rate_lookup"
        },
        {
            "question": "How much does Blue Cross pay for CPT 99213?",
            "ground_truth": "Blue Cross pays $88.00 for CPT 99213 (Office/Outpatient Visit - Level 3 for Established Patient).",
            "category": "rate_lookup"
        },
        {
            "question": "What is the reimbursement for CPT 73721 under United Healthcare?",
            "ground_truth": "United Healthcare reimburses $180.00 for CPT 73721 (MRI of Knee).",
            "category": "rate_lookup"
        },
        {
            "question": "What does Aetna pay for CPT 99285?",
            "ground_truth": "Aetna pays $420.00 for CPT 99285 (Emergency Department Visit - High Severity).",
            "category": "rate_lookup"
        },
        {
            "question": "What is Blue Cross's rate for CPT 99214?",
            "ground_truth": "Blue Cross's rate for CPT 99214 (Office/Outpatient Visit - Level 4 for Established Patient) is $128.00.",
            "category": "rate_lookup"
        },
        {
            "question": "How much does United Healthcare reimburse for CPT 29881?",
            "ground_truth": "United Healthcare reimburses $2,300.00 for CPT 29881 (Knee Arthroscopy with Meniscectomy).",
            "category": "rate_lookup"
        },

        # ===== Payer Comparisons (10 questions) =====
        {
            "question": "Which payer offers the highest reimbursement for CPT 99213?",
            "ground_truth": "United Healthcare offers the highest reimbursement for CPT 99213 at $90.00, compared to Aetna ($85.00) and Blue Cross ($88.00).",
            "category": "comparison"
        },
        {
            "question": "Compare the reimbursement rates for CPT 27447 across all three payers.",
            "ground_truth": "For CPT 27447 (Total Knee Arthroplasty): Blue Cross pays $16,000.00, United Healthcare pays $15,500.00, and Aetna pays $15,000.00. Blue Cross offers the highest rate.",
            "category": "comparison"
        },
        {
            "question": "Which payer has the best rate for CPT 99214?",
            "ground_truth": "Blue Cross has the best rate for CPT 99214 at $128.00, followed by Aetna at $125.00 and United Healthcare at $120.00.",
            "category": "comparison"
        },
        {
            "question": "What is the difference in reimbursement for CPT 99285 between United Healthcare and Aetna?",
            "ground_truth": "The difference in reimbursement for CPT 99285 (Emergency Department Visit - High Severity) between United Healthcare ($400.00) and Aetna ($420.00) is $20.00, with Aetna paying more.",
            "category": "comparison"
        },
        {
            "question": "Which payer offers the lowest rate for CPT 73721?",
            "ground_truth": "Aetna offers the lowest rate for CPT 73721 (MRI of Knee) at $175.00, compared to United Healthcare ($180.00) and Blue Cross ($185.00).",
            "category": "comparison"
        },
        {
            "question": "Compare payment timeframes across all three payers.",
            "ground_truth": "United Healthcare pays within 30 days (Net 30), Aetna pays within 45 days (Net 45), and Blue Cross pays within 30 days (Net 30).",
            "category": "comparison"
        },
        {
            "question": "Which payer has the fastest payment terms?",
            "ground_truth": "United Healthcare and Blue Cross have the fastest payment terms at Net 30 days, while Aetna has Net 45 days.",
            "category": "comparison"
        },
        {
            "question": "What is the average reimbursement rate for CPT 99213 across all payers?",
            "ground_truth": "The average reimbursement rate for CPT 99213 across all three payers is $87.67 (United Healthcare: $90.00, Blue Cross: $88.00, Aetna: $85.00).",
            "category": "comparison"
        },
        {
            "question": "Which payer pays the most for knee surgery (CPT 27447)?",
            "ground_truth": "Blue Cross pays the most for knee surgery (CPT 27447 - Total Knee Arthroplasty) at $16,000.00.",
            "category": "comparison"
        },
        {
            "question": "Compare the rates for CPT 29881 between United Healthcare and Aetna.",
            "ground_truth": "For CPT 29881 (Knee Arthroscopy with Meniscectomy), Aetna pays $2,400.00 while United Healthcare pays $2,300.00. Aetna offers $100 more.",
            "category": "comparison"
        },

        # ===== Contract Terms & Policies (10 questions) =====
        {
            "question": "What are the payment terms for United Healthcare?",
            "ground_truth": "United Healthcare's payment terms are Net 30 days from receipt of clean claims.",
            "category": "policy"
        },
        {
            "question": "What is the contract effective date for the Aetna agreement?",
            "ground_truth": "The Aetna contract is effective from January 1, 2024 through December 31, 2026.",
            "category": "policy"
        },
        {
            "question": "What is Blue Cross's policy on prior authorization?",
            "ground_truth": "Blue Cross requires prior authorization for all procedures over $5,000 and all elective surgeries. Authorization must be obtained within 3 business days of the scheduled procedure.",
            "category": "policy"
        },
        {
            "question": "What happens if a claim is denied by United Healthcare?",
            "ground_truth": "If a claim is denied by United Healthcare, the provider has 90 days from the denial date to submit an appeal with supporting documentation.",
            "category": "policy"
        },
        {
            "question": "What is Aetna's policy on claim submission deadlines?",
            "ground_truth": "Aetna requires that all claims must be submitted within 120 days of the date of service, or the claim will be denied as untimely.",
            "category": "policy"
        },
        {
            "question": "When does the United Healthcare contract expire?",
            "ground_truth": "The United Healthcare contract expires on December 31, 2026.",
            "category": "policy"
        },
        {
            "question": "What is Blue Cross's claim submission deadline?",
            "ground_truth": "Blue Cross requires all claims to be submitted within 90 days of the date of service.",
            "category": "policy"
        },
        {
            "question": "What is the termination notice period for the Aetna contract?",
            "ground_truth": "Either party may terminate the Aetna contract with 90 days written notice to the other party.",
            "category": "policy"
        },
        {
            "question": "Does United Healthcare require prior authorization for MRI procedures?",
            "ground_truth": "Yes, United Healthcare requires prior authorization for all advanced imaging procedures, including MRIs, with authorization obtained at least 48 hours before the procedure.",
            "category": "policy"
        },
        {
            "question": "What is Blue Cross's policy on timely payment?",
            "ground_truth": "Blue Cross commits to paying all clean claims within 30 days of receipt, as stated in their Net 30 payment terms.",
            "category": "policy"
        },

        # ===== Rate Calculations & Analysis (10 questions) =====
        {
            "question": "If a provider performs 10 CPT 99213 visits with United Healthcare, what is the total expected reimbursement?",
            "ground_truth": "For 10 CPT 99213 visits at $90.00 each, the total expected reimbursement from United Healthcare is $900.00.",
            "category": "calculation"
        },
        {
            "question": "What is the revenue difference between performing a CPT 27447 procedure with Blue Cross versus Aetna?",
            "ground_truth": "The revenue difference for CPT 27447 (Total Knee Arthroplasty) between Blue Cross ($16,000.00) and Aetna ($15,000.00) is $1,000.00.",
            "category": "calculation"
        },
        {
            "question": "If a provider bills United Healthcare for CPT 99214 but receives only $100, what is the underpayment amount?",
            "ground_truth": "If United Healthcare pays only $100 for CPT 99214 instead of the contracted rate of $120.00, the underpayment is $20.00.",
            "category": "calculation"
        },
        {
            "question": "What is the total reimbursement for performing CPT 99213, CPT 99214, and CPT 99215 with Aetna?",
            "ground_truth": "The total reimbursement from Aetna for CPT 99213 ($85.00), CPT 99214 ($125.00), and CPT 99215 ($165.00) is $375.00.",
            "category": "calculation"
        },
        {
            "question": "How much more does Blue Cross pay for CPT 99214 compared to United Healthcare?",
            "ground_truth": "Blue Cross pays $128.00 for CPT 99214 while United Healthcare pays $120.00, so Blue Cross pays $8.00 more.",
            "category": "calculation"
        },
        {
            "question": "What is the total expected revenue from performing 5 knee surgeries (CPT 27447) with Blue Cross?",
            "ground_truth": "For 5 knee surgeries (CPT 27447) at $16,000.00 each with Blue Cross, the total expected revenue is $80,000.00.",
            "category": "calculation"
        },
        {
            "question": "If Aetna takes 45 days to pay and United Healthcare takes 30 days, what is the payment delay difference?",
            "ground_truth": "The payment delay difference between Aetna (Net 45 days) and United Healthcare (Net 30 days) is 15 days.",
            "category": "calculation"
        },
        {
            "question": "What is the percentage difference between the highest and lowest reimbursement rates for CPT 99213?",
            "ground_truth": "The highest rate for CPT 99213 is $90.00 (United Healthcare) and the lowest is $85.00 (Aetna). The percentage difference is approximately 5.88%.",
            "category": "calculation"
        },
        {
            "question": "How much would a provider lose by choosing Aetna over Blue Cross for 10 knee surgeries (CPT 27447)?",
            "ground_truth": "For 10 knee surgeries, Blue Cross pays $160,000 ($16,000 × 10) while Aetna pays $150,000 ($15,000 × 10). The provider would lose $10,000 by choosing Aetna.",
            "category": "calculation"
        },
        {
            "question": "What is the combined value of performing CPT 73721, CPT 99285, and CPT 29881 with United Healthcare?",
            "ground_truth": "The combined reimbursement from United Healthcare for CPT 73721 ($180.00), CPT 99285 ($400.00), and CPT 29881 ($2,300.00) is $2,880.00.",
            "category": "calculation"
        },

        # ===== Complex Multi-Step Queries (10 questions) =====
        {
            "question": "Which payer should a provider choose for maximizing revenue on office visits (CPT 99213-99215)?",
            "ground_truth": "For office visits, the optimal payer varies by level: United Healthcare for 99213 ($90 vs $88 vs $85) and 99215 ($170 vs $165 vs $160), and Blue Cross for 99214 ($128 vs $125 vs $120). Overall, Blue Cross and United Healthcare are competitive for maximum office visit revenue.",
            "category": "complex"
        },
        {
            "question": "What are the key differences in contract terms between United Healthcare and Aetna?",
            "ground_truth": "Key differences: United Healthcare has Net 30 payment terms vs Aetna's Net 45; United Healthcare requires 48-hour prior auth for imaging vs Aetna's varying requirements; United Healthcare's contract runs through 12/31/2026 like Aetna's. Payment speed is faster with United Healthcare.",
            "category": "complex"
        },
        {
            "question": "If a provider performs a mix of 20 office visits and 2 knee surgeries monthly, which payer maximizes revenue?",
            "ground_truth": "Assuming a balanced mix of office visit levels (99213-99215) and knee surgeries (CPT 27447), Blue Cross would maximize revenue due to the highest rate for knee surgery ($16,000) which far outweighs small office visit rate differences. The 2 knee surgeries contribute $32,000 with Blue Cross vs $31,000 with United Healthcare and $30,000 with Aetna.",
            "category": "complex"
        },
        {
            "question": "What are the prior authorization requirements across all three payers?",
            "ground_truth": "United Healthcare requires prior authorization 48 hours before advanced imaging procedures. Blue Cross requires prior authorization for all procedures over $5,000 and elective surgeries within 3 business days of the procedure. Aetna's specific prior authorization requirements would need to be referenced from the full contract terms.",
            "category": "complex"
        },
        {
            "question": "Which payer has the most provider-friendly payment and authorization policies?",
            "ground_truth": "United Healthcare has the most provider-friendly policies: fastest payment terms (Net 30), clear 48-hour prior auth timeline for imaging, and 90-day appeal window for denials. Blue Cross also has Net 30 payment but requires 3-day prior auth for procedures over $5,000, making it slightly less flexible.",
            "category": "complex"
        },
        {
            "question": "What is the contract number for each payer?",
            "ground_truth": "United Healthcare contract number is UHC-2024-7589, Aetna contract number is AET-2024-3421, and Blue Cross contract number is BCBS-2024-9876.",
            "category": "complex"
        },
        {
            "question": "For a high-volume orthopedic practice, which payer offers the best overall rates?",
            "ground_truth": "For a high-volume orthopedic practice, Blue Cross offers the best overall rates: highest knee surgery rate ($16,000 for CPT 27447), competitive knee arthroscopy rate ($2,450 for CPT 29881), and highest MRI rate ($185 for CPT 73721). This makes Blue Cross optimal for orthopedic procedures.",
            "category": "complex"
        },
        {
            "question": "What are the claim appeal timeframes for each payer?",
            "ground_truth": "United Healthcare allows 90 days from denial date to submit an appeal. Blue Cross and Aetna's specific appeal timeframes would need to be referenced from their full contract terms, though industry standard is typically 60-90 days.",
            "category": "complex"
        },
        {
            "question": "Which CPT codes have the largest rate variance across payers?",
            "ground_truth": "CPT 27447 (Total Knee Arthroplasty) has the largest absolute rate variance at $1,000 ($16,000 Blue Cross vs $15,000 Aetna). CPT 99214 has notable variance of $8 ($128 Blue Cross vs $120 United Healthcare). The percentage variance is highest for CPT 99213 at approximately 5.9% difference.",
            "category": "complex"
        },
        {
            "question": "If all contracts expire simultaneously, what is the renewal consideration period?",
            "ground_truth": "All three contracts (United Healthcare, Aetna, and Blue Cross) expire on December 31, 2026. Considering Aetna requires 90-day termination notice, providers should begin renewal negotiations by early October 2026 to ensure continuous coverage.",
            "category": "complex"
        }
    ]

    return dataset


def get_dataset_summary() -> Dict[str, int]:
    """Returns a summary of the test dataset by category."""
    dataset = get_test_dataset()
    categories = {}
    for item in dataset:
        category = item['category']
        categories[category] = categories.get(category, 0) + 1

    return {
        'total_questions': len(dataset),
        'by_category': categories
    }


if __name__ == "__main__":
    # Print dataset summary
    summary = get_dataset_summary()
    print(f"Test Dataset Summary")
    print(f"=" * 50)
    print(f"Total Questions: {summary['total_questions']}")
    print(f"\nBreakdown by Category:")
    for category, count in sorted(summary['by_category'].items()):
        print(f"  - {category}: {count} questions")
