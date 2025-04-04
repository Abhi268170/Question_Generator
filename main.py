"""
Main application entry point for the PDF Question Generator system.
"""

import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
from app.question_generator import QuestionGenerator, QuestionMonitor
from app.llm_integration.llm_integration import LLMIntegration
from app.llm_integration.llm_models import LLMModels
from app.web_interface import create_app

def main():
    """
    Main entry point for the application.
    """
    # Create the Flask application
    app = create_app()
    
    # Initialize the question generator and monitor
    question_generator = QuestionGenerator(model_name="gemma3")
    question_monitor = QuestionMonitor()
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(__file__), 'logs'), exist_ok=True)
    
    # Register the question generator and monitor with the app
    app.config['QUESTION_GENERATOR'] = question_generator
    app.config['QUESTION_MONITOR'] = question_monitor
    
    # Get available LLM models
    llm_integration = LLMIntegration()
    app.config['AVAILABLE_MODELS'] = llm_integration.available_models
    app.config['RECOMMENDED_MODELS'] = llm_integration.list_recommended_models()
    
    # Run the application
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()
