#!/usr/bin/env python3
"""
Complete Wazuh API test
"""
import requests
import urllib3
import os
from dotenv import load_dotenv
from integrations.wazuh_client import WazuhClient

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_wazuh_client():
    print("🔍 Testing WazuhClient integration...")
    
    try:
        client = WazuhClient()
        
        if not client.token:
            print("❌ Failed to get JWT token")
            return False
        
        print(f"✅ JWT token obtained: {client.token[:50]}...")
        
        # Test agents
        print(f"\n👥 Testing agents...")
        agents = client.get_agents()
        if agents.get('error'):
            print(f"❌ Agents error: {agents['error']}")
        else:
            items = agents.get('data', {}).get('affected_items', [])
            print(f"✅ Found {len(items)} agents")
            for agent in items[:3]:
                print(f"  - {agent.get('name', 'N/A')} ({agent.get('status', 'N/A')})")
        
        # Test rules
        print(f"\n📋 Testing rules...")
        rules = client.get_rules()
        if rules.get('error'):
            print(f"❌ Rules error: {rules['error']}")
        else:
            items = rules.get('data', {}).get('affected_items', [])
            print(f"✅ Found {len(items)} rules")
        
        # Test alerts
        print(f"\n🚨 Testing alerts...")
        alerts = client.get_alerts()
        if alerts.get('error'):
            print(f"❌ Alerts error: {alerts['error']}")
        else:
            items = alerts.get('data', {}).get('affected_items', [])
            print(f"✅ Found {len(items)} alerts")
        
        print(f"\n🎉 WazuhClient test completed!")
        return True
        
    except Exception as e:
        print(f"❌ WazuhClient error: {e}")
        return False

if __name__ == "__main__":
    success = test_wazuh_client()
    exit(0 if success else 1)