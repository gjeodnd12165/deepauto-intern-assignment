from pathlib import Path
import logging
import time
from typing import Literal
import requests

import asyncio

from fastmcp import FastMCP, Context

from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

from playwright.async_api import async_playwright

from bs4 import BeautifulSoup

from initialize_docling import initialize_docling

mcp = FastMCP("deepauto intern assignment mcp server")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@mcp.tool
async def greeting(name: str) -> str:
    """
    Greet the user with name!
    """
    return f"Hello {name}!"


# # Global storage for background tasks
# conversion_tasks: dict[str, str] = {}

# def read_as_markdown_background(task_id: str, input_file_path: str, ctx: Context):
#     """
#     Background conversion function
#     """

#     try:
#         # Update status
#         conversion_tasks[task_id]["status"] = "RUNNING"
        
#         # Optimized conversion
#         pipeline_options = PdfPipelineOptions()
#         pipeline_options.do_ocr = False
#         pipeline_options.do_table_structure = False
#         pipeline_options.generate_page_images = False
        
#         converter = DocumentConverter(
#         format_options={
#             InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
#         }
#     )
#         
#         ctx.debug("Pdf to docling document conversion starts")
#         conversion_start = time.time()
#         doc = converter.convert(input_file_path).document
#         conversion_time = time.time() - conversion_start
#         ctx.debug(f"Pdf to docling document conversion finished: {conversion_time:.2f}s")

#         markdown = doc.export_to_markdown()
        
#         # Store result
#         conversion_tasks[task_id]["status"] = "SUCCESS"
#         conversion_tasks[task_id]["result"] = markdown
        
#     except Exception as e:
#         conversion_tasks[task_id]["status"] = "ERROR"
#         conversion_tasks[task_id]["error"] = str(e)


# PDF_FILE_PATH = "pdf/Amazon.com Inc. - Form 8-K. 2024-05-14.pdf"

# @mcp.tool
# async def read_as_markdown(input_file_path: str, ctx: Context):
#     """
#     Read a pdf file and convert it into a markdown text.
#     """
    
#     if not Path(input_file_path).is_file():
#         error_message = f"{input_file_path} is not a valid file path."
#         ctx.error(error_message)
#         return error_message

#     # Check if we have an existing task for this file
#     task_key = f"convert_{hash(input_file_path)}"
    
#     if task_key in conversion_tasks:
#         task = conversion_tasks[task_key]
        
#         if task["status"] == "PENDING":
#             return {"status": "PENDING", "message": "Conversion starting..."}
#         elif task["status"] == "RUNNING":
#             return {"status": "RUNNING", "message": "Converting PDF, please wait..."}
#         elif task["status"] == "SUCCESS":
#             # Return result and clean up
#             result = task["result"]
#             del conversion_tasks[task_key]
#             return result
#         elif task["status"] == "ERROR":
#             error = task["error"]
#             del conversion_tasks[task_key]
#             return f"Conversion failed: {error}"
    
#     # Start new conversion task
#     conversion_tasks[task_key] = {"status": "PENDING"}
    
#     thread = threading.Thread(
#         target=read_as_markdown_background,
#         args=(task_key, input_file_path, ctx),
#         daemon=True  # Dies when main process dies
#     )
#     thread.start()
    
#     return {
#         "status": "PENDING", 
#         "message": "Starting PDF conversion. This may take a while. Please check back in a moment."
#     }

@mcp.tool
async def read_as_markdown(input_file_path: str, ctx: Context):
    """
    Read a pdf file and convert it into a markdown text.
    """
    
    if not Path(input_file_path).is_file():
        error_message = f"{input_file_path} is not a valid file path."
        ctx.error(error_message)
        return error_message

    # Use cached converter
    converter = await initialize_docling()
    
    try:
        ctx.info("Converting PDF (using cached models)...")
        
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        
        def sync_convert():
            doc = converter.convert(input_file_path).document
            return doc.export_to_markdown()
        
        markdown = await loop.run_in_executor(None, sync_convert)
        
        ctx.info("Conversion completed!")
        return markdown
        
    except Exception as e:
        ctx.error(f"Conversion failed: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool
async def html_to_pdf(input_file_path: str, output_file_path: str, ctx: Context) -> None:
    """
    Recieve a name of a htm/html file and
    save that as a pdf file.
    """

    if not Path(input_file_path).is_file():
        error_message = f"{input_file_path} is not a valid file path."
        await ctx.error(error_message)
        return error_message
    # elif not Path(output_file_path).is_file():
    #     error_message = f"{output_file_path} is not a valid file path" 
    #     await ctx.error(error_message)
    #     return error_message
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto(Path(input_file_path).resolve().as_uri())

        await page.pdf(
            path=output_file_path,
            format="A4",
            print_background=True,
            margin={"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"}
        )

        await browser.close()


_INPUT_EXAMPLE = {
    "cik": 1018724,
    "year": 2024,
    "filing_type": "8-K",
    "output_dir_path": "html/amzn_2024_8_k"
}

@mcp.tool
async def download_sec_filing(
    cik: int,
    year: Literal[2021, 2022, 2023, 2024, 2025],
    filing_type: Literal["8-K", "10-Q", "10-K", "DEF 14A"],
    output_dir_path: str,
    ctx: Context
) -> str:
    """
    Downloads SEC / EDGAR filing.
    """

    HEADERS = {"User-Agent": "gjeodnd12165/1.0 deepauto-intern-assignment (gjeodnd12165@gmail.com)"}

    cik_str = str(cik).zfill(10)

    ctx.info(f"Starting search for CIK {cik_str}, Year {year}, Type '{filing_type}'...")

    # Step 1: Get the company's submissions JSON
    submissions_url = f"https://data.sec.gov/submissions/CIK{cik_str.zfill(10)}.json"
    try:
        time.sleep(0.2) # temporary
        response = requests.get(submissions_url, headers=HEADERS)
        response.raise_for_status()
        submissions = response.json()
    except requests.exceptions.RequestException as e:
        error_message = f"Error fetching submissions for CIK {cik_str} from {submissions_url}: {e}"
        ctx.error(error_message)
        return error_message

    # Step 2: Find the most recent filing that matches the criteria
    recent_filings = submissions['filings']['recent']
    target_filing = None

    for i in range(len(recent_filings['form'])):
        if recent_filings['form'][i] == filing_type and \
           recent_filings['filingDate'][i].startswith(str(year)):
            target_filing = {
                "accession_number": recent_filings['accessionNumber'][i],
                "primary_document": recent_filings['primaryDocument'][i],
                "filing_date": recent_filings['filingDate'][i]
            }
            ctx.info(f"Found most recent matching filing from {target_filing['filing_date']}: {target_filing['accession_number']}")
            break

    if not target_filing:
        error_message = "No matching filing found for the specified year and type."
        ctx.error(error_message)
        return error_message

    # Step 3: Get the list of all files from the filing's index page
    accession_no_dashes = target_filing['accession_number'].replace('-', '')
    filing_base_url = f"https://www.sec.gov/Archives/edgar/data/{cik_str}/{accession_no_dashes}/"
    index_html_url = f"{filing_base_url}{target_filing['accession_number']}-index.html"

    ctx.info(f"Fetching file list from: {index_html_url}")

    try:
        time.sleep(0.2) # temporary
        response = requests.get(index_html_url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
    except requests.exceptions.RequestException as e:
        error_message = f"Error fetching filing index page from {index_html_url}: {e}"
        ctx.error(error_message)
        return error_message

    all_files = []
    for table in soup.find_all('table'):
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) > 2:
                link_tag = row.find('a', href=True)
                if link_tag:
                    # Get the filename from the href attribute for reliability
                    filename = Path(link_tag['href']).name
                    all_files.append(filename)

    ctx.info(f"Found {len(all_files)} files to download.")

    # Step 4: Download each file
    save_path = Path(output_dir_path)
    save_path.mkdir(parents=True, exist_ok=True)

    primary_file_local_path = None

    for filename in all_files:
        download_url = f"{filing_base_url}{filename}"
        local_path = save_path / filename

        try:
            ctx.info(f"Downloading {filename}...")
            time.sleep(0.2) # temporary
            file_response = requests.get(download_url, headers=HEADERS)
            file_response.raise_for_status()
            local_path.write_bytes(file_response.content)

            if filename == target_filing["primary_document"]:
                primary_file_local_path = str(local_path)

        except requests.exceptions.RequestException as e:
            error_message = f"Failed to download from {download_url}: {e}"
            ctx.error(error_message)
            # Decide if you want to stop all downloads or just skip this file.
            # This implementation stops everything if any file fails.
            return error_message

    if primary_file_local_path:
        ctx.info(f"\nDownload complete. Files saved in: {save_path}")
        return primary_file_local_path
    else:
        # This case would be hit if the primary document was listed but failed to download,
        # and the loop continued (which it won't with the current error handling).
        # Or, if the primary document was never found in the file list.
        error_message = f"Download process finished, but the primary document '{target_filing['primary_document']}' was not found or downloaded."
        ctx.error(error_message)
        return error_message

@mcp.tool
async def check_gpu_status() -> str:
    """Check GPU status in MCP server"""
    import torch
    
    info = []
    info.append(f"PyTorch version: {torch.__version__}")
    info.append(f"CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        info.append(f"CUDA version: {torch.version.cuda}")
        info.append(f"GPU count: {torch.cuda.device_count()}")
        info.append(f"Current device: {torch.cuda.current_device()}")
        info.append(f"Device name: {torch.cuda.get_device_name()}")
        info.append(f"Device memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
    else:
        info.append("No CUDA devices found")
    
    # Check if Docling can see GPU
    try:
        from docling.datamodel.accelerator_options import AcceleratorOptions, AcceleratorDevice
        info.append("Docling CUDA support available")
    except ImportError:
        info.append("Docling CUDA support not available")
    
    return "\n".join(info)

@mcp.tool
async def test_gpu_operation() -> str:
    """Test basic GPU operation"""
    import torch
    
    if not torch.cuda.is_available():
        return "CUDA not available"
    
    try:
        # Simple GPU test
        device = torch.device('cuda:0')
        a = torch.randn(1000, 1000, device=device)
        b = torch.randn(1000, 1000, device=device)
        c = torch.matmul(a, b)
        
        return f"GPU operation successful on {torch.cuda.get_device_name()}"
    except Exception as e:
        return f"GPU operation failed: {e}"

@mcp.tool
async def debug_docling_gpu() -> str:
    """Debug if Docling is actually using GPU"""
    import torch
    
    info = []
    info.append("=== Before Docling Initialization ===")
    if torch.cuda.is_available():
        info.append(f"GPU memory allocated: {torch.cuda.memory_allocated() / 1e6:.1f} MB")
        info.append(f"GPU memory cached: {torch.cuda.memory_reserved() / 1e6:.1f} MB")
    
    # Initialize Docling
    from docling.datamodel.accelerator_options import AcceleratorOptions, AcceleratorDevice
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.datamodel.base_models import InputFormat
    
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = False
    pipeline_options.generate_page_images = False
    
    # Explicit GPU config
    accelerator_options = AcceleratorOptions(device=AcceleratorDevice.CUDA)
    pipeline_options.accelerator_options = accelerator_options
    
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    
    info.append("\n=== After Docling Initialization ===")
    if torch.cuda.is_available():
        info.append(f"GPU memory allocated: {torch.cuda.memory_allocated() / 1e6:.1f} MB")
        info.append(f"GPU memory cached: {torch.cuda.memory_reserved() / 1e6:.1f} MB")
    
    # Check what device Docling models are actually on
    info.append("\n=== Docling Internal Model Devices ===")
    try:
        # This is a bit hacky but let's see what we can inspect
        info.append(f"Converter type: {type(converter)}")
        if hasattr(converter, '_pipeline'):
            info.append(f"Pipeline: {converter._pipeline}")
        
        # Try to access internal models if possible
        # (This might not work depending on Docling's internal structure)
        
    except Exception as e:
        info.append(f"Could not inspect internal models: {e}")
    
    return "\n".join(info)

@mcp.tool
async def debug_model_loading() -> str:
    """Debug what happens during model loading"""
    
    import torch
    from docling.datamodel.accelerator_options import AcceleratorOptions, AcceleratorDevice
    from docling.datamodel.base_models import InputFormat
    from docling.document_converter import DocumentConverter, PdfFormatOption
    
    info = []
    
    # Monitor model loading process
    info.append("=== Model Loading Debug ===")
    
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True  # Enable this to see if models load
    pipeline_options.generate_page_images = False
    
    # Explicit CUDA config
    accelerator_options = AcceleratorOptions(device=AcceleratorDevice.CUDA)
    pipeline_options.accelerator_options = accelerator_options
    
    info.append(f"Pipeline options configured")
    info.append(f"Accelerator device: {accelerator_options.device}")
    
    # Check initial GPU memory
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        initial_memory = torch.cuda.memory_allocated() / 1e6
        info.append(f"Initial GPU memory: {initial_memory:.1f} MB")
    
    try:
        # CORRECT DocumentConverter initialization
        info.append("Creating DocumentConverter with correct API...")
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        info.append("✅ DocumentConverter created successfully!")
        
        # Check GPU memory after initialization
        if torch.cuda.is_available():
            after_init_memory = torch.cuda.memory_allocated() / 1e6
            memory_increase = after_init_memory - initial_memory
            info.append(f"GPU memory after init: {after_init_memory:.1f} MB")
            info.append(f"Memory increase: {memory_increase:.1f} MB")
            
            if memory_increase > 100:  # More than 100MB increase
                info.append("🎉 Significant GPU memory usage - models likely loaded on GPU!")
            elif memory_increase > 10:
                info.append("⚠️ Some GPU memory usage - partial GPU utilization")
            else:
                info.append("❌ Minimal GPU memory usage - models likely on CPU")
        
        # Try to inspect the converter structure
        info.append(f"Converter type: {type(converter)}")
        
    except Exception as e:
        info.append(f"❌ Error during initialization: {e}")
        import traceback
        info.append(f"Traceback: {traceback.format_exc()}")
    
    return "\n".join(info)


async def startup():
    """
    Called when MCP server starts
    """
    await initialize_docling()

if __name__ == "__main__":
    asyncio.run(startup())
    mcp.run()