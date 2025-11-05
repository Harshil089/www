from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from agents.orchestrator import SOCOrchestrator
from api.stats import router as stats_router
from api.rag import router as rag_router
from api.dashboard import router as dashboard_router
from api.wazuh_proxy import router as wazuh_proxy_router
import json
import asyncio

app = FastAPI(title="Agentic Wazuh SOC API")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(stats_router, prefix="/api")
app.include_router(rag_router, prefix="/api/rag")
app.include_router(dashboard_router, prefix="/api/dashboard")
app.include_router(wazuh_proxy_router, prefix="/api/wazuh")

# Initialize orchestrator
try:
    orchestrator = SOCOrchestrator()
    print("✅ SOC Orchestrator initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize orchestrator: {e}")
    orchestrator = None

# Store active connections
active_connections: list[WebSocket] = []

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    # Send welcome message
    await websocket.send_json({
        "type": "bot",
        "content": "Hello! I'm your SOC assistant. Ask me about Wazuh alerts, rules, or agents."
    })
    
    try:
        while True:
            # Receive message from React frontend
            data = await websocket.receive_text()
            message = json.loads(data)
            
            user_query = message.get("query", "")
            
            if not orchestrator:
                await websocket.send_json({
                    "type": "bot",
                    "content": "Sorry, the SOC assistant is not available. Please check your Gemini API key configuration."
                })
                continue
            
            # Process through orchestrator in a separate thread
            def process_query():
                return orchestrator.process_query(user_query)
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, process_query)
            
            # Send response back
            await websocket.send_json({
                "type": "bot",
                "content": response
            })
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "orchestrator_ready": orchestrator is not None
    }

@app.get("/")
async def root():
    return {"message": "Agentic Wazuh SOC API is running"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Agentic Wazuh SOC Backend...")
    uvicorn.run(app, host="0.0.0.0", port=8000)