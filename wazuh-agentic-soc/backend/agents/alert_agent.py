from langchain_core.tools import tool
from integrations.wazuh_client import WazuhClient

def fetch_alerts(query: str) -> str:
    """Fetch and filter Wazuh alerts based on natural language query"""
    try:
        wazuh = WazuhClient()
        alerts = wazuh.get_alerts()
        
        if alerts.get('error', 0) != 0:
            return f"Error fetching alerts: {alerts['error']}"
        
        items = alerts.get('data', {}).get('affected_items', [])
        
        if not items:
            return "No alerts found matching the criteria."
        
        result = f"Found {len(items)} alerts:\n\n"
        for i, alert in enumerate(items[:5], 1):
            rule = alert.get('rule', {})
            result += f"{i}. Rule {rule.get('id', 'N/A')}: {rule.get('description', 'No description')}\n"
            result += f"   Level: {rule.get('level', 'N/A')} | Agent: {alert.get('agent', {}).get('name', 'N/A')}\n"
            result += f"   Timestamp: {alert.get('timestamp', 'N/A')}\n\n"
        
        if len(items) > 5:
            result += f"... and {len(items) - 5} more alerts"
        
        return result
    except Exception as e:
        return f"Error processing alert query: {str(e)}"

@tool
def alert_tool(query: str) -> str:
    """Fetch and analyze Wazuh alerts. Use for queries about alerts, incidents, or security events."""
    return fetch_alerts(query)