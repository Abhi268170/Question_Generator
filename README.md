# PDF Question Generator

A Python-based Corrective Retrieval-Augmented Generation System for generating structured questions from PDF documents.

## Features

- **PDF Processing & Chunking**: Intelligently extracts and chunks text from PDFs with context preservation
- **Vector Storage & Retrieval**: Uses FAISS and TF-IDF for efficient similarity search and retrieval
- **LLM Integration**: Connects to locally hosted LLM via Ollama
- **Question Generation**: Creates high-quality questions with filtering for accuracy
- **Modern Web Interface**: Clean, responsive design for easy interaction
- **Multiple Question Types**: Supports multiple choice, multiple selection, true/false, and short answer
- **Difficulty Levels**: Supports low, medium, and high difficulty settings
- **Language Support**: Generate questions in multiple languages

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pdf-question-generator.git
cd pdf-question-generator
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Install Ollama:
Follow the instructions at [https://ollama.ai/](https://ollama.ai/) to install Ollama on your system.

4. Pull the required model:
```bash
ollama pull llama3
```

## Usage

1. Start the application:
```bash
python main.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Upload a PDF, select parameters, and generate questions.

## Project Structure

```
pdf_question_generator/
├── app/
│   ├── pdf_processor/       # PDF text extraction and chunking
│   ├── vector_storage/      # Vector storage and retrieval using FAISS
│   ├── llm_integration/     # Integration with Ollama
│   ├── question_generator/  # Question generation orchestration
│   └── web_interface/       # Flask web application
├── docs/                    # Documentation
├── main.py                  # Application entry point
├── optimize_system.py       # Performance optimization script
├── test_system.py           # System tests
└── requirements.txt         # Dependencies
```

## Documentation

- [User Documentation](docs/user_documentation.md)
- [Technical Documentation](docs/technical_documentation.md)

## Requirements

- Python 3.10 or higher
- 4GB RAM minimum (8GB recommended)
- Ollama installed and running

## License

This project is licensed under the MIT License - see the LICENSE file for details.
