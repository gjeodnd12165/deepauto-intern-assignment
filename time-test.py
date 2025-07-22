import time
from docling.document_converter import DocumentConverter

def time_conversion_phases(input_file_path: str):
    start = time.time()
    
    # Phase 1: PDF → DoclingDocument
    converter = DocumentConverter()
    doc = converter.convert(input_file_path).document
    phase1_time = time.time() - start
    
    # Phase 2: DoclingDocument → Markdown  
    phase2_start = time.time()
    markdown = doc.export_to_markdown()
    phase2_time = time.time() - phase2_start
    
    print(f"PDF → DoclingDocument: {phase1_time:.2f}s")
    print(f"DoclingDocument → Markdown: {phase2_time:.2f}s")
    print(f"Ratio: {phase1_time/phase2_time:.1f}:1")
    
    return markdown

time_conversion_phases("sample.pdf")