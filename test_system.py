"""
Test script for the entire PDF Question Generator system
"""

import os
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from app.pdf_processor import PDFProcessor
from app.vector_storage import VectorStorage
from app.llm_integration import LLMIntegration
from app.question_generator import QuestionGenerator
from app.pdf_processor.test_utils import create_test_pdf, get_sample_text

class TestPDFQuestionGenerator(unittest.TestCase):
    """Integration tests for the PDF Question Generator system"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a test PDF
        full_text, _ = get_sample_text()
        self.test_pdf_path = create_test_pdf(full_text)
        
        # Create a temporary directory for outputs
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize the question generator with mocked LLM
        self.question_generator = QuestionGenerator(model_name="llama3")
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_pdf_path):
            os.remove(self.test_pdf_path)
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('app.llm_integration.LLMIntegration.generate_questions')
    def test_end_to_end_question_generation(self, mock_generate_questions):
        """Test the entire question generation pipeline"""
        # Set up the mock
        mock_questions = [
            {
                "question_text": "What is Artificial Intelligence?",
                "question_type": "multiple_choice",
                "options": [
                    {"letter": "A", "text": "A type of computer hardware"},
                    {"letter": "B", "text": "The field of creating systems capable of performing tasks that require human intelligence"},
                    {"letter": "C", "text": "A programming language"},
                    {"letter": "D", "text": "A database management system"}
                ],
                "correct_answer": "B"
            },
            {
                "question_text": "Which of these is a type of machine learning?",
                "question_type": "multiple_choice",
                "options": [
                    {"letter": "A", "text": "Supervised Learning"},
                    {"letter": "B", "text": "Quantum Learning"},
                    {"letter": "C", "text": "Analog Learning"},
                    {"letter": "D", "text": "Mechanical Learning"}
                ],
                "correct_answer": "A"
            }
        ]
        mock_generate_questions.return_value = mock_questions
        
        # Generate questions
        result = self.question_generator.generate_questions(
            pdf_path=self.test_pdf_path,
            question_type="multiple_choice",
            num_questions=5,
            topic="Artificial Intelligence",
            difficulty="medium",
            language="English"
        )
        
        # Verify the result
        self.assertIsNotNone(result)
        self.assertIn("questions", result)
        self.assertIn("metadata", result)
        self.assertEqual(len(result["questions"]), 2)
        self.assertEqual(result["metadata"]["question_type"], "multiple_choice")
        self.assertEqual(result["metadata"]["topic"], "Artificial Intelligence")
    
    def test_pdf_processor_integration(self):
        """Test the PDF processor component integration"""
        pdf_processor = PDFProcessor()
        result = pdf_processor.process_pdf(self.test_pdf_path)
        
        self.assertIn("full_text", result)
        self.assertIn("chunks", result)
        self.assertIn("metadata", result)
        self.assertTrue(len(result["chunks"]) > 0)
    
    def test_vector_storage_integration(self):
        """Test the vector storage component integration"""
        # Process PDF to get chunks
        pdf_processor = PDFProcessor()
        pdf_data = pdf_processor.process_pdf(self.test_pdf_path)
        
        # Test vector storage with the chunks
        vector_storage = VectorStorage()
        vector_storage.fit(pdf_data["chunks"])
        
        # Test retrieval
        retrieved_chunks, scores = vector_storage.search("Artificial Intelligence", k=2)
        self.assertEqual(len(retrieved_chunks), 2)
        self.assertEqual(len(scores), 2)
        
        # Test saving and loading
        save_path = os.path.join(self.temp_dir, "vector_storage")
        vector_storage.save(save_path)
        
        loaded_storage = VectorStorage.load(save_path)
        self.assertEqual(len(loaded_storage.chunks), len(vector_storage.chunks))
    
    def test_system_performance(self):
        """Test system performance with timing measurements"""
        import time
        
        # Measure PDF processing time
        start_time = time.time()
        pdf_processor = PDFProcessor()
        pdf_data = pdf_processor.process_pdf(self.test_pdf_path)
        pdf_processing_time = time.time() - start_time
        
        # Measure vector storage time
        start_time = time.time()
        vector_storage = VectorStorage()
        vector_storage.fit(pdf_data["chunks"])
        vector_storage_time = time.time() - start_time
        
        # Print performance metrics
        print(f"\nPerformance Metrics:")
        print(f"PDF Processing Time: {pdf_processing_time:.4f} seconds")
        print(f"Vector Storage Time: {vector_storage_time:.4f} seconds")
        print(f"Number of Chunks: {len(pdf_data['chunks'])}")
        
        # Assert reasonable performance
        self.assertLess(pdf_processing_time, 5.0, "PDF processing took too long")
        self.assertLess(vector_storage_time, 5.0, "Vector storage took too long")

if __name__ == "__main__":
    unittest.main()
