import logging

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat


logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

_converter = None

async def initialize_docling() -> DocumentConverter:
    """Download and cache Docling models at startup"""
    global _converter
    
    if _converter is not None:
        return _converter
    
    logger.info("Initializing Docling models (this may take a while for first run)...")
    
    try:
        # Configure pipeline
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False
        pipeline_options.do_table_structure = False
        pipeline_options.generate_page_images = False
        
        # Enable CUDA if available
        import torch
        if torch.cuda.is_available():
            from docling.datamodel.accelerator_options import AcceleratorOptions, AcceleratorDevice
            accelerator_options = AcceleratorOptions(device=AcceleratorDevice.CUDA)
            pipeline_options.accelerator_options = accelerator_options
            logger.debug("Using CUDA acceleration")
        
        # Create converter (this downloads models)
        _converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        
        logger.debug("Docling models loaded successfully!")
        return _converter
        
    except Exception as e:
        logger.error(f"Failed to initialize Docling: {e}")
        raise
