# Boataround Search Results Scraper

This repository is solution to Boataround's [python-tester](https://bitbucket.org/bodev/python-tester/src/main/) test.

provides a way to scrape and analyze boat search results from the Boataround website.
It includes functions for downloading search pages, extracting boat information, and processing the data.

## Features

`download_fun.py`:

- **down_page(url):** Downloads a single page from Boataround's search results.
- **retry_down_page(url, max_retries=5)** Retries downloading a page to handle potential internet connection issues.
- **check_page(id_search):** Checks if a page is the last page of the search results.
- **single_page_scraping(url):** Downloads a single page and extracts search results for analysis.
- **process_list(search_list):** Processes a list of search results, extracting boat information.
- **all_pages_scraping(url):** Iterates through all pages of search results and downloads them.
- **gen_dates(start_date_str, end_date_str):** Generates a list of dates between two given dates.
- **all_dates_scraping(destination, start_date_str, end_date_str):** Downloads boat information for a given estination and time frame.

`excel_export.py`:

- **exc_export(data, file_name='output'):** Writes a list of dictionaries,each containing the information about available boats
    into an Excel file. Formats data into their proper Excel formats.
    Uses pandas.

`excel_export_light.py`:

- **exc_export(data, file_name='output')**
- Writes a list of dictionaries,each containing the information about available boats
    into an Excel file. Does **not** formats data. Simple and lighter. Uses openpyxl.
  
## Usage

Create virtual enviroment and install dependencies.
If you are using `excel_export_light.py` you can skip `pandas`.

```bash
mkdir env
python -m venv env/
source env/bin/activate
pip install --upgrade pip
pip install beautifulsoup4
pip install requests
pip install openpyxl
pip install pandas
```

To use the script, import it into your project and call the desired functions with appropriate parameters.
The functions return relevant data structures containing information about available boats.

```python
from download_fun import all_dates_scraping
from excel_export_light import exc_export
# from excel_export import exc_export # pandas

# Example: Scraping all available boats for a specific destination and date range
destination = "split-1"
start_date = '2024-05-01'
end_date = '2024-09-30'
boat_data = all_dates_scraping(destination, start_date, end_date)

exc_export(date_data, file_name=f"{destination}_{start_date}_{end_date}")
```

# To Do

- Finish Task 2
- Refract code in `single_page_scraping(url)` into smaller parts
- Divide `download_fun.py` into multiple files.
- Find out reasonable values for:
    - `timeout` in `down_page(url)`
    - `max_retries` in `(url, max_retries=5)`
- replace `while still_none` with `for attempt in range(max_retries)` in `single_page_scraping(url)` 
- Complete data formatting in `excel_export.py`
- Delete unuseful comments and commented code
