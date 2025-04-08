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
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langdetect import detect, DetectorFactory
from collections import Counter

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
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text() + "\n\n"
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
        
        # Clean the extracted text
        text = self._clean_text(text)
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
        print(full_text)
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
        # metadata = self._extract_metadata(pdf_path)
        dominant_language = self.validate_dominant_language(full_text)
        print(dominant_language)
        return {
            "full_text": full_text,
            "chunks": chunks,
            "metadata": metadata,
            "topic": topic,
            "chunk_count": len(chunks)
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
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                if reader.metadata:
                    for key, value in reader.metadata.items():
                        if key.startswith('/'):
                            key = key[1:]  # Remove leading slash
                        metadata[key] = value
                
                metadata['page_count'] = len(reader.pages)
                metadata['filename'] = os.path.basename(pdf_path)
            # with pdfplumber.open(path) as pdf:
            #     content = ''
            #     for i in range(len(pdf.pages)):
            #         page = pdf.pages[i]
            #         page_content = '\n'.join(page.extract_text().split('\n')[:-1])
            #         content = content + page_content
            #     print(content)
        except Exception as e:
            print(f"Warning: Could not extract metadata: {str(e)}")
        
        return metadata
    def detect_languages(self, text: str, chunk_size: int = 500) -> Dict[str, float]:
        """
        Detect the distribution of languages in the text.
        
        Args:
            text: The cleaned text extracted from the PDF.
            chunk_size: Number of characters per chunk to analyze.
            
        Returns:
            A dictionary with language codes and their percentage frequencies.
        """
        chunks = self.chunk_text(text)
        detected = []

        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk:
                continue
            try:
                lang = detect(chunk)
                detected.append(lang)
            except Exception:
                continue  # Skip chunks where detection fails

        if not detected:
            return {"undetected": 100.0}

        counts = Counter(detected)
        total = sum(counts.values())

        return {
            lang: round((count / total) * 100, 2)
            for lang, count in counts.items()
        }
    def validate_dominant_language(self, text: str, threshold: float = 180.0) -> str:
        """
        Detect the dominant language and ensure it's allowed and above the threshold.

        Args:
            text: Extracted PDF text
            threshold: Minimum percentage required for a language to be considered dominant

        Returns:
            Dominant language code (e.g., 'en', 'fr', etc.)

        Raises:
            ValueError if no language exceeds the threshold or language not supported
        """
        allowed_languages = {'en', 'fr', 'de', 'zh', 'ar', 'it'}  # English-, French-, German-, Chinese, Arabic, Italian-

        language_distribution = self.detect_languages(text)
        print("---------------------------------------------------------------")
        print("Detected languages:", language_distribution)
        print("---------------------------------------------------------------")

        dominant_lang = max(language_distribution.items(), key=lambda x: x[1])

        if dominant_lang[1] >= threshold:
            if dominant_lang[0] in allowed_languages:
                return dominant_lang[0]
            else:
                raise ValueError("The detected dominant language is not supported. Allowed languages: French, English, German, Chinese, Arabic, Italian.")
        else:
            raise ValueError("Please upload a valid PDF with a dominant language (at least 70%).")

    def _is_junk_text(self, text: str) -> bool:
        # Check for very short text
        if len(text) < 100:
            return True

        # Check if same word repeats a lot
        words = re.findall(r'\w+', text)
        if not words:
            return True

        unique_word_ratio = len(set(words)) / len(words)
        if unique_word_ratio < 0.3:
            return True

        # Optional: check language detection
        # try:
        #     langs = detect_langs(text)
        #     if langs[0].lang not in ['hi', 'en'] or langs[0].prob < 0.7:
        #         return True
        # except:
        #     return True

        return False