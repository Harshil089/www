from fastapi import APIRouter, HTTPException
from integrations.wazuh_client import WazuhClient
import requests

router = APIRouter()

@router.get("/alerts")
async def proxy_alerts(limit: int = 100, sort: str = None, q: str = None):
    """Proxy alerts endpoint to Wazuh"""
    try:
        client = WazuhClient()
        if not client.token:
            raise HTTPException(status_code=401, detail="Wazuh authentication failed")
        
        # Build query parameters
        query_params = {"limit": limit}
        if sort:
            query_params["sort"] = sort
        if q:
            query_params["q"] = q
            
        alerts = client.get_alerts(**query_params)
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents")
async def proxy_agents(limit: int = 200):
    """Proxy agents endpoint to Wazuh"""
    try:
        client = WazuhClient()
        if not client.token:
            raise HTTPException(status_code=401, detail="Wazuh authentication failed")
            
        agents = client.get_agents()
        return agents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rules")
async def proxy_rules(limit: int = 200, offset: int = 0):
    """Proxy rules endpoint to Wazuh"""
    try:
        client = WazuhClient()
        if not client.token:
            raise HTTPException(status_code=401, detail="Wazuh authentication failed")
            
        rules = client.get_rules()
        return rules
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))