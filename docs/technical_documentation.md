# PDF Question Generator - Technical Documentation

## Architecture Overview

The PDF Question Generator is built with a modular architecture that separates concerns and allows for easy maintenance and extension. The system consists of the following main components:

1. **PDF Processor**: Handles PDF text extraction and intelligent chunking
2. **Vector Storage**: Manages text vectorization and similarity search using FAISS
3. **LLM Integration**: Connects to Ollama for question generation
4. **Question Generator**: Orchestrates the entire process
5. **Web Interface**: Provides a user-friendly interface using Flask

## System Components

### PDF Processor

The PDF Processor module (`app/pdf_processor`) is responsible for:
- Extracting text from PDF documents using PyPDF2
- Cleaning and normalizing the extracted text
- Intelligently chunking the text to preserve context
- Filtering content based on specified topics

Key classes:
- `PDFProcessor`: Main class that handles all PDF processing operations

### Vector Storage

The Vector Storage module (`app/vector_storage`) is responsible for:
- Converting text chunks to vector representations using TF-IDF
- Storing vectors in a FAISS index for efficient similarity search
- Retrieving the most relevant chunks based on a query
- Combining retrieved chunks into a cohesive text block

Key classes:
- `VectorStorage`: Main class that handles vectorization and retrieval operations

### LLM Integration

The LLM Integration module (`app/llm_integration`) is responsible for:
- Connecting to the Ollama API
- Creating optimized system prompts for different question types
- Generating questions using the LLM
- Parsing and filtering the generated questions

Key classes:
- `LLMIntegration`: Main class that handles all LLM operations

### Question Generator

The Question Generator module (`app/question_generator`) is responsible for:
- Orchestrating the entire question generation process
- Coordinating between PDF processing, vector storage, and LLM integration
- Managing the generation pipeline from PDF to questions

Key classes:
- `QuestionGenerator`: Main class that integrates all components

### Web Interface

The Web Interface module (`app/web_interface`) is responsible for:
- Providing a user-friendly web interface using Flask
- Handling file uploads and parameter selection
- Displaying generated questions
- Enabling JSON export

Key files:
- `app.py`: Main Flask application
- Templates: HTML templates for the web interface
- Static: CSS and JavaScript files

## Data Flow

1. **PDF Upload**: User uploads a PDF document through the web interface
2. **PDF Processing**: The PDF is processed to extract text and create chunks
3. **Vector Storage**: Text chunks are vectorized and stored in FAISS
4. **Topic Retrieval**: If a topic is specified, relevant chunks are retrieved
5. **Question Generation**: The LLM generates questions based on the retrieved content
6. **Quality Filtering**: Generated questions are filtered for quality
7. **Result Display**: Questions are displayed to the user

## Implementation Details

### PDF Processing

The PDF processing implementation uses a recursive character text splitter to create chunks that preserve context. The chunking algorithm considers paragraph breaks and sentence boundaries to create meaningful chunks.

Optimization parameters:
- Chunk size: 2000 characters (optimized)
- Chunk overlap: 50 characters (optimized)

### Vector Storage

The vector storage implementation uses TF-IDF vectorization from scikit-learn and FAISS for efficient similarity search. This approach was chosen as a lightweight alternative to transformer-based embeddings to accommodate memory constraints.

Optimization parameters:
- Max features: 5000 (optimized)
- Use IDF: True
- Stop words: English
- N-gram range: (1, 2)

### LLM Integration

The LLM integration uses the Ollama API to generate questions. The system includes specialized prompts for different question types, which are designed to maximize the quality and relevance of the generated questions.

Question types supported:
- Multiple Choice
- Multiple Selection
- True/False
- Short Answer

### Web Interface

The web interface is built with Flask and uses Bootstrap for responsive design. It includes:
- A form for uploading PDFs and selecting parameters
- A processing page with progress indication
- A results page for displaying generated questions
- JSON export functionality

## Performance Considerations

The system has been optimized for performance in several ways:
- Efficient PDF text extraction
- Optimized chunking parameters
- Lightweight TF-IDF vectorization instead of transformer models
- Caching of vector storage for repeated queries
- Asynchronous question generation

## Security Considerations

- File uploads are validated and restricted to PDF format
- Maximum file size is limited to 16MB
- User inputs are sanitized to prevent injection attacks
- Temporary files are stored in a secure location
- No external API calls except to the local Ollama instance

## Extending the System

The modular architecture makes it easy to extend the system:

1. **Adding new question types**:
   - Add a new system prompt in `LLMIntegration._initialize_system_prompts()`
   - Implement a new parsing method in `LLMIntegration._parse_questions()`
   - Update the web interface to include the new question type

2. **Supporting new languages**:
   - Add the language to the language selection dropdown
   - Ensure the LLM model supports the language

3. **Using different LLM models**:
   - Update the `model_name` parameter in `LLMIntegration`
   - Adjust system prompts if necessary for the new model

4. **Improving vectorization**:
   - Replace TF-IDF with a more sophisticated embedding model if resources allow
   - Update the `VectorStorage` class to use the new embedding method

## Dependencies

- **PDF Processing**: PyPDF2
- **Vector Storage**: faiss-cpu, scikit-learn
- **LLM Integration**: ollama, langchain
- **Web Interface**: Flask, Flask-WTF
- **Utilities**: numpy, tqdm, python-dotenv

## Testing

The system includes comprehensive tests:
- Unit tests for individual components
- Integration tests for component interactions
- End-to-end tests for the entire system
- Performance tests for optimization

## Known Limitations

- PDF documents with scanned images require OCR (not implemented)
- Very large PDFs may exceed memory limits
- Question quality depends on the capabilities of the LLM model
- Limited support for complex mathematical or scientific notation
- Performance may vary based on hardware capabilities
