"""
Test script for the vector storage module
"""

import os
import unittest
import tempfile
import shutil
import numpy as np
from app.vector_storage.vector_storage import VectorStorage
from app.vector_storage.test_utils import get_sample_chunks, get_sample_queries

class TestVectorStorage(unittest.TestCase):
    """Test cases for the VectorStorage class"""
    
    def setUp(self):
        """Set up test environment"""
        self.chunks = get_sample_chunks()
        self.queries = get_sample_queries()
        self.vector_storage = VectorStorage(max_features=100)
        self.vector_storage.fit(self.chunks)
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_fit_and_transform(self):
        """Test fitting the vectorizer and transforming text"""
        # Check if the vectorizer is fitted
        self.assertTrue(self.vector_storage.is_fitted)
        
        # Test transforming a single text
        vector = self.vector_storage.transform(["This is a test"])
        self.assertIsInstance(vector, np.ndarray)
        self.assertEqual(vector.shape[0], 1)  # One row for one text
    
    def test_search(self):
        """Test searching for similar chunks"""
        for query, expected_indices in self.queries:
            chunks, scores = self.vector_storage.search(query, k=3)
            
            # Check that we got the expected number of results
            self.assertLessEqual(len(chunks), 3)
            self.assertEqual(len(chunks), len(scores))
            
            # Check that at least one of the expected chunks is in the results
            found = False
            for idx in expected_indices:
                expected_chunk = self.chunks[idx]
                if any(expected_chunk in chunk for chunk in chunks):
                    found = True
                    break
            
            self.assertTrue(found, f"Expected chunk not found for query: {query}")
            
            # Check that scores are in descending order
            self.assertEqual(scores, sorted(scores, reverse=True))
    
    def test_combine_chunks(self):
        """Test combining chunks into a cohesive text"""
        combined = self.vector_storage.combine_chunks(self.chunks[:3], max_length=1000)
        
        # Check that the combined text contains all three chunks
        for i in range(3):
            self.assertIn(self.chunks[i], combined)
        
        # Test with a small max_length
        small_combined = self.vector_storage.combine_chunks(self.chunks, max_length=100)
        self.assertLessEqual(len(small_combined), 100 + len(self.chunks[0]))  # Allow for the first chunk to exceed max_length
    
    def test_retrieve_for_topic(self):
        """Test retrieving chunks for a specific topic"""
        topic = "neural networks and deep learning"
        combined = self.vector_storage.retrieve_for_topic(topic, k=3)
        
        # Check that the combined text is not empty
        self.assertTrue(len(combined) > 0)
        
        # Check that it contains relevant information
        self.assertTrue("neural" in combined.lower() or "deep" in combined.lower())
    
    def test_save_and_load(self):
        """Test saving and loading the vector storage"""
        # Save the vector storage
        save_path = os.path.join(self.temp_dir, "vector_storage")
        self.vector_storage.save(save_path)
        
        # Check that the files were created
        self.assertTrue(os.path.exists(os.path.join(save_path, "vectorizer.pkl")))
        self.assertTrue(os.path.exists(os.path.join(save_path, "chunks.pkl")))
        self.assertTrue(os.path.exists(os.path.join(save_path, "index.faiss")))
        
        # Load the vector storage
        loaded_storage = VectorStorage.load(save_path)
        
        # Check that the loaded storage has the same properties
        self.assertEqual(len(loaded_storage.chunks), len(self.vector_storage.chunks))
        self.assertTrue(loaded_storage.is_fitted)
        
        # Test search with the loaded storage
        chunks, scores = loaded_storage.search("neural networks", k=2)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(len(scores), 2)

if __name__ == "__main__":
    unittest.main()
