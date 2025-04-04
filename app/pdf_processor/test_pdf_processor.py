"""
Test script for the PDF processor module
"""

import os
import unittest
from app.pdf_processor.pdf_processor import PDFProcessor
from app.pdf_processor.test_utils import create_test_pdf, get_sample_text

class TestPDFProcessor(unittest.TestCase):
    """Test cases for the PDFProcessor class"""
    
    def setUp(self):
        """Set up test environment"""
        self.processor = PDFProcessor(chunk_size=200, chunk_overlap=50)
        self.full_text, self.topic_text = get_sample_text()
        self.test_pdf_path = create_test_pdf(self.full_text)
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_pdf_path):
            os.remove(self.test_pdf_path)
    
    def test_extract_text_from_pdf(self):
        """Test text extraction from PDF"""
        extracted_text = self.processor.extract_text_from_pdf(self.test_pdf_path)
        # Check if the extracted text contains key phrases from our sample text
        self.assertIn("Artificial Intelligence", extracted_text)
        self.assertIn("Machine Learning", extracted_text)
    
    def test_chunk_text(self):
        """Test text chunking functionality"""
        chunks = self.processor.chunk_text(self.full_text)
        # Verify we have multiple chunks
        self.assertTrue(len(chunks) > 1)
        # Verify chunk size is approximately as expected
        for chunk in chunks:
            self.assertLessEqual(len(chunk), self.processor.chunk_size + 100)  # Allow some flexibility
    
    def test_extract_topic_content(self):
        """Test topic extraction functionality"""
        topic = "Neural Networks"
        topic_content = self.processor.extract_topic_content(self.full_text, topic)
        # Verify the topic content contains relevant information
        self.assertIn("Neural Networks", topic_content)
        self.assertIn("Deep Learning", topic_content)
    
    def test_process_pdf(self):
        """Test the complete PDF processing pipeline"""
        # Test with no topic
        result = self.processor.process_pdf(self.test_pdf_path)
        self.assertIn("full_text", result)
        self.assertIn("chunks", result)
        self.assertIn("metadata", result)
        self.assertTrue(len(result["chunks"]) > 0)
        
        # Test with a specific topic
        topic_result = self.processor.process_pdf(self.test_pdf_path, topic="Neural Networks")
        self.assertIn("full_text", topic_result)
        self.assertIn("chunks", topic_result)
        self.assertIn("metadata", topic_result)
        self.assertEqual(topic_result["topic"], "Neural Networks")

if __name__ == "__main__":
    unittest.main()
