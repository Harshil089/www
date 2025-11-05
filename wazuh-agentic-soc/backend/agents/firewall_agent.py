from langchain_core.tools import tool
import subprocess
import re

def execute_firewall_command(command: str) -> str:
    """Execute firewall commands safely"""
    try:
        # For demonstration - in production, add proper validation
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        return f"Command executed: {command}\nOutput: {result.stdout}\nError: {result.stderr}"
    except Exception as e:
        return f"Error executing command: {str(e)}"

def parse_firewall_request(query: str) -> str:
    """Parse natural language firewall requests"""
    query_lower = query.lower()
    
    # Block IP patterns
    if "block" in query_lower and "ip" in query_lower:
        ip_match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', query)
        if ip_match:
            ip = ip_match.group()
            command = f"sudo iptables -A INPUT -s {ip} -j DROP"
            return execute_firewall_command(command)
    
    # Allow port patterns  
    if "allow" in query_lower and "port" in query_lower:
        port_match = re.search(r'\b\d{1,5}\b', query)
        if port_match:
            port = port_match.group()
            command = f"sudo iptables -A INPUT -p tcp --dport {port} -j ACCEPT"
            return execute_firewall_command(command)
    
    # Block port patterns
    if "block" in query_lower and "port" in query_lower:
        port_match = re.search(r'\b\d{1,5}\b', query)
        if port_match:
            port = port_match.group()
            command = f"sudo iptables -A INPUT -p tcp --dport {port} -j DROP"
            return execute_firewall_command(command)
    
    return "I can help you with firewall rules. Try: 'block IP 192.168.1.100' or 'allow port 80'"

@tool
def firewall_tool(query: str) -> str:
    """Modify firewall rules based on natural language commands. Use for blocking IPs, allowing/blocking ports."""
    return parse_firewall_request(query)