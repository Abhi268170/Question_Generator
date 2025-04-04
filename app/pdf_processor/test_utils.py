"""
Test utilities for the PDF processor module
"""

import os
import tempfile
from typing import Tuple

def create_test_pdf(content: str) -> str:
    """
    Create a temporary PDF file with the given content for testing purposes.
    
    Args:
        content: Text content to include in the PDF
        
    Returns:
        Path to the created temporary PDF file
    """
    try:
        # Try to use reportlab to create a PDF
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Create a temporary file
        fd, path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        
        # Create the PDF
        c = canvas.Canvas(path, pagesize=letter)
        width, height = letter
        
        # Split content into lines
        lines = content.split('\n')
        y_position = height - 50  # Start from top with margin
        
        for line in lines:
            if line.strip():
                c.drawString(50, y_position, line)
                y_position -= 12  # Move down for next line
                
                # If we reach the bottom of the page, create a new page
                if y_position < 50:
                    c.showPage()
                    y_position = height - 50
        
        c.save()
        return path
    
    except ImportError:
        # If reportlab is not available, create a simple text file with .pdf extension
        # This is just for testing the interface, not for actual PDF functionality
        fd, path = tempfile.mkstemp(suffix='.pdf')
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        return path

def get_sample_text() -> Tuple[str, str]:
    """
    Get sample text for testing the PDF processor.
    
    Returns:
        Tuple containing (full_text, topic_text)
    """
    full_text = """
Introduction to Artificial Intelligence

Artificial Intelligence (AI) is the field of computer science dedicated to creating systems capable of performing tasks that typically require human intelligence. These tasks include learning, reasoning, problem-solving, perception, and language understanding.

History of Artificial Intelligence

The term "Artificial Intelligence" was coined in 1956 at the Dartmouth Conference, where the field was formally founded. Early AI research focused on symbolic methods and problem-solving. During the 1960s and 1970s, AI researchers developed algorithms that could solve mathematical problems and understand simple natural language.

The field experienced cycles of optimism followed by disappointment and funding cuts, known as "AI winters." The first AI winter occurred in the 1970s when researchers faced the reality that many AI problems were more difficult than initially anticipated.

Machine Learning Fundamentals

Machine Learning is a subset of AI that focuses on developing algorithms that can learn from and make predictions based on data. Instead of explicitly programming rules, machine learning systems identify patterns in data and improve their performance with experience.

There are three main types of machine learning:

1. Supervised Learning: The algorithm learns from labeled training data, making predictions or decisions based on that learning.

2. Unsupervised Learning: The algorithm finds patterns or structures in unlabeled data.

3. Reinforcement Learning: The algorithm learns by interacting with an environment, receiving rewards or penalties for its actions.

Neural Networks and Deep Learning

Neural networks are computing systems inspired by the biological neural networks in animal brains. They consist of interconnected nodes or "neurons" that process and transmit information.

Deep Learning is a subset of machine learning that uses neural networks with many layers (hence "deep"). These deep neural networks have revolutionized fields such as computer vision, natural language processing, and speech recognition.

Applications of AI in Modern Society

AI has numerous applications across various sectors:

Healthcare: AI systems can analyze medical images, predict disease outbreaks, and assist in drug discovery.

Finance: AI algorithms detect fraudulent transactions, automate trading, and provide personalized financial advice.

Transportation: Self-driving cars use AI to navigate and make decisions on the road.

Entertainment: Streaming services use AI to recommend content based on user preferences.

Education: AI tutoring systems provide personalized learning experiences.

Ethical Considerations in AI

As AI becomes more integrated into society, ethical considerations become increasingly important:

Bias and Fairness: AI systems can perpetuate or amplify existing biases in their training data.

Privacy: AI systems often require large amounts of data, raising concerns about privacy and data protection.

Accountability: Determining responsibility when AI systems make mistakes is challenging.

Job Displacement: Automation through AI may lead to job losses in certain sectors.

Future of Artificial Intelligence

The future of AI holds both promise and challenges. Researchers are working on developing more advanced AI systems, including:

Artificial General Intelligence (AGI): Systems that possess the ability to understand, learn, and apply knowledge across a wide range of tasks at a human level.

Explainable AI: Making AI systems more transparent and interpretable.

AI Ethics and Governance: Establishing frameworks to ensure AI is developed and used responsibly.

As AI continues to evolve, collaboration between technologists, policymakers, ethicists, and the public will be essential to harness its benefits while mitigating potential risks.
"""
    
    topic_text = """
Neural Networks and Deep Learning

Neural networks are computing systems inspired by the biological neural networks in animal brains. They consist of interconnected nodes or "neurons" that process and transmit information.

Deep Learning is a subset of machine learning that uses neural networks with many layers (hence "deep"). These deep neural networks have revolutionized fields such as computer vision, natural language processing, and speech recognition.
"""
    
    return full_text, topic_text
