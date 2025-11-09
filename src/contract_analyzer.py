"""
Enhanced Healthcare Contract Analyzer

This module extends the basic RAG pipeline with healthcare contract-specific
features including rate comparison, contract summary extraction, and
underpayment detection.
"""

import re
import pandas as pd
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging

from rag_pipeline import HealthcareContractRAG

logger = logging.getLogger(__name__)


class ContractAnalyzer(HealthcareContractRAG):
    """
    Enhanced RAG system with healthcare contract analysis capabilities.

    Extends base HealthcareContractRAG with:
    - CPT code rate extraction
    - Multi-contract comparison
    - Underpayment detection
    - Contract summaries
    - Best rate finding
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.contract_data = {}

    def extract_cpt_rates(self, payer_name: Optional[str] = None) -> pd.DataFrame:
        """
        Extract CPT code rates from all contracts or a specific payer.

        Args:
            payer_name: Optional payer name to filter results

        Returns:
            DataFrame with columns: payer, cpt_code, description, rate
        """
        try:
            logger.info(f"Extracting CPT rates for {payer_name if payer_name else 'all payers'}")

            query = f"""
            Extract all CPT codes and their reimbursement rates from the
            {payer_name + ' ' if payer_name else ''}contract(s).
            List each CPT code with its exact dollar amount in a structured format.
            Include the payer name for each rate.
            """

            result = self.ask_question(query)

            # Parse the response to extract structured data
            rates_data = self._parse_rates_from_response(result['answer'])

            return pd.DataFrame(rates_data)

        except Exception as e:
            logger.error(f"Error extracting CPT rates: {str(e)}")
            raise

    def _parse_rates_from_response(self, response: str) -> List[Dict]:
        """Parse CPT rates from LLM response."""
        rates = []

        # Pattern to match CPT codes and dollar amounts
        # Example: "CPT 99213: $85.00" or "99213 - $85"
        pattern = r'CPT\s*(\d{5})[:\s-]+\$?([\d,]+\.?\d*)'

        matches = re.finditer(pattern, response, re.IGNORECASE)

        for match in matches:
            cpt_code = match.group(1)
            rate = float(match.group(2).replace(',', ''))
            rates.append({
                'cpt_code': cpt_code,
                'rate': rate
            })

        return rates

    def compare_rates(self, cpt_code: str) -> Dict:
        """
        Compare rates across all payers for a specific CPT code.

        Args:
            cpt_code: CPT code to compare

        Returns:
            Dictionary with comparison results including best and worst rates
        """
        try:
            logger.info(f"Comparing rates for CPT {cpt_code}")

            query = f"""
            Compare the reimbursement rates for CPT code {cpt_code} across all payer contracts.
            For each payer, provide:
            1. Payer name
            2. Exact reimbursement rate in dollars
            3. Payment terms (e.g., Net 30 days)

            Then identify which payer offers the highest rate and which offers the lowest.
            Calculate the difference between highest and lowest rates.
            """

            result = self.ask_question(query)

            return {
                'cpt_code': cpt_code,
                'comparison': result['answer'],
                'sources': result['source_documents']
            }

        except Exception as e:
            logger.error(f"Error comparing rates: {str(e)}")
            raise

    def find_best_rate(self, cpt_code: str) -> Dict:
        """
        Find the payer with the highest rate for a CPT code.

        Args:
            cpt_code: CPT code to analyze

        Returns:
            Dictionary with best payer and rate information
        """
        try:
            logger.info(f"Finding best rate for CPT {cpt_code}")

            query = f"""
            Which payer offers the highest reimbursement rate for CPT code {cpt_code}?

            Provide:
            1. Payer name
            2. Exact rate amount
            3. How much more this is compared to other payers (percentage and dollar amount)
            4. Any special terms or modifiers that affect this rate
            """

            result = self.ask_question(query)

            return {
                'cpt_code': cpt_code,
                'analysis': result['answer'],
                'sources': result['source_documents']
            }

        except Exception as e:
            logger.error(f"Error finding best rate: {str(e)}")
            raise

    def get_payment_terms_summary(self) -> Dict:
        """
        Get summary of payment terms across all contracts.

        Returns:
            Dictionary with payment terms for each payer
        """
        try:
            logger.info("Extracting payment terms summary")

            query = """
            Summarize the payment terms for all payer contracts.

            For each payer, include:
            1. Payer name
            2. Payment timeframe (e.g., Net 30 days)
            3. Interest rate on late payments (if specified)
            4. Claim submission deadline
            5. Appeal timeframe

            Compare which payer has the most favorable payment terms for providers.
            """

            result = self.ask_question(query)

            return {
                'summary': result['answer'],
                'sources': result['source_documents']
            }

        except Exception as e:
            logger.error(f"Error getting payment terms: {str(e)}")
            raise

    def analyze_modifiers(self) -> Dict:
        """
        Analyze modifier reimbursement across contracts.

        Returns:
            Dictionary with modifier analysis
        """
        try:
            logger.info("Analyzing modifier reimbursement")

            query = """
            Compare the modifier reimbursement policies across all payer contracts.

            Focus on:
            1. Modifier 25 reimbursement amounts for each payer
            2. Modifier 59 reimbursement
            3. Modifier 76 reimbursement percentages
            4. Which payer has the most favorable modifier policies

            Calculate potential revenue impact if a practice performs 100 procedures
            per month with modifier 25.
            """

            result = self.ask_question(query)

            return {
                'analysis': result['answer'],
                'sources': result['source_documents']
            }

        except Exception as e:
            logger.error(f"Error analyzing modifiers: {str(e)}")
            raise

    def detect_underpayments(self, benchmark_cpt: str, benchmark_rate: float) -> Dict:
        """
        Detect which payers pay below a benchmark rate.

        Args:
            benchmark_cpt: CPT code to check
            benchmark_rate: Benchmark rate (e.g., Medicare rate)

        Returns:
            Dictionary with underpayment analysis
        """
        try:
            logger.info(f"Detecting underpayments for CPT {benchmark_cpt} vs ${benchmark_rate}")

            query = f"""
            Compare all payer reimbursement rates for CPT code {benchmark_cpt}
            against a benchmark rate of ${benchmark_rate:.2f}.

            For each payer:
            1. State their rate
            2. Calculate if they pay above or below benchmark
            3. Calculate the dollar difference and percentage difference
            4. Identify if this represents an underpayment concern

            Provide recommendations for contract renegotiation where rates are below benchmark.
            """

            result = self.ask_question(query)

            return {
                'cpt_code': benchmark_cpt,
                'benchmark_rate': benchmark_rate,
                'analysis': result['answer'],
                'sources': result['source_documents']
            }

        except Exception as e:
            logger.error(f"Error detecting underpayments: {str(e)}")
            raise

    def calculate_revenue_impact(
        self,
        cpt_code: str,
        monthly_volume: int,
        current_payer: str,
        comparison_payer: str
    ) -> Dict:
        """
        Calculate revenue impact of switching payers or renegotiating.

        Args:
            cpt_code: CPT code to analyze
            monthly_volume: Number of procedures per month
            current_payer: Current payer name
            comparison_payer: Payer to compare against

        Returns:
            Dictionary with revenue impact analysis
        """
        try:
            logger.info(f"Calculating revenue impact for {cpt_code} between {current_payer} and {comparison_payer}")

            query = f"""
            Calculate the revenue impact analysis for CPT code {cpt_code}.

            Given:
            - Monthly procedure volume: {monthly_volume}
            - Current payer: {current_payer}
            - Comparison payer: {comparison_payer}

            Calculate:
            1. Current payer's rate per procedure
            2. Comparison payer's rate per procedure
            3. Rate difference per procedure
            4. Monthly revenue difference ({monthly_volume} procedures)
            5. Annual revenue impact (12 months)

            Provide business recommendation on whether switching payers or
            renegotiating would be financially beneficial.
            """

            result = self.ask_question(query)

            return {
                'cpt_code': cpt_code,
                'monthly_volume': monthly_volume,
                'current_payer': current_payer,
                'comparison_payer': comparison_payer,
                'analysis': result['answer'],
                'sources': result['source_documents']
            }

        except Exception as e:
            logger.error(f"Error calculating revenue impact: {str(e)}")
            raise

    def get_prior_auth_requirements(self) -> Dict:
        """
        Extract and compare prior authorization requirements.

        Returns:
            Dictionary with prior auth requirements for each payer
        """
        try:
            logger.info("Extracting prior authorization requirements")

            query = """
            Compare prior authorization requirements across all payer contracts.

            For each payer, list:
            1. Services requiring prior authorization
            2. How requirements differ between payers
            3. Which payer has the most restrictive requirements
            4. Which has the most provider-friendly policies

            Highlight any services that require auth with some payers but not others.
            """

            result = self.ask_question(query)

            return {
                'analysis': result['answer'],
                'sources': result['source_documents']
            }

        except Exception as e:
            logger.error(f"Error getting prior auth requirements: {str(e)}")
            raise

    def analyze_denial_policies(self) -> Dict:
        """
        Analyze denial and appeal policies across contracts.

        Returns:
            Dictionary with denial policy analysis
        """
        try:
            logger.info("Analyzing denial and appeal policies")

            query = """
            Compare denial and appeal policies across all payer contracts.

            For each payer, analyze:
            1. Common denial reasons listed in contract
            2. Appeal timeframe (how many days to appeal)
            3. Number of appeal levels available
            4. Any unique or unfavorable denial clauses

            Identify which payer has the most provider-friendly appeal process
            and which has the most restrictive policies.
            """

            result = self.ask_question(query)

            return {
                'analysis': result['answer'],
                'sources': result['source_documents']
            }

        except Exception as e:
            logger.error(f"Error analyzing denial policies: {str(e)}")
            raise

    def generate_contract_summary(self, payer_name: str) -> Dict:
        """
        Generate comprehensive summary of a specific contract.

        Args:
            payer_name: Name of payer to summarize

        Returns:
            Dictionary with comprehensive contract summary
        """
        try:
            logger.info(f"Generating contract summary for {payer_name}")

            query = f"""
            Provide a comprehensive summary of the {payer_name} contract.

            Include:
            1. Contract basics (effective dates, contract number)
            2. Top 5 most common CPT code rates (office visits, procedures)
            3. Payment terms and timing
            4. Modifier reimbursement policies
            5. Prior authorization requirements
            6. Appeal timeframes and process
            7. Termination notice period
            8. Any unique or notable contract clauses

            Highlight any provisions that could impact revenue or operational efficiency.
            """

            result = self.ask_question(query)

            return {
                'payer': payer_name,
                'summary': result['answer'],
                'sources': result['source_documents']
            }

        except Exception as e:
            logger.error(f"Error generating contract summary: {str(e)}")
            raise

    def generate_negotiation_report(self, current_payer: str) -> Dict:
        """
        Generate a contract negotiation report for a payer.

        Args:
            current_payer: Payer to analyze for negotiation

        Returns:
            Dictionary with negotiation talking points
        """
        try:
            logger.info(f"Generating negotiation report for {current_payer}")

            query = f"""
            Generate a contract negotiation analysis for {current_payer}.

            Compare {current_payer}'s rates and terms against the other payers to identify:

            1. CPT codes where {current_payer} pays significantly below competitors
               (list specific codes and the rate gaps)

            2. Payment terms comparison (identify if {current_payer}'s payment timing
               is slower than competitors)

            3. Modifier policies comparison (identify if {current_payer} pays less
               for modifiers than competitors)

            4. Prior authorization requirements (identify if {current_payer} has
               more restrictive requirements than competitors)

            5. Recommended negotiation priorities (which rates or terms to focus on
               for maximum revenue impact)

            6. Estimated annual revenue opportunity if rates were increased to match
               the highest-paying competitor

            Present this as a business case for contract renegotiation.
            """

            result = self.ask_question(query)

            return {
                'payer': current_payer,
                'negotiation_analysis': result['answer'],
                'sources': result['source_documents']
            }

        except Exception as e:
            logger.error(f"Error generating negotiation report: {str(e)}")
            raise
