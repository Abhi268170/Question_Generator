"""
PDF Processor Module

This module handles the extraction and chunking of text from PDF documents.
It provides functionality to:
1. Extract text from PDF files
2. Intelligently chunk the text to preserve context
3. Process the chunks for further use in the RAG system
"""

import os
import re
from typing import List, Dict, Tuple, Optional
import pdfplumber
# import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
import fasttext
# from lingua import Language, LanguageDetectorBuilder
from collections import defaultdict

class PDFProcessor:
    """
    A class for processing PDF documents, extracting text, and chunking it intelligently.
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the PDF processor with chunking parameters.
        
        Args:
            chunk_size: The target size of each text chunk
            chunk_overlap: The overlap between consecutive chunks to maintain context
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        model_path = os.path.join(os.path.dirname(__file__), "../models/lid.176.bin")
        self.model = fasttext.load_model(model_path)
        self.allowed_languages = {
        'en': 'ENGLISH',
        'fr': 'FRENCH',
        'de': 'GERMAN',
        'zh': 'CHINESE',
        'ar': 'ARABIC',
        'it': 'ITALIAN',
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as a string
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at {pdf_path}")
        
        text = ""
        try:
            # with open(pdf_path, 'rb') as file:
            #     reader = PyPDF2.PdfReader(file)
            #     for page_num in range(len(reader.pages)):
            #         page = reader.pages[page_num]
            #         text += page.extract_text() + "\n\n"
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n\n"
            print(text)
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
        
        # Clean the extracted text
        # text = self._clean_text(text)
        if self._is_junk_text(text):
            raise ValueError("Extracted text appears to be garbage or unreadable.")
        return text
    
    def _clean_text(self, text: str) -> str:
        """
        Clean the extracted text by removing extra whitespace and normalizing line breaks.
        
        Args:
            text: The text to clean
            
        Returns:
            Cleaned text
        """
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text)
        
        # Replace multiple newlines with double newlines to preserve paragraph breaks
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove any non-printable characters
        text = re.sub(r'[^\x20-\x7E\n]', '', text)
        
        return text.strip()
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split the text into chunks using the configured text splitter.
        
        Args:
            text: The text to split into chunks
            
        Returns:
            List of text chunks
        """
        return self.text_splitter.split_text(text)
    
    def extract_topic_content(self, text: str, topic: str) -> str:
        """
        Extract content related to a specific topic from the text.
        
        Args:
            text: The full text to search within
            topic: The topic to extract content for
            
        Returns:
            Text content related to the specified topic
        """
        # Simple implementation - find paragraphs containing the topic
        # This could be enhanced with more sophisticated NLP techniques
        paragraphs = text.split('\n\n')
        topic_paragraphs = []
        
        for paragraph in paragraphs:
            if topic.lower() in paragraph.lower():
                topic_paragraphs.append(paragraph)
        
        if not topic_paragraphs:
            # If no exact matches, try to find partial matches
            for paragraph in paragraphs:
                # Split topic into words and check if any word appears in the paragraph
                topic_words = topic.lower().split()
                if any(word in paragraph.lower() for word in topic_words if len(word) > 3):
                    topic_paragraphs.append(paragraph)
        
        return '\n\n'.join(topic_paragraphs)
    
    def process_pdf(self, pdf_path: str, topic: Optional[str] = None) -> Dict:
        """
        Process a PDF file: extract text, optionally filter by topic, and chunk the text.
        
        Args:
            pdf_path: Path to the PDF file
            topic: Optional topic to filter content by
            
        Returns:
            Dictionary containing the full text, chunks, and metadata
        """
        # Extract text from PDF
        full_text = self.extract_text_from_pdf(pdf_path)

        # Filter by topic if specified
        if topic and topic.strip():
            topic_text = self.extract_topic_content(full_text, topic)
            # If topic content was found, use it; otherwise, use the full text
            text_to_chunk = topic_text if topic_text else full_text
        else:
            text_to_chunk = full_text
        
        # Chunk the text
        chunks = self.chunk_text(text_to_chunk)
        
        # Get PDF metadata
        metadata = self._extract_metadata(pdf_path)
        language = self.validate_language(full_text)
        print(language)
        return {
            "full_text": full_text,
            "chunks": chunks,
            "metadata": metadata,
            "topic": topic,
            "chunk_count": len(chunks),
            "language": language
        }
    
    def _extract_metadata(self, pdf_path: str) -> Dict:
        """
        Extract metadata from the PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing PDF metadata
        """
        metadata = {}
        try:
            # with open(pdf_path, 'rb') as file:
            #     reader = PyPDF2.PdfReader(file)
            #     if reader.metadata:
            #         for key, value in reader.metadata.items():
            #             if key.startswith('/'):
            #                 key = key[1:]  # Remove leading slash
            #             metadata[key] = value
                
            #     metadata['page_count'] = len(reader.pages)
            #     metadata['filename'] = os.path.basename(pdf_path)
            with pdfplumber.open(pdf_path) as pdf:
                content = ''
                for i in range(len(pdf.pages)):
                    page = pdf.pages[i]
                    page_content = '\n'.join(page.extract_text().split('\n')[:-1])
                    content = content + page_content
        except Exception as e:
            print(f"Warning: Could not extract metadata: {str(e)}")
        
        return metadata

    def validate_language(self, text: str, threshold: float = 70.0) -> str:
        """
        Validate the dominant language in a text against allowed languages.

        Args:
            text: Extracted PDF text
            threshold: Minimum confidence score required for a language to be considered valid

        Returns:
            Dominant language code (e.g., 'en', 'fr', etc.)

        Raises:
            ValueError if the language is not supported or under threshold
        """
        # FastText returns a tuple: (labels, probabilities)
        labels, probabilities = self.model.predict(text.replace('\n', ' '), k=1)

        if not labels or not probabilities:
            raise ValueError("Language detection failed.")

        lang_label = labels[0].replace('__label__', '')
        confidence = probabilities[0] * 100  # Convert to percentage


        print(lang_label)
        if lang_label not in self.allowed_languages:
            raise ValueError(f"Unsupported language detected: '{lang_label}'. Supported languages are: {', '.join(self.allowed_languages.values())}")

        if confidence < threshold:
            raise ValueError(f"Language confidence too low: {confidence:.2f}%. Threshold is {threshold}%")

        return self.allowed_languages[lang_label]

    def _is_junk_text(self, text: str) -> bool:
        # Very short text
        if len(text) < 100:
            print("Text lenght is <100")
            return True

        # Word-based analysis
        words = re.findall(r'\w+', text)
        if not words:
            return True
        return False