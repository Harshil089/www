#!/usr/bin/env python3
"""
Test Wazuh connection with username, password, and JWT token
"""
import requests
import urllib3
import os
from dotenv import load_dotenv
from base64 import b64encode

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_wazuh_connection():
    host = os.getenv("WAZUH_HOST")
    port = os.getenv("WAZUH_PORT")
    user = os.getenv("WAZUH_USER")
    password = os.getenv("WAZUH_PASSWORD")
    
    print(f"🔍 Testing Wazuh Connection...")
    print(f"Host: {host}:{port}")
    print(f"User: {user}")
    
    # Step 1: Get JWT Token
    auth = f"{user}:{password}".encode()
    headers = {
        'Authorization': f'Basic {b64encode(auth).decode()}',
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"\n1️⃣ Getting JWT Token...")
        response = requests.post(
            f"https://{host}:{port}/security/user/authenticate",
            headers=headers,
            verify=False,
            timeout=30
        )
        
        if response.status_code == 200:
            token = response.json()['data']['token']
            print(f"✅ JWT Token obtained: {token[:50]}...")
            
            # Step 2: Test API with token
            print(f"\n2️⃣ Testing API endpoints...")
            jwt_headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Test agents endpoint
            agents_response = requests.get(
                f"https://{host}:{port}/agents?pretty=true",
                headers=jwt_headers,
                verify=False,
                timeout=10
            )
            
            if agents_response.status_code == 200:
                agents_data = agents_response.json()
                agent_count = len(agents_data.get('data', {}).get('affected_items', []))
                print(f"✅ Agents endpoint: {agent_count} agents found")
            else:
                print(f"❌ Agents endpoint failed: {agents_response.status_code}")
            
            # Test alerts endpoint
            alerts_response = requests.get(
                f"https://{host}:{port}/alerts?limit=5&pretty=true",
                headers=jwt_headers,
                verify=False,
                timeout=10
            )
            
            if alerts_response.status_code == 200:
                alerts_data = alerts_response.json()
                alert_count = len(alerts_data.get('data', {}).get('affected_items', []))
                print(f"✅ Alerts endpoint: {alert_count} alerts found")
            else:
                print(f"❌ Alerts endpoint failed: {alerts_response.status_code}")
            
            # Test rules endpoint
            rules_response = requests.get(
                f"https://{host}:{port}/rules?limit=5&pretty=true",
                headers=jwt_headers,
                verify=False,
                timeout=10
            )
            
            if rules_response.status_code == 200:
                rules_data = rules_response.json()
                rule_count = len(rules_data.get('data', {}).get('affected_items', []))
                print(f"✅ Rules endpoint: {rule_count} rules found")
            else:
                print(f"❌ Rules endpoint failed: {rules_response.status_code}")
            
            print(f"\n🎉 Wazuh connection test completed successfully!")
            return True
            
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    success = test_wazuh_connection()
    exit(0 if success else 1)