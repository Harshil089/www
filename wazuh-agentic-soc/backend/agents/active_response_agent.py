from langchain_core.tools import tool
from integrations.wazuh_client import WazuhClient
import re

def active_response_agent(query: str) -> str:
    """Active Response and Orchestration Agent - Executes automated responses"""
    try:
        wazuh = WazuhClient()
        query_lower = query.lower()
        
        result = "🤖 Active Response and Orchestration\n"
        result += "=" * 50 + "\n\n"
        
        # Get available active response commands
        ar_data = wazuh.get_active_response()
        
        if 'list' in query_lower or 'show' in query_lower or 'available' in query_lower:
            result += f"📋 Available Active Response Commands:\n"
            result += f"- firewall-drop: Block IP address\n"
            result += f"- disconnect-agent: Disconnect agent from manager\n"
            result += f"- restart-ossec: Restart Wazuh agent\n"
            result += f"- custom-command: Execute custom script\n\n"
            result += f"💡 Usage: 'trigger [command] for agent [id]'\n"
            return result
        
        # Extract command
        command = None
        if 'firewall' in query_lower or 'drop' in query_lower or 'block' in query_lower:
            command = 'firewall-drop'
        elif 'disconnect' in query_lower or 'isolate' in query_lower:
            command = 'disconnect-agent'
        elif 'restart' in query_lower:
            command = 'restart-ossec'
        
        # Extract agent ID
        agent_match = re.search(r'agent\s+(\d+)', query_lower)
        agent_id = agent_match.group(1) if agent_match else None
        
        # Extract IP if firewall command
        ip_address = None
        if command == 'firewall-drop':
            ip_match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', query)
            if ip_match:
                ip_address = ip_match.group()
        
        if command and agent_id:
            result += f"⚠️ PROPOSED ACTIVE RESPONSE ACTION:\n\n"
            result += f"Command: {command}\n"
            result += f"Target Agent: {agent_id}\n"
            if ip_address:
                result += f"IP Address: {ip_address}\n"
            result += f"\n"
            
            # Get context
            alerts = wazuh.get_alerts(limit=10, severity_min=7)
            items = alerts.get('data', {}).get('affected_items', [])
            agent_alerts = [a for a in items if str(a.get('agent', {}).get('id')) == agent_id]
            
            if agent_alerts:
                result += f"📋 Context - Recent Alerts from Agent {agent_id}:\n"
                for alert in agent_alerts[:3]:
                    rule = alert.get('rule', {})
                    result += f"- Rule {rule.get('id')}: {rule.get('description', 'N/A')[:50]}...\n"
                    result += f"  Level: {rule.get('level')}\n"
            
            result += f"\n⚠️ REQUIRES APPROVAL\n"
            result += f"This action will be executed immediately upon approval.\n"
            result += f"To approve, respond: 'approve {command} agent {agent_id}'\n"
        
        elif 'approve' in query_lower and command and agent_id:
            # Execute approved action
            arguments = []
            if command == 'firewall-drop' and ip_address:
                arguments = [ip_address]
            
            ar_result = wazuh.trigger_active_response(
                command=command,
                agent_id=agent_id,
                arguments=arguments if arguments else None
            )
            
            if ar_result.get('error'):
                result += f"❌ Error executing active response: {ar_result['error']}\n"
            else:
                result += f"✅ Active Response Executed Successfully:\n"
                result += f"- Command: {command}\n"
                result += f"- Agent: {agent_id}\n"
                if ip_address:
                    result += f"- IP: {ip_address}\n"
                result += f"- Status: Success\n"
                result += f"\n📝 Action logged for audit trail.\n"
        
        elif 'orchestrate' in query_lower or 'workflow' in query_lower:
            # Multi-step workflow
            result += f"🔄 Orchestrated Response Workflow:\n\n"
            result += f"1. Detect Threat\n"
            result += f"   - Analyze alerts\n"
            result += f"   - Identify indicators\n\n"
            result += f"2. Assess Impact\n"
            result += f"   - Determine severity\n"
            result += f"   - Identify affected systems\n\n"
            result += f"3. Execute Response\n"
            result += f"   - Block IP addresses\n"
            result += f"   - Isolate affected agents\n"
            result += f"   - Collect evidence\n\n"
            result += f"4. Escalate if Needed\n"
            result += f"   - Generate incident report\n"
            result += f"   - Notify security team\n\n"
            result += f"💡 To trigger orchestrated response:\n"
            result += f"'orchestrate response for incident [description]'\n"
        
        else:
            result += f"💡 Active Response Agent Commands:\n"
            result += f"- 'list active responses' - Show available commands\n"
            result += f"- 'trigger firewall-drop for agent [id] IP [address]' - Block IP\n"
            result += f"- 'trigger disconnect-agent for agent [id]' - Isolate agent\n"
            result += f"- 'show orchestration workflow' - View multi-step workflows\n"
        
        return result
    
    except Exception as e:
        return f"Error in Active Response Agent: {str(e)}"

@tool
def active_response_tool(query: str) -> str:
    """Active Response and Orchestration Agent. Use for: 'active response', 'trigger command', 'orchestrate response', 'automated response'."""
    return active_response_agent(query)

