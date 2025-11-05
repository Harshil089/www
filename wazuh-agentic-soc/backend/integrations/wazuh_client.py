import requests
import urllib3
from base64 import b64encode
import os
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WazuhClient:
    def __init__(self):
        self.host = os.getenv("WAZUH_HOST")
        self.port = os.getenv("WAZUH_PORT")
        self.user = os.getenv("WAZUH_USER")
        self.password = os.getenv("WAZUH_PASSWORD")
        self.base_url = f"https://{self.host}:{self.port}"
        self.token = self._authenticate()
    
    def _authenticate(self):
        """Get JWT token from Wazuh using Basic Auth"""
        auth = f"{self.user}:{self.password}".encode()
        headers = {
            'Authorization': f'Basic {b64encode(auth).decode()}',
            'Content-Type': 'application/json'
        }
        try:
            print(f"Authenticating with {self.user}@{self.host}:{self.port}")
            response = requests.post(
                f"{self.base_url}/security/user/authenticate",
                headers=headers,
                verify=False,
                timeout=10
            )
            print(f"Auth response: {response.status_code}")
            
            if response.status_code == 200:
                token = response.json()['data']['token']
                print("✅ JWT token obtained successfully")
                return token
            else:
                print(f"❌ Auth failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return None
    
    def _get_headers(self):
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def get_alerts(self, limit=50, severity_min=5):
        """Fetch recent alerts"""
        try:
            response = requests.get(
                f"{self.base_url}/alerts?limit={limit}&q=rule.level>{severity_min}&pretty=true",
                headers=self._get_headers(),
                verify=False,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"data": {"affected_items": []}, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"data": {"affected_items": []}, "error": str(e)}
    
    def get_agents(self):
        """List all agents"""
        try:
            response = requests.get(
                f"{self.base_url}/agents?pretty=true",
                headers=self._get_headers(),
                verify=False,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"data": {"affected_items": []}, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"data": {"affected_items": []}, "error": str(e)}
    
    def get_rules(self, rule_id=None):
        """Get Wazuh rules"""
        try:
            url = f"{self.base_url}/rules?pretty=true"
            if rule_id:
                url += f"&rule_ids={rule_id}"
            response = requests.get(url, headers=self._get_headers(), verify=False, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"data": {"affected_items": []}, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"data": {"affected_items": []}, "error": str(e)}
    
    def get_fim_events(self, agent_id=None, limit=50):
        """Get File Integrity Monitoring events"""
        try:
            url = f"{self.base_url}/fim/events?pretty=true&limit={limit}"
            if agent_id:
                url += f"&agents_list={agent_id}"
            response = requests.get(url, headers=self._get_headers(), verify=False, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"data": {"affected_items": []}, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"data": {"affected_items": []}, "error": str(e)}
    
    def get_sca_checks(self, agent_id=None):
        """Get Security Configuration Assessment results"""
        try:
            url = f"{self.base_url}/sca/{agent_id}?pretty=true" if agent_id else f"{self.base_url}/sca?pretty=true"
            response = requests.get(url, headers=self._get_headers(), verify=False, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"data": {"affected_items": []}, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"data": {"affected_items": []}, "error": str(e)}
    
    def get_active_response(self):
        """Get active response commands"""
        try:
            response = requests.get(
                f"{self.base_url}/active-response?pretty=true",
                headers=self._get_headers(),
                verify=False,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"data": {"affected_items": []}, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"data": {"affected_items": []}, "error": str(e)}
    
    def trigger_active_response(self, command, agent_id, arguments=None):
        """Trigger active response command"""
        try:
            payload = {
                "command": command,
                "agents_list": [agent_id] if agent_id else ["all"]
            }
            if arguments:
                payload["arguments"] = arguments
            
            response = requests.put(
                f"{self.base_url}/active-response",
                headers=self._get_headers(),
                json=payload,
                verify=False,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_vulnerabilities(self, agent_id=None):
        """Get vulnerability assessment results"""
        try:
            url = f"{self.base_url}/vulnerability/{agent_id}?pretty=true" if agent_id else f"{self.base_url}/vulnerability?pretty=true"
            response = requests.get(url, headers=self._get_headers(), verify=False, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"data": {"affected_items": []}, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"data": {"affected_items": []}, "error": str(e)}
    
    def get_logs(self, agent_id=None, limit=50, query=None):
        """Get logs from agents"""
        try:
            url = f"{self.base_url}/logs?pretty=true&limit={limit}"
            if agent_id:
                url += f"&agents_list={agent_id}"
            if query:
                url += f"&q={query}"
            response = requests.get(url, headers=self._get_headers(), verify=False, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"data": {"affected_items": []}, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"data": {"affected_items": []}, "error": str(e)}
    
    def get_decoders(self, decoder_name=None):
        """Get Wazuh decoders"""
        try:
            url = f"{self.base_url}/decoders?pretty=true"
            if decoder_name:
                url += f"&decoder={decoder_name}"
            response = requests.get(url, headers=self._get_headers(), verify=False, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"data": {"affected_items": []}, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"data": {"affected_items": []}, "error": str(e)}
    
    def get_agent_config(self, agent_id):
        """Get agent configuration"""
        try:
            response = requests.get(
                f"{self.base_url}/agents/{agent_id}/config?pretty=true",
                headers=self._get_headers(),
                verify=False,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"error": str(e)}