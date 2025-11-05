from langchain_core.tools import tool
import json

def dashboard_agent(event_data: dict) -> dict:
    """WAZUH_DASH_AGENT - Maps UI events to Wazuh API calls"""
    event = event_data.get("event")
    target_id = event_data.get("target_id")
    params = event_data.get("params", {})
    
    if event == "click":
        if target_id == "view_all_alerts":
            return {
                "navigate": "/alerts",
                "http": [{
                    "id": "alerts",
                    "method": "GET",
                    "url": "/alerts",
                    "query": {"limit": 100, "sort": "-timestamp"},
                    "headers": {"Authorization": "Bearer {{JWT}}"}
                }],
                "render": [{
                    "target": "#alerts_table",
                    "type": "table",
                    "from_http": "alerts",
                    "columns": ["timestamp", "severity", "agent.name", "rule.id", "rule.description"],
                    "empty": "No alerts in the selected window."
                }],
                "toasts": []
            }
        
        elif target_id == "agent_status":
            return {
                "navigate": "/agents",
                "http": [{
                    "id": "agents",
                    "method": "GET",
                    "url": "/agents",
                    "query": {"limit": 200},
                    "headers": {"Authorization": "Bearer {{JWT}}"}
                }],
                "render": [{
                    "target": "#agents_table",
                    "type": "table",
                    "from_http": "agents",
                    "columns": ["id", "name", "ip", "status", "os.platform", "last_keepalive"],
                    "empty": "No agents found."
                }],
                "toasts": []
            }
        
        elif target_id == "rule_management":
            return {
                "navigate": "/rules",
                "http": [{
                    "id": "rules",
                    "method": "GET",
                    "url": "/rules",
                    "query": {"limit": 200},
                    "headers": {"Authorization": "Bearer {{JWT}}"}
                }],
                "render": [{
                    "target": "#rules_table",
                    "type": "table",
                    "from_http": "rules",
                    "columns": ["id", "level", "description", "file"],
                    "empty": "No rules found."
                }],
                "toasts": []
            }
        
        elif target_id == "threat_intelligence":
            return {
                "navigate": "/intel",
                "http": [{
                    "id": "high_alerts",
                    "method": "GET",
                    "url": "/alerts",
                    "query": {"limit": 50, "q": "rule.level>7"},
                    "headers": {"Authorization": "Bearer {{JWT}}"}
                }],
                "render": [{
                    "target": "#intel_panel",
                    "type": "cards",
                    "from_http": "high_alerts",
                    "empty": "No threat intelligence data."
                }],
                "toasts": []
            }
    
    return {
        "navigate": None,
        "http": [],
        "render": [],
        "toasts": [f"Unknown action: {target_id}"],
        "state": {}
    }

@tool
def dashboard_tool(event_data: str) -> str:
    """Dashboard Agent for UI button actions."""
    try:
        data = json.loads(event_data)
        result = dashboard_agent(data)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})