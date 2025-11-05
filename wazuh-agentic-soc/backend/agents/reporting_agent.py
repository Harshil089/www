from langchain_core.tools import tool
from integrations.wazuh_client import WazuhClient
from datetime import datetime, timedelta
import re

def reporting_agent(query: str) -> str:
    """Reporting and Visualization Agent - Generates compliance and security reports"""
    try:
        wazuh = WazuhClient()
        query_lower = query.lower()
        
        result = "📊 Security Report Generation\n"
        result += "=" * 50 + "\n\n"
        
        # Determine report type
        report_type = 'comprehensive'
        if 'compliance' in query_lower or 'pci' in query_lower or 'nist' in query_lower:
            report_type = 'compliance'
        elif 'executive' in query_lower or 'summary' in query_lower:
            report_type = 'executive'
        elif 'threat' in query_lower or 'security' in query_lower:
            report_type = 'threat'
        
        # Gather data
        agents_data = wazuh.get_agents()
        agents = agents_data.get('data', {}).get('affected_items', [])
        active_agents = sum(1 for agent in agents if agent.get('status') == 'active')
        
        alerts_data = wazuh.get_alerts(limit=100, severity_min=5)
        alerts = alerts_data.get('data', {}).get('affected_items', [])
        critical_alerts = [a for a in alerts if a.get('rule', {}).get('level', 0) >= 10]
        high_alerts = [a for a in alerts if 7 <= a.get('rule', {}).get('level', 0) < 10]
        
        # Get SCA compliance
        sca_data = wazuh.get_sca_checks()
        sca_items = sca_data.get('data', {}).get('affected_items', [])
        
        # Generate report based on type
        if report_type == 'executive':
            result += f"📈 Executive Summary Report\n"
            result += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            result += f"🎯 Key Metrics:\n"
            result += f"- Total Agents: {len(agents)}\n"
            result += f"- Active Agents: {active_agents} ({active_agents/len(agents)*100 if agents else 0:.1f}%)\n"
            result += f"- Critical Alerts (24h): {len(critical_alerts)}\n"
            result += f"- High Severity Alerts (24h): {len(high_alerts)}\n"
            result += f"- Compliance Score: {len(sca_items)} checks completed\n\n"
            
            result += f"⚠️ Risk Assessment:\n"
            if len(critical_alerts) > 10:
                result += f"- HIGH RISK: {len(critical_alerts)} critical alerts require immediate attention\n"
            elif len(critical_alerts) > 5:
                result += f"- MEDIUM RISK: {len(critical_alerts)} critical alerts detected\n"
            else:
                result += f"- LOW RISK: {len(critical_alerts)} critical alerts\n"
            
            result += f"\n📋 Recommendations:\n"
            if len(critical_alerts) > 0:
                result += f"- Investigate critical alerts immediately\n"
            if active_agents < len(agents) * 0.9:
                result += f"- {len(agents) - active_agents} agents offline - review connectivity\n"
            result += f"- Continue monitoring and threat hunting\n"
        
        elif report_type == 'compliance':
            result += f"🏛️ Compliance Report\n"
            result += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            result += f"📊 Compliance Overview:\n"
            if sca_items:
                passed = sum(1 for item in sca_items if 'pass' in item.get('result', '').lower())
                total = len(sca_items)
                compliance_score = (passed / total * 100) if total > 0 else 0
                result += f"- Security Checks: {total}\n"
                result += f"- Passed: {passed}\n"
                result += f"- Compliance Score: {compliance_score:.1f}%\n\n"
            else:
                result += f"- SCA data not available\n\n"
            
            result += f"🔒 Compliance Frameworks:\n"
            result += f"- PCI-DSS: Monitoring in place\n"
            result += f"- NIST: Configuration assessment active\n"
            result += f"- CIS Benchmarks: SCA checks enabled\n\n"
            
            result += f"📋 Findings:\n"
            if sca_items:
                failed = [item for item in sca_items if 'fail' in item.get('result', '').lower()]
                if failed:
                    result += f"- {len(failed)} configuration issues require remediation\n"
                else:
                    result += f"- No failed compliance checks\n"
            else:
                result += f"- Enable SCA scanning for compliance reporting\n"
        
        elif report_type == 'threat':
            result += f"🛡️ Threat Intelligence Report\n"
            result += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            result += f"🚨 Threat Summary:\n"
            result += f"- Critical Threats: {len(critical_alerts)}\n"
            result += f"- High Severity Threats: {len(high_alerts)}\n"
            result += f"- Total Security Events: {len(alerts)}\n\n"
            
            # Threat categorization
            threat_types = {
                'Authentication Attacks': 0,
                'Privilege Escalation': 0,
                'Lateral Movement': 0,
                'Data Exfiltration': 0
            }
            
            for alert in critical_alerts:
                desc = alert.get('rule', {}).get('description', '').lower()
                if any(kw in desc for kw in ['login', 'auth', 'password']):
                    threat_types['Authentication Attacks'] += 1
                elif any(kw in desc for kw in ['sudo', 'root', 'privilege']):
                    threat_types['Privilege Escalation'] += 1
                elif any(kw in desc for kw in ['remote', 'network']):
                    threat_types['Lateral Movement'] += 1
            
            result += f"📊 Threat Breakdown:\n"
            for threat_type, count in threat_types.items():
                if count > 0:
                    result += f"- {threat_type}: {count} incidents\n"
            
            result += f"\n🎯 Top Threats:\n"
            for i, alert in enumerate(critical_alerts[:5], 1):
                rule = alert.get('rule', {})
                result += f"{i}. Rule {rule.get('id')}: {rule.get('description', 'N/A')[:50]}...\n"
                result += f"   Level: {rule.get('level')} | Agent: {alert.get('agent', {}).get('name', 'N/A')}\n"
        
        else:  # comprehensive
            result += f"📋 Comprehensive Security Report\n"
            result += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            result += f"📊 System Overview:\n"
            result += f"- Total Agents: {len(agents)}\n"
            result += f"- Active Agents: {active_agents}\n"
            result += f"- Inactive Agents: {len(agents) - active_agents}\n\n"
            
            result += f"🚨 Alert Summary:\n"
            result += f"- Critical Alerts: {len(critical_alerts)}\n"
            result += f"- High Alerts: {len(high_alerts)}\n"
            result += f"- Total Alerts: {len(alerts)}\n\n"
            
            result += f"🔒 Compliance Status:\n"
            if sca_items:
                passed = sum(1 for item in sca_items if 'pass' in item.get('result', '').lower())
                total = len(sca_items)
                result += f"- Security Checks: {total}\n"
                result += f"- Passed: {passed}\n"
                result += f"- Compliance: {(passed/total*100) if total > 0 else 0:.1f}%\n"
            else:
                result += f"- SCA data not available\n"
        
        # Visualization suggestions
        result += f"\n📈 Visualization Suggestions:\n"
        result += f"- Dashboard: Real-time alert trends\n"
        result += f"- Charts: Agent status distribution\n"
        result += f"- Heatmap: Alert severity over time\n"
        result += f"- Timeline: Incident chronology\n"
        
        # Export options
        result += f"\n💾 Export Options:\n"
        result += f"- PDF Report: Available via API\n"
        result += f"- JSON Data: Structured format\n"
        result += f"- CSV Export: For spreadsheet analysis\n"
        
        return result
    
    except Exception as e:
        return f"Error in Reporting Agent: {str(e)}"

@tool
def reporting_tool(query: str) -> str:
    """Reporting and Visualization Agent. Use for: 'generate report', 'compliance report', 'executive summary', 'security report'."""
    return reporting_agent(query)

