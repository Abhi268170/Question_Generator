"""
Test utilities for the LLM integration module
"""

from typing import Dict, Any, List

def get_mock_ollama_response() -> Dict[str, Any]:
    """
    Get a mock Ollama response for testing without actual API calls.
    
    Returns:
        Mock Ollama response
    """
    return {
        "model": "llama3",
        "created_at": "2025-04-03T11:35:00.000Z",
        "message": {
            "role": "assistant",
            "content": """Q1. What is the primary goal of Artificial Intelligence?
A. To replace human workers
B. To create systems capable of performing tasks that require human intelligence
C. To develop self-aware machines
D. To maximize computational efficiency
Correct Answer: B

Q2. Which of the following is NOT a type of machine learning mentioned in the text?
A. Supervised Learning
B. Unsupervised Learning
C. Reinforcement Learning
D. Quantum Learning
Correct Answer: D

Q3. Deep Learning is characterized by:
A. Using only shallow neural networks
B. Avoiding neural networks entirely
C. Using neural networks with many layers
D. Focusing exclusively on symbolic methods
Correct Answer: C"""
        },
        "done": True
    }

def get_sample_content() -> str:
    """
    Get sample content for testing the LLM integration.
    
    Returns:
        Sample content text
    """
    return """
Artificial Intelligence (AI) is the field of computer science dedicated to creating systems capable of performing tasks that typically require human intelligence. These tasks include learning, reasoning, problem-solving, perception, and language understanding.

Machine Learning is a subset of AI that focuses on developing algorithms that can learn from and make predictions based on data. Instead of explicitly programming rules, machine learning systems identify patterns in data and improve their performance with experience.

There are three main types of machine learning:

1. Supervised Learning: The algorithm learns from labeled training data, making predictions or decisions based on that learning.

2. Unsupervised Learning: The algorithm finds patterns or structures in unlabeled data.

3. Reinforcement Learning: The algorithm learns by interacting with an environment, receiving rewards or penalties for its actions.

Neural networks are computing systems inspired by the biological neural networks in animal brains. They consist of interconnected nodes or "neurons" that process and transmit information.

Deep Learning is a subset of machine learning that uses neural networks with many layers (hence "deep"). These deep neural networks have revolutionized fields such as computer vision, natural language processing, and speech recognition.
"""

def get_expected_parsed_questions() -> List[Dict[str, Any]]:
    """
    Get expected parsed questions for testing the parsing functionality.
    
    Returns:
        List of expected parsed question objects
    """
    return [
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
        },
        {
            "question_text": "Deep Learning is characterized by:",
            "question_type": "multiple_choice",
            "options": [
                {"letter": "A", "text": "Using only shallow neural networks"},
                {"letter": "B", "text": "Avoiding neural networks entirely"},
                {"letter": "C", "text": "Using neural networks with many layers"},
                {"letter": "D", "text": "Focusing exclusively on symbolic methods"}
            ],
            "correct_answer": "C"
        }
    ]
