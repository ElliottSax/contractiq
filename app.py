"""
Healthcare Payer Contract Analyzer - Streamlit Web Interface

A professional web interface for analyzing healthcare payer contracts using
RAG (Retrieval-Augmented Generation) technology.
"""

import streamlit as st
import sys
from pathlib import Path
import os
from io import BytesIO
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from contract_analyzer import ContractAnalyzer
from rag_pipeline import HealthcareContractRAG

# Page configuration
st.set_page_config(
    page_title="Healthcare Contract Analyzer",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional healthcare theme
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #003366;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #5A6C7D;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F0F8FF;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #003366;
        margin: 1rem 0;
    }
    .example-button {
        background-color: #E8F4F8;
        padding: 0.75rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border: 1px solid #B0D4E3;
        cursor: pointer;
    }
    .source-citation {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 5px;
        margin-top: 1rem;
        font-size: 0.9rem;
        border-left: 3px solid #5A6C7D;
    }
    .business-impact {
        background-color: #E8F5E9;
        padding: 1.5rem;
        border-radius: 10px;
        margin-top: 1.5rem;
        border-left: 5px solid #4CAF50;
    }
    .warning-box {
        background-color: #FFF3E0;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #FF9800;
        margin: 1rem 0;
    }
    .stButton>button {
        background-color: #003366;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #004080;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_analyzer():
    """Initialize the contract analyzer (cached for performance)."""
    try:
        analyzer = ContractAnalyzer()

        # Check if vector store exists
        vectorstore_path = Path("outputs/vectorstore")

        if vectorstore_path.exists():
            analyzer.load_vectorstore()
            analyzer.create_qa_chain()
            return analyzer, "loaded"
        else:
            analyzer.build_pipeline(save_vectorstore=True)
            return analyzer, "built"

    except Exception as e:
        st.error(f"Error initializing analyzer: {str(e)}")
        return None, "error"


def display_header():
    """Display the application header."""
    st.markdown('<h1 class="main-header">🏥 Healthcare Payer Contract Analyzer</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Powered by RAG Technology | Analyze Insurance Contracts for Optimal Reimbursement</p>',
        unsafe_allow_html=True
    )


def display_sidebar(analyzer):
    """Display the sidebar with contract information and settings."""
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/003366/FFFFFF?text=Contract+Intelligence", use_column_width=True)

        st.markdown("### 📊 System Status")

        # Count PDFs in data directory
        data_dir = Path("data")
        if data_dir.exists():
            pdf_files = list(data_dir.glob("*.pdf"))
            st.metric("Loaded Contracts", len(pdf_files))

            if pdf_files:
                st.markdown("**Payer Contracts:**")
                for pdf in pdf_files:
                    payer_name = pdf.stem.replace('_', ' ').title()
                    st.markdown(f"✓ {payer_name}")
        else:
            st.warning("No contracts loaded")

        st.markdown("---")

        # Analysis Tools
        st.markdown("### 🔧 Analysis Tools")

        if st.button("📋 Payment Terms Summary"):
            st.session_state['run_analysis'] = 'payment_terms'

        if st.button("🔍 Modifier Analysis"):
            st.session_state['run_analysis'] = 'modifiers'

        if st.button("⚠️ Prior Auth Requirements"):
            st.session_state['run_analysis'] = 'prior_auth'

        if st.button("📝 Denial Policies"):
            st.session_state['run_analysis'] = 'denial_policies'

        st.markdown("---")

        # Contract Upload (placeholder for now)
        st.markdown("### 📤 Upload Contract")
        uploaded_file = st.file_uploader(
            "Upload a payer contract PDF",
            type=['pdf'],
            help="Upload additional payer contracts for analysis"
        )

        if uploaded_file:
            st.info("Contract upload feature coming soon!")

        st.markdown("---")

        # Info section
        st.markdown("### ℹ️ About")
        st.markdown("""
        This system uses advanced AI to analyze healthcare payer contracts and identify:
        - Rate discrepancies
        - Underpayment opportunities
        - Contract optimization strategies
        - Revenue improvement potential
        """)


def display_example_queries():
    """Display clickable example query buttons."""
    st.markdown("### 💡 Example Queries")
    st.markdown("Click any question below to analyze your contracts:")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Compare United Healthcare and Aetna rates for office visits", use_container_width=True):
            st.session_state['query'] = "Compare the reimbursement rates for office visit CPT codes (99213, 99214) between United Healthcare and Aetna. Which payer offers better rates?"

        if st.button("🏆 What is the highest paying contract for total knee replacement?", use_container_width=True):
            st.session_state['query'] = "Which payer offers the highest reimbursement rate for CPT code 27447 (total knee replacement)? Show all payer rates and the differences."

    with col2:
        if st.button("📅 Show me all payment terms across contracts", use_container_width=True):
            st.session_state['query'] = "Compare payment terms across all payer contracts. Which payer pays the fastest? Include net payment days and interest rates on late payments."

        if st.button("➕ Which payer has the most favorable modifier policies?", use_container_width=True):
            st.session_state['query'] = "Compare modifier 25 reimbursement across all payers. Which payer pays the most for modifier 25 and what is the revenue impact?"


def display_analysis_results(analyzer, query):
    """Display analysis results for a query."""
    with st.spinner("🔍 Analyzing contracts..."):
        try:
            result = analyzer.ask_question(query)

            # Display answer
            st.markdown("### 📊 Analysis Results")
            st.markdown(result['answer'])

            # Extract and highlight key numbers
            import re
            dollar_amounts = re.findall(r'\$[\d,]+\.?\d*', result['answer'])
            if dollar_amounts:
                st.markdown("---")
                st.markdown("### 💰 Key Financial Figures")
                cols = st.columns(min(len(dollar_amounts), 4))
                for idx, amount in enumerate(dollar_amounts[:4]):
                    with cols[idx]:
                        st.metric("Amount", amount)

            # Display source citations
            if result.get('source_documents'):
                st.markdown("---")
                st.markdown("### 📚 Source Citations")

                for idx, doc in enumerate(result['source_documents'], 1):
                    source_file = Path(doc.metadata.get('source', 'Unknown')).name
                    page_num = doc.metadata.get('page', 'Unknown')

                    with st.expander(f"📄 Source {idx}: {source_file} (Page {page_num})"):
                        st.markdown(f"**File:** {source_file}")
                        st.markdown(f"**Page:** {page_num}")
                        st.markdown("**Excerpt:**")
                        st.text(doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content)

            # Business Impact Section
            display_business_impact(result['answer'])

        except Exception as e:
            st.error(f"Error processing query: {str(e)}")


def display_business_impact(analysis_text):
    """Display business impact analysis based on results."""
    st.markdown("---")
    st.markdown('<div class="business-impact">', unsafe_allow_html=True)
    st.markdown("### 💼 Business Impact Analysis")

    # Look for rate differences in the analysis
    import re
    dollar_amounts = re.findall(r'\$?([\d,]+\.?\d*)', analysis_text)

    if len(dollar_amounts) >= 2:
        try:
            rates = [float(amt.replace(',', '')) for amt in dollar_amounts if amt.replace(',', '').replace('.', '').isdigit()]

            if len(rates) >= 2:
                max_rate = max(rates)
                min_rate = min(rates)
                difference = max_rate - min_rate
                percent_diff = (difference / min_rate * 100) if min_rate > 0 else 0

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Highest Rate", f"${max_rate:,.2f}")
                with col2:
                    st.metric("Lowest Rate", f"${min_rate:,.2f}")
                with col3:
                    st.metric("Rate Difference", f"${difference:,.2f}", f"{percent_diff:.1f}%")

                # Revenue impact calculation
                st.markdown("#### 📈 Revenue Opportunity")
                monthly_volume = st.number_input(
                    "Estimated monthly procedure volume:",
                    min_value=1,
                    max_value=10000,
                    value=100,
                    step=10
                )

                monthly_impact = difference * monthly_volume
                annual_impact = monthly_impact * 12

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Monthly Revenue Opportunity", f"${monthly_impact:,.2f}")
                with col2:
                    st.metric("Annual Revenue Opportunity", f"${annual_impact:,.2f}")

                if annual_impact > 10000:
                    st.markdown(f"""
                    <div class="warning-box">
                    <strong>⚠️ Significant Revenue Opportunity Detected</strong><br>
                    Negotiating rates to match the highest payer could generate an additional
                    <strong>${annual_impact:,.2f}</strong> annually. This represents a strong case
                    for contract renegotiation.
                    </div>
                    """, unsafe_allow_html=True)

        except Exception:
            pass

    st.markdown('</div>', unsafe_allow_html=True)


def run_specialized_analysis(analyzer, analysis_type):
    """Run specialized analysis based on sidebar button clicks."""
    st.markdown(f"### 🔍 {analysis_type.replace('_', ' ').title()}")

    with st.spinner("Running analysis..."):
        try:
            if analysis_type == 'payment_terms':
                result = analyzer.get_payment_terms_summary()
                st.markdown(result['summary'])

            elif analysis_type == 'modifiers':
                result = analyzer.analyze_modifiers()
                st.markdown(result['analysis'])

            elif analysis_type == 'prior_auth':
                result = analyzer.get_prior_auth_requirements()
                st.markdown(result['analysis'])

            elif analysis_type == 'denial_policies':
                result = analyzer.analyze_denial_policies()
                st.markdown(result['analysis'])

            # Display sources
            if result.get('sources'):
                st.markdown("---")
                st.markdown("### 📚 Sources")
                for idx, doc in enumerate(result['sources'], 1):
                    source = Path(doc.metadata.get('source', 'Unknown')).name
                    page = doc.metadata.get('page', 'Unknown')
                    st.markdown(f"**[{idx}]** {source} - Page {page}")

        except Exception as e:
            st.error(f"Error running analysis: {str(e)}")

    # Clear the analysis flag
    if 'run_analysis' in st.session_state:
        del st.session_state['run_analysis']


def main():
    """Main application entry point."""

    # Initialize session state
    if 'query' not in st.session_state:
        st.session_state['query'] = ""

    # Display header
    display_header()

    # Initialize analyzer
    with st.spinner("🔄 Initializing contract analyzer..."):
        analyzer, status = initialize_analyzer()

    if analyzer is None:
        st.error("Failed to initialize analyzer. Please check your configuration.")
        st.stop()

    if status == "built":
        st.success("✓ Contract database built successfully!")
    elif status == "loaded":
        st.success("✓ Contract database loaded successfully!")

    # Display sidebar
    display_sidebar(analyzer)

    # Check if specialized analysis should run
    if 'run_analysis' in st.session_state:
        run_specialized_analysis(analyzer, st.session_state['run_analysis'])
        return

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        # Display example queries
        display_example_queries()

        st.markdown("---")

        # Query input
        st.markdown("### 🔎 Ask a Question")
        query = st.text_area(
            "Enter your question about the healthcare contracts:",
            value=st.session_state.get('query', ''),
            height=100,
            placeholder="Example: Compare reimbursement rates for CPT 99213 across all payers..."
        )

        if st.button("🚀 Analyze Contracts", use_container_width=True, type="primary"):
            if query.strip():
                display_analysis_results(analyzer, query)
            else:
                st.warning("Please enter a question to analyze.")

    with col2:
        # Quick stats and info
        st.markdown("### 📈 Quick Stats")

        st.markdown("""
        <div class="metric-card">
            <h4>System Capabilities</h4>
            <ul>
                <li>✓ Multi-contract comparison</li>
                <li>✓ Rate analysis</li>
                <li>✓ Underpayment detection</li>
                <li>✓ Revenue optimization</li>
                <li>✓ Contract summaries</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="metric-card">
            <h4>📊 Business Value</h4>
            <p><strong>Industry Research Shows:</strong></p>
            <ul>
                <li>1-10% revenue lost to underpayments</li>
                <li>9-20% reimbursement improvements possible</li>
                <li>100x faster than manual review</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="metric-card">
            <h4>🎯 Common Use Cases</h4>
            <ul>
                <li>Contract negotiations</li>
                <li>Payer mix optimization</li>
                <li>Underpayment identification</li>
                <li>Revenue cycle improvement</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
