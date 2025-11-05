from langchain_core.tools import tool
from integrations.wazuh_client import WazuhClient
import requests
import re

# Note: In production, use environment variable for API key
VIRUSTOTAL_API_KEY = None  # Set via environment variable if needed

def check_virustotal_ip(ip_address: str) -> dict:
    """Check IP address against VirusTotal"""
    if not VIRUSTOTAL_API_KEY:
        return {"status": "VirusTotal API key not configured", "harmless": 0, "malicious": 0}
    
    try:
        url = f"https://www.virustotal.com/vtapi/v2/ip-address/report"
        params = {'apikey': VIRUSTOTAL_API_KEY, 'ip': ip_address}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "found",
                "harmless": data.get('detected_urls', []),
                "malicious": len([url for url in data.get('detected_urls', []) if url.get('positives', 0) > 0])
            }
        return {"status": "not_found"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_virustotal_hash(file_hash: str) -> dict:
    """Check file hash against VirusTotal"""
    if not VIRUSTOTAL_API_KEY:
        return {"status": "VirusTotal API key not configured"}
    
    try:
        url = f"https://www.virustotal.com/vtapi/v2/file/report"
        params = {'apikey': VIRUSTOTAL_API_KEY, 'resource': file_hash}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "found",
                "positives": data.get('positives', 0),
                "total": data.get('total', 0),
                "scan_date": data.get('scan_date', 'N/A')
            }
        return {"status": "not_found"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def threat_intelligence_agent(query: str) -> str:
    """Threat Intelligence Integrator Agent - Pulls external feeds and updates rules"""
    try:
        wazuh = WazuhClient()
        query_lower = query.lower()
        
        # Extract IP addresses
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ip_addresses = re.findall(ip_pattern, query)
        
        # Extract hashes (MD5, SHA1, SHA256)
        hash_pattern = r'\b[a-fA-F0-9]{32,64}\b'
        hashes = re.findall(hash_pattern, query)
        
        result = "🔍 Threat Intelligence Analysis\n"
        result += "=" * 50 + "\n\n"
        
        # Check IPs
        if ip_addresses:
            result += f"📡 IP Address Analysis:\n"
            for ip in ip_addresses[:3]:  # Limit to 3 IPs
                vt_result = check_virustotal_ip(ip)
                if vt_result.get('status') == 'found':
                    result += f"\n- IP: {ip}\n"
                    result += f"  Malicious indicators found: {vt_result.get('malicious', 0)}\n"
                    result += f"  Recommendation: Consider blocking this IP\n"
                elif vt_result.get('status') == 'VirusTotal API key not configured':
                    result += f"\n- IP: {ip}\n"
                    result += f"  ⚠️ VirusTotal integration not configured. Set VIRUSTOTAL_API_KEY in .env\n"
                    result += f"  Recommendation: Add IP {ip} to threat intelligence watchlist\n"
                else:
                    result += f"\n- IP: {ip}\n"
                    result += f"  No intelligence data found (may be benign or not in database)\n"
            
            # Suggest rule creation
            if ip_addresses:
                result += f"\n💡 Suggested Action:\n"
                result += f"Create a Wazuh rule to block these IPs:\n"
                result += f"Use XML Editor Agent: 'create rule to block IP addresses {', '.join(ip_addresses[:3])}'\n"
        
        # Check hashes
        if hashes:
            result += f"\n📁 File Hash Analysis:\n"
            for file_hash in hashes[:3]:  # Limit to 3 hashes
                vt_result = check_virustotal_hash(file_hash)
                if vt_result.get('status') == 'found':
                    positives = vt_result.get('positives', 0)
                    total = vt_result.get('total', 0)
                    result += f"\n- Hash: {file_hash[:16]}...\n"
                    result += f"  Detected by {positives}/{total} engines\n"
                    if positives > 0:
                        result += f"  ⚠️ MALICIOUS - Immediate action required\n"
                elif vt_result.get('status') == 'VirusTotal API key not configured':
                    result += f"\n- Hash: {file_hash[:16]}...\n"
                    result += f"  ⚠️ VirusTotal integration not configured\n"
                    result += f"  Recommendation: Add hash to IOC database\n"
                else:
                    result += f"\n- Hash: {file_hash[:16]}...\n"
                    result += f"  Not found in VirusTotal database\n"
        
        # IOC extraction from alerts
        if 'update' in query_lower or 'sync' in query_lower or 'ioc' in query_lower:
            result += f"\n🔄 IOC Update Process:\n"
            result += f"1. Fetching recent high-severity alerts...\n"
            
            alerts = wazuh.get_alerts(limit=20, severity_min=7)
            items = alerts.get('data', {}).get('affected_items', [])
            
            if items:
                result += f"2. Found {len(items)} high-severity alerts\n"
                result += f"3. Extracting IOCs from alerts...\n\n"
                
                # Extract potential IOCs
                extracted_ips = set()
                for alert in items:
                    full_log = str(alert.get('full_log', ''))
                    ips = re.findall(ip_pattern, full_log)
                    extracted_ips.update(ips)
                
                if extracted_ips:
                    result += f"📋 Extracted IOCs:\n"
                    for ip in list(extracted_ips)[:5]:
                        result += f"- IP: {ip}\n"
                    result += f"\n💡 Recommendation: Review these IOCs and update Wazuh rules if needed.\n"
                else:
                    result += f"No IP addresses found in alert logs.\n"
            else:
                result += f"No high-severity alerts found.\n"
        
        # Rule update suggestions
        if 'rule' in query_lower or 'update' in query_lower:
            result += f"\n📝 Rule Update Suggestions:\n"
            result += f"To integrate threat intelligence:\n"
            result += f"1. Use XML Editor Agent to create rules for detected IOCs\n"
            result += f"2. Configure Active Response to block malicious IPs\n"
            result += f"3. Set up automated IOC feed updates\n"
        
        if not ip_addresses and not hashes and 'update' not in query_lower:
            result += f"💡 Usage Examples:\n"
            result += f"- 'Check IP 192.168.1.100 in threat intelligence'\n"
            result += f"- 'Analyze hash abc123def456...'\n"
            result += f"- 'Update IOCs from recent alerts'\n"
        
        return result
    
    except Exception as e:
        return f"Error in Threat Intelligence Agent: {str(e)}"

@tool
def threat_intelligence_tool(query: str) -> str:
    """Threat Intelligence Integrator Agent. Use for: 'check IP', 'analyze hash', 'update IOCs', 'threat intelligence'."""
    return threat_intelligence_agent(query)

