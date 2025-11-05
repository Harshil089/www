#!/usr/bin/env python3
"""
Simple Wazuh connection test with manual token
"""
import requests
import urllib3
import os
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_wazuh_with_token():
    host = os.getenv("WAZUH_HOST")
    port = os.getenv("WAZUH_PORT")
    
    # Use the working token from your Kali machine
    token = "eyJhbGciOiJFUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ3YXp1aCIsImF1ZCI6IldhenVoIEFQSSBSRVNUIiwibmJmIjoxNzYyMzA4OTM4LCJleHAiOjE3NjIzMDk4MzgsInN1YiI6ImFpYWdlbnQiLCJydW5fYXMiOmZhbHNlLCJyYmFjX3JvbGVzIjpbMV0sInJiYWNfbW9kZSI6IndoaXRlIn0.ARwjFASfnzhygiH-3ABqy2p4Tg9gD_WQnMGqfPHkaRJ-onGqAay8uTco_EUaYebWmSIhy0p7rfY_gTdg56EfiEUoAXgHxumId82cb8qXVPFMFWgppcKrwc--WYg-DDukHKMChsNJ7mi5mLqjNxVA8rgAU9UJogC_zhbN2BEpl6HianYn"
    
    print(f"🔍 Testing Wazuh API with token...")
    print(f"Host: {host}:{port}")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test agents endpoint
        print(f"\n📡 Testing agents endpoint...")
        response = requests.get(
            f"https://{host}:{port}/agents?limit=5",
            headers=headers,
            verify=False,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            agents = data.get('data', {}).get('affected_items', [])
            print(f"✅ Found {len(agents)} agents")
            for agent in agents[:3]:
                print(f"  - {agent.get('name', 'N/A')} ({agent.get('status', 'N/A')})")
        else:
            print(f"❌ Error: {response.text}")
            
        # Test alerts endpoint
        print(f"\n🚨 Testing alerts endpoint...")
        response = requests.get(
            f"https://{host}:{port}/alerts?limit=5",
            headers=headers,
            verify=False,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            alerts = data.get('data', {}).get('affected_items', [])
            print(f"✅ Found {len(alerts)} alerts")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_wazuh_with_token()