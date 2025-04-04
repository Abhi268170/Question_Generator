"""
Question Monitoring Module

This module provides functionality to monitor and analyze generated questions
for quality, correctness, and relevance.
"""

import os
import json
import time
import requests
from typing import List, Dict, Any, Optional, Union
import numpy as np
from collections import Counter

class QuestionMonitor:
    """
    A class for monitoring and analyzing generated questions.
    """
    
    def __init__(self, log_dir: str = None):
        """
        Initialize the question monitor.
        
        Args:
            log_dir: Directory to store question logs
        """
        self.log_dir = log_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Initialize metrics
        self.metrics = {
            "total_questions_generated": 0,
            "questions_by_type": Counter(),
            "questions_by_difficulty": Counter(),
            "questions_by_language": Counter(),
            "average_options_per_question": 0,
            "average_question_length": 0,
            "generation_success_rate": 0,
            "filter_pass_rate": 0
        }
    
    def log_generation(self, questions: List[Dict[str, Any]], metadata: Dict[str, Any]) -> str:
        """
        Log a batch of generated questions and update metrics.
        
        Args:
            questions: List of generated questions
            metadata: Metadata about the generation
            
        Returns:
            Path to the log file
        """
        # Create a log entry
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "metadata": metadata,
            "questions": questions,
            "metrics": self._calculate_metrics(questions, metadata)
        }
        
        # Create a filename based on timestamp
        filename = f"questions_{time.strftime('%Y%m%d_%H%M%S')}.json"
        log_path = os.path.join(self.log_dir, filename)
        
        # Write the log to file
        with open(log_path, 'w') as f:
            json.dump(log_entry, f, indent=2)
        
        # Update overall metrics
        self._update_metrics(log_entry["metrics"])
        
        return log_path
    
    def _calculate_metrics(self, questions: List[Dict[str, Any]], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate metrics for a batch of questions.
        
        Args:
            questions: List of questions
            metadata: Metadata about the generation
            
        Returns:
            Dictionary of metrics
        """
        metrics = {}
        
        # Basic counts
        metrics["question_count"] = len(questions)
        metrics["question_type"] = metadata.get("question_type", "unknown")
        metrics["difficulty"] = metadata.get("difficulty", "unknown")
        metrics["language"] = metadata.get("language", "unknown")
        
        # Success rates
        metrics["generation_success_rate"] = len(questions) / metadata.get("requested_count", 1) if metadata.get("requested_count", 0) > 0 else 0
        metrics["filter_pass_rate"] = len(questions) / metadata.get("generated_count", 1) if metadata.get("generated_count", 0) > 0 else 0
        
        # Question characteristics
        if questions:
            # Average question length
            question_lengths = [len(q.get("question_text", "")) for q in questions]
            metrics["average_question_length"] = sum(question_lengths) / len(questions)
            metrics["min_question_length"] = min(question_lengths)
            metrics["max_question_length"] = max(question_lengths)
            
            # Options analysis (for multiple choice/selection)
            if metadata.get("question_type") in ["multiple_choice", "multiple_selection"]:
                option_counts = [len(q.get("options", [])) for q in questions]
                metrics["average_options_per_question"] = sum(option_counts) / len(questions) if option_counts else 0
                
                # Analyze option diversity
                option_lengths = []
                for q in questions:
                    if "options" in q:
                        option_lengths.extend([len(opt.get("text", "")) for opt in q.get("options", [])])
                
                if option_lengths:
                    metrics["average_option_length"] = sum(option_lengths) / len(option_lengths)
                    metrics["min_option_length"] = min(option_lengths)
                    metrics["max_option_length"] = max(option_lengths)
        
        return metrics
    
    def _update_metrics(self, batch_metrics: Dict[str, Any]) -> None:
        """
        Update overall metrics with a new batch.
        
        Args:
            batch_metrics: Metrics from a new batch
        """
        # Update counters
        self.metrics["total_questions_generated"] += batch_metrics.get("question_count", 0)
        self.metrics["questions_by_type"][batch_metrics.get("question_type", "unknown")] += batch_metrics.get("question_count", 0)
        self.metrics["questions_by_difficulty"][batch_metrics.get("difficulty", "unknown")] += batch_metrics.get("question_count", 0)
        self.metrics["questions_by_language"][batch_metrics.get("language", "unknown")] += batch_metrics.get("question_count", 0)
        
        # Update averages (weighted by question count)
        count = batch_metrics.get("question_count", 0)
        if count > 0:
            total = self.metrics["total_questions_generated"]
            prev_total = total - count
            
            # Helper function for weighted average update
            def update_avg(metric_name, new_value):
                if prev_total > 0:
                    prev_avg = self.metrics[metric_name]
                    self.metrics[metric_name] = (prev_avg * prev_total + new_value * count) / total
                else:
                    self.metrics[metric_name] = new_value
            
            # Update averages
            update_avg("average_question_length", batch_metrics.get("average_question_length", 0))
            update_avg("average_options_per_question", batch_metrics.get("average_options_per_question", 0))
            update_avg("generation_success_rate", batch_metrics.get("generation_success_rate", 0))
            update_avg("filter_pass_rate", batch_metrics.get("filter_pass_rate", 0))
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get the current metrics.
        
        Returns:
            Dictionary of metrics
        """
        return self.metrics
    
    def get_recent_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recent question logs.
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of log entries
        """
        log_files = sorted([f for f in os.listdir(self.log_dir) if f.startswith("questions_") and f.endswith(".json")], reverse=True)
        
        logs = []
        for filename in log_files[:limit]:
            try:
                with open(os.path.join(self.log_dir, filename), 'r') as f:
                    logs.append(json.load(f))
            except Exception as e:
                print(f"Error loading log file {filename}: {e}")
        
        return logs
    
    def verify_question_accuracy(self, question: Dict[str, Any], content: str = None) -> Dict[str, Any]:
        """
        Verify the accuracy of a question using web search if needed.
        
        Args:
            question: Question to verify
            content: Original content to check against
            
        Returns:
            Dictionary with verification results
        """
        result = {
            "question_id": id(question),
            "question_text": question.get("question_text", ""),
            "verified": False,
            "confidence": 0.0,
            "verification_method": "none",
            "verification_details": {}
        }
        
        # First try to verify against the content
        if content:
            content_verification = self._verify_against_content(question, content)
            result["verification_method"] = "content"
            result["verified"] = content_verification["verified"]
            result["confidence"] = content_verification["confidence"]
            result["verification_details"] = content_verification
            
            # If we're confident enough, return the result
            if result["confidence"] >= 0.8:
                return result
        
        # If we couldn't verify against the content or confidence is low, try web search
        try:
            web_verification = self._verify_with_web_search(question)
            
            # If web verification has higher confidence, use it
            if web_verification["confidence"] > result["confidence"]:
                result["verification_method"] = "web"
                result["verified"] = web_verification["verified"]
                result["confidence"] = web_verification["confidence"]
                result["verification_details"] = web_verification
        except Exception as e:
            # If web verification fails, add error to details
            result["verification_details"]["web_error"] = str(e)
        
        return result
    
    def _verify_against_content(self, question: Dict[str, Any], content: str) -> Dict[str, Any]:
        """
        Verify a question against the original content.
        
        Args:
            question: Question to verify
            content: Original content
            
        Returns:
            Dictionary with verification results
        """
        result = {
            "verified": False,
            "confidence": 0.0,
            "content_matches": []
        }
        
        # Convert to lowercase for case-insensitive matching
        question_text = question.get("question_text", "").lower()
        content_lower = content.lower()
        
        # Extract important words (longer than 4 chars)
        words = question_text.split()
        important_words = [w for w in words if len(w) > 4 and w.isalpha()]
        
        # Check for matches in content
        matches = []
        for word in important_words:
            if word in content_lower:
                # Find the context around the match
                index = content_lower.find(word)
                start = max(0, index - 50)
                end = min(len(content_lower), index + len(word) + 50)
                context = content[start:end]
                matches.append({"word": word, "context": context})
        
        result["content_matches"] = matches
        
        # Calculate confidence based on matches
        if important_words:
            match_ratio = len(matches) / len(important_words)
            result["confidence"] = match_ratio
            
            # If more than 70% of important words match, consider it verified
            if match_ratio > 0.7:
                result["verified"] = True
        
        return result
    
    def _verify_with_web_search(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify a question using web search.
        
        Args:
            question: Question to verify
            
        Returns:
            Dictionary with verification results
        """
        result = {
            "verified": False,
            "confidence": 0.0,
            "search_results": []
        }
        
        # This is a placeholder for web search verification
        # In a real implementation, you would:
        # 1. Extract key terms from the question
        # 2. Perform a web search
        # 3. Analyze search results to verify the question
        
        # For now, we'll just simulate this with a random confidence
        # In a real implementation, replace this with actual web search logic
        import random
        result["confidence"] = random.uniform(0.5, 0.9)
        result["verified"] = result["confidence"] > 0.7
        result["search_results"] = [
            {"title": "Example search result 1", "snippet": "This is a simulated search result."},
            {"title": "Example search result 2", "snippet": "Another simulated search result."}
        ]
        
        return result
    
    def analyze_question_quality(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze the quality of a batch of questions.
        
        Args:
            questions: List of questions to analyze
            
        Returns:
            Dictionary with quality analysis
        """
        if not questions:
            return {"overall_quality": 0, "details": {}}
        
        analysis = {
            "overall_quality": 0,
            "question_type_distribution": {},
            "average_question_length": 0,
            "option_quality": {},
            "difficulty_analysis": {},
            "improvement_suggestions": []
        }
        
        # Calculate question type distribution
        question_types = [q.get("question_type", "unknown") for q in questions]
        type_counter = Counter(question_types)
        total = len(questions)
        analysis["question_type_distribution"] = {k: v/total for k, v in type_counter.items()}
        
        # Calculate average question length
        question_lengths = [len(q.get("question_text", "")) for q in questions]
        analysis["average_question_length"] = sum(question_lengths) / len(questions)
        
        # Analyze options for multiple choice/selection questions
        mc_questions = [q for q in questions if q.get("question_type") in ["multiple_choice", "multiple_selection"]]
        if mc_questions:
            # Calculate option lengths
            option_lengths = []
            for q in mc_questions:
                if "options" in q:
                    option_lengths.extend([len(opt.get("text", "")) for opt in q.get("options", [])])
            
            if option_lengths:
                analysis["option_quality"] = {
                    "average_length": sum(option_lengths) / len(option_lengths),
                    "min_length": min(option_lengths),
                    "max_length": max(option_lengths),
                    "length_variance": np.var(option_lengths) if len(option_lengths) > 1 else 0
                }
                
                # Check for very short options (potential quality issue)
                short_options = [l for l in option_lengths if l < 5]
                if short_options:
                    analysis["improvement_suggestions"].append(
                        f"Found {len(short_options)} very short options (less than 5 characters). Consider making options more descriptive."
                    )
        
        # Calculate overall quality score (0-100)
        quality_score = 0
        
        # Factor 1: Question length (ideal range: 30-150 chars)
        avg_length = analysis["average_question_length"]
        if avg_length < 20:
            length_score = avg_length / 20 * 25  # Scale up to 25 points max
        elif avg_length > 200:
            length_score = max(0, 25 - (avg_length - 200) / 100 * 10)  # Penalize very long questions
        else:
            length_score = 25  # Full points for ideal length
        
        quality_score += length_score
        
        # Factor 2: Option quality for MC questions
        if "option_quality" in analysis:
            option_length = analysis["option_quality"]["average_length"]
            length_variance = analysis["option_quality"]["length_variance"]
            
            # Score for option length (ideal: 10-50 chars)
            if option_length < 5:
                option_length_score = option_length / 5 * 15
            elif option_length > 100:
                option_length_score = max(0, 15 - (option_length - 100) / 50 * 5)
            else:
                option_length_score = 15
            
            # Score for variance (some variance is good, too much is bad)
            if length_variance < 5:
                variance_score = length_variance / 5 * 10
            elif length_variance > 500:
                variance_score = max(0, 10 - (length_variance - 500) / 500 * 5)
            else:
                variance_score = 10
            
            quality_score += option_length_score + variance_score
        else:
            # If no MC questions, give average points for this factor
            quality_score += 15
        
        # Factor 3: Question type diversity (more diverse is better)
        diversity_score = min(25, len(analysis["question_type_distribution"]) * 6.25)
        quality_score += diversity_score
        
        # Factor 4: Basic structural quality
        structure_score = 0
        valid_count = 0
        for q in questions:
            if self._is_structurally_valid(q):
                valid_count += 1
        
        structure_score = (valid_count / len(questions)) * 25
        quality_score += structure_score
        
        # Set the overall quality
        analysis["overall_quality"] = round(quality_score)
        
        # Add quality breakdown
        analysis["quality_breakdown"] = {
            "question_length_score": round(length_score, 1),
            "option_quality_score": round(option_length_score + variance_score, 1) if "option_quality" in analysis else "N/A",
            "diversity_score": round(diversity_score, 1),
            "structure_score": round(structure_score, 1)
        }
        
        # Generate improvement suggestions
        if analysis["overall_quality"] < 60:
            analysis["improvement_suggestions"].append(
                "Overall quality is low. Consider reviewing the question generation parameters and prompts."
            )
        
        if length_score < 15:
            if avg_length < 20:
                analysis["improvement_suggestions"].append(
                    "Questions are too short. Consider adjusting prompts to generate more detailed questions."
                )
            else:
                analysis["improvement_suggestions"].append(
                    "Questions are too long. Consider adjusting prompts to generate more concise questions."
                )
        
        if "option_quality" in analysis and option_length_score + variance_score < 15:
            analysis["improvement_suggestions"].append(
                "Option quality could be improved. Ensure options are descriptive and have appropriate length."
            )
        
        if diversity_score < 15:
            analysis["improvement_suggestions"].append(
                "Question type diversity is low. Consider generating a mix of different question types."
            )
        
        if structure_score < 20:
            analysis["improvement_suggestions"].append(
                "Some questions have structural issues. Check for missing options or answers."
            )
        
        return analysis
    
    def _is_structurally_valid(self, question: Dict[str, Any]) -> bool:
        """
        Check if a question is structurally valid.
        
        Args:
            question: Question to check
            
        Returns:
            True if valid, False otherwise
        """
        # Check basic structure
        if not question.get("question_text") or not question.get("question_type"):
            return False
            
        # Check type-specific requirements
        if question["question_type"] in ["multiple_choice", "multiple_selection"]:
            if not question.get("options") or not question.get("correct_answer"):
                return False
                
            # For multiple choice, ensure we have exactly 4 options
            if question["question_type"] == "multiple_choice" and len(question.get("options", [])) != 4:
                return False
                
            # For multiple selection, ensure we have exactly 5 options
            if question["question_type"] == "multiple_selection" and len(question.get("options", [])) != 5:
                return False
                
        elif question["question_type"] == "true_false":
            if not question.get("correct_answer"):
                return False
                
        elif question["question_type"] == "short_answer":
            if not question.get("model_answer"):
                return False
                
        return True
