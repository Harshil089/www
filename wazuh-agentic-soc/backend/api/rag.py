from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from rag_system import RAGSystem
from pydantic import BaseModel
import os

router = APIRouter()
rag_system = RAGSystem()

class Query(BaseModel):
    question: str

@router.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload documents to RAG knowledge base"""
    try:
        uploaded_files = []
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        for file in files:
            # Save file
            file_path = os.path.join(upload_dir, file.filename)
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Process based on file type
            if file.filename.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                rag_system.add_text_chunks(text)
            
            uploaded_files.append(file.filename)
        
        return JSONResponse(
            content={
                "message": f"Successfully uploaded {len(uploaded_files)} files",
                "files": uploaded_files
            },
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def query_knowledge_base(query: Query):
    """Query the RAG knowledge base"""
    try:
        result = rag_system.query(query.question)
        return JSONResponse(
            content=result,
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def rag_status():
    """Get RAG system status"""
    return {
        "documents_count": len(rag_system.texts),
        "gemini_configured": rag_system.llm is not None,
        "index_ready": rag_system.index is not None
    }