"""
Question Generator Module

This module integrates PDF processing, vector storage, and LLM components
to generate questions from PDF documents based on specified parameters.
"""

import os
import time
import math
from typing import List, Dict, Any, Optional, Union
from app.pdf_processor import PDFProcessor
from app.vector_storage import VectorStorage
from app.llm_integration import LLMIntegration

class QuestionGenerator:
    """
    A class for generating questions from PDF documents based on specified parameters.
    """
    
    def __init__(self, model_name: str = "llama3"):
        """
        Initialize the question generator with component instances.
        
        Args:
            model_name: Name of the Ollama model to use
        """
        self.pdf_processor = PDFProcessor(chunk_size=2000, chunk_overlap=50)  # Using optimized values
        self.vector_storage = VectorStorage(max_features=5000)  # Using optimized values
        self.llm_integration = LLMIntegration(model_name=model_name)
    
    def process_pdf(self, pdf_path: str, topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a PDF file and prepare it for question generation.
        
        Args:
            pdf_path: Path to the PDF file
            topic: Optional topic to filter content by
            
        Returns:
            Dictionary containing processed PDF data
        """
        # Process the PDF to extract text and chunks
        pdf_data = self.pdf_processor.process_pdf(pdf_path, topic)
        
        # Fit the vector storage on the chunks
        self.vector_storage.fit(pdf_data["chunks"])
        
        return pdf_data
    
    def generate_questions(
        self,
        pdf_path: str,
        question_type: str,
        num_questions: int = 10,
        topic: Optional[str] = None,
        difficulty: str = "medium",
        language: str = "English",
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate questions from a PDF document based on specified parameters.
        
        Args:
            pdf_path: Path to the PDF file
            question_type: Type of questions to generate (multiple_choice, multiple_selection, true_false, short_answer)
            num_questions: Number of questions to generate
            topic: Optional topic to filter content by
            difficulty: Difficulty level (low, medium, high)
            language: Language to generate questions in
            temperature: Temperature parameter for generation
            
        Returns:
            Dictionary containing generated questions and metadata
        """
        # Process the PDF
        pdf_data = self.process_pdf(pdf_path, topic)
        
        # For large documents, we need to extract multiple content sections
        # to provide enough context for generating the requested number of questions
        content_sections = self._extract_content_sections(pdf_data, topic, num_questions)
        
        # Generate questions using the LLM with multiple content sections if needed
        all_raw_questions = []
        
        # Calculate questions per section
        questions_per_section = math.ceil(num_questions / len(content_sections))
        
        # Generate questions for each content section
        for section in content_sections:
            # Generate questions for this section
            section_questions = self.llm_integration.generate_questions(
                content=section,
                question_type=question_type,
                num_questions=questions_per_section,
                difficulty=difficulty,
                language=language,
                topic=topic or "general",
                temperature=temperature
            )
            
            # Add to our collection, avoiding duplicates
            existing_question_texts = {q["question_text"] for q in all_raw_questions}
            for question in section_questions:
                if question["question_text"] not in existing_question_texts:
                    all_raw_questions.append(question)
                    existing_question_texts.add(question["question_text"])
            
            # If we've reached or exceeded the requested number, stop
            if len(all_raw_questions) >= num_questions:
                break
        
        # Limit to the requested number
        all_raw_questions = all_raw_questions[:num_questions]
        
        # Filter questions for quality
        filtered_questions = self.llm_integration.filter_questions(all_raw_questions, " ".join(content_sections))
        
        # Prepare the result
        result = {
            "questions": filtered_questions,
            "metadata": {
                "pdf_filename": os.path.basename(pdf_path),
                "question_type": question_type,
                "topic": topic,
                "difficulty": difficulty,
                "language": language,
                "requested_count": num_questions,
                "generated_count": len(all_raw_questions),
                "filtered_count": len(filtered_questions),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        return result
    
    def _extract_content_sections(self, pdf_data: Dict[str, Any], topic: Optional[str], num_questions: int) -> List[str]:
        """
        Extract content sections from the PDF data for question generation.
        
        Args:
            pdf_data: Processed PDF data
            topic: Optional topic to filter content by
            num_questions: Number of questions to generate
            
        Returns:
            List of content sections
        """
        # Determine how many sections we need based on the number of questions
        # Each section can generate about 10-15 questions
        num_sections = max(1, math.ceil(num_questions / 10))
        
        # If a topic is specified, retrieve relevant content
        if topic and topic.strip():
            # Get more chunks for more questions
            k = min(5 * num_sections, len(pdf_data["chunks"]))
            
            # Retrieve relevant chunks
            content = self.vector_storage.retrieve_for_topic(topic, k=k)
            
            # If no relevant content found, use the full text
            if not content:
                # Split the full text into sections
                return self._split_text_into_sections(pdf_data["full_text"], num_sections)
            
            # If we have content but need multiple sections, split it
            if num_sections > 1:
                return self._split_text_into_sections(content, num_sections)
            
            return [content]
        else:
            # Use the full text split into sections
            return self._split_text_into_sections(pdf_data["full_text"], num_sections)
    
    def _split_text_into_sections(self, text: str, num_sections: int) -> List[str]:
        """
        Split text into multiple sections for question generation.
        
        Args:
            text: Text to split
            num_sections: Number of sections to create
            
        Returns:
            List of text sections
        """
        # Maximum length per section to avoid token limits
        max_section_length = 4000
        
        # If the text is short enough, just return it as a single section
        if len(text) <= max_section_length:
            return [text]
        
        # Calculate section length
        section_length = min(max_section_length, len(text) // num_sections)
        
        # Create sections with some overlap
        sections = []
        for i in range(num_sections):
            start = i * section_length
            # Add some overlap between sections
            if i > 0:
                start = max(0, start - 200)
            
            end = min(len(text), start + section_length)
            
            # Try to end at a sentence boundary
            if end < len(text):
                # Look for sentence endings (.!?) followed by a space or newline
                for j in range(end, max(start, end - 100), -1):
                    if j < len(text) and text[j] in ".!?" and (j + 1 == len(text) or text[j + 1].isspace()):
                        end = j + 1
                        break
            
            sections.append(text[start:end])
            
            # If we've reached the end of the text, stop
            if end >= len(text):
                break
        
        return sections
    
    def save_vector_storage(self, directory: str) -> None:
        """
        Save the vector storage to disk for later reuse.
        
        Args:
            directory: Directory to save the vector storage in
        """
        self.vector_storage.save(directory)
    
    def load_vector_storage(self, directory: str) -> None:
        """
        Load a previously saved vector storage from disk.
        
        Args:
            directory: Directory to load the vector storage from
        """
        self.vector_storage = VectorStorage.load(directory)
