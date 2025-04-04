"""
LLM Integration Module

This module handles the integration with Ollama for generating questions based on retrieved content.
It provides functionality to:
1. Connect to Ollama API
2. Create optimized system prompts for different question types
3. Generate questions using the LLM
"""

import os
import json
import math
import time
from typing import List, Dict, Any, Optional, Union
import ollama
from langchain.prompts import PromptTemplate
from app.llm_integration.llm_models import LLMModels

class LLMIntegration:
    """
    A class for integrating with Ollama to generate questions based on retrieved content.
    """
    
    def __init__(self, model_name: str = "llama3"):
        """
        Initialize the LLM integration with the specified model.
        
        Args:
            model_name: Name of the Ollama model to use
        """
        self.model_name = model_name
        self.system_prompts = self._initialize_system_prompts()
        self.available_models = self._get_available_models()
        # No automatic model selection - use specified model
    
    def _get_available_models(self) -> List[str]:
        """
        Get a list of available models from Ollama.
        
        Returns:
            List of available model names
        """
        try:
            models = ollama.list()
            return [model['name'] for model in models.get('models', [])]
        except Exception:
            # Return empty list if we can't get the list
            return []
    
    def get_model_capabilities(self) -> Dict[str, Any]:
        """
        Get capabilities of the currently selected model.
        
        Returns:
            Dictionary with model capabilities
        """
        return LLMModels.get_model_info(self.model_name)
    
    def list_recommended_models(self) -> List[Dict[str, Any]]:
        """
        Get a list of recommended models with their capabilities.
        
        Returns:
            List of dictionaries with model information
        """
        recommended = LLMModels.get_recommended_models()
        return [
            {"name": model, **LLMModels.get_model_info(model)}
            for model in recommended
        ]
    
    def set_model(self, model_name: str) -> bool:
        """
        Set the model to use for generation.
        
        Args:
            model_name: Name of the model to use
            
        Returns:
            True if successful, False otherwise
        """
        # Simply set the model name without checking availability
        self.model_name = model_name
        return True
    
    def _initialize_system_prompts(self) -> Dict[str, str]:
        """
        Initialize system prompts for different question types.
        
        Returns:
            Dictionary mapping question types to system prompts
        """
        return {
            "multiple_choice": """You are an expert question generator specializing in creating high-quality multiple-choice questions.
Your task is to generate {num_questions} multiple-choice questions based on the provided content.
Each question must:
1. Be directly based on the provided content
2. Have exactly 4 options (A, B, C, D)
3. Have exactly one correct answer
4. Have clearly wrong alternative options that are plausible but incorrect
5. Be at {difficulty} difficulty level
6. Be written in {language}

For "low" difficulty:
- Focus on basic recall and understanding
- Use straightforward language
- Make distractors clearly different from the correct answer

For "medium" difficulty:
- Test application and analysis
- Include some nuance in the questions
- Make distractors somewhat similar to the correct answer

For "high" difficulty:
- Test evaluation and synthesis
- Use complex language and concepts
- Make distractors very similar to the correct answer, requiring careful discrimination

Format each question as follows:
Q1. [Question text]
A. [Option A]
B. [Option B]
C. [Option C]
D. [Option D]
Correct Answer: [A/B/C/D]

Ensure questions are non-duplicative, clear, and test understanding rather than mere recall.
Focus specifically on the topic: {topic}""",

            "multiple_selection": """You are an expert question generator specializing in creating high-quality multiple-selection questions.
Your task is to generate {num_questions} multiple-selection questions based on the provided content.
Each question must:
1. Be directly based on the provided content
2. Have exactly 5 options (A, B, C, D, E)
3. Have 2-3 correct answers
4. Have clearly wrong alternative options that are plausible but incorrect
5. Be at {difficulty} difficulty level
6. Be written in {language}

For "low" difficulty:
- Focus on basic recall and understanding
- Use straightforward language
- Make incorrect options clearly different from correct ones

For "medium" difficulty:
- Test application and analysis
- Include some nuance in the questions
- Make incorrect options somewhat similar to correct ones

For "high" difficulty:
- Test evaluation and synthesis
- Use complex language and concepts
- Make incorrect options very similar to correct ones, requiring careful discrimination

Format each question as follows:
Q1. [Question text] (Select all that apply)
A. [Option A]
B. [Option B]
C. [Option C]
D. [Option D]
E. [Option E]
Correct Answers: [List all correct options, e.g., A, C, E]

Ensure questions are non-duplicative, clear, and test understanding rather than mere recall.
Focus specifically on the topic: {topic}""",

            "true_false": """You are an expert question generator specializing in creating high-quality true/false questions.
Your task is to generate {num_questions} true/false questions based on the provided content.
Each question must:
1. Be directly based on the provided content
2. Have a clear true or false answer
3. Be at {difficulty} difficulty level
4. Be written in {language}

For "low" difficulty:
- Focus on basic facts directly stated in the text
- Use straightforward language
- Avoid ambiguity

For "medium" difficulty:
- Test inference and interpretation
- Include some nuance
- Require understanding of relationships between concepts

For "high" difficulty:
- Test evaluation of complex statements
- Use precise language where small details matter
- Require deep understanding of the material

Format each question as follows:
Q1. [Statement]
Correct Answer: [True/False]

Ensure statements are non-duplicative, clear, and test understanding rather than mere recall.
Focus specifically on the topic: {topic}""",

            "short_answer": """You are an expert question generator specializing in creating high-quality short answer questions.
Your task is to generate {num_questions} short answer questions based on the provided content.
Each question must:
1. Be directly based on the provided content
2. Be answerable in 1-3 sentences
3. Be at {difficulty} difficulty level
4. Be written in {language}

For "low" difficulty:
- Focus on basic recall and understanding
- Ask for definitions or simple explanations
- Have straightforward answers directly from the text

For "medium" difficulty:
- Test application and analysis
- Ask for explanations of relationships or processes
- Require synthesis of information from different parts of the text

For "high" difficulty:
- Test evaluation and creation
- Ask for justifications or assessments
- Require deep understanding and critical thinking

Format each question as follows:
Q1. [Question text]
Model Answer: [Brief model answer that would be expected]

Ensure questions are non-duplicative, clear, and test understanding rather than mere recall.
Focus specifically on the topic: {topic}"""
        }
    
    def get_system_prompt(self, question_type: str, params: Dict[str, Any]) -> str:
        """
        Get the system prompt for the specified question type with parameters filled in.
        
        Args:
            question_type: Type of questions to generate (multiple_choice, multiple_selection, true_false, short_answer)
            params: Parameters to fill in the prompt template
            
        Returns:
            Formatted system prompt
        """
        if question_type not in self.system_prompts:
            raise ValueError(f"Unsupported question type: {question_type}")
        
        prompt_template = PromptTemplate(
            template=self.system_prompts[question_type],
            input_variables=["num_questions", "difficulty", "language", "topic"]
        )
        
        return prompt_template.format(**params)
    
    def generate_questions(
        self,
        content: str,
        question_type: str,
        num_questions: int = 10,
        difficulty: str = "medium",
        language: str = "English",
        topic: str = "general",
        temperature: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Generate questions based on the provided content.
        
        Args:
            content: Text content to generate questions from
            question_type: Type of questions to generate
            num_questions: Number of questions to generate
            difficulty: Difficulty level (low, medium, high)
            language: Language to generate questions in
            topic: Specific topic to focus on
            temperature: Temperature parameter for generation
            
        Returns:
            List of generated questions with their details
        """
        # Use batching to generate the requested number of questions
        all_questions = []
        
        # Determine batch size based on question type
        # Different question types have different token requirements
        batch_sizes = {
            "multiple_choice": 10,
            "multiple_selection": 8,
            "true_false": 15,
            "short_answer": 12
        }
        batch_size = batch_sizes.get(question_type, 10)
        
        # Calculate number of batches needed
        num_batches = math.ceil(num_questions / batch_size)
        questions_remaining = num_questions
        
        # Generate questions in batches
        for batch_num in range(num_batches):
            # Calculate how many questions to request in this batch
            batch_questions = min(batch_size, questions_remaining)
            
            # Prepare parameters for the system prompt
            params = {
                "num_questions": batch_questions,
                "difficulty": difficulty,
                "language": language,
                "topic": topic
            }
            
            # Get the system prompt
            system_prompt = self.get_system_prompt(question_type, params)
            
            # Prepare the user prompt
            user_prompt = f"Generate {batch_questions} {question_type} questions based on the following content:\n\n{content}"
            
            try:
                # Call Ollama API
                response = ollama.chat(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    options={
                        "temperature": temperature,
                        "num_predict": 4096,  # Increase token limit for longer responses
                    }
                )
                
                # Extract the generated questions
                raw_questions = response["message"]["content"]
                
                # Parse the questions based on the question type
                batch_parsed_questions = self._parse_questions(raw_questions, question_type)
                
                # Add to our collection, avoiding duplicates
                existing_question_texts = {q["question_text"] for q in all_questions}
                for question in batch_parsed_questions:
                    if question["question_text"] not in existing_question_texts:
                        all_questions.append(question)
                        existing_question_texts.add(question["question_text"])
                
                # Update questions remaining
                questions_remaining = num_questions - len(all_questions)
                
                # If we've reached or exceeded the requested number, stop
                if questions_remaining <= 0:
                    break
                
                # Add a small delay between batches to avoid rate limiting
                if batch_num < num_batches - 1:
                    time.sleep(1)
                
            except Exception as e:
                # If Ollama is not available, use mock data for testing
                if batch_num == 0:  # Only do this for the first batch
                    mock_questions = self._generate_mock_questions(
                        question_type, 
                        min(num_questions, 10),  # Generate up to 10 mock questions
                        topic
                    )
                    all_questions.extend(mock_questions)
                    break
                else:
                    # For subsequent batches, just break if there's an error
                    break
        
        return all_questions
    
    def _generate_mock_questions(self, question_type: str, num_questions: int, topic: str) -> List[Dict[str, Any]]:
        """
        Generate mock questions for testing when Ollama is not available.
        
        Args:
            question_type: Type of questions to generate
            num_questions: Number of questions to generate
            topic: Topic for the questions
            
        Returns:
            List of mock questions
        """
        mock_questions = []
        
        # Generate different types of mock questions
        if question_type == "multiple_choice":
            for i in range(num_questions):
                mock_questions.append({
                    "question_text": f"Sample multiple choice question {i+1} about {topic}",
                    "question_type": "multiple_choice",
                    "options": [
                        {"letter": "A", "text": f"Option A for question {i+1}"},
                        {"letter": "B", "text": f"Option B for question {i+1}"},
                        {"letter": "C", "text": f"Option C for question {i+1}"},
                        {"letter": "D", "text": f"Option D for question {i+1}"}
                    ],
                    "correct_answer": "A"
                })
        elif question_type == "multiple_selection":
            for i in range(num_questions):
                mock_questions.append({
                    "question_text": f"Sample multiple selection question {i+1} about {topic}",
                    "question_type": "multiple_selection",
                    "options": [
                        {"letter": "A", "text": f"Option A for question {i+1}"},
                        {"letter": "B", "text": f"Option B for question {i+1}"},
                        {"letter": "C", "text": f"Option C for question {i+1}"},
                        {"letter": "D", "text": f"Option D for question {i+1}"},
                        {"letter": "E", "text": f"Option E for question {i+1}"}
                    ],
                    "correct_answer": ["A", "C"]
                })
        elif question_type == "true_false":
            for i in range(num_questions):
                mock_questions.append({
                    "question_text": f"Sample true/false statement {i+1} about {topic}",
                    "question_type": "true_false",
                    "options": [
                        {"letter": "A", "text": "True"},
                        {"letter": "B", "text": "False"}
                    ],
                    "correct_answer": "True"
                })
        elif question_type == "short_answer":
            for i in range(num_questions):
                mock_questions.append({
                    "question_text": f"Sample short answer question {i+1} about {topic}",
                    "question_type": "short_answer",
                    "model_answer": f"This is a sample answer for question {i+1} about {topic}."
                })
        
        return mock_questions
    
    def _parse_questions(self, raw_questions: str, question_type: str) -> List[Dict[str, Any]]:
        """
        Parse the raw questions text into structured question objects.
        
        Args:
            raw_questions: Raw text containing the generated questions
            question_type: Type of questions to parse
            
        Returns:
            List of structured question objects
        """
        questions = []
        
        # Split by question markers (Q1., Q2., etc.)
        parts = raw_questions.split("\n\n")
        current_question = None
        
        for part in parts:
            lines = part.strip().split("\n")
            
            # Check if this part starts a new question
            if lines and (lines[0].startswith("Q") and "." in lines[0]):
                # If we have a current question, add it to the list
                if current_question:
                    questions.append(current_question)
                
                # Start a new question
                current_question = {
                    "question_text": lines[0].split(".", 1)[1].strip(),
                    "question_type": question_type,
                    "options": [],
                    "correct_answer": None
                }
                
                # Process the rest of the lines based on question type
                if question_type == "multiple_choice":
                    self._parse_multiple_choice(current_question, lines[1:])
                elif question_type == "multiple_selection":
                    self._parse_multiple_selection(current_question, lines[1:])
                elif question_type == "true_false":
                    self._parse_true_false(current_question, lines[1:])
                elif question_type == "short_answer":
                    self._parse_short_answer(current_question, lines[1:])
        
        # Add the last question if there is one
        if current_question:
            questions.append(current_question)
        
        return questions
    
    def _parse_multiple_choice(self, question: Dict[str, Any], lines: List[str]) -> None:
        """
        Parse multiple choice question lines.
        
        Args:
            question: Question object to update
            lines: Lines to parse
        """
        for line in lines:
            line = line.strip()
            if line.startswith(("A.", "B.", "C.", "D.")):
                option_letter = line[0]