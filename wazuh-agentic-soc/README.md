# 🛡️ Agentic Wazuh SOC Dashboard

An intelligent SOC dashboard with AI-powered chatbot for Wazuh SIEM management using Google Gemini AI.

![Dashboard Preview](https://img.shields.io/badge/Status-Ready-green) ![Python](https://img.shields.io/badge/Python-3.11+-blue) ![React](https://img.shields.io/badge/React-18+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)

## 🚀 Quick Start

### 1. Run Setup Script
```bash
./setup.sh
```

### 2. Configure Environment
Edit `backend/.env` with your credentials:

```bash
# Get your Gemini API key from https://aistudio.google.com/
# Gemini AI Configuration
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# Replace with your Windows Wazuh manager IP
WAZUH_HOST=192.168.1.100
WAZUH_PORT=55000
WAZUH_USER=wazuh
WAZUH_PASSWORD=wazuh

DATABASE_URL=postgresql://localhost/wazuh_soc
```

### 3. Start Application
```bash
./start.sh
```

- 📊 **Dashboard**: http://localhost:5173
- 🔌 **API**: http://localhost:8000

### 4. Test Wazuh Connection (Optional)
```bash
cd backend
source venv/bin/activate
python test_wazuh.py
```

## 🤖 Demo Queries

Try asking the chatbot:

### Security Operations:
- **"Show me recent critical alerts"**
- **"How many agents are online?"**
- **"What does rule 5710 do?"**
- **"Triage alerts with MITRE ATT&CK"**
- **"Generate compliance report"**
- **"Show FIM events"**

### Knowledge Base (RAG):
- **"Search knowledge about Wazuh"**
- **"Find information about SIEM"**
- **"Query documents for security procedures"**

## 🏗️ Architecture

```
┌─────────────────┐    WebSocket    ┌──────────────────┐
│   React Frontend│◄──────────────►│  FastAPI Backend │
│   (Port 5173)   │                 │   (Port 8000)    │
└─────────────────┘                 └──────────────────┘
                                             │
                                             ▼
                                    ┌──────────────────┐
                                    │ SOC Orchestrator │
                                    │   (Gemini AI)    │
                                    └──────────────────┘
                                             │
                        ┌────────────────────┼────────────────────┐
                        ▼                    ▼                    ▼
                ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
                │ Alert Agent  │    │ Rule Agent   │    │ Agent Manager│
                └──────────────┘    └──────────────┘    └──────────────┘
                        │                    │                    │
                        └────────────────────┼────────────────────┘
                                             ▼
                                    ┌──────────────────┐
                                    │  Wazuh Manager   │
                                    │ (Windows Server) │
                                    └──────────────────┘
```

## 📁 Project Structure

```
wazuh-agentic-soc/
├── 🚀 start.sh              # Start both servers
├── 🔧 setup.sh              # Install dependencies
├── 📖 README.md             # This file
├── backend/
│   ├── 🤖 agents/           # AI agents
│   │   ├── orchestrator.py  # Main coordinator
│   │   ├── alert_agent.py   # Alert analysis
│   │   ├── rule_agent.py    # Rule management
│   │   └── agent_manager.py # Agent monitoring
│   ├── 🔌 integrations/     # External APIs
│   │   └── wazuh_client.py  # Wazuh API wrapper
│   ├── ⚡ main.py           # FastAPI server
│   ├── 🧪 test_wazuh.py     # Connection test
│   ├── 📦 requirements.txt  # Python deps
│   └── ⚙️ .env              # Configuration
└── frontend/
    ├── 🎨 src/components/   # React components
    │   ├── Dashboard.jsx    # Main dashboard
    │   └── ChatBot.jsx      # AI chatbot
    ├── 📦 package.json      # Node deps
    └── ⚙️ tailwind.config.js # Styling
```

## 🎯 Features

- ✅ **Real-time Alert Monitoring** - Live security alerts from Wazuh
- ✅ **AI-Powered Chat Interface** - Natural language queries with Gemini AI
- ✅ **Agent Status Tracking** - Monitor endpoint health and connectivity
- ✅ **Rule Management** - Search and analyze Wazuh rules
- ✅ **Interactive Dashboard** - Modern, responsive UI with Tailwind CSS
- ✅ **WebSocket Communication** - Real-time bidirectional messaging
- ✅ **Intelligent Tool Selection** - Automatic routing to appropriate agents

## 🔧 Manual Setup (Alternative)

If the scripts don't work, follow these manual steps:

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🔍 Troubleshooting

### Common Issues

1. **"Please set your GEMINI_API_KEY"**
   - Get API key from https://aistudio.google.com/
   - Update `backend/.env` file

2. **"Wazuh authentication failed"**
   - Verify Windows Wazuh manager IP address
   - Check firewall allows port 55000
   - Confirm credentials in `.env`

3. **"WebSocket connection failed"**
   - Ensure backend is running on port 8000
   - Check for port conflicts

4. **"No alerts found"**
   - Verify Wazuh has generated some alerts
   - Check agent connectivity to Wazuh manager

### Debug Commands
```bash
# Test Wazuh connection
cd backend && source venv/bin/activate && python test_wazuh.py

# Check API health
curl http://localhost:8000/api/health

# View backend logs
cd backend && source venv/bin/activate && python main.py
```

## 🧠 RAG Knowledge Base

The system now includes a RAG (Retrieval-Augmented Generation) knowledge base:

- **Document Upload**: Upload text files to build knowledge base
- **Intelligent Search**: Query documents using natural language
- **Gemini Integration**: AI-powered responses based on your documents
- **API Endpoints**: `/api/rag/upload`, `/api/rag/query`, `/api/rag/status`

### RAG Usage Examples:
- "Search knowledge about Wazuh rules"
- "Find information about SIEM configuration"
- "Query documents for incident response procedures"

## 🔮 Future Enhancements

- 🎯 **Threat Intelligence Integration** - VirusTotal, AbuseIPDB
- 🤖 **Automated Response Actions** - Block IPs, isolate agents
- 📊 **Custom Report Generation** - Compliance and executive reports
- 🏢 **Multi-tenant Support** - Multiple organizations
- 📱 **Mobile App** - iOS/Android companion
- 🔔 **Alert Notifications** - Slack, Teams, email integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- 📧 **Issues**: Create a GitHub issue
- 💬 **Discussions**: Use GitHub discussions
- 📖 **Documentation**: Check the wiki

---

**Built with ❤️ for the cybersecurity community**