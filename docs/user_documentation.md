# PDF Question Generator - User Documentation

## Overview

The PDF Question Generator is a powerful tool that processes PDF documents and generates structured questions based on the content. It uses artificial intelligence to create high-quality questions in various formats, making it ideal for educators, content creators, and anyone who needs to generate questions from textual content.

## Features

- **PDF Processing**: Upload any PDF document and extract its textual content
- **Topic Filtering**: Focus questions on specific topics within the document
- **Multiple Question Types**: Generate different types of questions:
  - Multiple Choice (single correct answer)
  - Multiple Selection (multiple correct answers)
  - True/False
  - Short Answer
- **Difficulty Levels**: Choose from low, medium, or high difficulty
- **Language Support**: Generate questions in multiple languages
- **Customizable**: Control the number of questions generated (up to 100)
- **Quality Assurance**: Built-in filtering ensures high-quality, relevant questions
- **Modern Interface**: Clean, responsive design for easy use on any device
- **Export Functionality**: Download generated questions in JSON format

## Getting Started

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/pdf-question-generator.git
   cd pdf-question-generator
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Install Ollama:
   Follow the instructions at [https://ollama.ai/](https://ollama.ai/) to install Ollama on your system.

4. Pull the required model:
   ```
   ollama pull llama3
   ```

5. Start the application:
   ```
   python main.py
   ```

6. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

### Using the Application

1. **Upload a PDF**:
   - Click the "Choose File" button and select a PDF document
   - The maximum file size is 16MB

2. **Configure Question Generation**:
   - Select the question type (Multiple Choice, Multiple Selection, True/False, or Short Answer)
   - Enter the number of questions to generate (1-100)
   - Optionally specify a topic to focus on
   - Select the difficulty level (Low, Medium, High)
   - Choose the language for the questions

3. **Generate Questions**:
   - Click the "Generate Questions" button
   - The system will process the PDF and generate questions
   - This may take a few moments depending on the size of the document

4. **View and Use Questions**:
   - Review the generated questions on the results page
   - Correct answers are highlighted
   - Click "Download JSON" to export the questions in JSON format
   - Click "Generate More Questions" to start over with a new document or different parameters

## Technical Requirements

- Python 3.10 or higher
- 4GB RAM minimum (8GB recommended)
- Ollama installed and running
- Internet connection (for initial setup only)

## Troubleshooting

### Common Issues

1. **PDF Not Loading**:
   - Ensure the PDF is not password-protected
   - Check that the file size is under 16MB
   - Try converting the PDF to a newer format if it's very old

2. **No Questions Generated**:
   - Check that the PDF contains extractable text (not just scanned images)
   - Try specifying a different topic that appears in the document
   - Increase the number of questions requested

3. **Ollama Connection Issues**:
   - Ensure Ollama is running on your system
   - Check that the llama3 model has been pulled correctly
   - Restart Ollama if it's unresponsive

4. **Application Not Starting**:
   - Verify all dependencies are installed correctly
   - Check that port 5000 is not in use by another application
   - Ensure you have sufficient disk space

### Getting Help

If you encounter issues not covered in this documentation, please:
1. Check the GitHub repository for known issues
2. Submit a detailed bug report including:
   - Steps to reproduce the issue
   - Error messages (if any)
   - System information
   - PDF document details (if relevant)

## Privacy and Data Handling

- All processing happens locally on your machine
- PDF documents and generated questions are not sent to external servers
- Uploaded PDFs are stored temporarily in the application's uploads folder
- Clear the uploads folder periodically to free up disk space

## License

This project is licensed under the MIT License - see the LICENSE file for details.
