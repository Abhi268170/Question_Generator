"""
Test utilities for the question generator module
"""

import os
import tempfile
from typing import Dict, Any

def get_test_pdf_path() -> str:
    """
    Create a temporary PDF file for testing.
    
    Returns:
        Path to the temporary PDF file
    """
    from app.pdf_processor.test_utils import create_test_pdf, get_sample_text
    
    full_text, _ = get_sample_text()
    return create_test_pdf(full_text)

def get_mock_question_generation_result() -> Dict[str, Any]:
    """
    Get a mock question generation result for testing.
    
    Returns:
        Mock question generation result
    """
    return {
        "questions": [
            {
                "question_text": "What is the primary goal of Artificial Intelligence?",
                "question_type": "multiple_choice",
                "options": [
                    {"letter": "A", "text": "To replace human workers"},
                    {"letter": "B", "text": "To create systems capable of performing tasks that require human intelligence"},
                    {"letter": "C", "text": "To develop self-aware machines"},
                    {"letter": "D", "text": "To maximize computational efficiency"}
                ],
                "correct_answer": "B"
            },
            {
                "question_text": "Which of the following is NOT a type of machine learning mentioned in the text?",
                "question_type": "multiple_choice",
                "options": [
                    {"letter": "A", "text": "Supervised Learning"},
                    {"letter": "B", "text": "Unsupervised Learning"},
                    {"letter": "C", "text": "Reinforcement Learning"},
                    {"letter": "D", "text": "Quantum Learning"}
                ],
                "correct_answer": "D"
            }
        ],
        "metadata": {
            "pdf_filename": "test.pdf",
            "question_type": "multiple_choice",
            "topic": "Artificial Intelligence",
            "difficulty": "medium",
            "language": "English",
            "requested_count": 5,
            "generated_count": 2,
            "filtered_count": 2,
            "timestamp": "2025-04-03 11:37:00"
        }
    }
