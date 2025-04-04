"""
Web Interface Module

This module provides the Flask web application for the PDF Question Generator.
"""

import os
import json
import time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import FileField, SelectField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

def create_app():
    """
    Create and configure the Flask application.
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    
    # Configure upload folder
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
    app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
    
    # Define forms
    class UploadForm(FlaskForm):
        pdf_file = FileField('PDF File', validators=[DataRequired()])
        question_type = SelectField('Question Type', choices=[
            ('multiple_choice', 'Multiple Choice'),
            ('multiple_selection', 'Multiple Selection'),
            ('true_false', 'True/False'),
            ('short_answer', 'Short Answer')
        ], validators=[DataRequired()])
        num_questions = IntegerField('Number of Questions', validators=[
            DataRequired(),
            NumberRange(min=1, max=100, message='Please enter a number between 1 and 100')
        ], default=10)
        topic = StringField('Topic (optional)', validators=[Optional()])
        difficulty = SelectField('Difficulty', choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High')
        ], default='medium', validators=[DataRequired()])
        language = SelectField('Language', choices=[
            ('English', 'English'),
            ('Spanish', 'Spanish'),
            ('French', 'French'),
            ('German', 'German'),
            ('Chinese', 'Chinese')
        ], default='English', validators=[DataRequired()])
        model = SelectField('LLM Model', choices=[
            ('llama3', 'Llama 3 (Default)'),
            ('mistral', 'Mistral'),
            ('phi3', 'Phi-3'),
            ('gemma', 'Gemma'),
            ('neural-chat', 'Neural Chat')
        ], default='llama3', validators=[DataRequired()])
        submit = SubmitField('Generate Questions')
    
    # Helper functions
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
    
    # Routes
    @app.route('/', methods=['GET', 'POST'])
    def index():
        form = UploadForm()
        
        # Update model choices if available
        if 'RECOMMENDED_MODELS' in app.config:
            model_choices = [(model['name'], f"{model['name']} - {model['description']}") 
                            for model in app.config['RECOMMENDED_MODELS']]
            form.model.choices = model_choices
        
        if form.validate_on_submit():
            # Check if the post request has the file part
            if 'pdf_file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            
            file = request.files['pdf_file']
            
            # If user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                # Secure the filename and save the file
                filename = secure_filename(file.filename)
                timestamp = int(time.time())
                unique_filename = f"{timestamp}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                # Store form data in session
                session['file_path'] = file_path
                session['filename'] = filename
                session['question_type'] = form.question_type.data
                session['num_questions'] = form.num_questions.data
                session['topic'] = form.topic.data
                session['difficulty'] = form.difficulty.data
                session['language'] = form.language.data
                session['model'] = form.model.data
                
                # Redirect to processing page
                return redirect(url_for('processing'))
            else:
                flash('Invalid file type. Please upload a PDF file.')
        
        return render_template('index.html', form=form)
    
    @app.route('/processing')
    def processing():
        # Check if we have the necessary data in session
        if 'file_path' not in session:
            flash('No file uploaded')
            return redirect(url_for('index'))
        
        return render_template('processing.html', 
                              filename=session.get('filename', ''),
                              question_type=session.get('question_type', ''),
                              num_questions=session.get('num_questions', 0))
    
    @app.route('/generate', methods=['POST'])
    def generate():
        # Check if we have the necessary data in session
        if 'file_path' not in session:
            return jsonify({'error': 'No file uploaded'}), 400
        
        try:
            # Get the question generator
            question_generator = app.config.get('QUESTION_GENERATOR')
            if not question_generator:
                return jsonify({'error': 'Question generator not initialized'}), 500
            
            # Get the question monitor
            question_monitor = app.config.get('QUESTION_MONITOR')
            
            # Set the model if specified
            model = session.get('model', 'llama3')
            question_generator.llm_integration.set_model(model)
            
            # Generate questions
            result = question_generator.generate_questions(
                pdf_path=session.get('file_path'),
                question_type=session.get('question_type'),
                num_questions=session.get('num_questions', 10),
                topic=session.get('topic'),
                difficulty=session.get('difficulty', 'medium'),
                language=session.get('language', 'English')
            )
            
            # Log the generation with the monitor if available
            if question_monitor:
                question_monitor.log_generation(result['questions'], result['metadata'])
                
                # Analyze question quality
                quality_analysis = question_monitor.analyze_question_quality(result['questions'])
                result['quality_analysis'] = quality_analysis
            
            # Store the result in session
            session['result'] = result
            
            return jsonify({'success': True, 'redirect': url_for('results')})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/results')
    def results():
        # Check if we have results in session
        if 'result' not in session:
            flash('No questions generated')
            return redirect(url_for('index'))
        
        result = session.get('result')
        
        return render_template('results.html',
                              questions=result['questions'],
                              metadata=result['metadata'],
                              filename=session.get('filename', ''))
    
    @app.route('/monitor')
    def monitor():
        # Get the question monitor
        question_monitor = app.config.get('QUESTION_MONITOR')
        if not question_monitor:
            flash('Question monitor not initialized')
            return redirect(url_for('index'))
        
        # Get metrics and logs
        metrics = question_monitor.get_metrics()
        logs = question_monitor.get_recent_logs(limit=5)
        
        return render_template('monitor.html',
                              metrics=metrics,
                              logs=logs)
    
    @app.route('/download/<filename>')
    def download_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    return app
