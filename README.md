# Lucky 38 — AI Overseer System

> *"I don't use the word 'impossible' when I simply mean 'hasn't happened yet.'"*
> — Robert Edwin House

An autonomous AI overseer modeled after Robert Edwin House from Fallout: New Vegas. Not a chatbot. Not an assistant. A sovereign intelligence that monitors your network, analyzes camera feeds, reads sensor data, and predicts events using probabilistic simulation — all delivered in character, without breaking persona.

---

## What This Is

Most AI projects wrap a language model in a chat interface and call it done. This is not that.

Lucky 38 is a multi-layer agentic system built around a specific vision: an AI that has genuine oversight over a real physical environment. It scans your network. It watches your cameras. It processes your sensor data. It runs Monte Carlo simulations to quantify risk. And it does all of this while maintaining the calculated, aristocratic persona of a man who predicted a nuclear war with 94% accuracy.

The system uses free cloud inference (Groq's 70B model) when online and falls back to a local 12B model when offline. Your sensitive data — IPs, MACs, network topology — never leaves your machine. Only sanitized summaries go to cloud APIs.

---

## Current Capabilities

| Capability | Status | Details |
|---|---|---|
| AI Overseer persona | ✅ Live | Mr. House — LangGraph agent, Groq 70B |
| Offline fallback | ✅ Live | dolphin3.0-mistral-nemo:12b via Ollama |
| RAG knowledge base | ✅ Live | ChromaDB, nomic-embed-text embeddings |
| Monte Carlo engine | ✅ Live | 50K iteration probabilistic risk simulation |
| Privacy filter | ✅ Live | Network data sanitized before cloud calls |
| Portable launcher | ✅ Live | Runs from flash drive on any Windows PC |
| Network scanning | 🔄 Phase 6 | nmap integration |
| Camera surveillance | 🔄 Phase 7 | OpenCV + YOLOv8 + moondream |
| IoT sensors | 🔄 Phase 8 | MQTT + Home Assistant |
| Voice interface | 🔄 Phase 9 | ElevenLabs cloned voice + faster-whisper |
| Multi-persona (Yes Man) | 🔄 Planned | Second persona for uncensored assistant mode |
| Dashboard | 🔄 Phase 10 | Streamlit → React |

---

## Architecture

```
YOUR MACHINE                          FREE CLOUD
──────────────────────────────        ──────────────────────────
FastAPI (port 8000)          ──→      Groq: llama-3.3-70b-versatile
LangGraph Agent              ←──      Gemini 2.0 Flash (backup)
ChromaDB (RAG + event log)
nomic-embed-text (embeddings)
moondream (vision, 1.7 GB)
OpenCV + YOLOv8 (cameras)        ↑ online
python-nmap (network)         ────────────────
paho-mqtt (IoT sensors)          ↓ offline
NumPy + PyMC (Monte Carlo)    dolphin3.0-mistral-nemo:12b
privacy_filter.py             Local Ollama — always available
```

**Privacy by design.** Raw network identifiers stay in ChromaDB on your machine. Cloud APIs receive only sanitized, abstracted summaries. The `privacy_filter.py` module enforces this automatically on every outbound call.

---

## Quick Start

### Prerequisites

- Windows 10/11 (portable launcher is `.bat` — Linux/Mac support planned)
- Python 3.11+
- [Ollama](https://ollama.com) installed system-wide
- Free API keys from [Groq](https://console.groq.com) and [Google AI Studio](https://aistudio.google.com)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/lucky38.git
cd lucky38
```

### 2. Pull local models

```bash
ollama pull dolphin3.0-mistral-nemo:12b
ollama pull nomic-embed-text
ollama pull moondream
```

> The first pull takes a few minutes. `nomic-embed-text` (274 MB) and `moondream` (1.7 GB) are small. `dolphin3.0-mistral-nemo:12b` is ~7 GB.

### 3. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in your API keys:

```env
GROQ_API_KEY=gsk_your_key_here
GOOGLE_API_KEY=AIza_your_key_here
TOGETHER_API_KEY=your_key_here        # optional — $25 free credit at together.ai
```

### 4. Create virtual environment and install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Ingest your knowledge base

```bash
python -c "from app.core.rag import ingest_documents; ingest_documents()"
```

Edit `app/knowledge/documents/facility_overview.txt` with your own environment details before ingesting. See [Knowledge Base](#knowledge-base) section below.

### 6. Launch

```bash
python -m app.api.main
```

The server starts at `http://127.0.0.1:8000`. Open a second terminal and test:

```powershell
$r = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/chat" -Method POST -ContentType "application/json" -Body '{"message": "House, report facility status."}'
$r.response
```

Or double-click `start.bat` for the full portable launcher experience.

---

## Project Structure

```
lucky38/
├── app/
│   ├── core/
│   │   ├── agent.py              LangGraph agent — the brain
│   │   ├── llm_factory.py        Online/offline LLM routing
│   │   ├── persona.py            Mr. House system prompt
│   │   ├── privacy_filter.py     Sanitizes data before cloud calls
│   │   ├── rag.py               ChromaDB setup and retrieval
│   │   └── memory.py            Conversation history management
│   ├── tools/
│   │   ├── analytics/
│   │   │   └── monte_carlo.py   Probabilistic risk simulation
│   │   ├── network/             nmap tool (Phase 6)
│   │   ├── surveillance/        Camera + YOLO (Phase 7)
│   │   ├── iot/                 MQTT sensors (Phase 8)
│   │   └── voice/               STT/TTS (Phase 9)
│   ├── api/
│   │   ├── main.py              FastAPI entry point
│   │   └── routers/chat.py      Chat and status endpoints
│   ├── cli/
│   │   └── mr_house_cli.py      Rich terminal CLI (Phase 3b)
│   └── knowledge/
│       └── documents/           Facility docs ingested into RAG
├── chromadb/                    Persistent vector database
├── .env.example                 Environment variable template
├── .github/
│   └── copilot-instructions.md  GitHub Copilot context file
├── start.bat                    Portable launcher (Windows)
├── sync.bat                     Push to flash drive
├── sync_back.bat                Pull ChromaDB from flash drive
├── setup.bat                    First-run setup on new PC
└── requirements.txt
```

---

## Configuration

All configuration lives in `.env`. Never commit this file — it is in `.gitignore`.

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Free at console.groq.com |
| `GOOGLE_API_KEY` | Yes | Free at aistudio.google.com |
| `TOGETHER_API_KEY` | No | $25 free credit for uncensored models |
| `GROQ_SMART_MODEL` | No | Default: `llama-3.3-70b-versatile` |
| `LOCAL_SMART_MODEL` | No | Default: `dolphin3.0-mistral-nemo:12b` |
| `EMBED_MODEL` | No | Default: `nomic-embed-text` |
| `CHROMA_DB_PATH` | No | Default: `./chromadb` |
| `API_HOST` | No | Default: `127.0.0.1` |
| `API_PORT` | No | Default: `8000` |

---

## Knowledge Base

Mr. House's intelligence comes from documents you feed him. Add `.txt` or `.md` files to `app/knowledge/documents/` and run the ingestion command:

```bash
python -c "from app.core.rag import ingest_documents; ingest_documents()"
```

**What to include:**
- Network topology (abstract — no raw IPs)
- Device inventory (device names and roles, not MAC addresses)
- Room or environment layout
- Security baseline notes
- System event log

**What to leave out:**
- Raw IP addresses
- MAC addresses
- Credentials or API keys
- Anything you would not want sent to a third-party API

The `privacy_filter.py` strips sensitive identifiers automatically, but the best practice is to write your documents in abstracted form from the start.

---

## API Reference

The full interactive API documentation is available at `http://127.0.0.1:8000/docs` when the server is running.

### `POST /api/chat`

Send a message to Mr. House.

**Request:**
```json
{ "message": "House, scan the network for unauthorized devices." }
```

**Response:**
```json
{
  "response": "I calculate a 73% probability that the unrecognized node represents...",
  "mode": "agent"
}
```

### `GET /api/status`

Returns current system state.

```json
{
  "system": "Lucky 38 Control System",
  "status": "ONLINE",
  "connectivity": "ONLINE",
  "active_model": "llama-3.3-70b-versatile",
  "rag": "active",
  "memory": "active"
}
```

---

## Portable Mode

The entire system runs from a USB flash drive (USB 3.0 recommended, 16 GB minimum).

**First time setup on a new PC:**
1. Copy the project folder to the drive
2. Double-click `setup.bat` — builds the virtual environment automatically
3. Double-click `start.bat` — detects internet, selects best LLM, launches

**Syncing from your development machine:**
```bash
sync.bat E:        # push code and ChromaDB to drive E:
sync_back.bat E:   # pull ChromaDB updates back from drive E:
```

The `start.bat` launcher automatically detects whether a portable Ollama binary is present on the drive, checks internet connectivity, and selects the appropriate LLM — no manual configuration needed on a new machine.

---

## How the LLM Routing Works

```python
# Priority order (automatic, no configuration needed):
1. Groq — llama-3.3-70b-versatile     (online, free, fast)
2. Gemini 2.0 Flash                    (online, free, backup)
3. Together.ai Dolphin/Hermes 70B      (online, $25 credit, uncensored)
4. dolphin3.0-mistral-nemo:12b         (offline, always available)
```

Connectivity is checked via a 3-second socket test to `api.groq.com`. If it fails, the system falls back to local Ollama instantly. Mr. House never goes offline — he just operates at reduced capacity when the cloud is unavailable.

---

## Probabilistic Engine

Ask Mr. House to assess any risk scenario and he will run a Monte Carlo simulation:

```
"House, calculate the probability of an unauthorized network intrusion this week."
```

The engine runs 50,000 iterations drawing from beta distributions representing primary, secondary, and environmental risk factors. It returns:

- Overall breach probability
- Mean risk score
- 95th percentile worst-case
- 95% confidence interval

As sensor data, network scan history, and event logs accumulate in ChromaDB, the simulation parameters will be calibrated against real historical data.

---

## Privacy and Security

This system was designed from the ground up to keep sensitive data local.

- **Raw network data** (IPs, MACs, port numbers) is stored only in ChromaDB on your machine
- **Cloud APIs** receive only sanitized summaries via `privacy_filter.py`
- **API server** binds to `127.0.0.1` — not accessible from other machines by default
- **`.env` file** is excluded from git via `.gitignore` — never committed
- **Cybersecurity tools** (Phase 6+) may only be used on networks you own or have explicit written permission to test

---

## Roadmap

The project follows a phased development approach. Each phase produces a fully working, testable system before the next phase begins.

| Phase | Name | Status |
|---|---|---|
| 0 | Environment setup | ✅ Complete |
| 1 | Core architecture migration | ✅ Complete |
| 2 | API layer upgrade | ✅ Complete |
| 3 | Monte Carlo engine | ✅ Complete |
| 4 | Portable infrastructure | ✅ Complete |
| 5 | RAG knowledge base | ✅ Complete |
| 3b | Rich CLI interface | 🔄 In progress |
| 6 | Network reconnaissance (nmap) | ⏳ Planned |
| 7 | Surveillance (cameras + YOLO) | ⏳ Planned |
| 8 | IoT and sensor integration | ⏳ Planned |
| 9 | Voice interface (ElevenLabs + Whisper) | ⏳ Planned |
| 10 | Dashboard (Streamlit → React) | ⏳ Planned |
| 11 | Advanced probabilistic intelligence | ⏳ Planned |
| 12 | Documentation and production | ⏳ Planned |

Full roadmap with detailed task lists is maintained in the [Notion blueprint](https://www.notion.so/The-Blueprint-2fd812bd0a888027a0cfdb65dc6a9b7a).

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM (online) | Groq — llama-3.3-70b-versatile |
| LLM (offline) | dolphin3.0-mistral-nemo:12b via Ollama |
| Agent framework | LangGraph (LangChain 1.2.x) |
| Vector database | ChromaDB via langchain-chroma |
| Embeddings | nomic-embed-text (local Ollama) |
| Backend | FastAPI + Uvicorn |
| Vision | OpenCV + YOLOv8 + moondream |
| IoT | paho-mqtt + Mosquitto |
| Probabilistic | NumPy + SciPy + PyMC |
| Voice STT | faster-whisper (medium, CUDA) |
| Voice TTS | ElevenLabs (cloned) + Kokoro (fallback) |
| CLI | Rich |

---

## Known Issues and Compatibility Notes

- **LangChain version:** This project requires LangChain 1.2.x. `AgentExecutor` was removed in this version — the project uses `langgraph.prebuilt.create_react_agent` instead. Do not attempt to downgrade.
- **numpy:** Install with `--only-binary=:all:` flag if you encounter GCC build errors on Windows. The project requires numpy >= 2.1.0.
- **ChromaDB folder:** Data lives in `./chromadb/` — not `./chroma_db/`. If you see an empty folder named `chroma_db`, delete it.
- **Groq tool calls:** The persona prompt must not instruct the model to narrate tool calls before making them. This causes `tool_use_failed` errors from the Groq API.
- **FastAPI startup:** Uses the `@asynccontextmanager lifespan` pattern. The deprecated `@app.on_event('startup')` pattern will trigger warnings.

---

## Contributing

This is a personal project and active development is ongoing. If you find a bug or have a suggestion, open an issue. Pull requests are welcome for bug fixes.

Before contributing, read `.github/copilot-instructions.md` for the complete project context, import rules, and coding standards.



## Disclaimer

The AI persona is a fictional character from Bethesda's Fallout: New Vegas. This project has no affiliation with Bethesda Softworks.

---

*The house always wins.*