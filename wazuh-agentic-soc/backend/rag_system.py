import os
import faiss
import numpy as np
import pickle
import hashlib
from typing import List, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI

class SimpleHashEmbeddings:
    def __init__(self, dim: int = 256):
        self.dim = dim

    def _text_to_vector(self, text: str) -> np.ndarray:
        out = np.zeros(self.dim, dtype=np.float32)
        i = 0
        counter = 0
        while i < self.dim:
            m = hashlib.sha256()
            m.update(text.encode("utf-8"))
            m.update(counter.to_bytes(4, "little", signed=False))
            digest = m.digest()
            for b in digest:
                if i >= self.dim:
                    break
                out[i] = (b - 128) / 128.0
                i += 1
            counter += 1
        norm = np.linalg.norm(out)
        if norm > 0:
            out = out / norm
        return out

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._text_to_vector(t).tolist() for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._text_to_vector(text).tolist()

class RAGSystem:
    def __init__(self, persist_directory: str = "vectorstore"):
        self.persist_directory = persist_directory
        self.embeddings = SimpleHashEmbeddings(dim=256)
        self.texts: List[str] = []
        self.index = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Initialize Gemini LLM
        api_key = os.getenv("GEMINI_API_KEY")
        model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        
        if api_key and api_key != "your_gemini_api_key_here":
            self.llm = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=api_key,
                temperature=0.1
            )
        else:
            self.llm = None
        
        self._load_index()

    def _load_index(self):
        index_path = os.path.join(self.persist_directory, "index.faiss")
        meta_path = os.path.join(self.persist_directory, "meta.pkl")
        
        if os.path.exists(index_path) and os.path.exists(meta_path):
            try:
                self.index = faiss.read_index(index_path)
                with open(meta_path, "rb") as f:
                    self.texts = pickle.load(f)
            except Exception:
                self.index = None

    def add_documents(self, texts: List[str]):
        if not texts:
            return
            
        vectors = self.embeddings.embed_documents(texts)
        vecs = np.array(vectors).astype("float32")
        
        if self.index is None:
            self.index = faiss.IndexFlatL2(vecs.shape[1])
            
        self.index.add(vecs)
        self.texts.extend(texts)
        self._save_index()

    def _save_index(self):
        os.makedirs(self.persist_directory, exist_ok=True)
        index_path = os.path.join(self.persist_directory, "index.faiss")
        meta_path = os.path.join(self.persist_directory, "meta.pkl")
        
        if self.index is not None:
            faiss.write_index(self.index, index_path)
            with open(meta_path, "wb") as f:
                pickle.dump(self.texts, f)

    def query(self, question: str, k: int = 4) -> dict:
        if self.index is None or len(self.texts) == 0:
            return {"answer": "No documents in knowledge base", "sources": []}
            
        # Retrieve relevant documents
        qv = np.array([self.embeddings.embed_query(question)]).astype("float32")
        D, I = self.index.search(qv, k)
        
        sources = []
        for idx in I[0]:
            if idx < len(self.texts):
                sources.append(self.texts[idx])
        
        if not self.llm:
            return {"answer": "Gemini API not configured", "sources": sources}
            
        # Generate answer using Gemini
        context = "\n\n".join(sources)
        prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer based on the context:"
        
        try:
            response = self.llm.invoke(prompt)
            return {"answer": response.content, "sources": sources}
        except Exception as e:
            return {"answer": f"Error generating response: {str(e)}", "sources": sources}

    def add_text_chunks(self, text: str):
        chunks = self.text_splitter.split_text(text)
        self.add_documents(chunks)