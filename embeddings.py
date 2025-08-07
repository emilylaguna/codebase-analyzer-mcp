import spacy
from typing import List
import logging

logger = logging.getLogger(__name__)


class EmbeddingManager:
    def __init__(self, model_name: str = "en_core_web_lg"):
        """
        Initialize the embedding manager with SpaCy model.
        
        Args:
            model_name: SpaCy model name (default: en_core_web_md)
        """
        self.model_name = model_name
        self.nlp = None
        self._load_model()
    
    def _load_model(self):
        """Load the SpaCy model."""
        try:
            self.nlp = spacy.load(self.model_name)
            logger.info(f"Loaded SpaCy model: {self.model_name}")
        except OSError:
            logger.error(f"SpaCy model '{self.model_name}' not found. Please install it with:")
            logger.error(f"python -m spacy download {self.model_name}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for given text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of 300 float values representing the embedding
        """
        if not self.nlp:
            raise RuntimeError("SpaCy model not loaded")
        
        try:
            doc = self.nlp(text)
            # Get the vector representation
            embedding = doc.vector.tolist()
            
            # Ensure we have exactly 300 dimensions
            if len(embedding) != 300:
                logger.warning(f"Expected 300 dimensions, got {len(embedding)}")
                # Pad or truncate to 300 dimensions
                if len(embedding) < 300:
                    embedding.extend([0.0] * (300 - len(embedding)))
                else:
                    embedding = embedding[:300]
            
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding for text: {e}")
            # Return zero vector as fallback
            return [0.0] * 300
    
    def get_embedding_for_code(self, code_snippet: str, symbol_name: str = "", symbol_type: str = "") -> List[float]:
        """
        Generate embedding specifically for code snippets.
        
        Args:
            code_snippet: The code snippet to embed
            symbol_name: Name of the symbol (optional, for context)
            symbol_type: Type of the symbol (optional, for context)
            
        Returns:
            List of 300 float values representing the embedding
        """
        # Create a context-aware text for better embeddings
        context_text = f"{symbol_type} {symbol_name} {code_snippet}"
        
        # Clean up the text for better embedding quality
        cleaned_text = self._clean_code_text(context_text)
        
        return self.get_embedding(cleaned_text)
    
    def _clean_code_text(self, text: str) -> str:
        """
        Clean code text for better embedding quality.
        
        Args:
            text: Raw code text
            
        Returns:
            Cleaned text suitable for embedding
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove common code patterns that don't add semantic value
        # Keep function names, class names, and meaningful identifiers
        # Remove excessive punctuation and special characters
        
        # Limit length to avoid token limits
        max_length = 1000
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text
    
    def batch_get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
        """
        if not self.nlp:
            raise RuntimeError("SpaCy model not loaded")
        
        try:
            # Limit batch size to prevent memory issues
            max_batch_size = 50
            if len(texts) > max_batch_size:
                logger.warning(f"Large batch size ({len(texts)}), processing in chunks of {max_batch_size}")
                all_embeddings = []
                for i in range(0, len(texts), max_batch_size):
                    chunk = texts[i:i + max_batch_size]
                    chunk_embeddings = self._process_batch_chunk(chunk)
                    all_embeddings.extend(chunk_embeddings)
                return all_embeddings
            else:
                return self._process_batch_chunk(texts)
                
        except Exception as e:
            logger.error(f"Error in batch embedding generation: {e}")
            # Return zero vectors as fallback
            return [[0.0] * 300 for _ in texts]
    
    def _process_batch_chunk(self, texts: List[str]) -> List[List[float]]:
        """Process a chunk of texts for batch embedding generation."""
        try:
            # Clean texts first to reduce memory usage
            cleaned_texts = [self._clean_code_text(text) for text in texts]
            
            # Process with SpaCy pipe
            docs = list(self.nlp.pipe(cleaned_texts))
            embeddings = []
            
            for doc in docs:
                embedding = doc.vector.tolist()
                
                # Ensure 300 dimensions
                if len(embedding) != 300:
                    if len(embedding) < 300:
                        embedding.extend([0.0] * (300 - len(embedding)))
                    else:
                        embedding = embedding[:300]
                
                embeddings.append(embedding)
            
            return embeddings
        except Exception as e:
            logger.error(f"Error processing batch chunk: {e}")
            # Return zero vectors as fallback
            return [[0.0] * 300 for _ in texts]
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model."""
        if not self.nlp:
            return {"error": "Model not loaded"}
        
        return {
            "model_name": self.model_name,
            "vector_dimensions": len(self.nlp.vocab.vectors),
            "vocab_size": len(self.nlp.vocab),
            "pipeline": list(self.nlp.pipe_names)
        } 