# DSPy LM Backend Setup Guide

## Current Status

**Agents Refactored**: 3/6
- ✅ Supervisor (Tier 1)
- ✅ Architect (Tier 3)
- ✅ Coder (Tier 3)

**LM Backend**: Not yet configured

---

## Quick Setup (Choose One)

### Option 1: Local LM Studio (Recommended)

**Best for**: Privacy, no API costs, offline use

1. Download LM Studio: https://lmstudio.ai/
2. Install and open LM Studio
3. Download a model (Recommended: `mistral-7b` or `llama-3.1-8b`)
4. Start the Local API Server:
   - Click "Local Server" tab
   - Click "Start Server"
   - Default port: `localhost:1234`
5. Done! _SUDOTEER will auto-detect it

**No `.env` changes needed** - works out of the box!

---

### Option 2: Google Gemini API

**Best for**: Latest models, fast inference, generous free tier

1. Get API key: https://aistudio.google.com/app/apikey
2. Edit `.env` file:
   ```bash
   GEMINI_API_KEY=your_actual_gemini_key_here
   ```
3. Done! _SUDOTEER will auto-detect it

**Free tier**: 15 RPM, 1M TPM, 1500 RPD

---

### Option 3: OpenAI API

**Best for**: GPT-4o models, production reliability

1. Get API key: https://platform.openai.com/api-keys
2. Edit `.env` file:
   ```bash
   OPENAI_API_KEY=your_actual_openai_key_here
   ```
3. Done! _SUDOTEER will auto-detect it

**Cost**: ~$0.15 per 1M input tokens (gpt-4o-mini)

---

## Auto-Configuration Priority

_SUDOTEER checks in this order:

1. **Local LM Studio** (`localhost:1234`) - Free, private
2. **Gemini API** (`GEMINI_API_KEY` in `.env`) - Fast, generous free tier
3. **OpenAI API** (`OPENAI_API_KEY` in `.env`) - Fallback

---

## Testing Your Setup

### Test DSPy Configuration
```powershell
cd C:\Users\NAMAN\electron\_SUDOTEER
.venv\Scripts\python.exe -c "from backend.core.dspy_config import initialize_dspy; initialize_dspy()"
```

**Expected Output**:
```
[DSPy] Auto-configuring LM backend...
[DSPy] ✓ Configured: LM Studio (Local)  # or Gemini/OpenAI
[DSPy] ✓ Ready: LM Studio (Local)
```

### Test Supervisor Agent
```powershell
.venv\Scripts\python.exe webserver.py
```

Then in another terminal:
```powershell
curl -X POST http://localhost:8000/api/goal `
  -H "Content-Type: application/json" `
  -d '{"goal": "Check greenhouse temperature"}'
```

---

## Troubleshooting

### "DSPy initialization failed!"

**Cause**: No LM backend available

**Fix**:
1. Check if LM Studio is running (localhost:1234)
2. Check `.env` for valid API keys
3. Run the test command above to see details

### "Connection refused" (LM Studio)

**Cause**: LM Studio server not started

**Fix**:
1. Open LM Studio
2. Go to "Local Server" tab
3. Click "Start Server"
4. Ensure port is 1234

### "Invalid API key" (Gemini/OpenAI)

**Cause**: Wrong or expired API key

**Fix**:
1. Generate new API key from provider
2. Update `.env` file
3. Restart webserver

---

## Current `.env` Template

```bash
# LLM Providers (fill in your keys)
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_gemini_key_here
LM_STUDIO_URL=http://localhost:1234/v1

# Leave these for later
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

---

## Next Steps

1. **Choose an LM backend** (LM Studio recommended)
2. **Test configuration** with the test command
3. **Continue refactoring** remaining 3 agents:
   - Tester
   - Documenter
   - Validator
4. **Test full workflow**: User Goal → Supervisor → Agents → Results
