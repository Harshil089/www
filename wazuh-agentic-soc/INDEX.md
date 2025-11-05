# 📚 Codebase Index & Quick Reference

## 📖 Documentation Files

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Complete architecture documentation
- **[AGENTIC_AI.md](./AGENTIC_AI.md)** - Detailed explanation of agentic AI system
- **[README.md](./README.md)** - User guide and setup instructions

---

## 🗂️ Directory Structure

```
wazuh-agentic-soc/
├── backend/                    # FastAPI backend
│   ├── agents/                 # AI agents
│   │   ├── orchestrator.py    # Main coordinator (⭐ KEY FILE)
│   │   ├── alert_agent.py     # Alert queries
│   │   ├── rule_agent.py      # Rule queries
│   │   ├── agent_manager.py   # Agent status queries
│   │   └── firewall_agent.py  # Firewall commands
│   ├── integrations/
│   │   └── wazuh_client.py    # Wazuh API wrapper (⭐ KEY FILE)
│   ├── api/
│   │   └── stats.py           # Dashboard statistics endpoint
│   ├── main.py                # FastAPI server entry point (⭐ KEY FILE)
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx  # Main dashboard (⭐ KEY FILE)
│   │   │   └── ChatBot.jsx    # AI chat interface (⭐ KEY FILE)
│   │   ├── App.jsx            # Root component
│   │   └── main.jsx           # Entry point
│   └── package.json           # Node dependencies
│
└── Documentation files...
```

---

## 🔑 Key Files Explained

### Backend Core Files

| File | Purpose | Key Functions |
|------|---------|---------------|
| `main.py` | FastAPI server | WebSocket endpoint, CORS, routing |
| `agents/orchestrator.py` | AI coordinator | Tool selection, LLM enhancement |
| `integrations/wazuh_client.py` | Wazuh integration | Authentication, API calls |

### Backend Agents

| File | Purpose | Handles |
|------|---------|---------|
| `alert_agent.py` | Alert queries | Security alerts, incidents |
| `rule_agent.py` | Rule queries | Wazuh rule definitions |
| `agent_manager.py` | Agent status | Endpoint health, connectivity |
| `firewall_agent.py` | Firewall commands | IP blocking, port management |

### Frontend Components

| File | Purpose | Key Features |
|------|---------|--------------|
| `Dashboard.jsx` | Main UI | Stats cards, alerts table, health panel |
| `ChatBot.jsx` | Chat interface | WebSocket communication, message history |

---

## 🔄 Quick Flow Reference

### Chat Query Flow
```
User → ChatBot.jsx → WebSocket → main.py → orchestrator.py 
→ Agent (alert/rule/agent/firewall) → wazuh_client.py 
→ Wazuh API → LLM Enhancement → Response → ChatBot.jsx → User
```

### Dashboard Stats Flow
```
Dashboard.jsx → HTTP GET /api/stats → stats.py → wazuh_client.py 
→ Wazuh API → Aggregated Stats → Dashboard.jsx
```

---

## 🤖 Agent Routing Quick Reference

| Query Keywords | → | Agent | Function |
|---------------|---|-------|----------|
| `block`, `allow`, `firewall`, `iptables`, `port` | → | Firewall | `parse_firewall_request()` |
| `alert`, `incident`, `attack`, `critical`, `high` | → | Alerts | `fetch_alerts()` |
| `rule`, `policy`, `regulation`, `compliance` | → | Rules | `fetch_rules()` |
| `agent`, `host`, `server`, `endpoint`, `status` | → | Agents | `fetch_agents()` |
| (default) | → | Alerts | `fetch_alerts()` |

---

## 🔌 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Root endpoint |
| `/api/health` | GET | Health check |
| `/api/stats` | GET | Dashboard statistics |
| `/ws/chat` | WebSocket | Chat interface |

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.121.0
- **ASGI**: Uvicorn 0.38.0
- **AI/LLM**: LangChain + Google Gemini 2.0 Flash
- **HTTP**: requests 2.32.5
- **WebSocket**: websockets 15.0.1

### Frontend
- **Framework**: React 19.1.1
- **Build**: Vite 7.1.7
- **Styling**: Tailwind CSS 4.1.16
- **Icons**: Lucide React

---

## 🔐 Environment Variables

Required in `backend/.env`:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
WAZUH_HOST=192.168.1.100
WAZUH_PORT=55000
WAZUH_USER=wazuh
WAZUH_PASSWORD=wazuh
```

---

## 🚀 Quick Start Commands

```bash
# Setup
./setup.sh

# Start (both frontend and backend)
./start.sh

# Or manually:
# Backend
cd backend && source venv/bin/activate && python main.py

# Frontend
cd frontend && npm run dev
```

---

## 📊 Key Metrics

- **Query Response Time**: ~1.1-2.5 seconds
- **Tool Selection**: <1ms (keyword-based)
- **LLM Enhancement**: 1-2 seconds
- **Dashboard Refresh**: Every 10 seconds

---

## 🎯 Core Concepts

1. **Hybrid Agentic System**: Keyword routing + LLM enhancement
2. **Specialized Agents**: Each agent handles one domain
3. **Real-time Communication**: WebSocket for chat, REST for stats
4. **Wazuh Integration**: JWT authentication, HTTPS API calls

---

## 🔍 Debugging Tips

1. **Check orchestrator initialization**: Look for `✅ SOC Orchestrator initialized`
2. **Verify Wazuh connection**: Check `connection_status` in `/api/stats`
3. **WebSocket issues**: Check browser console for connection errors
4. **LLM errors**: Verify `GEMINI_API_KEY` is set correctly

---

## 📝 Next Steps for Understanding

1. Read `ARCHITECTURE.md` for complete system overview
2. Read `AGENTIC_AI.md` for detailed agentic system explanation
3. Examine `backend/agents/orchestrator.py` to see routing logic
4. Check `frontend/src/components/ChatBot.jsx` for WebSocket implementation
5. Review `backend/integrations/wazuh_client.py` for API integration

---

**Last Updated**: 2024-01-15

