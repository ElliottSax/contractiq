"""
Utility Functions for Healthcare Contract Analysis

This module provides utility functions for underpayment calculations,
report generation, and data export.
"""

import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import csv
import logging

logger = logging.getLogger(__name__)


class UnderpaymentCalculator:
    """Calculate and analyze underpayments against contract rates."""

    @staticmethod
    def calculate_underpayment(
        expected_rate: float,
        actual_payment: float,
        quantity: int = 1
    ) -> Dict:
        """
        Calculate underpayment amount and percentage.

        Args:
            expected_rate: Expected contract rate per unit
            actual_payment: Actual payment received per unit
            quantity: Number of units/procedures

        Returns:
            Dictionary with underpayment analysis
        """
        expected_total = expected_rate * quantity
        actual_total = actual_payment * quantity
        underpayment_amount = expected_total - actual_total
        underpayment_percent = (underpayment_amount / expected_total * 100) if expected_total > 0 else 0

        return {
            'expected_rate': expected_rate,
            'actual_payment': actual_payment,
            'quantity': quantity,
            'expected_total': expected_total,
            'actual_total': actual_total,
            'underpayment_amount': underpayment_amount,
            'underpayment_percent': underpayment_percent,
            'is_underpaid': underpayment_amount > 0
        }

    @staticmethod
    def generate_appeal_letter(
        payer_name: str,
        patient_name: str,
        claim_number: str,
        cpt_code: str,
        expected_rate: float,
        actual_payment: float,
        date_of_service: str,
        contract_reference: str = ""
    ) -> str:
        """
        Generate a draft appeal letter for underpayment.

        Args:
            payer_name: Name of insurance payer
            patient_name: Patient name
            claim_number: Claim number
            cpt_code: CPT code for service
            expected_rate: Expected contract rate
            actual_payment: Actual payment received
            date_of_service: Date of service
            contract_reference: Optional contract reference number

        Returns:
            Formatted appeal letter text
        """
        underpayment = expected_rate - actual_payment
        today = datetime.now().strftime("%B %d, %Y")

        letter = f"""
[Provider Name]
[Provider Address]
[Provider Tax ID]

{today}

{payer_name}
Claims Appeals Department
[Payer Address]

RE: APPEAL FOR UNDERPAYMENT
Claim Number: {claim_number}
Patient: {patient_name}
Date of Service: {date_of_service}
CPT Code: {cpt_code}

Dear Appeals Coordinator,

I am writing to appeal the underpayment of the above-referenced claim. Our contracted rate
for CPT code {cpt_code} is ${expected_rate:.2f} as specified in our provider agreement{
' (' + contract_reference + ')' if contract_reference else ''}.

PAYMENT DISCREPANCY:
- Contract Rate: ${expected_rate:.2f}
- Payment Received: ${actual_payment:.2f}
- Underpayment: ${underpayment:.2f}

The service was medically necessary, properly documented, and billed in accordance with
current CPT coding guidelines. This claim should be reprocessed at the contracted rate.

REQUESTED ACTION:
Please issue additional payment of ${underpayment:.2f} to correct this underpayment.

I request a response to this appeal within 30 days as specified in our provider agreement.
If you require additional documentation, please contact our billing department.

Thank you for your prompt attention to this matter.

Sincerely,

[Provider Name]
[Provider Contact Information]

Enclosures:
- Copy of contract fee schedule
- Copy of original claim
- Copy of EOB showing underpayment
"""
        return letter


class ReportExporter:
    """Export contract analysis results to various formats."""

    @staticmethod
    def export_to_csv(data: List[Dict], filename: str, output_dir: str = "outputs") -> Path:
        """
        Export data to CSV file.

        Args:
            data: List of dictionaries to export
            filename: Output filename (without extension)
            output_dir: Output directory

        Returns:
            Path to created CSV file
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True, parents=True)

            csv_path = output_path / f"{filename}.csv"

            if data:
                df = pd.DataFrame(data)
                df.to_csv(csv_path, index=False)
                logger.info(f"Exported data to {csv_path}")
                return csv_path
            else:
                logger.warning("No data to export")
                return None

        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            raise

    @staticmethod
    def export_rate_comparison(
        comparison_data: Dict,
        filename: str = "rate_comparison",
        output_dir: str = "outputs"
    ) -> Path:
        """
        Export rate comparison to CSV.

        Args:
            comparison_data: Rate comparison dictionary
            filename: Output filename
            output_dir: Output directory

        Returns:
            Path to CSV file
        """
        try:
            # Convert comparison data to list of dicts for CSV
            rows = []
            for cpt_code, payers in comparison_data.items():
                for payer, rate in payers.items():
                    rows.append({
                        'CPT_Code': cpt_code,
                        'Payer': payer,
                        'Rate': rate
                    })

            return ReportExporter.export_to_csv(rows, filename, output_dir)

        except Exception as e:
            logger.error(f"Error exporting rate comparison: {str(e)}")
            raise

    @staticmethod
    def create_fee_schedule_export(
        cpt_rates: Dict[str, Dict[str, float]],
        output_dir: str = "outputs"
    ) -> Path:
        """
        Create a comprehensive fee schedule export.

        Args:
            cpt_rates: Dictionary of {cpt_code: {payer: rate}}
            output_dir: Output directory

        Returns:
            Path to created Excel file
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True, parents=True)

            excel_path = output_path / f"fee_schedule_{datetime.now().strftime('%Y%m%d')}.xlsx"

            # Create DataFrame
            data = []
            for cpt_code, payer_rates in cpt_rates.items():
                row = {'CPT_Code': cpt_code}
                row.update(payer_rates)
                data.append(row)

            df = pd.DataFrame(data)

            # Write to Excel with formatting
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Fee Schedule', index=False)

            logger.info(f"Created fee schedule export at {excel_path}")
            return excel_path

        except Exception as e:
            logger.error(f"Error creating fee schedule export: {str(e)}")
            raise


class ContractComparison:
    """Tools for comparing multiple contracts side-by-side."""

    @staticmethod
    def create_comparison_table(
        rates_by_payer: Dict[str, Dict[str, float]]
    ) -> pd.DataFrame:
        """
        Create a comparison table showing rates across payers.

        Args:
            rates_by_payer: Dictionary of {payer: {cpt_code: rate}}

        Returns:
            DataFrame with comparison
        """
        try:
            # Restructure data for comparison
            all_cpt_codes = set()
            for payer_rates in rates_by_payer.values():
                all_cpt_codes.update(payer_rates.keys())

            comparison_data = []
            for cpt_code in sorted(all_cpt_codes):
                row = {'CPT_Code': cpt_code}
                for payer, rates in rates_by_payer.items():
                    row[payer] = rates.get(cpt_code, None)
                comparison_data.append(row)

            df = pd.DataFrame(comparison_data)

            # Add analysis columns
            if len(rates_by_payer) > 1:
                payer_columns = [col for col in df.columns if col != 'CPT_Code']

                # Add highest/lowest columns
                df['Highest_Rate'] = df[payer_columns].max(axis=1)
                df['Lowest_Rate'] = df[payer_columns].min(axis=1)
                df['Rate_Variance'] = df['Highest_Rate'] - df['Lowest_Rate']
                df['Variance_Percent'] = (df['Rate_Variance'] / df['Lowest_Rate'] * 100).round(2)

            return df

        except Exception as e:
            logger.error(f"Error creating comparison table: {str(e)}")
            raise

    @staticmethod
    def identify_best_payer_by_cpt(
        rates_by_payer: Dict[str, Dict[str, float]]
    ) -> Dict[str, Dict]:
        """
        Identify which payer pays best for each CPT code.

        Args:
            rates_by_payer: Dictionary of {payer: {cpt_code: rate}}

        Returns:
            Dictionary of {cpt_code: {best_payer, rate, advantage}}
        """
        try:
            all_cpt_codes = set()
            for payer_rates in rates_by_payer.values():
                all_cpt_codes.update(payer_rates.keys())

            best_payers = {}

            for cpt_code in all_cpt_codes:
                rates = {}
                for payer, payer_rates in rates_by_payer.items():
                    if cpt_code in payer_rates:
                        rates[payer] = payer_rates[cpt_code]

                if rates:
                    best_payer = max(rates, key=rates.get)
                    best_rate = rates[best_payer]
                    avg_rate = sum(rates.values()) / len(rates)
                    advantage = best_rate - avg_rate

                    best_payers[cpt_code] = {
                        'best_payer': best_payer,
                        'rate': best_rate,
                        'average_rate': avg_rate,
                        'advantage': advantage,
                        'advantage_percent': (advantage / avg_rate * 100) if avg_rate > 0 else 0
                    }

            return best_payers

        except Exception as e:
            logger.error(f"Error identifying best payers: {str(e)}")
            raise

    @staticmethod
    def calculate_payer_mix_impact(
        current_volumes: Dict[str, int],
        current_payer: str,
        target_payer: str,
        rates_by_payer: Dict[str, Dict[str, float]]
    ) -> Dict:
        """
        Calculate revenue impact of changing payer mix.

        Args:
            current_volumes: Dictionary of {cpt_code: monthly_volume}
            current_payer: Current payer name
            target_payer: Target payer name
            rates_by_payer: Dictionary of {payer: {cpt_code: rate}}

        Returns:
            Dictionary with impact analysis
        """
        try:
            current_rates = rates_by_payer.get(current_payer, {})
            target_rates = rates_by_payer.get(target_payer, {})

            impact_by_cpt = {}
            total_current_revenue = 0
            total_target_revenue = 0

            for cpt_code, volume in current_volumes.items():
                current_rate = current_rates.get(cpt_code, 0)
                target_rate = target_rates.get(cpt_code, 0)

                current_revenue = current_rate * volume
                target_revenue = target_rate * volume
                difference = target_revenue - current_revenue

                impact_by_cpt[cpt_code] = {
                    'volume': volume,
                    'current_rate': current_rate,
                    'target_rate': target_rate,
                    'current_revenue': current_revenue,
                    'target_revenue': target_revenue,
                    'monthly_difference': difference,
                    'annual_difference': difference * 12
                }

                total_current_revenue += current_revenue
                total_target_revenue += target_revenue

            total_monthly_impact = total_target_revenue - total_current_revenue
            total_annual_impact = total_monthly_impact * 12

            return {
                'current_payer': current_payer,
                'target_payer': target_payer,
                'by_cpt_code': impact_by_cpt,
                'total_current_monthly_revenue': total_current_revenue,
                'total_target_monthly_revenue': total_target_revenue,
                'total_monthly_impact': total_monthly_impact,
                'total_annual_impact': total_annual_impact,
                'percent_change': (total_monthly_impact / total_current_revenue * 100) if total_current_revenue > 0 else 0
            }

        except Exception as e:
            logger.error(f"Error calculating payer mix impact: {str(e)}")
            raise
