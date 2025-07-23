from shared import mcp

from pathlib import Path
import time
from typing import Literal
import requests

from fastmcp import Context

from bs4 import BeautifulSoup

@mcp.tool
async def download_sec_filing(
    cik: int,
    year: Literal[2021, 2022, 2023, 2024, 2025],
    filing_type: Literal["8-K", "10-Q", "10-K", "DEF 14A"],
    output_dir_path: str,
    ctx: Context
) -> str:
    """Fetches SEC / EDGAR filings.

    Downloads filings from SEC by the given criteria.  
    To limit the complexity, it fetches the most recent one from the year.

    Args:
        cik: The central index key of a company.
        year: A year to find filings. Only in 2021-2025 are allowed.
        filing_type: A specific type of a primary document of a filing.
            Only "8-K", "10-Q", "10-K", "DEF 14A" are allowed.
        output_dir_path: A path to a directory to store fetched filings
            relative to main server directory. It should be under html/ .
    
    Returns:
        A string of the path to the primary document of the filing.
        
        For exmaple:

        html/amzn_2024_8_k/amzn-20241031.htm

        The primary document would be html file, 
        letting other tools to use.

    Raises:
        ConnectionError: If one of the requests of fetching is failed.
        FileNotFoundError: If filing with given criteria is not found,
            or a path to the fetched primary document was not set.
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
        raise ConnectionError(f"Error fetching submissions for CIK {cik_str} from {submissions_url}: {e}")

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
        raise FileNotFoundError("No matching filing found for the specified year and type.")

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
        raise ConnectionError(f"Error fetching filing index page from {index_html_url}: {e}")

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
            raise ConnectionError(f"Failed to download from {download_url}: {e}")

    if primary_file_local_path:
        ctx.info(f"\nDownload complete. Files saved in: {save_path}")
        return primary_file_local_path
    else:
        # This case would be hit if the primary document was listed but failed to download,
        # and the loop continued (which it won't with the current error handling).
        # Or, if the primary document was never found in the file list.
        raise FileNotFoundError(f"Download process finished, but the primary document '{target_filing['primary_document']}' was not found or downloaded.")
