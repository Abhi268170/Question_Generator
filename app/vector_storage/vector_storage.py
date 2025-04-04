"""
Vector Storage Module

This module handles the vectorization and storage of text chunks for efficient retrieval.
It provides functionality to:
1. Convert text chunks to vector representations using TF-IDF
2. Store vectors in a FAISS index for efficient similarity search
3. Retrieve the most relevant chunks based on a query
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Tuple, Any, Optional
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer

class VectorStorage:
    """
    A class for vectorizing, storing, and retrieving text chunks using TF-IDF and FAISS.
    """
    
    def __init__(self, use_idf: bool = True, max_features: int = 5000):
        """
        Initialize the vector storage with vectorization parameters.
        
        Args:
            use_idf: Whether to use inverse document frequency weighting
            max_features: Maximum number of features for the TF-IDF vectorizer
        """
        self.vectorizer = TfidfVectorizer(
            use_idf=use_idf,
            max_features=max_features,
            stop_words='english',
            ngram_range=(1, 2)  # Use unigrams and bigrams
        )
        self.index = None
        self.chunks = []
        self.is_fitted = False
    
    def fit(self, chunks: List[str]) -> None:
        """
        Fit the vectorizer to the provided text chunks and build the FAISS index.
        
        Args:
            chunks: List of text chunks to fit the vectorizer on
        """
        if not chunks:
            raise ValueError("Cannot fit on empty chunks list")
        
        # Store the original chunks
        self.chunks = chunks
        
        # Fit and transform the chunks to get TF-IDF vectors
        vectors = self.vectorizer.fit_transform(chunks).toarray().astype(np.float32)
        
        # Create and train the FAISS index
        dimension = vectors.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product similarity (cosine when vectors are normalized)
        
        # Normalize vectors for cosine similarity
        faiss.normalize_L2(vectors)
        
        # Add vectors to the index
        self.index.add(vectors)
        
        self.is_fitted = True
    
    def transform(self, texts: List[str]) -> np.ndarray:
        """
        Transform texts to vector representations using the fitted vectorizer.
        
        Args:
            texts: List of texts to transform
            
        Returns:
            Array of vector representations
        """
        if not self.is_fitted:
            raise ValueError("Vectorizer is not fitted yet. Call fit() first.")
        
        vectors = self.vectorizer.transform(texts).toarray().astype(np.float32)
        
        # Normalize vectors for cosine similarity
        faiss.normalize_L2(vectors)
        
        return vectors
    
    def search(self, query: str, k: int = 5) -> Tuple[List[str], List[float]]:
        """
        Search for the k most similar chunks to the query.
        
        Args:
            query: The search query
            k: Number of results to return
            
        Returns:
            Tuple of (list of retrieved chunks, list of similarity scores)
        """
        if not self.is_fitted:
            raise ValueError("Index is not built yet. Call fit() first.")
        
        # Ensure k is not larger than the number of chunks
        k = min(k, len(self.chunks))
        
        # Transform the query to a vector
        query_vector = self.transform([query])
        
        # Search the index
        scores, indices = self.index.search(query_vector, k)
        
        # Get the corresponding chunks and scores
        retrieved_chunks = [self.chunks[idx] for idx in indices[0]]
        similarity_scores = scores[0].tolist()
        
        return retrieved_chunks, similarity_scores
    
    def combine_chunks(self, chunks: List[str], max_length: int = 4000) -> str:
        """
        Combine retrieved chunks into a cohesive text block while preserving meaning.
        
        Args:
            chunks: List of text chunks to combine
            max_length: Maximum length of the combined text
            
        Returns:
            Combined text
        """
        if not chunks:
            return ""
        
        combined_text = chunks[0]
        current_length = len(combined_text)
        
        for chunk in chunks[1:]:
            # Check if adding this chunk would exceed the max length
            if current_length + len(chunk) > max_length:
                break
            
            # Add the chunk with a separator
            combined_text += "\n\n" + chunk
            current_length += len(chunk) + 2  # +2 for the newlines
        
        return combined_text
    
    def retrieve_for_topic(self, topic: str, k: int = 5, max_length: int = 4000) -> str:
        """
        Retrieve and combine chunks relevant to a specific topic.
        
        Args:
            topic: The topic to retrieve chunks for
            k: Number of chunks to retrieve
            max_length: Maximum length of the combined text
            
        Returns:
            Combined text of the most relevant chunks
        """
        chunks, _ = self.search(topic, k)
        return self.combine_chunks(chunks, max_length)
    
    def save(self, directory: str) -> None:
        """
        Save the vector storage to disk.
        
        Args:
            directory: Directory to save the vector storage in
        """
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted vector storage")
        
        os.makedirs(directory, exist_ok=True)
        
        # Save the vectorizer
        with open(os.path.join(directory, "vectorizer.pkl"), "wb") as f:
            pickle.dump(self.vectorizer, f)
        
        # Save the chunks
        with open(os.path.join(directory, "chunks.pkl"), "wb") as f:
            pickle.dump(self.chunks, f)
        
        # Save the FAISS index
        faiss.write_index(self.index, os.path.join(directory, "index.faiss"))
    
    @classmethod
    def load(cls, directory: str) -> 'VectorStorage':
        """
        Load a vector storage from disk.
        
        Args:
            directory: Directory to load the vector storage from
            
        Returns:
            Loaded VectorStorage instance
        """
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory {directory} does not exist")
        
        # Create a new instance
        instance = cls()
        
        # Load the vectorizer
        with open(os.path.join(directory, "vectorizer.pkl"), "rb") as f:
            instance.vectorizer = pickle.load(f)
        
        # Load the chunks
        with open(os.path.join(directory, "chunks.pkl"), "rb") as f:
            instance.chunks = pickle.load(f)
        
        # Load the FAISS index
        instance.index = faiss.read_index(os.path.join(directory, "index.faiss"))
        
        instance.is_fitted = True
        
        return instance
