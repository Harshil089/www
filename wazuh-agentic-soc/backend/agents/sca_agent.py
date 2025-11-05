from langchain_core.tools import tool
from integrations.wazuh_client import WazuhClient
import re

def sca_agent(query: str) -> str:
    """Security Configuration Assessment Agent - CIS/NIST compliance checks"""
    try:
        wazuh = WazuhClient()
        query_lower = query.lower()
        
        result = "🔒 Security Configuration Assessment (SCA) Report\n"
        result += "=" * 50 + "\n\n"
        
        # Extract agent ID
        agent_match = re.search(r'agent\s+(\d+)', query_lower)
        agent_id = agent_match.group(1) if agent_match else None
        
        # Get SCA results
        sca_data = wazuh.get_sca_checks(agent_id=agent_id)
        
        if sca_data.get('error', 0) != 0:
            return f"Error fetching SCA results: {sca_data['error']}"
        
        items = sca_data.get('data', {}).get('affected_items', [])
        
        if not items:
            result += "⚠️ No SCA scan results found. SCA may not be configured for this agent.\n"
            result += f"💡 To enable SCA:\n"
            result += f"1. Configure SCA policies in Wazuh manager\n"
            result += f"2. Enable SCA module on agent\n"
            result += f"3. Run SCA scan\n"
            return result
        
        # Analyze SCA results
        passed = 0
        failed = 0
        warnings = 0
        
        policy_results = {}
        
        for item in items:
            policy_id = item.get('policy_id', 'unknown')
            result_status = item.get('result', '').lower()
            
            if policy_id not in policy_results:
                policy_results[policy_id] = {'passed': 0, 'failed': 0, 'warnings': 0}
            
            if 'pass' in result_status:
                passed += 1
                policy_results[policy_id]['passed'] += 1
            elif 'fail' in result_status:
                failed += 1
                policy_results[policy_id]['failed'] += 1
            else:
                warnings += 1
                policy_results[policy_id]['warnings'] += 1
        
        total = passed + failed + warnings
        compliance_score = (passed / total * 100) if total > 0 else 0
        
        result += f"📊 Compliance Summary:\n"
        result += f"- Total Checks: {total}\n"
        result += f"- Passed: {passed} ✅\n"
        result += f"- Failed: {failed} ❌\n"
        result += f"- Warnings: {warnings} ⚠️\n"
        result += f"- Compliance Score: {compliance_score:.1f}%\n\n"
        
        # Policy breakdown
        result += f"📋 Policy Assessment:\n"
        for policy_id, counts in list(policy_results.items())[:5]:
            result += f"- Policy {policy_id}:\n"
            result += f"  Passed: {counts['passed']} | Failed: {counts['failed']} | Warnings: {counts['warnings']}\n"
        
        # Failed checks
        failed_checks = [item for item in items if 'fail' in item.get('result', '').lower()]
        if failed_checks:
            result += f"\n❌ Failed Security Checks:\n"
            for i, check in enumerate(failed_checks[:10], 1):
                result += f"{i}. {check.get('title', 'N/A')}\n"
                result += f"   Policy: {check.get('policy_id', 'N/A')}\n"
                result += f"   Rationale: {check.get('rationale', 'N/A')[:60]}...\n"
                result += f"   Remediation: {check.get('remediation', 'N/A')[:60]}...\n\n"
        
        # CIS/NIST compliance
        if 'cis' in query_lower or 'nist' in query_lower:
            result += f"\n🏛️ Compliance Framework Alignment:\n"
            result += f"SCA checks align with:\n"
            result += f"- CIS Benchmarks\n"
            result += f"- NIST Guidelines\n"
            result += f"- PCI-DSS Requirements\n\n"
        
        # Recommendations
        result += f"\n💡 Recommendations:\n"
        if compliance_score < 70:
            result += f"- CRITICAL: Low compliance score ({compliance_score:.1f}%). Immediate remediation required.\n"
        elif compliance_score < 90:
            result += f"- WARNING: Compliance score below target. Review and fix failed checks.\n"
        else:
            result += f"- GOOD: Compliance score is acceptable. Continue monitoring.\n"
        
        if failed > 0:
            result += f"- Review {failed} failed checks and apply remediation steps\n"
            result += f"- Prioritize critical security configuration issues\n"
        
        # Misconfiguration detection
        critical_misconfigs = [
            'password', 'authentication', 'permission', 'firewall', 'encryption'
        ]
        critical_failed = [
            check for check in failed_checks 
            if any(keyword in check.get('title', '').lower() for keyword in critical_misconfigs)
        ]
        
        if critical_failed:
            result += f"\n🚨 Critical Misconfigurations Detected:\n"
            for check in critical_failed[:5]:
                result += f"- {check.get('title', 'N/A')}\n"
        
        return result
    
    except Exception as e:
        return f"Error in SCA Agent: {str(e)}"

@tool
def sca_tool(query: str) -> str:
    """Security Configuration Assessment Agent. Use for: 'SCA scan', 'compliance check', 'security assessment', 'CIS benchmark'."""
    return sca_agent(query)

