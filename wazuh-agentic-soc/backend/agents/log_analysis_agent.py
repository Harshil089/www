from langchain_core.tools import tool
from integrations.wazuh_client import WazuhClient
import re

def log_analysis_agent(query: str) -> str:
    """Log Collection and Analysis Agent - Aggregates and analyzes logs"""
    try:
        wazuh = WazuhClient()
        query_lower = query.lower()
        
        result = "📋 Log Collection and Analysis Report\n"
        result += "=" * 50 + "\n\n"
        
        # Extract agent ID
        agent_match = re.search(r'agent\s+(\d+)', query_lower)
        agent_id = agent_match.group(1) if agent_match else None
        
        # Build query
        search_query = None
        if 'error' in query_lower:
            search_query = "level=error"
        elif 'warning' in query_lower:
            search_query = "level=warning"
        elif 'auth' in query_lower or 'login' in query_lower:
            search_query = "type=auth"
        
        # Get logs
        logs_data = wazuh.get_logs(agent_id=agent_id, limit=50, query=search_query)
        
        if logs_data.get('error', 0) != 0:
            return f"Error fetching logs: {logs_data['error']}"
        
        items = logs_data.get('data', {}).get('affected_items', [])
        
        if not items:
            result += "No logs found matching the criteria.\n"
            return result
        
        # Analyze logs
        result += f"📊 Log Analysis Summary:\n"
        result += f"- Total Logs Retrieved: {len(items)}\n"
        
        # Categorize logs
        error_logs = []
        auth_logs = []
        syslog_logs = []
        ioc_matches = []
        
        # Common IOC patterns
        ioc_patterns = {
            'ip': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'hash': r'\b[a-fA-F0-9]{32,64}\b',
            'url': r'https?://[^\s]+',
            'domain': r'\b[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}'
        }
        
        for log_item in items:
            log_content = str(log_item.get('log', {}).get('data', '')).lower()
            
            if 'error' in log_content:
                error_logs.append(log_item)
            if 'auth' in log_content or 'login' in log_content:
                auth_logs.append(log_item)
            if 'syslog' in log_content:
                syslog_logs.append(log_item)
            
            # Check for IOCs
            for ioc_type, pattern in ioc_patterns.items():
                if re.search(pattern, str(log_item.get('log', {}).get('data', ''))):
                    ioc_matches.append({
                        'type': ioc_type,
                        'log': log_item
                    })
        
        result += f"- Error Logs: {len(error_logs)}\n"
        result += f"- Authentication Logs: {len(auth_logs)}\n"
        result += f"- Syslog Entries: {len(syslog_logs)}\n"
        result += f"- IOC Matches: {len(ioc_matches)}\n\n"
        
        # IOC Detection
        if ioc_matches:
            result += f"🔍 Indicators of Compromise (IOCs) Detected:\n"
            ioc_types = {}
            for match in ioc_matches:
                ioc_type = match['type']
                if ioc_type not in ioc_types:
                    ioc_types[ioc_type] = []
                ioc_types[ioc_type].append(match['log'])
            
            for ioc_type, logs in ioc_types.items():
                result += f"\n- {ioc_type.upper()} IOCs: {len(logs)} matches\n"
                for log in logs[:3]:
                    log_data = log.get('log', {}).get('data', 'N/A')[:60]
                    result += f"  • {log_data}...\n"
        
        # Recent logs
        result += f"\n📝 Recent Log Entries:\n"
        for i, log_item in enumerate(items[:10], 1):
            timestamp = log_item.get('timestamp', 'N/A')
            agent_name = log_item.get('agent', {}).get('name', 'N/A')
            log_data = log_item.get('log', {}).get('data', 'N/A')
            
            result += f"{i}. [{timestamp}] Agent: {agent_name}\n"
            result += f"   {log_data[:80]}...\n\n"
        
        # Correlation with alerts
        if 'correlate' in query_lower or 'analyze' in query_lower:
            result += f"\n🔗 Log-Alert Correlation:\n"
            alerts = wazuh.get_alerts(limit=20, severity_min=5)
            alert_items = alerts.get('data', {}).get('affected_items', [])
            
            if alert_items:
                correlated = 0
                for log_item in items[:5]:
                    log_time = log_item.get('timestamp', '')
                    for alert in alert_items:
                        alert_time = alert.get('timestamp', '')
                        # Simple time-based correlation (within same hour)
                        if log_time[:13] == alert_time[:13]:
                            correlated += 1
                            break
                
                result += f"- Logs correlated with alerts: {correlated}\n"
                result += f"- Possible security incidents detected\n"
        
        # Recommendations
        result += f"\n💡 Recommendations:\n"
        if len(error_logs) > 10:
            result += f"- High error log volume detected. Investigate root cause.\n"
        if len(ioc_matches) > 0:
            result += f"- IOCs detected in logs. Review and escalate if suspicious.\n"
        if len(auth_logs) > 20:
            result += f"- High authentication activity. Review for brute force attempts.\n"
        
        return result
    
    except Exception as e:
        return f"Error in Log Analysis Agent: {str(e)}"

@tool
def log_analysis_tool(query: str) -> str:
    """Log Collection and Analysis Agent. Use for: 'analyze logs', 'log collection', 'search logs', 'IOC detection'."""
    return log_analysis_agent(query)

