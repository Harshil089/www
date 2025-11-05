# 🤖 Agentic AI System - How It Works

## Overview

The Wazuh Agentic SOC uses a **hybrid agentic AI architecture** that combines keyword-based routing with LLM-enhanced responses. This document explains exactly how the agentic system processes queries and selects agents.

---

## 🎯 Core Concept

The system uses **two-stage processing**:
1. **Stage 1: Fast Tool Selection** - Keyword-based routing (deterministic, no LLM)
2. **Stage 2: Response Enhancement** - LLM processing (conversational output)

---

## 📋 Architecture Components

### 1. SOCOrchestrator (Main Coordinator)

**Location**: `backend/agents/orchestrator.py`

**Purpose**: Central intelligence that routes queries and enhances responses

**Key Components**:
```python
class SOCOrchestrator:
    - llm: ChatGoogleGenerativeAI (Gemini 2.0 Flash)
    - tools: Dictionary mapping tool names to functions
        {
            "alerts": fetch_alerts,
            "rules": fetch_rules,
            "agents": fetch_agents,
            "firewall": parse_firewall_request
        }
```

### 2. Specialized Agents

Each agent is a **specialized function** that handles a specific domain:

| Agent | Purpose | Function | Data Source |
|-------|---------|----------|-------------|
| **Alert Agent** | Security alerts | `fetch_alerts()` | Wazuh Alerts API |
| **Rule Agent** | Wazuh rules | `fetch_rules()` | Wazuh Rules API |
| **Agent Manager** | Endpoint status | `fetch_agents()` | Wazuh Agents API |
| **Firewall Agent** | Firewall commands | `parse_firewall_request()` | System iptables |

---

## 🔄 Complete Query Processing Flow

### Step-by-Step Execution

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: User Query                                          │
│ "Show me critical alerts from the last hour"                │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: WebSocket Transmission                              │
│ Frontend → Backend: { query: "Show me critical alerts..." } │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Orchestrator Receives Query                        │
│ orchestrator.process_query(user_query)                     │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Tool Selection (Keyword Matching)                  │
│ _determine_tool(query)                                      │
│                                                             │
│ Keyword Detection:                                          │
│ - "critical" → found in alerts keywords                    │
│ - "alerts" → found in alerts keywords                      │
│                                                             │
│ Result: tool_name = "alerts"                               │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Agent Execution                                     │
│ tool_func = self.tools["alerts"]  # fetch_alerts           │
│ result = fetch_alerts(query)                                │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: Wazuh API Call                                      │
│ WazuhClient.get_alerts(limit=50, severity_min=5)          │
│                                                             │
│ HTTPS Request:                                              │
│ GET https://{host}:{port}/alerts?limit=50&q=rule.level>5   │
│ Headers: Authorization: Bearer {JWT_TOKEN}                │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 7: Raw Data Received                                   │
│ {                                                           │
│   "data": {                                                 │
│     "affected_items": [                                     │
│       {                                                     │
│         "rule": {"id": 5710, "level": 10, ...},           │
│         "agent": {"name": "server-01", ...},               │
│         "timestamp": "2024-01-15T10:30:00Z"               │
│       }, ...                                                │
│     ]                                                       │
│   }                                                         │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 8: Data Formatting                                     │
│ Alert agent formats data into readable string:             │
│                                                             │
│ "Found 5 alerts:                                            │
│                                                             │
│ 1. Rule 5710: Login attempt failure                        │
│    Level: 10 | Agent: server-01                            │
│    Timestamp: 2024-01-15T10:30:00Z                         │
│                                                             │
│ 2. Rule 5503: ..."                                         │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 9: LLM Enhancement                                     │
│ Enhanced prompt sent to Gemini:                             │
│                                                             │
│ "User asked: 'Show me critical alerts from the last hour'  │
│                                                             │
│ Raw data from system:                                       │
│ Found 5 alerts:                                             │
│ 1. Rule 5710: Login attempt failure                        │
│ ...                                                         │
│                                                             │
│ Please provide a helpful, conversational response that:    │
│ 1. Directly answers the user's question                    │
│ 2. Summarizes the key findings                             │
│ 3. Provides actionable insights if relevant                │
│ 4. Uses a friendly, professional SOC analyst tone"          │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 10: LLM Response                                       │
│ Gemini generates conversational response:                   │
│                                                             │
│ "I found 5 critical security alerts from the last hour.    │
│ The most significant issue is a login attempt failure      │
│ (Rule 5710) detected on server-01 at 10:30 AM. This       │
│ could indicate a potential brute force attack. I recommend  │
│ reviewing the source IP address and considering temporary   │
│ IP blocking if the pattern continues..."                   │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 11: Response Transmission                              │
│ WebSocket.send_json({                                       │
│   "type": "bot",                                            │
│   "content": "I found 5 critical security alerts..."       │
│ })                                                          │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 12: Frontend Display                                   │
│ ChatBot component displays enhanced response to user       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Tool Selection Algorithm

### Keyword-Based Routing Logic

The `_determine_tool()` method uses a **priority-based keyword matching** system:

```python
def _determine_tool(self, query: str) -> str:
    query_lower = query.lower()
    
    # Priority 1: Firewall (highest priority - actions)
    if any(word in query_lower for word in [
        'block', 'allow', 'firewall', 'iptables', 'port'
    ]):
        return "firewall"
    
    # Priority 2: Alerts (security events)
    if any(word in query_lower for word in [
        'alert', 'incident', 'security event', 'attack', 
        'breach', 'critical', 'high', 'threat'
    ]):
        return "alerts"
    
    # Priority 3: Rules (policy/rule definitions)
    if any(word in query_lower for word in [
        'rule', 'policy', 'regulation', 'compliance'
    ]):
        return "rules"
    
    # Priority 4: Agents (endpoint status)
    if any(word in query_lower for word in [
        'agent', 'host', 'server', 'endpoint', 'machine',
        'online', 'offline', 'status', 'connectivity'
    ]):
        return "agents"
    
    # Default: Alerts (safest fallback for security queries)
    return "alerts"
```

### Example Queries and Routing

| User Query | Detected Keywords | Selected Tool | Agent Function |
|------------|------------------|---------------|----------------|
| "Show me critical alerts" | `critical`, `alerts` | `alerts` | `fetch_alerts()` |
| "How many agents are online?" | `agents`, `online` | `agents` | `fetch_agents()` |
| "What does rule 5710 do?" | `rule` | `rules` | `fetch_rules()` |
| "Block IP 192.168.1.100" | `block`, `ip` | `firewall` | `parse_firewall_request()` |
| "Show me recent security events" | `security event` | `alerts` | `fetch_alerts()` |
| "List all endpoints" | `endpoint` | `agents` | `fetch_agents()` |

### Ambiguity Handling

**Case 1: Multiple keywords match**
- Priority order determines selection (firewall > alerts > rules > agents)
- Example: "Block alerts from agent" → selects `firewall` (action keyword)

**Case 2: No keywords match**
- Defaults to `alerts` (safest for SOC context)
- Example: "What's happening?" → selects `alerts`

**Case 3: Ambiguous query**
- First matching keyword wins
- Example: "Show me rule alerts" → selects `alerts` (checked first)

---

## 🧠 LLM Enhancement Process

### Why LLM Enhancement?

The raw data from Wazuh APIs is **structured but not conversational**:
- Raw: "Found 5 alerts: Rule 5710: Login attempt failure..."
- Enhanced: "I found 5 critical security alerts. The most significant issue..."

### Enhancement Prompt Structure

```python
enhanced_prompt = f"""
User asked: "{user_query}"

Raw data from system:
{result}

Please provide a helpful, conversational response that:
1. Directly answers the user's question
2. Summarizes the key findings
3. Provides actionable insights if relevant
4. Uses a friendly, professional SOC analyst tone

Keep the response concise but informative.
"""
```

### LLM Configuration

```python
self.llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",  # Google Gemini 2.0 Flash (experimental)
    google_api_key=api_key,
    temperature=0.1  # Low temperature for consistent, focused responses
)
```

**Why Low Temperature (0.1)?**
- Ensures consistent, factual responses
- Reduces hallucination
- Better for SOC analyst queries requiring accuracy

---

## 🔧 Agent Implementations

### Alert Agent (`fetch_alerts()`)

**Function Signature**: `fetch_alerts(query: str) -> str`

**Process**:
1. Creates `WazuhClient` instance
2. Calls `wazuh.get_alerts(limit=50, severity_min=5)`
3. Extracts `affected_items` from response
4. Formats first 5 alerts with:
   - Rule ID and description
   - Severity level
   - Agent name
   - Timestamp
5. Returns formatted string

**Example Output**:
```
Found 5 alerts:

1. Rule 5710: Login attempt failure
   Level: 10 | Agent: server-01
   Timestamp: 2024-01-15T10:30:00Z

2. Rule 5503: Invalid login attempt
   Level: 10 | Agent: server-02
   Timestamp: 2024-01-15T10:25:00Z

... and 3 more alerts
```

### Rule Agent (`fetch_rules()`)

**Function Signature**: `fetch_rules(query: str) -> str`

**Process**:
1. Creates `WazuhClient` instance
2. Calls `wazuh.get_rules()` (can filter by rule_id if parsed)
3. Formats rule information:
   - Rule ID and description
   - Severity level
   - Associated groups
4. Returns formatted string

**Example Output**:
```
Found 100 rules:

1. Rule 5710: Login attempt failure
   Level: 10 | Groups: authentication, failed_login

2. Rule 5503: Invalid login attempt
   Level: 10 | Groups: authentication, invalid_login

... and 95 more rules
```

### Agent Manager (`fetch_agents()`)

**Function Signature**: `fetch_agents(query: str) -> str`

**Process**:
1. Creates `WazuhClient` instance
2. Calls `wazuh.get_agents()`
3. Calculates statistics:
   - Total agents count
   - Active agents count (status == 'active')
   - Inactive agents count
4. Formats agent details:
   - Agent name and ID
   - Status (active/inactive)
   - OS information
   - IP address
   - Last keep-alive timestamp
5. Returns formatted string

**Example Output**:
```
Agent Status Summary:
Total Agents: 25
Active Agents: 23
Inactive Agents: 2

Recent Agents:
1. server-01 (001)
   Status: active | OS: Linux Ubuntu 22.04
   IP: 192.168.1.100 | Last Keep Alive: 2024-01-15T10:30:00Z

2. server-02 (002)
   Status: active | OS: Linux CentOS 8
   IP: 192.168.1.101 | Last Keep Alive: 2024-01-15T10:29:00Z

... and 3 more agents
```

### Firewall Agent (`parse_firewall_request()`)

**Function Signature**: `parse_firewall_request(query: str) -> str`

**Process**:
1. Uses regex to extract:
   - IP addresses: `\b(?:\d{1,3}\.){3}\d{1,3}\b`
   - Port numbers: `\b\d{1,5}\b`
2. Determines action type:
   - Block IP → `iptables -A INPUT -s {ip} -j DROP`
   - Allow port → `iptables -A INPUT -p tcp --dport {port} -j ACCEPT`
   - Block port → `iptables -A INPUT -p tcp --dport {port} -j DROP`
3. Executes command via `subprocess.run()`
4. Returns execution result

**Example Commands**:
- "Block IP 192.168.1.100" → `sudo iptables -A INPUT -s 192.168.1.100 -j DROP`
- "Allow port 80" → `sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT`
- "Block port 22" → `sudo iptables -A INPUT -p tcp --dport 22 -j DROP`

**⚠️ Security Note**: In production, add:
- Input validation
- Command whitelisting
- Permission checks
- Audit logging

---

## 🎯 Design Decisions

### Why Keyword-Based Routing?

**Advantages**:
- ✅ **Fast**: No LLM latency for tool selection
- ✅ **Deterministic**: Same query always routes to same agent
- ✅ **Reliable**: No hallucination in tool selection
- ✅ **Cost-effective**: Only one LLM call per query
- ✅ **Debuggable**: Easy to trace routing decisions

**Disadvantages**:
- ❌ **Limited flexibility**: Can't handle complex intent
- ❌ **Keyword maintenance**: Needs keyword updates for new patterns
- ❌ **Ambiguity**: Can misroute ambiguous queries

### Why LLM Enhancement?

**Advantages**:
- ✅ **Conversational**: Natural language responses
- ✅ **Context-aware**: Understands user intent
- ✅ **Actionable**: Provides insights and recommendations
- ✅ **Professional tone**: Matches SOC analyst communication style

**Trade-offs**:
- ⚠️ **Latency**: Adds ~1-2 seconds per query
- ⚠️ **Cost**: LLM API calls cost money
- ⚠️ **Variability**: Responses may vary slightly

---

## 🔮 Future Enhancements

### Potential Improvements

1. **LLM-Based Tool Selection**:
   ```python
   # Use Gemini's function calling
   tools = [alert_tool, rule_tool, agent_tool, firewall_tool]
   response = llm.bind_tools(tools).invoke(query)
   # LLM selects tool automatically
   ```

2. **Multi-Agent Collaboration**:
   ```python
   # Agents can call other agents
   if alert_agent detects rule issue:
       rule_details = rule_agent.fetch_rules(rule_id)
       combined_response = combine(alert, rule_details)
   ```

3. **Context Memory**:
   ```python
   # Maintain conversation context
   conversation_history = [...]
   enhanced_prompt = include_context(conversation_history, query)
   ```

4. **Structured Output**:
   ```python
   # Use Pydantic models for structured responses
   class AlertResponse(BaseModel):
       count: int
       critical_alerts: List[Alert]
       recommendations: List[str]
   ```

5. **Tool Chaining**:
   ```python
   # Chain multiple tools for complex queries
   if query needs alerts AND rules:
       alerts = fetch_alerts(query)
       rules = fetch_rules(query)
       combined = combine_results(alerts, rules)
   ```

---

## 📊 Performance Characteristics

### Latency Breakdown

| Stage | Duration | Notes |
|-------|----------|-------|
| Keyword matching | <1ms | Instant |
| Agent execution | 100-500ms | Wazuh API call |
| LLM enhancement | 1000-2000ms | Gemini API call |
| **Total** | **~1.1-2.5s** | Per query |

### Optimization Opportunities

1. **Parallel Processing**: Execute agent and LLM enhancement in parallel
2. **Caching**: Cache frequent queries (e.g., "show me agents")
3. **Streaming**: Stream LLM responses word-by-word
4. **Batch Processing**: Batch multiple queries

---

## 🎓 Summary

The agentic AI system uses a **hybrid approach**:

1. **Fast, deterministic routing** (keyword-based) → selects agent
2. **Intelligent enhancement** (LLM-based) → improves response

This design balances:
- ⚡ **Speed**: Fast tool selection
- 🎯 **Accuracy**: Reliable routing
- 💬 **Intelligence**: Conversational responses
- 💰 **Cost**: Single LLM call per query

The system is **production-ready** for basic SOC operations but has room for enhancement with advanced agentic patterns like LLM-based tool selection and multi-agent collaboration.

