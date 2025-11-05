from langchain_google_genai import ChatGoogleGenerativeAI
from agents.alert_agent import fetch_alerts
from agents.rule_agent import fetch_rules
from agents.agent_manager import fetch_agents
from agents.firewall_agent import parse_firewall_request
from agents.xml_editor_agent import xml_editor_agent
from agents.alert_triage_agent import alert_triage_agent
from agents.threat_intelligence_agent import threat_intelligence_agent
from agents.incident_response_agent import incident_response_agent
from agents.fim_agent import fim_agent
from agents.sca_agent import sca_agent
from agents.log_analysis_agent import log_analysis_agent
from agents.active_response_agent import active_response_agent
from agents.reporting_agent import reporting_agent
import os

class SOCOrchestrator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError("Please set your GEMINI_API_KEY in the .env file")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=api_key,
            temperature=0.1
        )
        
        # Define tool functions - expanded agentic system
        self.tools = {
            "alerts": fetch_alerts,
            "rules": fetch_rules,
            "agents": fetch_agents,
            "firewall": parse_firewall_request,
            "xml_editor": xml_editor_agent,
            "alert_triage": alert_triage_agent,
            "threat_intelligence": threat_intelligence_agent,
            "incident_response": incident_response_agent,
            "fim": fim_agent,
            "sca": sca_agent,
            "log_analysis": log_analysis_agent,
            "active_response": active_response_agent,
            "reporting": reporting_agent
        }
        
        # Store pending approvals
        self.pending_approvals = {}
    
    def _determine_tool(self, query: str) -> str:
        """Intelligent tool selection using LLM-enhanced keyword matching"""
        query_lower = query.lower()
        
        # Priority-based routing (highest priority first)
        
        # XML Editor - Rule creation/modification
        if any(word in query_lower for word in ['create rule', 'add rule', 'new rule', 'modify rule', 'edit rule', 'xml', 'decoder']):
            return "xml_editor"
        
        # Active Response - Automated actions
        if any(word in query_lower for word in ['trigger', 'active response', 'orchestrate', 'automated response', 'execute command']):
            return "active_response"
        
        # Incident Response - Isolation, blocking
        if any(word in query_lower for word in ['isolate', 'quarantine', 'block ip', 'escalate', 'incident response']):
            return "incident_response"
        
        # Alert Triage - MITRE ATT&CK analysis
        if any(word in query_lower for word in ['triage', 'mitre', 'attack', 'correlate alerts', 'analyze incidents']):
            return "alert_triage"
        
        # Threat Intelligence - IOC checks
        if any(word in query_lower for word in ['threat intelligence', 'virustotal', 'ioc', 'check ip', 'analyze hash', 'threat feed']):
            return "threat_intelligence"
        
        # FIM - File integrity
        if any(word in query_lower for word in ['fim', 'file integrity', 'file change', 'file monitoring', 'baseline']):
            return "fim"
        
        # SCA - Compliance checks
        if any(word in query_lower for word in ['sca', 'compliance', 'cis', 'nist', 'security assessment', 'configuration check']):
            return "sca"
        
        # Log Analysis - Log collection
        if any(word in query_lower for word in ['analyze logs', 'log collection', 'search logs', 'log analysis', 'ioc detection']):
            return "log_analysis"
        
        # Reporting - Reports generation
        if any(word in query_lower for word in ['report', 'generate report', 'executive summary', 'compliance report', 'visualization']):
            return "reporting"
        
        # Firewall - Basic firewall commands
        if any(word in query_lower for word in ['block', 'allow', 'firewall', 'iptables', 'port']):
            return "firewall"
        
        # Alert-related keywords
        if any(word in query_lower for word in ['alert', 'incident', 'security event', 'attack', 'breach', 'critical', 'high']):
            return "alerts"
        
        # Rule-related keywords
        if any(word in query_lower for word in ['rule', 'policy', 'regulation']):
            return "rules"
        
        # Agent-related keywords
        if any(word in query_lower for word in ['agent', 'host', 'server', 'endpoint', 'machine', 'online', 'offline', 'status']):
            return "agents"
        
        # Default to alerts for general security queries
        return "alerts"
    
    def process_query(self, user_query: str) -> str:
        """Process user query through appropriate tool with LLM enhancement"""
        try:
            # Handle approval requests
            if user_query.lower().startswith('approve'):
                return self._handle_approval(user_query)
            
            # Determine which tool to use
            tool_name = self._determine_tool(user_query)
            tool_func = self.tools[tool_name]
            
            # Execute the tool (pass LLM for XML editor)
            if tool_name == "xml_editor":
                result = tool_func(user_query, self.llm)
            else:
                result = tool_func(user_query)
            
            # Enhance response with LLM
            enhanced_prompt = f"""
            User asked: "{user_query}"
            
            Raw data from system:
            {result}
            
            Please provide a helpful, conversational response that:
            1. Directly answers the user's question
            2. Summarizes the key findings
            3. Provides actionable insights if relevant
            4. Uses a friendly, professional SOC analyst tone
            5. If the response contains "REQUIRES APPROVAL", clearly explain what needs approval and why
            
            Keep the response concise but informative. If the raw data is already well-formatted, 
            you can present it in a more conversational way without losing important details.
            """
            
            enhanced_response = self.llm.invoke(enhanced_prompt)
            return enhanced_response.content
            
        except Exception as e:
            return f"I encountered an error while processing your request: {str(e)}. Please try rephrasing your question or check if the Wazuh connection is working properly."
    
    def _handle_approval(self, query: str) -> str:
        """Handle approval requests for critical actions"""
        query_lower = query.lower()
        
        # This is a simplified approval system
        # In production, implement proper approval workflow with user authentication
        
        if 'isolate' in query_lower and 'agent' in query_lower:
            return "✅ Approval registered. Isolating agent... (Note: Actual execution requires proper authentication)"
        
        if 'block' in query_lower and 'ip' in query_lower:
            return "✅ Approval registered. Blocking IP... (Note: Actual execution requires proper authentication)"
        
        return "Please specify what action to approve (e.g., 'approve isolate agent 001' or 'approve block IP 192.168.1.100')"