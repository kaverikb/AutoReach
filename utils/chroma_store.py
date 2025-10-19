import chromadb
import json
from datetime import datetime

class ChromaStore:
    """
    Persistent vector database for storing and retrieving lead data.
    """
    
    def __init__(self, persist_dir="./chroma_data"):
        """Initialize Chroma with persistent storage."""
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.leads_collection = self.client.get_or_create_collection(
            name="leads",
            metadata={"hnsw:space": "cosine"}
        )
        self.enriched_collection = self.client.get_or_create_collection(
            name="enriched_leads",
            metadata={"hnsw:space": "cosine"}
        )
        print("[ChromaStore] Initialized with persistent storage")

    def store_leads(self, leads):
        """Store raw leads from prospect search."""
        if not leads:
            return
        
        for idx, lead in enumerate(leads):
            lead_id = f"lead_{lead.get('apollo_id', idx)}"
            metadata = {
                "company": lead.get("company", ""),
                "contact_name": lead.get("contact_name", ""),
                "email": lead.get("email", ""),
                "signal": lead.get("signal", ""),
                "stored_at": datetime.now().isoformat()
            }
            
            # Use company + contact as document text for embedding
            document_text = f"{lead.get('company')} {lead.get('contact_name')} {lead.get('email')}"
            
            self.leads_collection.add(
                ids=[lead_id],
                documents=[document_text],
                metadatas=[metadata]
            )
        
        print(f"[ChromaStore] Stored {len(leads)} leads")

    def store_enriched_leads(self, enriched_leads):
        """Store enriched lead data."""
        if not enriched_leads:
            return
        
        for idx, lead in enumerate(enriched_leads):
            lead_id = f"enriched_{lead.get('company', idx)}_{lead.get('contact', idx)}"
            metadata = {
                "company": lead.get("company", ""),
                "contact": lead.get("contact", ""),
                "role": lead.get("role", ""),
                "seniority_level": lead.get("seniority_level", ""),
                "technologies": ",".join(lead.get("technologies", [])),
                "score": str(lead.get("total_score", 0)),
                "stored_at": datetime.now().isoformat()
            }
            
            # Use all enriched info for embedding
            document_text = f"{lead.get('company')} {lead.get('contact')} {lead.get('role')} {','.join(lead.get('technologies', []))}"
            
            self.enriched_collection.add(
                ids=[lead_id],
                documents=[document_text],
                metadatas=[metadata]
            )
        
        print(f"[ChromaStore] Stored {len(enriched_leads)} enriched leads")

    def get_similar_leads(self, query, collection_name="leads", n_results=5):
        """Search for similar leads by query."""
        collection = self.leads_collection if collection_name == "leads" else self.enriched_collection
        
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return results

    def get_all_leads(self, collection_name="enriched"):
        """Retrieve all stored leads."""
        collection = self.enriched_collection if collection_name == "enriched" else self.leads_collection
        results = collection.get()
        
        leads = []
        for idx, metadata in enumerate(results.get("metadatas", [])):
            leads.append(metadata)
        
        return leads

    def clear_collection(self, collection_name="leads"):
        """Clear a collection if needed."""
        collection = self.leads_collection if collection_name == "leads" else self.enriched_collection
        collection.delete(where={})
        print(f"[ChromaStore] Cleared {collection_name} collection")