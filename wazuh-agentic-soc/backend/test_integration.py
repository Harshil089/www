#!/usr/bin/env python3
"""
Test integration of RAG system with backend
"""
import sys
import os

def test_imports():
    """Test that all modules can be imported"""
    try:
        print("🧪 Testing imports...")
        
        # Test RAG system
        from rag_system import RAGSystem
        print("✅ RAG System imported")
        
        # Test RAG agent
        from agents.rag_agent import rag_agent
        print("✅ RAG Agent imported")
        
        # Test orchestrator
        from agents.orchestrator import SOCOrchestrator
        print("✅ Orchestrator imported")
        
        # Test API
        from api.rag import router
        print("✅ RAG API imported")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_rag_basic():
    """Test basic RAG functionality"""
    try:
        print("\n🧠 Testing RAG functionality...")
        
        # Check if Gemini is configured
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key or gemini_key == "your_gemini_api_key_here":
            print("⚠️  Gemini API key not configured - RAG will work with limited functionality")
        else:
            print("✅ Gemini API key configured")
        
        # Test RAG agent
        from agents.rag_agent import rag_agent
        response = rag_agent("test query")
        print("✅ RAG agent responds")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG test error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports() and test_rag_basic()
    sys.exit(0 if success else 1)