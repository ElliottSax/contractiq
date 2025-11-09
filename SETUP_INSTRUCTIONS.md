# 🚀 Quick Setup Instructions

## ✅ What I've Done For You

1. ✅ Configured `.env` to use Claude (avoids SSL issues)
2. ✅ Set up your API keys (Claude + DeepSeek for embeddings)
3. ✅ Created automated setup scripts
4. ✅ Ready to run!

---

## 📋 One-Command Setup

**In your terminal** (you're already in `/mnt/e/projects/contractiq`):

```bash
./setup.sh
```

This will:
- Install `python3-venv` (may ask for your password)
- Create virtual environment
- Install all dependencies (LangChain, Claude, Streamlit, etc.)

Takes about 3-5 minutes.

---

## 🎯 Run the System

### Option 1: CLI Mode (Interactive)
```bash
source venv/bin/activate
python3 src/cli.py --provider claude
```

Then ask questions like:
- "Compare United Healthcare and Aetna rates for CPT 99213"
- "Which payer has the best payment terms?"
- "Generate a negotiation report for United Healthcare"

Type `quit` to exit.

### Option 2: CLI Mode (Single Question)
```bash
source venv/bin/activate
python3 src/cli.py --provider claude -q "What is the reimbursement rate for CPT 99213?"
```

### Option 3: Web Interface (Streamlit)
```bash
source venv/bin/activate
streamlit run app.py
```

Opens at: http://localhost:8501

### Option 4: Quick Test
```bash
./quick_test.sh
```

Runs a quick test to verify everything works.

---

## 🔧 What's Configured

- **LLM Provider**: Claude (Anthropic) - Fast, reliable, no SSL issues
- **Embeddings**: DeepSeek API (OpenAI-compatible)
- **Contracts**: 3 synthetic payer contracts already generated
  - United Healthcare
  - Aetna
  - Blue Cross Blue Shield

---

## 📊 Project Features

✅ Multi-contract analysis
✅ Rate comparison across payers
✅ Payment terms analysis
✅ Modifier reimbursement tracking
✅ Prior authorization requirements
✅ Denial & appeal policy comparison
✅ Revenue impact calculator
✅ Underpayment detection
✅ Contract summaries
✅ Export to CSV/Excel

---

## 🆘 Troubleshooting

### If setup.sh fails:
Run commands manually:
```bash
sudo apt update && sudo apt install -y python3-venv python3-pip
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### If you get "Module not found":
Make sure you activated the virtual environment:
```bash
source venv/bin/activate
```

### If you see API errors:
Check your `.env` file has valid API keys:
```bash
cat .env
```

---

## 🎉 You're Ready!

Everything is configured. Just run:
```bash
./setup.sh
```

Then test with:
```bash
./quick_test.sh
```

Enjoy analyzing healthcare contracts! 🏥💰
