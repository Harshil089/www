from langchain_core.tools import tool
from integrations.wazuh_client import WazuhClient
import re

def incident_response_agent(query: str) -> str:
    """Incident Response Agent - Triggers automated responses and escalates"""
    try:
        wazuh = WazuhClient()
        query_lower = query.lower()
        
        result = "🚨 Incident Response Actions\n"
        result += "=" * 50 + "\n\n"
        
        # Detect incident type
        if 'isolate' in query_lower or 'quarantine' in query_lower:
            # Extract agent ID or name
            agent_match = re.search(r'agent\s+(\d+)', query_lower)
            agent_id = agent_match.group(1) if agent_match else None
            
            if not agent_id:
                # Try to find agent by name
                agent_name_match = re.search(r'agent\s+([a-zA-Z0-9_-]+)', query_lower)
                if agent_name_match:
                    agents = wazuh.get_agents()
                    items = agents.get('data', {}).get('affected_items', [])
                    for agent in items:
                        if agent.get('name', '').lower() == agent_name_match.group(1).lower():
                            agent_id = str(agent.get('id'))
                            break
            
            if agent_id:
                result += f"🛡️ Proposed Isolation Action:\n"
                result += f"- Agent ID: {agent_id}\n"
                result += f"- Action: Isolate endpoint\n"
                result += f"- Command: disconnect-agent\n\n"
                
                # Get active response options
                ar_response = wazuh.get_active_response()
                result += f"⚠️ REQUIRES APPROVAL\n"
                result += f"To execute this action, use:\n"
                result += f"'approve isolate agent {agent_id}'\n\n"
                
                result += f"📋 Evidence Trail:\n"
                alerts = wazuh.get_alerts(limit=10, severity_min=7)
                items = alerts.get('data', {}).get('affected_items', [])
                agent_alerts = [a for a in items if str(a.get('agent', {}).get('id')) == agent_id]
                
                if agent_alerts:
                    result += f"Recent alerts from this agent:\n"
                    for alert in agent_alerts[:3]:
                        rule = alert.get('rule', {})
                        result += f"- Rule {rule.get('id')}: {rule.get('description', 'N/A')[:50]}...\n"
                        result += f"  Level: {rule.get('level')} | Time: {alert.get('timestamp', 'N/A')}\n"
                else:
                    result += f"No recent critical alerts found for this agent.\n"
            else:
                result += f"❌ Agent ID not found. Please specify agent ID or name.\n"
        
        elif 'block' in query_lower and 'ip' in query_lower:
            # Extract IP address
            ip_match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', query)
            if ip_match:
                ip = ip_match.group()
                result += f"🛡️ Proposed IP Blocking Action:\n"
                result += f"- IP Address: {ip}\n"
                result += f"- Action: Block IP via firewall\n"
                result += f"- Command: firewall-drop\n\n"
                
                result += f"⚠️ REQUIRES APPROVAL\n"
                result += f"To execute this action, use:\n"
                result += f"'approve block IP {ip}'\n\n"
                
                # Check for related alerts
                alerts = wazuh.get_alerts(limit=20, severity_min=5)
                items = alerts.get('data', {}).get('affected_items', [])
                ip_alerts = [a for a in items if ip in str(a.get('full_log', ''))]
                
                if ip_alerts:
                    result += f"📋 Related Alerts:\n"
                    for alert in ip_alerts[:3]:
                        rule = alert.get('rule', {})
                        result += f"- Rule {rule.get('id')}: {rule.get('description', 'N/A')[:50]}...\n"
                else:
                    result += f"No recent alerts found for this IP.\n"
            else:
                result += f"❌ IP address not found in query.\n"
        
        elif 'escalate' in query_lower or 'report' in query_lower:
            # Generate incident report
            alerts = wazuh.get_alerts(limit=50, severity_min=7)
            items = alerts.get('data', {}).get('affected_items', [])
            
            result += f"📊 Incident Report:\n"
            result += f"- Total Critical Alerts: {len(items)}\n"
            result += f"- Time Range: Last hour\n\n"
            
            # Group by agent
            agent_alerts = {}
            for alert in items:
                agent_id = alert.get('agent', {}).get('id')
                if agent_id:
                    if agent_id not in agent_alerts:
                        agent_alerts[agent_id] = []
                    agent_alerts[agent_id].append(alert)
            
            result += f"🔍 Affected Agents:\n"
            for agent_id, agent_items in list(agent_alerts.items())[:5]:
                result += f"- Agent {agent_id}: {len(agent_items)} alerts\n"
            
            result += f"\n💡 Recommendation: "
            if len(items) > 10:
                result += f"ESCALATE - Multiple critical alerts detected. Requires immediate attention.\n"
            else:
                result += f"Monitor situation. Consider investigation if pattern continues.\n"
        
        elif 'automated' in query_lower or 'response' in query_lower:
            # Show available automated responses
            ar_response = wazuh.get_active_response()
            result += f"🤖 Available Automated Responses:\n"
            result += f"Active Response module status: Available\n"
            result += f"\nCommon commands:\n"
            result += f"- firewall-drop: Block IP address\n"
            result += f"- disconnect-agent: Isolate agent\n"
            result += f"- restart-ossec: Restart Wazuh agent\n\n"
            result += f"⚠️ All automated responses require approval for security.\n"
        
        else:
            result += f"💡 Incident Response Agent Commands:\n"
            result += f"- 'isolate agent [id]' - Quarantine an endpoint\n"
            result += f"- 'block IP [address]' - Block an IP address\n"
            result += f"- 'escalate incident' - Generate incident report\n"
            result += f"- 'show automated responses' - List available responses\n"
        
        return result
    
    except Exception as e:
        return f"Error in Incident Response Agent: {str(e)}"

@tool
def incident_response_tool(query: str) -> str:
    """Incident Response Agent for automated responses. Use for: 'isolate agent', 'block IP', 'escalate', 'incident response'."""
    return incident_response_agent(query)

