"""
LLM Models Module

This module provides information about available LLM models and their capabilities.
"""

from typing import List, Dict, Any

class LLMModels:
    """
    A class for managing information about LLM models.
    """
    
    # Model capabilities ratings (1-5 scale)
    MODEL_CAPABILITIES = {
        # Base models
        "llama3": {
            "question_quality": 3,
            "reasoning": 3,
            "knowledge": 3,
            "speed": 4,
            "size": "medium",
            "description": "Default model with balanced capabilities"
        },
        "mistral": {
            "question_quality": 4,
            "reasoning": 4,
            "knowledge": 3,
            "speed": 3,
            "size": "medium",
            "description": "Strong reasoning and instruction following"
        },
        "phi3": {
            "question_quality": 4,
            "reasoning": 4,
            "knowledge": 3,
            "speed": 5,
            "size": "small",
            "description": "Lightweight model with excellent reasoning"
        },
        "gemma": {
            "question_quality": 3,
            "reasoning": 3,
            "knowledge": 3,
            "speed": 4,
            "size": "small",
            "description": "Efficient model with good performance"
        },
        "neural-chat": {
            "question_quality": 4,
            "reasoning": 3,
            "knowledge": 4,
            "speed": 3,
            "size": "medium",
            "description": "Optimized for conversational tasks"
        },
        # Specialized models
        "llama3:8b": {
            "question_quality": 3,
            "reasoning": 3,
            "knowledge": 3,
            "speed": 5,
            "size": "small",
            "description": "Smaller, faster version of Llama 3"
        },
        "mistral:7b": {
            "question_quality": 3,
            "reasoning": 4,
            "knowledge": 3,
            "speed": 4,
            "size": "small",
            "description": "Compact version with strong reasoning"
        },
        "phi3:mini": {
            "question_quality": 3,
            "reasoning": 3,
            "knowledge": 2,
            "speed": 5,
            "size": "tiny",
            "description": "Very small and fast model"
        },
        "gemma:2b": {
            "question_quality": 2,
            "reasoning": 2,
            "knowledge": 2,
            "speed": 5,
            "size": "tiny",
            "description": "Extremely lightweight model"
        },
        "neural-chat:7b": {
            "question_quality": 4,
            "reasoning": 3,
            "knowledge": 3,
            "speed": 4,
            "size": "small",
            "description": "Smaller version optimized for chat"
        }
    }
    
    @classmethod
    def get_recommended_models(cls) -> List[str]:
        """
        Get a list of recommended models for question generation.
        
        Returns:
            List of recommended model names
        """
        return [
            "phi3",          # Best balance of quality and speed
            "mistral",       # Good for complex questions
            "neural-chat",   # Good for conversational style
            "llama3",        # Default option
            "gemma"          # Lightweight option
        ]
    
    @classmethod
    def get_model_info(cls, model_name: str) -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary with model information
        """
        return cls.MODEL_CAPABILITIES.get(model_name, cls.MODEL_CAPABILITIES["llama3"])
    
    @classmethod
    def get_best_model_for_task(cls, available_models: List[str], task: str = "question_generation") -> str:
        """
        Get the best available model for a specific task.
        
        Args:
            available_models: List of available model names
            task: Task to get the best model for
            
        Returns:
            Name of the best model
        """
        if not available_models:
            return "llama3"  # Default fallback
        
        # For question generation, prioritize models with high question_quality
        if task == "question_generation":
            # Filter to models we have capability data for
            known_models = [m for m in available_models if m in cls.MODEL_CAPABILITIES]
            
            if not known_models:
                return available_models[0]  # Use first available if none are known
            
            # Sort by question quality (higher is better)
            sorted_models = sorted(
                known_models,
                key=lambda m: cls.MODEL_CAPABILITIES[m]["question_quality"],
                reverse=True
            )
            
            return sorted_models[0]
        
        # Default to first available model
        return available_models[0]
