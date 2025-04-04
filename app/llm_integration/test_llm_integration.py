"""
Test script for the LLM integration module
"""

import unittest
from unittest.mock import patch, MagicMock
from app.llm_integration.llm_integration import LLMIntegration
from app.llm_integration.test_utils import (
    get_mock_ollama_response,
    get_sample_content,
    get_expected_parsed_questions
)

class TestLLMIntegration(unittest.TestCase):
    """Test cases for the LLMIntegration class"""
    
    def setUp(self):
        """Set up test environment"""
        self.llm = LLMIntegration(model_name="llama3")
        self.sample_content = get_sample_content()
    
    def test_get_system_prompt(self):
        """Test getting system prompts for different question types"""
        params = {
            "num_questions": 10,
            "difficulty": "medium",
            "language": "English",
            "topic": "Artificial Intelligence"
        }
        
        # Test multiple choice prompt
        mc_prompt = self.llm.get_system_prompt("multiple_choice", params)
        self.assertIn("multiple-choice questions", mc_prompt)
        self.assertIn("10", mc_prompt)
        self.assertIn("medium", mc_prompt)
        self.assertIn("English", mc_prompt)
        self.assertIn("Artificial Intelligence", mc_prompt)
        
        # Test true/false prompt
        tf_prompt = self.llm.get_system_prompt("true_false", params)
        self.assertIn("true/false questions", tf_prompt)
        
        # Test unsupported question type
        with self.assertRaises(ValueError):
            self.llm.get_system_prompt("unsupported_type", params)
    
    @patch('ollama.chat')
    def test_generate_questions(self, mock_chat):
        """Test generating questions with mocked Ollama API"""
        # Set up the mock
        mock_chat.return_value = get_mock_ollama_response()
        
        # Test generating multiple choice questions
        questions = self.llm.generate_questions(
            content=self.sample_content,
            question_type="multiple_choice",
            num_questions=3,
            difficulty="medium",
            language="English",
            topic="Artificial Intelligence"
        )
        
        # Verify the mock was called with expected arguments
        mock_chat.assert_called_once()
        args, kwargs = mock_chat.call_args
        self.assertEqual(kwargs["model"], "llama3")
        self.assertEqual(len(kwargs["messages"]), 2)
        self.assertEqual(kwargs["messages"][0]["role"], "system")
        self.assertEqual(kwargs["messages"][1]["role"], "user")
        self.assertIn("Generate 3 multiple_choice questions", kwargs["messages"][1]["content"])
        
        # Verify the parsed questions
        self.assertEqual(len(questions), 3)
        self.assertEqual(questions[0]["question_type"], "multiple_choice")
        self.assertEqual(len(questions[0]["options"]), 4)
        self.assertEqual(questions[0]["correct_answer"], "B")
    
    def test_parse_questions(self):
        """Test parsing raw question text into structured objects"""
        # Get mock response content
        raw_questions = get_mock_ollama_response()["message"]["content"]
        
        # Parse the questions
        parsed_questions = self.llm._parse_questions(raw_questions, "multiple_choice")
        
        # Get expected parsed questions
        expected_questions = get_expected_parsed_questions()
        
        # Verify the parsed questions match the expected structure
        self.assertEqual(len(parsed_questions), len(expected_questions))
        
        for i, question in enumerate(parsed_questions):
            expected = expected_questions[i]
            self.assertEqual(question["question_text"], expected["question_text"])
            self.assertEqual(question["question_type"], expected["question_type"])
            self.assertEqual(question["correct_answer"], expected["correct_answer"])
            self.assertEqual(len(question["options"]), len(expected["options"]))
    
    def test_filter_questions(self):
        """Test filtering questions for quality"""
        # Create some test questions
        questions = [
            {
                "question_text": "What is Artificial Intelligence?",
                "question_type": "multiple_choice",
                "options": [
                    {"letter": "A", "text": "Option A"},
                    {"letter": "B", "text": "Option B"}
                ],
                "correct_answer": "A"
            },
            {
                "question_text": "What is Quantum Computing?",  # Not in sample content
                "question_type": "multiple_choice",
                "options": [
                    {"letter": "A", "text": "Option A"},
                    {"letter": "B", "text": "Option B"}
                ],
                "correct_answer": "B"
            }
        ]
        
        # Filter the questions
        filtered = self.llm.filter_questions(questions, self.sample_content)
        
        # Verify only the relevant question is kept
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["question_text"], "What is Artificial Intelligence?")

if __name__ == "__main__":
    unittest.main()
