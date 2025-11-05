# 🏗️ Wazuh Agentic SOC - Architecture Documentation

## Overview

This is an **Agentic SOC (Security Operations Center) Dashboard** that integrates with Wazuh SIEM using Google Gemini AI for intelligent query processing and natural language interaction.

---

## 🎯 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  ┌──────────────┐                    ┌──────────────────────┐   │
│  │  Dashboard   │                    │     ChatBot         │   │
│  │  Component   │◄─────────┐         │   Component         │   │
│  └──────────────┘           │         └──────────────────────┘   │
│         │                   │                    │              │
│         │ HTTP REST         │     WebSocket      │              │
│         │ /api/stats        │     /ws/chat       │              │
└─────────┼───────────────────┼────────────────────┼──────────────┘
          │                   │                    │
          ▼                   ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              main.py (FastAPI Server)                    │  │
│  │  • WebSocket endpoint: /ws/chat                          │  │
│  │  • REST endpoint: /api/stats                             │  │
│  │  • REST endpoint: /api/health                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │        SOCOrchestrator (Agentic AI Coordinator)          │  │
│  │  • Uses Google Gemini 2.0 Flash (langchain_google_genai) │  │
│  │  • Keyword-based tool selection                          │  │
│  │  • LLM response enhancement                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│          ┌────────────────┼────────────────┐                   │
│          ▼                 ▼                 ▼                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Alert Agent  │  │ Rule Agent   │  │ Agent Manager│         │
│  │              │  │              │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│          │                 │                 │                  │
│          └─────────────────┼─────────────────┘                 │
│                            ▼                                    │
│              ┌─────────────────────────────┐                  │
│              │    WazuhClient               │                  │
│              │  (Integration Layer)          │                  │
│              └─────────────────────────────┘                  │
│                            │                                    │
└────────────────────────────┼────────────────────────────────────┘
                             ▼
              ┌─────────────────────────────┐
              │   Wazuh Manager API         │
              │   (Windows Server)          │
              │   HTTPS :55000              │
              └─────────────────────────────┘
```

---

## 📁 Frontend Architecture

### Technology Stack
- **Framework**: React 19.1.1
- **Build Tool**: Vite 7.1.7
- **Styling**: Tailwind CSS 4.1.16
- **Icons**: Lucide React
- **Communication**: WebSocket API (native), Fetch API (REST)

### Component Structure

#### `src/App.jsx`
- Root component that renders the Dashboard

#### `src/components/Dashboard.jsx`
**Purpose**: Main dashboard UI displaying SOC metrics and alerts

**Key Features**:
- **Stats Cards**: Displays critical alerts, active agents, total rules, and incidents
- **Recent Alerts Table**: Shows latest security alerts with severity indicators
- **System Health Panel**: Shows connection status to Wazuh manager
- **Quick Actions**: Buttons for common SOC operations

**Data Flow**:
- Polls `/api/stats` endpoint every 10 seconds
- Updates dashboard metrics in real-time
- Handles connection errors gracefully

**State Management**:
```javascript
- stats: { criticalAlerts, activeAgents, totalRules, incidents, connectionStatus }
- alerts: Array of recent alert objects
- chatOpen: Boolean to toggle chatbot sidebar
```

#### `src/components/ChatBot.jsx`
**Purpose**: AI-powered chat interface for natural language SOC queries

**Key Features**:
- **WebSocket Connection**: Connects to `ws://localhost:8000/ws/chat`
- **Real-time Messaging**: Bidirectional communication with backend
- **Connection Status**: Visual indicator (green/red dot) for connection state
- **Message History**: Displays conversation with user and bot messages

**Data Flow**:
```
User Input → WebSocket.send({ query: "..." }) → Backend Processing → WebSocket Response → UI Update
```

**State Management**:
```javascript
- messages: Array of { type: 'user'|'bot', content: string }
- input: Current input field value
- ws: WebSocket instance
- isConnected: Boolean connection status
```

---

## 🔧 Backend Architecture

### Technology Stack
- **Framework**: FastAPI 0.121.0
- **ASGI Server**: Uvicorn 0.38.0
- **AI/LLM**: LangChain 1.0.3 + langchain-google-genai 3.0.1
- **LLM Model**: Google Gemini 2.0 Flash (experimental)
- **WebSocket**: websockets 15.0.1
- **HTTP Client**: requests 2.32.5
- **Environment**: python-dotenv 1.2.1

### Core Components

#### `main.py` - FastAPI Application
**Purpose**: Main server entry point and API routing

**Endpoints**:
- `GET /` - Root endpoint
- `GET /api/health` - Health check endpoint
- `GET /api/stats` - Dashboard statistics (via stats router)
- `WebSocket /ws/chat` - Chat interface endpoint

**Key Features**:
- CORS middleware for React frontend
- WebSocket connection management
- Thread pool executor for non-blocking AI processing
- Error handling and graceful degradation

**WebSocket Flow**:
```python
1. Accept WebSocket connection
2. Send welcome message
3. Loop:
   - Receive user query as JSON
   - Process via orchestrator (async executor)
   - Send response back as JSON
4. Handle disconnection cleanup
```

#### `agents/orchestrator.py` - SOC Orchestrator
**Purpose**: Central coordinator for agentic AI system

**Key Components**:

1. **SOCOrchestrator Class**:
   - Initializes Google Gemini LLM (`gemini-2.0-flash-exp`)
   - Manages tool registry (alerts, rules, agents, firewall)
   - Routes queries to appropriate agents
   - Enhances responses with LLM

2. **Tool Selection Logic** (`_determine_tool()`):
   ```python
   Keyword-based routing:
   - Firewall: 'block', 'allow', 'firewall', 'iptables', 'port'
   - Alerts: 'alert', 'incident', 'security event', 'attack', 'breach', 'critical', 'high'
   - Rules: 'rule', 'policy', 'regulation', 'compliance'
   - Agents: 'agent', 'host', 'server', 'endpoint', 'machine', 'online', 'offline', 'status'
   - Default: 'alerts' (for general security queries)
   ```

3. **Query Processing Flow** (`process_query()`):
   ```
   User Query
      ↓
   Determine Tool (keyword matching)
      ↓
   Execute Agent Function
      ↓
   Get Raw Data from Wazuh
      ↓
   Enhance Response with LLM
      ↓
   Return Enhanced Response
   ```

**LLM Enhancement Prompt**:
```python
enhanced_prompt = f"""
User asked: "{user_query}"
Raw data from system: {result}
Please provide a helpful, conversational response that:
1. Directly answers the user's question
2. Summarizes the key findings
3. Provides actionable insights if relevant
4. Uses a friendly, professional SOC analyst tone
"""
```

#### `agents/alert_agent.py` - Alert Agent
**Purpose**: Handles queries related to security alerts

**Function**: `fetch_alerts(query: str) -> str`

**Implementation**:
- Uses `WazuhClient` to fetch alerts from Wazuh API
- Default: Fetches alerts with `level > 5` (medium+ severity)
- Limits to 50 alerts, displays top 5 in response
- Formats alert data: rule ID, description, level, agent name, timestamp

**Tool Registration**: `@tool` decorator for LangChain integration

#### `agents/rule_agent.py` - Rule Agent
**Purpose**: Handles queries related to Wazuh rules

**Function**: `fetch_rules(query: str) -> str`

**Implementation**:
- Uses `WazuhClient` to fetch rules from Wazuh API
- Can filter by rule ID if specified
- Displays rule ID, description, level, and groups
- Shows top 5 rules in response

#### `agents/agent_manager.py` - Agent Manager
**Purpose**: Handles queries related to Wazuh agents/endpoints

**Function**: `fetch_agents(query: str) -> str`

**Implementation**:
- Uses `WazuhClient` to fetch agent list
- Calculates active/inactive agent counts
- Displays agent details: name, ID, status, OS, IP, last keep-alive
- Shows top 5 agents in response

#### `agents/firewall_agent.py` - Firewall Agent
**Purpose**: Handles firewall-related queries and commands

**Function**: `parse_firewall_request(query: str) -> str`

**Implementation**:
- Uses regex to extract IP addresses and port numbers
- Supports commands:
  - Block IP: `"block IP 192.168.1.100"` → `iptables -A INPUT -s {ip} -j DROP`
  - Allow Port: `"allow port 80"` → `iptables -A INPUT -p tcp --dport {port} -j ACCEPT`
  - Block Port: `"block port 22"` → `iptables -A INPUT -p tcp --dport {port} -j DROP`
- Executes commands via `subprocess.run()` (⚠️ Security note: should validate in production)

#### `integrations/wazuh_client.py` - Wazuh Integration Layer
**Purpose**: API client for Wazuh Manager

**Class**: `WazuhClient`

**Authentication**:
- Uses Basic Auth to get JWT token from `/security/user/authenticate`
- Stores token for subsequent API calls
- Token used in `Authorization: Bearer {token}` header

**Methods**:
- `get_alerts(limit=50, severity_min=5)`: Fetch alerts with filtering
- `get_agents()`: List all agents
- `get_rules(rule_id=None)`: Fetch rules (optionally filtered by ID)

**Configuration** (from `.env`):
- `WAZUH_HOST`: Wazuh manager IP address
- `WAZUH_PORT`: Wazuh API port (default: 55000)
- `WAZUH_USER`: Wazuh API username
- `WAZUH_PASSWORD`: Wazuh API password

**Error Handling**:
- Returns structured error responses: `{"data": {"affected_items": []}, "error": "..."}`
- Handles connection failures gracefully

#### `api/stats.py` - Statistics API Router
**Purpose**: Provides dashboard statistics endpoint

**Endpoint**: `GET /api/stats`

**Response**:
```json
{
  "active_agents": int,
  "total_agents": int,
  "critical_alerts": int,
  "total_rules": int,
  "recent_alerts": [alert objects],
  "connection_status": "connected" | "disconnected"
}
```

**Implementation**:
- Aggregates data from multiple Wazuh API calls
- Calculates active agents (status == 'active')
- Fetches critical alerts (level >= 7)
- Returns top 5 recent alerts

---

## 🤖 Agentic AI Flow

### Complete Query Processing Flow

```
1. User types query in ChatBot component
   ↓
2. WebSocket sends: { query: "Show me critical alerts" }
   ↓
3. FastAPI receives query in /ws/chat endpoint
   ↓
4. Query passed to orchestrator.process_query()
   ↓
5. Orchestrator._determine_tool() analyzes keywords
   - Detects "critical alerts" → selects "alerts" tool
   ↓
6. Executes fetch_alerts(query)
   ↓
7. Alert agent calls WazuhClient.get_alerts()
   ↓
8. WazuhClient makes HTTPS request to Wazuh Manager
   ↓
9. Raw alert data returned to alert agent
   ↓
10. Alert agent formats data into string
   ↓
11. Orchestrator enhances response with Gemini LLM
    - Constructs enhancement prompt
    - Sends to Gemini 2.0 Flash
    - Receives conversational response
   ↓
12. Enhanced response sent back via WebSocket
   ↓
13. ChatBot component displays response to user
```

### Agent Selection Logic

The orchestrator uses **keyword-based routing** (not LLM-based tool selection):

```python
def _determine_tool(self, query: str) -> str:
    query_lower = query.lower()
    
    # Priority order matters!
    if any(word in query_lower for word in ['block', 'allow', 'firewall', ...]):
        return "firewall"
    if any(word in query_lower for word in ['alert', 'incident', ...]):
        return "alerts"
    if any(word in query_lower for word in ['rule', 'policy', ...]):
        return "rules"
    if any(word in query_lower for word in ['agent', 'host', ...]):
        return "agents"
    
    return "alerts"  # Default fallback
```

**Note**: This is a **hybrid approach**:
- **Tool Selection**: Keyword-based (deterministic, fast)
- **Response Enhancement**: LLM-based (intelligent, conversational)

### Why This Architecture?

1. **Fast Tool Selection**: Keyword matching is instant (no LLM latency)
2. **Reliable Routing**: Deterministic routing ensures correct agent selection
3. **Intelligent Responses**: LLM enhancement makes responses conversational and helpful
4. **Cost Effective**: Only one LLM call per query (not multiple calls for tool selection)

### Potential Improvements

1. **LLM-based Tool Selection**: Use Gemini's function calling for smarter routing
2. **Multi-agent Collaboration**: Allow agents to call other agents
3. **Tool Chaining**: Chain multiple tools for complex queries
4. **Memory/Context**: Maintain conversation context across queries
5. **Structured Output**: Use Pydantic models for structured agent responses

---

## 🔄 Data Flow Diagrams

### Real-time Stats Flow
```
Dashboard Component
    ↓ (every 10s)
HTTP GET /api/stats
    ↓
stats.py router
    ↓
WazuhClient.get_agents()
WazuhClient.get_alerts()
WazuhClient.get_rules()
    ↓
Wazuh Manager API
    ↓
Aggregated JSON Response
    ↓
Dashboard State Update
```

### Chat Query Flow
```
User Input
    ↓
WebSocket.send({ query: "..." })
    ↓
FastAPI WebSocket Handler
    ↓
orchestrator.process_query()
    ↓
_determine_tool() → selects agent
    ↓
Agent function execution
    ↓
WazuhClient API call
    ↓
Raw data formatting
    ↓
LLM enhancement (Gemini)
    ↓
Enhanced response
    ↓
WebSocket.send_json({ content: "..." })
    ↓
ChatBot component update
```

---

## 🔐 Security Considerations

### Current Implementation
- ✅ Environment variables for sensitive credentials
- ✅ HTTPS for Wazuh API (with SSL verification disabled for dev)
- ✅ JWT token authentication with Wazuh
- ⚠️ Firewall agent executes shell commands (needs validation)
- ⚠️ No input sanitization for user queries
- ⚠️ No rate limiting on WebSocket connections

### Recommendations
- Add input validation and sanitization
- Implement rate limiting
- Add authentication/authorization for API endpoints
- Validate firewall commands before execution
- Enable SSL verification in production
- Add request logging and monitoring

---

## 🚀 Deployment Architecture

### Development
- Frontend: Vite dev server on port 5173
- Backend: Uvicorn on port 8000
- WebSocket: Native WebSocket API

### Production Considerations
- Frontend: Build static files (`npm run build`), serve via Nginx/CDN
- Backend: Use production ASGI server (Gunicorn + Uvicorn workers)
- WebSocket: Consider WebSocket proxy (Nginx, Traefik)
- Database: Add PostgreSQL for persistent storage (currently unused)
- Monitoring: Add logging, metrics, alerting
- Scaling: Horizontal scaling with load balancer

---

## 📊 Key Metrics & Monitoring

### Current Metrics
- Critical alerts count
- Active agents count
- Total rules count
- Connection status

### Potential Additions
- Query response time
- Agent selection accuracy
- LLM token usage
- Error rates
- User query patterns

---

## 🔮 Future Enhancements

Based on the README and codebase analysis:

1. **Enhanced Agentic System**:
   - LLM-based tool selection
   - Multi-agent collaboration
   - Tool chaining

2. **Threat Intelligence**:
   - VirusTotal integration
   - AbuseIPDB integration

3. **Automated Response**:
   - IP blocking automation
   - Agent isolation

4. **Reporting**:
   - Custom report generation
   - Compliance reports

5. **Multi-tenancy**:
   - Multiple organization support
   - Role-based access control

---

## 📝 Summary

This is a **hybrid agentic AI system** that combines:
- **Deterministic routing** (keyword-based) for fast, reliable tool selection
- **LLM enhancement** (Gemini) for intelligent, conversational responses
- **Specialized agents** for different SOC functions (alerts, rules, agents, firewall)
- **Real-time communication** via WebSocket for chat interface
- **REST API** for dashboard statistics

The system is designed for **SOC analysts** to interact with Wazuh SIEM using natural language, making security operations more accessible and efficient.

