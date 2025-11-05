from langchain_core.tools import tool
from integrations.wazuh_client import WazuhClient
import re
import os

def generate_rule_xml(rule_description: str, rule_id: int, level: int = 5, groups: list = None):
    """Generate XML for a new Wazuh rule"""
    groups = groups or ['pci_dss_10.2.7']
    
    rule_xml = f"""    <rule id="{rule_id}" level="{level}">
        <description>{rule_description}</description>
        <group>{', '.join(groups)}</group>
    </rule>"""
    return rule_xml

def parse_rule_request(query: str, llm):
    """Use LLM to parse natural language rule request"""
    if llm is None:
        # Fallback parsing without LLM
        return {
            'rule_id': 100000,
            'level': 5,
            'description': query,
            'groups': ['custom']
        }
    
    prompt = f"""
Parse this user request for creating a Wazuh rule: "{query}"

Extract:
1. Rule description (what the rule should detect)
2. Suggested rule ID (use a number between 100000-110000)
3. Severity level (1-15, where 15 is critical)
4. Rule groups (common: authentication, failed_login, syslog, etc.)

Respond in this format:
ID: [number]
LEVEL: [number]
DESCRIPTION: [description]
GROUPS: [group1, group2]
"""
    try:
        response = llm.invoke(prompt)
        content = response.content
        
        # Extract values
        rule_id = int(re.search(r'ID:\s*(\d+)', content).group(1)) if re.search(r'ID:\s*(\d+)', content) else 100000
        level = int(re.search(r'LEVEL:\s*(\d+)', content).group(1)) if re.search(r'LEVEL:\s*(\d+)', content) else 5
        description = re.search(r'DESCRIPTION:\s*(.+?)(?=GROUPS:|$)', content, re.DOTALL).group(1).strip() if re.search(r'DESCRIPTION:\s*(.+?)(?=GROUPS:|$)', content, re.DOTALL) else query
        groups_match = re.search(r'GROUPS:\s*(.+)', content)
        groups = [g.strip() for g in groups_match.group(1).split(',')] if groups_match else ['custom']
        
        return {
            'rule_id': rule_id,
            'level': level,
            'description': description,
            'groups': groups
        }
    except Exception as e:
        return {
            'rule_id': 100000,
            'level': 5,
            'description': query,
            'groups': ['custom']
        }

def xml_editor_agent(query: str, llm) -> str:
    """XML Editor Agent - Creates/modifies Wazuh rules and decoders"""
    try:
        query_lower = query.lower()
        wazuh = WazuhClient()
        
        # Detect intent
        if any(word in query_lower for word in ['add', 'create', 'new', 'generate']):
            # Create new rule
            parsed = parse_rule_request(query, llm)
            rule_xml = generate_rule_xml(
                parsed['description'],
                parsed['rule_id'],
                parsed['level'],
                parsed['groups']
            )
            
            return f"""✅ Proposed Rule Addition:

{rule_xml}

📋 Rule Details:
- ID: {parsed['rule_id']}
- Level: {parsed['level']}
- Description: {parsed['description']}
- Groups: {', '.join(parsed['groups'])}

⚠️ This is a proposed change. To apply it:
1. Review the XML above
2. Add it to your Wazuh rules.xml file
3. Restart Wazuh manager

Would you like me to suggest modifications or check for conflicts with existing rules?"""
        
        elif any(word in query_lower for word in ['modify', 'update', 'change', 'edit']):
            # Modify existing rule
            rule_id_match = re.search(r'rule\s+(\d+)', query_lower)
            if rule_id_match:
                rule_id = rule_id_match.group(1)
                rules = wazuh.get_rules(rule_id=rule_id)
                items = rules.get('data', {}).get('affected_items', [])
                
                if items:
                    rule = items[0]
                    return f"""📝 Rule {rule_id} Current Configuration:

- Description: {rule.get('description', 'N/A')}
- Level: {rule.get('level', 'N/A')}
- Groups: {', '.join(rule.get('groups', []))}

Please specify what you'd like to modify about this rule."""
                else:
                    return f"Rule {rule_id} not found."
            else:
                return "Please specify which rule to modify (e.g., 'modify rule 5710')."
        
        elif any(word in query_lower for word in ['check', 'validate', 'syntax']):
            # Validate rules
            return "XML validation would check syntax. This requires access to Wazuh configuration files. Use 'ossec-logtest' tool on Wazuh manager for testing."
        
        else:
            # Get existing rules
            rules = wazuh.get_rules()
            items = rules.get('data', {}).get('affected_items', [])
            return f"Found {len(items)} existing rules. Use 'create rule for [description]' to add a new rule, or 'modify rule [id]' to edit an existing one."
    
    except Exception as e:
        return f"Error in XML Editor Agent: {str(e)}"

# Note: xml_editor_agent is called directly from orchestrator with LLM

