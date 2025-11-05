from langchain_core.tools import tool
from rag_system import RAGSystem
import os

# Initialize RAG system
rag_system = RAGSystem()

def rag_agent(query: str) -> str:
    """RAG Agent - Query knowledge base and generate responses"""
    try:
        # Check if query is for adding documents
        if query.lower().startswith('add document') or query.lower().startswith('upload'):
            return "Use the /upload endpoint to add documents to the knowledge base."
        
        # Query the RAG system
        result = rag_system.query(query)
        
        response = f"🧠 Knowledge Base Query\n"
        response += "=" * 50 + "\n\n"
        response += f"📝 Answer:\n{result['answer']}\n\n"
        
        if result['sources']:
            response += f"📚 Sources ({len(result['sources'])} documents):\n"
            for i, source in enumerate(result['sources'][:3], 1):
                preview = source[:100] + "..." if len(source) > 100 else source
                response += f"{i}. {preview}\n"
        
        return response
        
    except Exception as e:
        return f"Error in RAG Agent: {str(e)}"

@tool
def rag_tool(query: str) -> str:
    """RAG Knowledge Base Agent. Use for: 'search knowledge', 'query documents', 'ask about', 'find information'."""
    return rag_agent(query)