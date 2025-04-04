"""
Test utilities for the vector storage module
"""

import numpy as np
from typing import List, Tuple

def get_sample_chunks() -> List[str]:
    """
    Get sample text chunks for testing the vector storage.
    
    Returns:
        List of text chunks
    """
    return [
        "Artificial Intelligence (AI) is the field of computer science dedicated to creating systems capable of performing tasks that typically require human intelligence.",
        "Machine Learning is a subset of AI that focuses on developing algorithms that can learn from and make predictions based on data.",
        "Neural networks are computing systems inspired by the biological neural networks in animal brains.",
        "Deep Learning is a subset of machine learning that uses neural networks with many layers (hence 'deep').",
        "Supervised Learning is where the algorithm learns from labeled training data, making predictions based on that learning.",
        "Unsupervised Learning is where the algorithm finds patterns or structures in unlabeled data.",
        "Reinforcement Learning is where the algorithm learns by interacting with an environment, receiving rewards or penalties.",
        "Natural Language Processing (NLP) is a field of AI focused on enabling computers to understand and process human language.",
        "Computer Vision is an interdisciplinary field that deals with how computers can gain high-level understanding from digital images or videos.",
        "AI Ethics concerns the moral behaviors and responsible creation of artificially intelligent beings."
    ]

def get_sample_queries() -> List[Tuple[str, List[int]]]:
    """
    Get sample queries and expected relevant chunk indices for testing search functionality.
    
    Returns:
        List of tuples containing (query, list of expected relevant chunk indices)
    """
    return [
        ("What is artificial intelligence?", [0]),
        ("How do neural networks work?", [2, 3]),
        ("Types of machine learning", [1, 4, 5, 6]),
        ("Deep learning and neural networks", [2, 3]),
        ("AI applications in language", [7])
    ]
