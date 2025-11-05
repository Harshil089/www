from langchain_core.tools import tool
from integrations.wazuh_client import WazuhClient
import re

# MITRE ATT&CK tactic mapping for alert correlation
MITRE_TACTICS = {
    'authentication': ['T1078', 'T1110', 'T1078'],  # Valid Accounts, Brute Force
    'execution': ['T1059', 'T1106'],  # Command and Scripting Interpreter
    'persistence': ['T1543', 'T1053'],  # Create or Modify System Process
    'privilege_escalation': ['T1548', 'T1055'],  # Abuse Elevation Control Mechanism
    'defense_evasion': ['T1070', 'T1112'],  # Indicator Removal, Modify Registry
    'credential_access': ['T1003', 'T1040'],  # OS Credential Dumping
    'discovery': ['T1083', 'T1018'],  # File and Directory Discovery
    'lateral_movement': ['T1021', 'T1072'],  # Remote Services
    'command_and_control': ['T1071', 'T1105'],  # Application Layer Protocol
    'impact': ['T1486', 'T1490']  # Data Encrypted, Inhibit System Recovery
}

def map_alert_to_mitre(rule_description: str, rule_id: int):
    """Map Wazuh alert to MITRE ATT&CK tactics"""
    description_lower = rule_description.lower()
    tactics = []
    
    # Authentication-related
    if any(keyword in description_lower for keyword in ['login', 'authentication', 'password', 'credential', 'ssh', 'failed']):
        tactics.append('Credential Access (T1110 - Brute Force)')
        tactics.append('Initial Access (T1078 - Valid Accounts)')
    
    # Execution-related
    if any(keyword in description_lower for keyword in ['execute', 'command', 'script', 'shell']):
        tactics.append('Execution (T1059 - Command and Scripting Interpreter)')
    
    # Persistence-related
    if any(keyword in description_lower for keyword in ['service', 'startup', 'registry', 'persist']):
        tactics.append('Persistence (T1543 - Create or Modify System Process)')
    
    # Privilege escalation
    if any(keyword in description_lower for keyword in ['sudo', 'root', 'privilege', 'escalation', 'admin']):
        tactics.append('Privilege Escalation (T1548 - Abuse Elevation Control Mechanism)')
    
    # Defense evasion
    if any(keyword in description_lower for keyword in ['log', 'delete', 'modify', 'clear', 'evasion']):
        tactics.append('Defense Evasion (T1070 - Indicator Removal)')
    
    # Discovery
    if any(keyword in description_lower for keyword in ['scan', 'enumerate', 'discover', 'network']):
        tactics.append('Discovery (T1083 - File and Directory Discovery)')
    
    # Lateral movement
    if any(keyword in description_lower for keyword in ['remote', 'network', 'share', 'smb']):
        tactics.append('Lateral Movement (T1021 - Remote Services)')
    
    # Command and control
    if any(keyword in description_lower for keyword in ['connection', 'outbound', 'dns', 'http']):
        tactics.append('Command and Control (T1071 - Application Layer Protocol)')
    
    # Impact
    if any(keyword in description_lower for keyword in ['encrypt', 'delete', 'modify', 'destroy']):
        tactics.append('Impact (T1486 - Data Encrypted for Impact)')
    
    return tactics if tactics else ['Unable to map to specific MITRE tactic']

def correlate_alerts(alerts):
    """Correlate alerts to identify patterns"""
    if not alerts:
        return []
    
    patterns = {
        'brute_force': [],
        'privilege_escalation': [],
        'lateral_movement': [],
        'data_exfiltration': []
    }
    
    for alert in alerts:
        rule_desc = alert.get('rule', {}).get('description', '').lower()
        rule_level = alert.get('rule', {}).get('level', 0)
        
        if rule_level >= 10:
            if any(keyword in rule_desc for keyword in ['login', 'failed', 'authentication']):
                patterns['brute_force'].append(alert)
            elif any(keyword in rule_desc for keyword in ['sudo', 'root', 'privilege']):
                patterns['privilege_escalation'].append(alert)
            elif any(keyword in rule_desc for keyword in ['remote', 'network']):
                patterns['lateral_movement'].append(alert)
    
    return patterns

def alert_triage_agent(query: str) -> str:
    """Alert Triage Agent - Analyzes alerts with MITRE ATT&CK correlation"""
    try:
        wazuh = WazuhClient()
        
        # Determine severity filter
        severity_min = 7  # Default: high severity
        if 'critical' in query.lower():
            severity_min = 10
        elif 'high' in query.lower():
            severity_min = 7
        elif 'medium' in query.lower():
            severity_min = 5
        
        alerts_data = wazuh.get_alerts(limit=100, severity_min=severity_min)
        
        if alerts_data.get('error', 0) != 0:
            return f"Error fetching alerts: {alerts_data['error']}"
        
        items = alerts_data.get('data', {}).get('affected_items', [])
        
        if not items:
            return "No alerts found matching the criteria."
        
        # Correlate alerts
        patterns = correlate_alerts(items)
        
        # Build comprehensive report
        result = f"🚨 Alert Triage Report\n"
        result += f"{'='*50}\n\n"
        result += f"📊 Summary:\n"
        result += f"- Total Alerts: {len(items)}\n"
        result += f"- Critical Alerts (Level ≥10): {sum(1 for a in items if a.get('rule', {}).get('level', 0) >= 10)}\n"
        result += f"- High Alerts (Level ≥7): {sum(1 for a in items if a.get('rule', {}).get('level', 0) >= 7)}\n\n"
        
        # MITRE ATT&CK Analysis
        result += f"🎯 MITRE ATT&CK Analysis:\n"
        mitre_map = {}
        for alert in items[:10]:  # Analyze top 10 alerts
            rule = alert.get('rule', {})
            rule_id = rule.get('id', 'N/A')
            description = rule.get('description', 'N/A')
            tactics = map_alert_to_mitre(description, rule_id)
            
            for tactic in tactics:
                if tactic not in mitre_map:
                    mitre_map[tactic] = []
                mitre_map[tactic].append(f"Rule {rule_id}: {description[:50]}")
        
        for tactic, examples in list(mitre_map.items())[:5]:
            result += f"\n- {tactic}:\n"
            for example in examples[:2]:
                result += f"  • {example}\n"
        
        # Pattern Detection
        result += f"\n🔍 Detected Patterns:\n"
        if patterns['brute_force']:
            result += f"- Brute Force Attempts: {len(patterns['brute_force'])} alerts\n"
        if patterns['privilege_escalation']:
            result += f"- Privilege Escalation: {len(patterns['privilege_escalation'])} alerts\n"
        if patterns['lateral_movement']:
            result += f"- Lateral Movement: {len(patterns['lateral_movement'])} alerts\n"
        
        # Top Alerts
        result += f"\n🔝 Top Priority Alerts:\n"
        sorted_alerts = sorted(items, key=lambda x: x.get('rule', {}).get('level', 0), reverse=True)
        for i, alert in enumerate(sorted_alerts[:5], 1):
            rule = alert.get('rule', {})
            result += f"\n{i}. Rule {rule.get('id', 'N/A')} - Level {rule.get('level', 'N/A')}\n"
            result += f"   Description: {rule.get('description', 'N/A')[:60]}...\n"
            result += f"   Agent: {alert.get('agent', {}).get('name', 'N/A')}\n"
            result += f"   Time: {alert.get('timestamp', 'N/A')}\n"
            tactics = map_alert_to_mitre(rule.get('description', ''), rule.get('id', 0))
            if tactics:
                result += f"   MITRE: {tactics[0]}\n"
        
        # Recommendations
        result += f"\n💡 Recommendations:\n"
        if len(items) > 20:
            result += "- High alert volume detected. Consider reviewing alert filters.\n"
        if patterns['brute_force']:
            result += "- Implement IP blocking for repeated failed login attempts.\n"
        if sum(1 for a in items if a.get('rule', {}).get('level', 0) >= 10) > 5:
            result += "- Multiple critical alerts detected. Escalate to incident response team.\n"
        
        return result
    
    except Exception as e:
        return f"Error in Alert Triage Agent: {str(e)}"

@tool
def alert_triage_tool(query: str) -> str:
    """Alert Triage Agent for analyzing alerts with MITRE ATT&CK correlation. Use for: 'triage alerts', 'analyze incidents', 'critical alerts'."""
    return alert_triage_agent(query)

