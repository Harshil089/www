from fastapi import APIRouter
from integrations.wazuh_client import WazuhClient

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats():
    """Get real-time dashboard statistics"""
    try:
        client = WazuhClient()
        
        # Get agents
        agents_data = client.get_agents()
        agents = agents_data.get('data', {}).get('affected_items', [])
        active_agents = sum(1 for agent in agents if agent.get('status') == 'active')
        
        # Get alerts
        alerts_data = client.get_alerts(limit=100, severity_min=7)
        alerts = alerts_data.get('data', {}).get('affected_items', [])
        critical_alerts = len(alerts)
        
        # Get rules
        rules_data = client.get_rules()
        rules = rules_data.get('data', {}).get('affected_items', [])
        total_rules = len(rules)
        
        return {
            "active_agents": active_agents,
            "total_agents": len(agents),
            "critical_alerts": critical_alerts,
            "total_rules": total_rules,
            "recent_alerts": alerts[:5],
            "connection_status": "connected"
        }
    except Exception as e:
        return {
            "active_agents": 0,
            "total_agents": 0,
            "critical_alerts": 0,
            "total_rules": 0,
            "recent_alerts": [],
            "connection_status": "disconnected",
            "error": str(e)
        }