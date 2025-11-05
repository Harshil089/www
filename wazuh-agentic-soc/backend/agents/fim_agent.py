from langchain_core.tools import tool
from integrations.wazuh_client import WazuhClient
import re

def fim_agent(query: str) -> str:
    """File Integrity Monitoring Agent - Monitors file changes"""
    try:
        wazuh = WazuhClient()
        query_lower = query.lower()
        
        result = "📁 File Integrity Monitoring (FIM) Report\n"
        result += "=" * 50 + "\n\n"
        
        # Extract agent ID
        agent_match = re.search(r'agent\s+(\d+)', query_lower)
        agent_id = agent_match.group(1) if agent_match else None
        
        # Get FIM events
        fim_data = wazuh.get_fim_events(agent_id=agent_id, limit=50)
        
        if fim_data.get('error', 0) != 0:
            return f"Error fetching FIM events: {fim_data['error']}"
        
        items = fim_data.get('data', {}).get('affected_items', [])
        
        if not items:
            result += "✅ No FIM events detected - All monitored files are intact.\n"
            return result
        
        # Analyze FIM events
        result += f"📊 Summary:\n"
        result += f"- Total FIM Events: {len(items)}\n"
        
        # Categorize events
        file_changes = []
        file_additions = []
        file_deletions = []
        critical_files = []
        
        critical_paths = ['/etc/passwd', '/etc/shadow', '/etc/sudoers', '/etc/hosts', '/etc/crontab']
        
        for event in items:
            path = event.get('path', '').lower()
            event_type = event.get('type', '').lower()
            
            if any(critical in path for critical in critical_paths):
                critical_files.append(event)
            
            if 'added' in event_type or 'create' in event_type:
                file_additions.append(event)
            elif 'delete' in event_type or 'remove' in event_type:
                file_deletions.append(event)
            else:
                file_changes.append(event)
        
        result += f"- File Changes: {len(file_changes)}\n"
        result += f"- File Additions: {len(file_additions)}\n"
        result += f"- File Deletions: {len(file_deletions)}\n"
        result += f"- Critical File Changes: {len(critical_files)}\n\n"
        
        # Critical file alerts
        if critical_files:
            result += f"🚨 CRITICAL FILE CHANGES DETECTED:\n"
            for event in critical_files[:5]:
                result += f"- Path: {event.get('path', 'N/A')}\n"
                result += f"  Agent: {event.get('agent', {}).get('name', 'N/A')}\n"
                result += f"  Type: {event.get('type', 'N/A')}\n"
                result += f"  Timestamp: {event.get('timestamp', 'N/A')}\n\n"
            result += f"⚠️ IMMEDIATE INVESTIGATION REQUIRED\n\n"
        
        # Recent changes
        result += f"📝 Recent File Changes:\n"
        for i, event in enumerate(items[:10], 1):
            path = event.get('path', 'N/A')
            result += f"{i}. {path[:60]}...\n"
            result += f"   Agent: {event.get('agent', {}).get('name', 'N/A')} | "
            result += f"Type: {event.get('type', 'N/A')} | "
            result += f"Time: {event.get('timestamp', 'N/A')}\n\n"
        
        # Baseline status
        if 'baseline' in query_lower:
            result += f"\n📋 Baseline Status:\n"
            result += f"FIM baseline is maintained automatically.\n"
            result += f"Any changes from baseline trigger alerts.\n"
        
        # Recommendations
        result += f"\n💡 Recommendations:\n"
        if len(critical_files) > 0:
            result += f"- Investigate critical file changes immediately\n"
            result += f"- Verify changes are authorized\n"
            result += f"- Consider isolating affected agents\n"
        if len(file_deletions) > 5:
            result += f"- Multiple file deletions detected - possible malware activity\n"
        if len(items) > 20:
            result += f"- High FIM activity - review file monitoring policies\n"
        
        return result
    
    except Exception as e:
        return f"Error in FIM Agent: {str(e)}"

@tool
def fim_tool(query: str) -> str:
    """File Integrity Monitoring Agent. Use for: 'FIM events', 'file changes', 'file integrity', 'check FIM'."""
    return fim_agent(query)

