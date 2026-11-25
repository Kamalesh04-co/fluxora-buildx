# 🚢 Fluxora — Autonomous Maritime & Cold-Chain Command Center

**Built by Team Runtime Rebells** for **BUiLDX (AI & ML Track)**

Fluxora is an autonomous maritime supply chain and pharmaceutical cold-chain decision-intelligence platform. It bridges ship captains and port authorities with zero-quota live disruption sensing, local Edge-AI multi-variable rerouting, and a tamper-proof SHA-256 audit trail.

---

## 🌟 Key Features
* **Role-Based Dual Portals (`Firebase Auth`):** Separate authenticated dashboards for **Ship Captains** (7 operational tabs) and **Port Authorities** (4 operational tabs).
* **Zero-Quota Live Disruption Sensing (`Google News RSS`):** Fetches real-time cyclone alerts, port strikes, and geopolitical updates with zero API rate limits.
* **Local Edge-AI Scenario Engine (`Ollama + Phi-3`):** Evaluates vessel telemetry, cold-chain cargo temperature, fuel, and port availability to rank 3 rerouting options across 7 trade-offs (ETA, fuel cost, safety score, port taxes, profit/loss, customer comfort, and document verification speed).
* **Cryptographic Audit Ledger (`SHA-256 Blockchain`):** Records every reroute request, document submission, and berth approval in an immutable hash-chained ledger.

---

## 🗂️ Project Structure
```text
fluxora-maritime-command/
├── app.py              # Main Streamlit UI & workflow logic
├── config.py           # Firebase Auth & Ollama configuration
├── database.py         # JSON persistence & SHA-256 blockchain ledger
├── news_agent.py       # Google News RSS parser & local LLM summarizer
├── style.css           # Custom maritime dark-theme CSS
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
