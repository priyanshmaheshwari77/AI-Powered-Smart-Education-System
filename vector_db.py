from upstash_vector import Index
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

load_dotenv()

class VectorDB:
    def __init__(self):
        # Upstash Vector Credentials
        url = os.getenv("UPSTASH_VECTOR_REST_URL")
        token = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
        
        if not url or not token:
            print("WARNING: Upstash Vector credentials not found in .env")
            self.index = None
        else:
            self.index = Index(url=url, token=token)
        
        # Local Embedding Model (same as used for local ChromaDB)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def add_content(self, topic, content_dict):
        """
        Add educational content to Upstash Vector DB.
        """
        if not self.index:
            return

        # Content needs to be a string for embedding
        text_to_embed = f"Topic: {topic}\n\nContent: {content_dict.get('article', '')}"
        
        # Generate embedding locally
        embedding = self.model.encode(text_to_embed).tolist()
        
        # Upsert to Upstash
        self.index.upsert(
            vectors=[
                (
                    topic.lower().replace(" ", "_"), # ID
                    embedding,                        # Vector
                    {"topic": topic}                  # Metadata
                )
            ]
        )

    def search(self, query, n_results=1):
        """
        Search for relevant content in Upstash.
        """
        if not self.index:
            return None

        # Generate query embedding locally
        query_vector = self.model.encode(query).tolist()
        
        # Query Upstash
        results = self.index.query(
            vector=query_vector,
            top_k=n_results,
            include_metadata=True
        )
        
        if results:
            # Check similarity (Upstash score is usually 0 to 1)
            # Higher is better for Cosine similarity in Upstash
            match = results[0]
            if match.score > 0.7: # Threshold for semantic match
                return match.metadata["topic"]
        
        return None

# Singleton instance
vector_db_instance = VectorDB()
