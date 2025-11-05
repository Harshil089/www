#!/usr/bin/env python3
"""
Test network connectivity to Wazuh host
"""
import socket
import os
from dotenv import load_dotenv

load_dotenv()

def test_network():
    host = os.getenv("WAZUH_HOST")
    port = int(os.getenv("WAZUH_PORT"))
    
    print(f"🌐 Testing network connectivity to {host}:{port}")
    
    try:
        # Test TCP connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Network connection successful")
            return True
        else:
            print(f"❌ Network connection failed (error code: {result})")
            return False
            
    except Exception as e:
        print(f"❌ Network error: {e}")
        return False

if __name__ == "__main__":
    test_network()