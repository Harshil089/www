#!/usr/bin/env python3
"""
Test script to verify Wazuh connection
Run this after updating your .env file with correct credentials
"""

from integrations.wazuh_client import WazuhClient
import os
from dotenv import load_dotenv

def test_wazuh_connection():
    load_dotenv()
    
    print("🔍 Testing Wazuh Connection...")
    print(f"Host: {os.getenv('WAZUH_HOST')}")
    print(f"Port: {os.getenv('WAZUH_PORT')}")
    print(f"User: {os.getenv('WAZUH_USER')}")
    
    try:
        client = WazuhClient()
        
        if not client.token:
            print("❌ Authentication failed - check your credentials")
            return False
        
        print("✅ Authentication successful")
        
        # Test alerts
        alerts = client.get_alerts(limit=5)
        if "error" in alerts:
            print(f"❌ Error fetching alerts: {alerts['error']}")
        else:
            alert_count = len(alerts.get('data', {}).get('affected_items', []))
            print(f"✅ Fetched {alert_count} alerts")
        
        # Test agents
        agents = client.get_agents()
        if "error" in agents:
            print(f"❌ Error fetching agents: {agents['error']}")
        else:
            agent_count = len(agents.get('data', {}).get('affected_items', []))
            print(f"✅ Fetched {agent_count} agents")
        
        print("🎉 Wazuh connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    test_wazuh_connection()