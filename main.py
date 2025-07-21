from pathlib import Path
import logging

from fastmcp import FastMCP, Context

from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
)
from docling.datamodel.settings import settings
from docling.document_converter import DocumentConverter, PdfFormatOption


mcp = FastMCP("deepauto intern assignment mcp server")

@mcp.tool
def greeting(name: str) -> str:
    """
    Greet the user with name!
    """
    return f"Hello {name}!"

@mcp.tool
async def read_as_markdown(input_file_path: str, ctx: Context) -> str:
    """
    Recieve a name of a pdf file in the pdf/ directory and
    convert that as markdown text.
    """
    await ctx.debug(f"Tool called with file: '{input_file_path}'")

    target_file = Path("pdf") / input_file_path

    if not Path(target_file).is_file():
        error_message = f"The file '{input_file_path}' does not exist in the pdf/ directory."
        await ctx.error(error_message)
        return error_message
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logging.getLogger("docling").setLevel(logging.DEBUG)
    
    acceleator_options = AcceleratorOptions(
        num_threads=8, device=AcceleratorDevice.AUTO
    )
    pipeline_options = PdfPipelineOptions()
    pipeline_options.accelerator_options = acceleator_options
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = False
    pipeline_options.table_structure_options.do_cell_matching = True

    try:
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options,
                )
            }
        )
        await ctx.debug(f"Starting conversion for '{target_file}' in a worker thread.")

        # Enable the profiling to measure the time spent
        settings.debug.profile_pipeline_timings = True

        # Conversion
        conversion_result = converter.convert(target_file)
        doc = conversion_result.document

        # list with total time per document
        doc_conversion_secs = conversion_result.timings["pipeline_total"].times

        md = doc.export_to_markdown()

        await ctx.debug(f"Successfully converted '{target_file}'.")
        await ctx.debug(doc_conversion_secs)
        return md

    except Exception as e:
        # Catch any exceptions from the library
        error_message = f"An unexpected error occurred while converting '{input_file_path}'"
        await ctx.error(f"{error_message}: {e}")
        return f"{error_message}. Please check the server logs for details."


if __name__ == "__main__":
    mcp.run()