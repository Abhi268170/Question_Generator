"""
Test script for the question generator module
"""

import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil

from app.question_generator.question_generator import QuestionGenerator
from app.question_generator.test_utils import get_test_pdf_path, get_mock_question_generation_result

class TestQuestionGenerator(unittest.TestCase):
    """Test cases for the QuestionGenerator class"""
    
    def setUp(self):
        """Set up test environment"""
        self.question_generator = QuestionGenerator(model_name="llama3")
        self.test_pdf_path = get_test_pdf_path()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_pdf_path):
            os.remove(self.test_pdf_path)
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('app.pdf_processor.PDFProcessor.process_pdf')
    @patch('app.vector_storage.VectorStorage.fit')
    def test_process_pdf(self, mock_fit, mock_process_pdf):
        """Test processing a PDF file"""
        # Set up the mocks
        mock_process_pdf.return_value = {
            "full_text": "Sample text",
            "chunks": ["Chunk 1", "Chunk 2"],
            "metadata": {"page_count": 1}
        }
        
        # Process the PDF
        result = self.question_generator.process_pdf(self.test_pdf_path, topic="AI")
        
        # Verify the mocks were called with expected arguments
        mock_process_pdf.assert_called_once_with(self.test_pdf_path, "AI")
        mock_fit.assert_called_once_with(["Chunk 1", "Chunk 2"])
        
        # Verify the result
        self.assertEqual(result["full_text"], "Sample text")
        self.assertEqual(result["chunks"], ["Chunk 1", "Chunk 2"])
        self.assertEqual(result["metadata"], {"page_count": 1})
    
    @patch('app.question_generator.QuestionGenerator.process_pdf')
    @patch('app.vector_storage.VectorStorage.retrieve_for_topic')
    @patch('app.llm_integration.LLMIntegration.generate_questions')
    @patch('app.llm_integration.LLMIntegration.filter_questions')
    def test_generate_questions(self, mock_filter, mock_generate, mock_retrieve, mock_process_pdf):
        """Test generating questions from a PDF"""
        # Set up the mocks
        mock_process_pdf.return_value = {
            "full_text": "Sample text about AI",
            "chunks": ["Chunk 1", "Chunk 2"],
            "metadata": {"page_count": 1}
        }
        mock_retrieve.return_value = "Relevant content about AI"
        mock_generate.return_value = [{"question_text": "Q1"}, {"question_text": "Q2"}]
        mock_filter.return_value = [{"question_text": "Q1"}]
        
        # Generate questions
        result = self.question_generator.generate_questions(
            pdf_path=self.test_pdf_path,
            question_type="multiple_choice",
            num_questions=5,
            topic="AI",
            difficulty="medium",
            language="English"
        )
        
        # Verify the mocks were called with expected arguments
        mock_process_pdf.assert_called_once_with(self.test_pdf_path, "AI")
        mock_retrieve.assert_called_once()
        mock_generate.assert_called_once_with(
            content="Relevant content about AI",
            question_type="multiple_choice",
            num_questions=5,
            difficulty="medium",
            language="English",
            topic="AI",
            temperature=0.7
        )
        mock_filter.assert_called_once_with(
            [{"question_text": "Q1"}, {"question_text": "Q2"}],
            "Relevant content about AI"
        )
        
        # Verify the result
        self.assertEqual(len(result["questions"]), 1)
        self.assertEqual(result["questions"][0]["question_text"], "Q1")
        self.assertEqual(result["metadata"]["question_type"], "multiple_choice")
        self.assertEqual(result["metadata"]["topic"], "AI")
        self.assertEqual(result["metadata"]["requested_count"], 5)
        self.assertEqual(result["metadata"]["generated_count"], 2)
        self.assertEqual(result["metadata"]["filtered_count"], 1)
    
    @patch('app.vector_storage.VectorStorage.save')
    def test_save_vector_storage(self, mock_save):
        """Test saving vector storage"""
        save_dir = os.path.join(self.temp_dir, "vector_storage")
        self.question_generator.save_vector_storage(save_dir)
        mock_save.assert_called_once_with(save_dir)
    
    @patch('app.vector_storage.VectorStorage.load')
    def test_load_vector_storage(self, mock_load):
        """Test loading vector storage"""
        # Set up the mock
        mock_storage = MagicMock()
        mock_load.return_value = mock_storage
        
        # Load vector storage
        load_dir = os.path.join(self.temp_dir, "vector_storage")
        self.question_generator.load_vector_storage(load_dir)
        
        # Verify the mock was called with expected arguments
        mock_load.assert_called_once_with(load_dir)
        
        # Verify the vector storage was updated
        self.assertEqual(self.question_generator.vector_storage, mock_storage)

if __name__ == "__main__":
    unittest.main()
