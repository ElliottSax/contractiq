# Weaviate Cloud Setup Guide

This guide walks you through setting up Weaviate Cloud for hybrid search in ContractIQ.

## Why Weaviate?

Weaviate provides **hybrid search** combining:
- **Semantic Search:** Vector similarity (what we currently use)
- **Keyword Search (BM25):** Exact term matching for CPT codes, dollar amounts
- **Alpha Parameter:** Balance between semantic and keyword (0.7 recommended for healthcare)

This is critical for healthcare contracts where exact matches (CPT codes, rates) matter alongside semantic understanding.

## Step 1: Sign Up for Weaviate Cloud

1. Visit: https://console.weaviate.cloud/
2. Click "Sign Up" (14-day free trial, no credit card required)
3. Create an account with your email
4. Verify your email address

## Step 2: Create a Cluster

1. After login, click "Create Cluster"
2. Select:
   - **Region:** Choose closest to you (US-East, EU-West, etc.)
   - **Cluster Type:** Sandbox (free 14-day trial)
   - **Cluster Name:** `contractiq` (or your preference)
3. Click "Create"
4. Wait 2-3 minutes for cluster provisioning

## Step 3: Get Your Credentials

Once your cluster is ready:

1. Click on your cluster name
2. Navigate to "Details" tab
3. Copy these values:
   - **Cluster URL:** Should look like `https://contractiq-xxx.weaviate.network`
   - **API Key:** Click "Generate API Key" if not shown

## Step 4: Configure ContractIQ

Add your Weaviate credentials to `.env`:

```bash
# Weaviate Configuration
WEAVIATE_URL=https://your-cluster-url.weaviate.network
WEAVIATE_API_KEY=your-api-key-here
```

**Example:**
```bash
WEAVIATE_URL=https://contractiq-a1b2c3d4.weaviate.network
WEAVIATE_API_KEY=xeK9vZ2Bq7YfH3wN8mP5...
```

## Step 5: Test the Connection

Run the test script:

```bash
source venv/bin/activate
python3 src/test_weaviate_connection.py
```

You should see:
```
✅ Successfully connected to Weaviate Cloud!
✅ Cluster is ready
```

## Step 6: Migrate from FAISS to Weaviate

Run the migration script:

```bash
source venv/bin/activate
python3 src/migrate_to_weaviate.py
```

This will:
1. Create the ContractIQ schema in Weaviate
2. Upload all contract documents with metadata
3. Enable hybrid search with alpha=0.7
4. Test retrieval performance

## Hybrid Search Configuration

### Alpha Parameter

The `alpha` parameter controls the balance between semantic and keyword search:

- **alpha = 0.0:** Pure keyword search (BM25 only)
- **alpha = 0.5:** 50/50 balance
- **alpha = 0.7:** 70% semantic, 30% keyword (recommended for healthcare)
- **alpha = 1.0:** Pure semantic search (current FAISS behavior)

**Why 0.7 for Healthcare?**
- Semantic search helps understand context and intent
- Keyword search ensures exact CPT codes, amounts are matched
- 0.7 provides best of both worlds

### Metadata Filtering

Weaviate allows filtering by payer name:

```python
# Example: Search only United Healthcare contracts
results = weaviate_client.query(
    question="What is the rate for CPT 99213?",
    where_filter={"payer": "United Healthcare"}
)
```

## Troubleshooting

### Connection Issues

If you can't connect:

1. **Check URL format:** Must include `https://`
2. **Verify API Key:** Copy fresh from Weaviate Console
3. **Check cluster status:** Ensure it's "Ready" in console
4. **Firewall/SSL:** Same SSL issues as before may apply

### SSL Certificate Errors

If you encounter SSL errors (like with other APIs):

```bash
# Option 1: Disable SSL verification (development only)
export PYTHONHTTPSVERIFY=0

# Option 2: Use local Weaviate instance instead
docker run -d -p 8080:8080 semitechnologies/weaviate:latest
WEAVIATE_URL=http://localhost:8080
```

### Cluster Limits

Free tier limitations:
- **Storage:** 100MB (sufficient for ContractIQ)
- **Requests:** 1M/month (more than enough for testing)
- **Duration:** 14 days (can recreate cluster after)

## Alternative: Local Weaviate

If Weaviate Cloud doesn't work (SSL issues), run locally:

```bash
# Start Weaviate with Docker
docker run -d \
  -p 8080:8080 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH=/var/lib/weaviate \
  semitechnologies/weaviate:latest

# Update .env
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=  # Leave empty for local
```

## Next Steps

Once Weaviate is configured:

1. ✅ Test connection
2. ✅ Migrate data from FAISS
3. ✅ Run hybrid search benchmarks
4. ✅ Compare with pure semantic search
5. ✅ Update README with results

## Benefits of Hybrid Search

Expected improvements:
- **CPT Code Retrieval:** 95%+ accuracy (up from ~80% with semantic only)
- **Dollar Amount Matching:** Exact matches guaranteed
- **Policy Queries:** Better context understanding
- **Complex Queries:** Combines keyword precision with semantic reasoning

## Support

- **Weaviate Docs:** https://weaviate.io/developers/weaviate
- **Community Slack:** https://weaviate.io/slack
- **Pricing:** https://weaviate.io/pricing

---

*Note: Keep your API key secure. Never commit it to Git. It's already in `.gitignore`.*
