"""
Performance optimization for the PDF Question Generator system
"""

import os
import time
from app.pdf_processor import PDFProcessor
from app.vector_storage import VectorStorage
from app.question_generator import QuestionGenerator

def optimize_chunk_size(pdf_path, sizes=[500, 1000, 1500, 2000], overlaps=[50, 100, 200]):
    """
    Find the optimal chunk size and overlap for a given PDF.
    
    Args:
        pdf_path: Path to the PDF file
        sizes: List of chunk sizes to test
        overlaps: List of overlap sizes to test
        
    Returns:
        Tuple of (optimal_chunk_size, optimal_overlap)
    """
    results = []
    
    for size in sizes:
        for overlap in overlaps:
            # Skip if overlap is larger than chunk size
            if overlap >= size:
                continue
                
            start_time = time.time()
            
            # Process PDF with current parameters
            processor = PDFProcessor(chunk_size=size, chunk_overlap=overlap)
            pdf_data = processor.process_pdf(pdf_path)
            
            # Fit vector storage
            vector_storage = VectorStorage()
            vector_storage.fit(pdf_data["chunks"])
            
            # Measure time
            elapsed_time = time.time() - start_time
            
            # Store results
            results.append({
                "chunk_size": size,
                "chunk_overlap": overlap,
                "num_chunks": len(pdf_data["chunks"]),
                "processing_time": elapsed_time
            })
            
            print(f"Chunk Size: {size}, Overlap: {overlap}, Chunks: {len(pdf_data['chunks'])}, Time: {elapsed_time:.4f}s")
    
    # Find the configuration with the best balance of processing time and chunk count
    # We want to minimize processing time while maintaining a reasonable number of chunks
    optimal_result = min(results, key=lambda x: x["processing_time"] * (1 + 0.01 * x["num_chunks"]))
    
    return optimal_result["chunk_size"], optimal_result["chunk_overlap"]

def optimize_vector_storage(pdf_path, max_features_options=[1000, 5000, 10000]):
    """
    Find the optimal max_features parameter for vector storage.
    
    Args:
        pdf_path: Path to the PDF file
        max_features_options: List of max_features values to test
        
    Returns:
        Optimal max_features value
    """
    results = []
    
    # Process PDF
    processor = PDFProcessor()
    pdf_data = processor.process_pdf(pdf_path)
    
    for max_features in max_features_options:
        start_time = time.time()
        
        # Create and fit vector storage
        vector_storage = VectorStorage(max_features=max_features)
        vector_storage.fit(pdf_data["chunks"])
        
        # Test search performance
        search_start = time.time()
        vector_storage.search("test query", k=5)
        search_time = time.time() - search_start
        
        # Measure total time
        total_time = time.time() - start_time
        
        # Store results
        results.append({
            "max_features": max_features,
            "fit_time": total_time - search_time,
            "search_time": search_time,
            "total_time": total_time
        })
        
        print(f"Max Features: {max_features}, Fit Time: {total_time - search_time:.4f}s, Search Time: {search_time:.4f}s")
    
    # Find the configuration with the best search performance
    optimal_result = min(results, key=lambda x: x["search_time"])
    
    return optimal_result["max_features"]

def apply_optimizations(test_pdf_path):
    """
    Apply optimizations based on test results and update the system.
    
    Args:
        test_pdf_path: Path to a test PDF file
    """
    print("\n=== Optimizing Chunk Parameters ===")
    optimal_chunk_size, optimal_overlap = optimize_chunk_size(test_pdf_path)
    
    print("\n=== Optimizing Vector Storage Parameters ===")
    optimal_max_features = optimize_vector_storage(test_pdf_path)
    
    print("\n=== Optimization Results ===")
    print(f"Optimal Chunk Size: {optimal_chunk_size}")
    print(f"Optimal Chunk Overlap: {optimal_overlap}")
    print(f"Optimal Max Features: {optimal_max_features}")
    
    # Create an optimized question generator
    optimized_generator = QuestionGenerator()
    optimized_generator.pdf_processor = PDFProcessor(
        chunk_size=optimal_chunk_size, 
        chunk_overlap=optimal_overlap
    )
    optimized_generator.vector_storage = VectorStorage(
        max_features=optimal_max_features
    )
    
    return optimized_generator

if __name__ == "__main__":
    from app.pdf_processor.test_utils import create_test_pdf, get_sample_text
    
    # Create a test PDF
    print("Creating test PDF...")
    full_text, _ = get_sample_text()
    test_pdf_path = create_test_pdf(full_text)
    
    try:
        # Run optimizations
        print("Running optimizations...")
        optimized_generator = apply_optimizations(test_pdf_path)
        
        print("\nOptimization complete. The system has been tuned for better performance.")
    finally:
        # Clean up
        if os.path.exists(test_pdf_path):
            os.remove(test_pdf_path)
