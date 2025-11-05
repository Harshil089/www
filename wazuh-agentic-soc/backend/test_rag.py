#!/usr/bin/env python3
"""
Test RAG system functionality
"""
from rag_system import RAGSystem
import os

def test_rag():
    print("🧠 Testing RAG System...")
    
    # Initialize RAG system
    rag = RAGSystem()
    
    # Test adding documents
    test_docs = [
        "Wazuh is an open-source security monitoring platform.",
        "SIEM stands for Security Information and Event Management.",
        "Agents collect security data from endpoints and send to manager.",
        "Rules define how to detect security events in log data."
    ]
    
    print("📝 Adding test documents...")
    rag.add_documents(test_docs)
    
    # Test queries
    queries = [
        "What is Wazuh?",
        "What does SIEM mean?",
        "How do agents work?",
        "What are rules used for?"
    ]
    
    for query in queries:
        print(f"\n❓ Query: {query}")
        result = rag.query(query)
        print(f"✅ Answer: {result['answer']}")
        print(f"📚 Sources: {len(result['sources'])} documents")
    
    print(f"\n📊 Total documents in knowledge base: {len(rag.texts)}")

if __name__ == "__main__":
    test_rag()