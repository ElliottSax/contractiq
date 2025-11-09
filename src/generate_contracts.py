"""
Generate Synthetic Healthcare Payer Contract PDFs

This script generates realistic healthcare payer contract PDFs for testing
the RAG system. Each contract includes fee schedules, payment terms, and
standard contract language.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from datetime import datetime
import os


def create_contract_pdf(filename, contract_data):
    """
    Create a professional healthcare payer contract PDF.

    Args:
        filename: Output PDF filename
        contract_data: Dictionary containing contract information
    """
    doc = SimpleDocTemplate(filename, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CustomTitle',
                             parent=styles['Heading1'],
                             fontSize=18,
                             textColor=colors.HexColor('#003366'),
                             spaceAfter=30,
                             alignment=TA_CENTER,
                             fontName='Helvetica-Bold'))

    styles.add(ParagraphStyle(name='SectionHeader',
                             parent=styles['Heading2'],
                             fontSize=14,
                             textColor=colors.HexColor('#003366'),
                             spaceAfter=12,
                             spaceBefore=12,
                             fontName='Helvetica-Bold'))

    styles.add(ParagraphStyle(name='ContractBody',
                             parent=styles['BodyText'],
                             fontSize=10,
                             alignment=TA_JUSTIFY,
                             spaceAfter=12))

    # Title
    title = Paragraph(f"HEALTHCARE PROVIDER AGREEMENT<br/>{contract_data['payer_name']}",
                     styles['CustomTitle'])
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))

    # Contract Information
    contract_info = f"""
    <b>Contract Number:</b> {contract_data['contract_number']}<br/>
    <b>Effective Date:</b> {contract_data['start_date']}<br/>
    <b>Expiration Date:</b> {contract_data['end_date']}<br/>
    <b>Provider Type:</b> {contract_data['provider_type']}<br/>
    <b>Network Type:</b> {contract_data['network_type']}
    """
    elements.append(Paragraph(contract_info, styles['ContractBody']))
    elements.append(Spacer(1, 0.3*inch))

    # Article 1: Definitions
    elements.append(Paragraph("ARTICLE 1: DEFINITIONS", styles['SectionHeader']))
    definitions = """
    <b>1.1 Covered Services:</b> Medically necessary healthcare services provided to Members
    as defined in the applicable benefit plan documents and this Agreement.<br/><br/>

    <b>1.2 Member:</b> An individual enrolled in a health benefit plan offered by the Payer
    and entitled to receive Covered Services under such plan.<br/><br/>

    <b>1.3 Provider:</b> Healthcare professional or facility authorized to provide Covered
    Services to Members under the terms of this Agreement.<br/><br/>

    <b>1.4 Clean Claim:</b> A claim for payment that contains all necessary information
    required for adjudication without the need for additional documentation.
    """
    elements.append(Paragraph(definitions, styles['ContractBody']))
    elements.append(Spacer(1, 0.2*inch))

    # Article 2: Reimbursement
    elements.append(Paragraph("ARTICLE 2: REIMBURSEMENT RATES", styles['SectionHeader']))
    reimbursement_intro = f"""
    Provider shall be reimbursed for Covered Services according to the Fee Schedule
    attached hereto and incorporated by reference. All rates are effective as of
    {contract_data['start_date']} and remain in effect through {contract_data['end_date']}
    unless modified by written amendment.
    """
    elements.append(Paragraph(reimbursement_intro, styles['ContractBody']))
    elements.append(Spacer(1, 0.2*inch))

    # Fee Schedule Table
    elements.append(Paragraph("<b>Fee Schedule - Professional Services</b>", styles['ContractBody']))

    fee_data = [['CPT Code', 'Service Description', 'Reimbursement Rate']]
    for cpt, description, rate in contract_data['fee_schedule']:
        fee_data.append([cpt, description, f"${rate:,.2f}"])

    fee_table = Table(fee_data, colWidths=[1.2*inch, 3.5*inch, 1.5*inch])
    fee_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))

    elements.append(fee_table)
    elements.append(Spacer(1, 0.3*inch))

    # Modifier Rules
    elements.append(Paragraph("<b>2.1 Modifier Reimbursement</b>", styles['ContractBody']))
    modifier_text = f"""
    The following modifiers shall be reimbursed in addition to the base procedure rate:<br/>
    <b>• Modifier 25:</b> Significant, separately identifiable evaluation and management
    service - Additional ${contract_data['modifier_25_amount']:.2f}<br/>
    <b>• Modifier 59:</b> Distinct procedural service - Additional ${contract_data.get('modifier_59_amount', 0):.2f}<br/>
    <b>• Modifier 76:</b> Repeat procedure by same physician - {contract_data.get('modifier_76_percent', 100)}% of base rate
    """
    elements.append(Paragraph(modifier_text, styles['ContractBody']))
    elements.append(Spacer(1, 0.2*inch))

    # Page Break
    elements.append(PageBreak())

    # Article 3: Payment Terms
    elements.append(Paragraph("ARTICLE 3: PAYMENT TERMS", styles['SectionHeader']))
    payment_terms = f"""
    <b>3.1 Payment Timeframe:</b> Payer shall remit payment for all Clean Claims within
    {contract_data['payment_terms']} from the date of receipt. Interest shall accrue on
    unpaid Clean Claims at the rate of {contract_data.get('interest_rate', '1.5%')} per month
    after the payment deadline.<br/><br/>

    <b>3.2 Electronic Funds Transfer:</b> All payments shall be made via electronic funds
    transfer (EFT) to the Provider's designated bank account. Electronic Remittance Advice
    (ERA) shall accompany all payments.<br/><br/>

    <b>3.3 Coordination of Benefits:</b> When a Member has coverage under multiple health
    plans, reimbursement shall be coordinated according to applicable state and federal
    regulations. Provider agrees to bill the primary payer first.<br/><br/>

    <b>3.4 Claim Submission Requirements:</b> All claims must be submitted electronically
    using the ANSI X12N 837 format within {contract_data.get('claim_submission_days', 90)}
    days of the date of service. Claims submitted after this timeframe may be denied.
    """
    elements.append(Paragraph(payment_terms, styles['ContractBody']))
    elements.append(Spacer(1, 0.2*inch))

    # Article 4: Denial and Appeal Process
    elements.append(Paragraph("ARTICLE 4: CLAIMS DENIAL AND APPEAL PROCESS", styles['SectionHeader']))
    denial_text = f"""
    <b>4.1 Denial Reasons:</b> Claims may be denied for the following reasons:<br/>
    • Service not medically necessary<br/>
    • Service not covered under Member's benefit plan<br/>
    • Prior authorization not obtained when required<br/>
    • Claim submitted beyond timely filing deadline<br/>
    • Incorrect or incomplete claim information<br/>
    • Duplicate claim submission<br/><br/>

    <b>4.2 Prior Authorization Requirements:</b> The following services require prior
    authorization: {contract_data.get('prior_auth_services', 'Advanced imaging (MRI, CT, PET scans), Inpatient admissions, Surgical procedures over $5,000, Durable medical equipment over $1,000')}<br/><br/>

    <b>4.3 Appeal Rights:</b> Provider has the right to appeal any claim denial within
    {contract_data.get('appeal_days', 180)} days of the denial date. Appeals must be submitted
    in writing with supporting documentation to:<br/>
    {contract_data['payer_name']} Claims Appeals Department<br/>
    P.O. Box {contract_data.get('appeal_po_box', '12345')}<br/>
    {contract_data.get('payer_city', 'New York')}, {contract_data.get('payer_state', 'NY')}
    {contract_data.get('payer_zip', '10001')}<br/><br/>

    <b>4.4 Appeal Process:</b><br/>
    • First Level Appeal: Decision within 30 days<br/>
    • Second Level Appeal: Decision within 60 days<br/>
    • External Review: Available after exhaustion of internal appeals<br/><br/>

    <b>4.5 Reconsideration of Denied Claims:</b> Payer shall reconsider denied claims when
    Provider submits additional documentation supporting medical necessity or corrects claim
    submission errors within the appeal timeframe.
    """
    elements.append(Paragraph(denial_text, styles['ContractBody']))
    elements.append(Spacer(1, 0.2*inch))

    # Article 5: Billing Guidelines
    elements.append(Paragraph("ARTICLE 5: BILLING GUIDELINES", styles['SectionHeader']))
    billing_text = f"""
    <b>5.1 Coding Requirements:</b> Provider shall use current CPT, HCPCS, and ICD-10 codes
    when billing for services. All coding must be accurate and reflect services actually
    rendered.<br/><br/>

    <b>5.2 Documentation Requirements:</b> Provider shall maintain complete and accurate
    medical records supporting all billed services for a minimum of {contract_data.get('record_retention_years', 7)}
    years. Records must be available for Payer review upon request.<br/><br/>

    <b>5.3 Prohibited Billing Practices:</b> Provider shall not engage in upcoding, unbundling,
    or other billing practices that inflate reimbursement beyond the value of services actually
    rendered. Violations may result in contract termination and recovery of overpayments.<br/><br/>

    <b>5.4 Balance Billing Prohibition:</b> Provider agrees not to bill Members for Covered
    Services except for applicable copayments, coinsurance, and deductibles as specified in
    the Member's benefit plan.
    """
    elements.append(Paragraph(billing_text, styles['ContractBody']))

    # Page Break
    elements.append(PageBreak())

    # Article 6: Credentialing
    elements.append(Paragraph("ARTICLE 6: CREDENTIALING AND QUALITY STANDARDS", styles['SectionHeader']))
    credentialing_text = """
    <b>6.1 Initial Credentialing:</b> Provider must complete Payer's credentialing process
    before providing services to Members. This includes verification of licensure, education,
    training, malpractice insurance, and work history.<br/><br/>

    <b>6.2 Recredentialing:</b> Provider shall undergo recredentialing every three (3) years.
    Failure to complete recredentialing may result in network removal.<br/><br/>

    <b>6.3 Quality Metrics:</b> Provider agrees to participate in Payer's quality measurement
    and improvement programs, including HEDIS, patient satisfaction surveys, and clinical
    outcome reporting.
    """
    elements.append(Paragraph(credentialing_text, styles['ContractBody']))
    elements.append(Spacer(1, 0.2*inch))

    # Article 7: Term and Termination
    elements.append(Paragraph("ARTICLE 7: TERM AND TERMINATION", styles['SectionHeader']))
    termination_text = f"""
    <b>7.1 Contract Term:</b> This Agreement is effective {contract_data['start_date']} and
    continues through {contract_data['end_date']}, unless terminated earlier in accordance
    with this Article.<br/><br/>

    <b>7.2 Termination Without Cause:</b> Either party may terminate this Agreement without
    cause upon {contract_data.get('termination_notice_days', 90)} days written notice to the
    other party.<br/><br/>

    <b>7.3 Termination With Cause:</b> Either party may terminate immediately for material
    breach, loss of licensure, fraud, or other cause as specified in the Agreement.<br/><br/>

    <b>7.4 Effect of Termination:</b> Upon termination, Provider shall continue to provide
    services to Members currently under active treatment for up to 90 days to ensure continuity
    of care.
    """
    elements.append(Paragraph(termination_text, styles['ContractBody']))
    elements.append(Spacer(1, 0.3*inch))

    # Signature Block
    signature_data = [
        ['PROVIDER', 'PAYER'],
        ['', ''],
        ['_________________________', '_________________________'],
        ['Signature', 'Signature'],
        ['', ''],
        ['_________________________', '_________________________'],
        ['Printed Name', 'Printed Name'],
        ['', ''],
        ['_________________________', '_________________________'],
        [f'Date: {contract_data["start_date"]}', f'Date: {contract_data["start_date"]}'],
    ]

    signature_table = Table(signature_data, colWidths=[3*inch, 3*inch])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(Spacer(1, 0.3*inch))
    elements.append(signature_table)

    # Build PDF
    doc.build(elements)
    print(f"Generated: {filename}")


def generate_all_contracts():
    """Generate all three synthetic healthcare payer contracts."""

    # United Healthcare Contract
    united_data = {
        'payer_name': 'United Healthcare',
        'contract_number': 'UHC-2024-7589',
        'start_date': 'January 1, 2024',
        'end_date': 'December 31, 2026',
        'provider_type': 'Multi-Specialty Medical Group',
        'network_type': 'Preferred Provider Organization (PPO)',
        'payment_terms': 'Net 30 days',
        'modifier_25_amount': 45.00,
        'modifier_59_amount': 35.00,
        'modifier_76_percent': 75,
        'interest_rate': '1.5%',
        'claim_submission_days': 90,
        'appeal_days': 180,
        'appeal_po_box': '30770',
        'payer_city': 'Minneapolis',
        'payer_state': 'MN',
        'payer_zip': '55430',
        'record_retention_years': 7,
        'termination_notice_days': 90,
        'prior_auth_services': 'MRI, CT, PET scans, Inpatient admissions, Surgeries over $5,000, DME over $1,000, Orthopedic surgeries',
        'fee_schedule': [
            ('99213', 'Office/Outpatient Visit - Level 3 (Established Patient)', 85.00),
            ('99214', 'Office/Outpatient Visit - Level 4 (Established Patient)', 125.00),
            ('99215', 'Office/Outpatient Visit - Level 5 (Established Patient)', 165.00),
            ('99203', 'Office/Outpatient Visit - Level 3 (New Patient)', 105.00),
            ('99204', 'Office/Outpatient Visit - Level 4 (New Patient)', 155.00),
            ('27447', 'Total Knee Arthroplasty (Knee Replacement)', 15000.00),
            ('29881', 'Knee Arthroscopy with Meniscectomy', 3500.00),
            ('93000', 'Electrocardiogram (EKG) Complete', 45.00),
            ('80053', 'Comprehensive Metabolic Panel', 35.00),
            ('71045', 'Chest X-Ray Single View', 65.00),
        ]
    }

    # Aetna Contract
    aetna_data = {
        'payer_name': 'Aetna Insurance',
        'contract_number': 'AET-2024-4432',
        'start_date': 'January 1, 2024',
        'end_date': 'December 31, 2026',
        'provider_type': 'Multi-Specialty Medical Group',
        'network_type': 'Exclusive Provider Organization (EPO)',
        'payment_terms': 'Net 45 days',
        'modifier_25_amount': 40.00,
        'modifier_59_amount': 30.00,
        'modifier_76_percent': 80,
        'interest_rate': '1.25%',
        'claim_submission_days': 120,
        'appeal_days': 180,
        'appeal_po_box': '14079',
        'payer_city': 'Hartford',
        'payer_state': 'CT',
        'payer_zip': '06101',
        'record_retention_years': 10,
        'termination_notice_days': 120,
        'prior_auth_services': 'Advanced imaging, Inpatient stays, Surgical procedures over $3,000, Sleep studies, Home health services',
        'fee_schedule': [
            ('99213', 'Office/Outpatient Visit - Level 3 (Established Patient)', 80.00),
            ('99214', 'Office/Outpatient Visit - Level 4 (Established Patient)', 120.00),
            ('99215', 'Office/Outpatient Visit - Level 5 (Established Patient)', 160.00),
            ('99203', 'Office/Outpatient Visit - Level 3 (New Patient)', 100.00),
            ('99204', 'Office/Outpatient Visit - Level 4 (New Patient)', 150.00),
            ('27447', 'Total Knee Arthroplasty (Knee Replacement)', 14500.00),
            ('29881', 'Knee Arthroscopy with Meniscectomy', 3200.00),
            ('93000', 'Electrocardiogram (EKG) Complete', 42.00),
            ('80053', 'Comprehensive Metabolic Panel', 32.00),
            ('71045', 'Chest X-Ray Single View', 60.00),
        ]
    }

    # Blue Cross Blue Shield Contract
    bcbs_data = {
        'payer_name': 'Blue Cross Blue Shield',
        'contract_number': 'BCBS-2024-9921',
        'start_date': 'January 1, 2024',
        'end_date': 'December 31, 2026',
        'provider_type': 'Multi-Specialty Medical Group',
        'network_type': 'Preferred Provider Organization (PPO)',
        'payment_terms': 'Net 30 days',
        'modifier_25_amount': 50.00,
        'modifier_59_amount': 40.00,
        'modifier_76_percent': 85,
        'interest_rate': '1.75%',
        'claim_submission_days': 90,
        'appeal_days': 365,
        'appeal_po_box': '2923',
        'payer_city': 'Chicago',
        'payer_state': 'IL',
        'payer_zip': '60601',
        'record_retention_years': 7,
        'termination_notice_days': 90,
        'prior_auth_services': 'MRI, CT, PET scans, Inpatient admissions, Major surgeries, Radiation therapy, Chemotherapy',
        'fee_schedule': [
            ('99213', 'Office/Outpatient Visit - Level 3 (Established Patient)', 90.00),
            ('99214', 'Office/Outpatient Visit - Level 4 (Established Patient)', 130.00),
            ('99215', 'Office/Outpatient Visit - Level 5 (Established Patient)', 175.00),
            ('99203', 'Office/Outpatient Visit - Level 3 (New Patient)', 110.00),
            ('99204', 'Office/Outpatient Visit - Level 4 (New Patient)', 160.00),
            ('27447', 'Total Knee Arthroplasty (Knee Replacement)', 16000.00),
            ('29881', 'Knee Arthroscopy with Meniscectomy', 3800.00),
            ('93000', 'Electrocardiogram (EKG) Complete', 48.00),
            ('80053', 'Comprehensive Metabolic Panel', 38.00),
            ('71045', 'Chest X-Ray Single View', 70.00),
        ]
    }

    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)

    # Generate PDFs
    create_contract_pdf('data/united_healthcare_contract.pdf', united_data)
    create_contract_pdf('data/aetna_contract.pdf', aetna_data)
    create_contract_pdf('data/blue_cross_contract.pdf', bcbs_data)

    print("\n✓ All synthetic healthcare contracts generated successfully!")
    print("  - data/united_healthcare_contract.pdf")
    print("  - data/aetna_contract.pdf")
    print("  - data/blue_cross_contract.pdf")


if __name__ == '__main__':
    generate_all_contracts()
