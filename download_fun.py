"""
Module for downloading and processing boat search results from Boataround.
<https://bt2stag.boataround.com/search?>

This module provides functions for downloading search results from the Boataround website,
extracting relevant information about available boats, and processing the data.

Functions:
- down_page(url): Downloads a single page from Boataround's search results.
- check_page(id_search): Checks if a page is the last page of the search results.
- single_page_scraping(url): Downloads a single page and extracts search results for analysis.
- process_list(search_list): Processes a list of search results, extracting boat information.
- all_pages_scraping(url): Iterates through all pages of search results and downloads them.
- gen_dates(start_date_str, end_date_str): Generates a list of dates between two given dates.
- all_dates_scraping(destination, start_date_str, end_date_str): Downloads boat information
  for a given destination and time frame.
"""

import sys
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
import requests
#from requests.exceptions import RequestException, ReadTimeout
#from urllib3.exceptions import MaxRetryError
from bs4 import BeautifulSoup


# Eficienct for making multiple requests to the same domain
# creates a Session object that persists parameters (e.g., headers, cookies) across requests
session = requests.Session()

# usually there are no automatic retries
# adding retries adds resilience to transient network issues
#requests.adapters.DEFAULT_RETRIES = 99999
#session.mount("https://", requests.adapters.HTTPAdapter(
#    max_retries=requests.adapters.Retry(total=99999)))

# value `True` enables SSL certificates verification
#session.verify = True  # Set False for debugging

# sets user agent to Chrome browser on Windows
#session.headers.update({
#    'User-Agent': (
#        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
#        '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
#    )
#})

def down_page(url):
    """
    Downloads single page from <https://bt2stag.boataround.com/search?>

    Args:
        url (str): The URL of the search page on bt2stag.boataround.com.
        Expected format of the url is
        `f"https://bt2stag.boataround.com/search" \
        f"?destinations={destination_name}-1&checkIn={yyyy-mm-dd}&checkOut={yyyy-mm-dd}"`

   Returns:
   requests.Response: The response object containing the downloaded page.

    Raises:
        requests.exceptions.SSLError: If an SSL error occurs during the request.
        requests.exceptions.RequestException: If any other request-related error occurs.
    """
    #global session
    url = url.strip()

    headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                )
            }

    try:
        response = requests.get(url, headers, timeout=99999)
        # response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        return response
    except requests.exceptions.SSLError as ssl_error:
        print(f"SSL Error: {ssl_error}")
        sys.exit(1)
    except requests.exceptions.RequestException as error_name:
        print(f"Error occurred while fetching the page: {str(error_name)}")
        sys.exit(1)


    #while True:
    #    retries = 5  # Number of retries
    #    for attempt in range(retries):
    #        #print(f"Attempt: {attempt}")
    #        try:
    #            response = session.get(url, timeout=300)
    #            #response = requests.get(url, timeout=99999)
    #            response.raise_for_status()
    #            return response  # If successful, exit the loop
    #        except requests.exceptions.SSLError as ssl_error:
    #            print(f"SSL Error: {ssl_error}")
    #            sys.exit(1)
    #        except requests.exceptions.RequestException as error_name:
    #            print(f"Error occurred while fetching the page: {str(error_name)}")
    #            if attempt < retries - 1:
    #                print(f"Retrying request (Retry {attempt + 1}/{retries})...")
    #            else:
    #                print("Max retries exceeded. Restarting the session.")
    #                session.close()  # Close the existing session
    #                session = requests.Session()  # Create a new session

        #except ReadTimeout as timeout_error:
        #    print(f"Read Timeout Error: {timeout_error}")
        #    if attempt < retries - 1:
        #        print(f"Retrying request (attempt {attempt + 2}/{retries})...")
        #    else:
        #        print("Max retries exceeded. Exiting.")
        #        sys.exit(1)
        #except (RequestException, MaxRetryError) as error_name:
        #    print(f"Error occurred while fetching the page: {str(error_name)}")
        #    sys.exit(1)



def check_page(id_search):
    """
    check if the page is the last page of the search results

    Args:
        id_search (bs4.element.Tag): The part of the HTML inside the division with id "search".

    Return:
         last_page (bool): True if it is the last page, False otherwise.
    """
    paginator = id_search.find("div", class_="paginator--desktop")
    paginator_arrows = paginator.find_all("a", class_="paginator__arrow")
    last_page = 'disabled' == paginator_arrows[1].get('disabled','')
    return last_page


def single_page_scraping(url):
    """
    Downloads single page from <https://bt2stag.boataround.com/search?>
    and extracts list with search results for further analysis

    Args:
        url (str): The URL of the search page on bt2stag.boataround.com.

    Returns:
        search_list (list):
           a list of beautifulsoup elements representing individual search results.
           Each element corresponds to a boat listing on the search page.
           The list can be further analyzed for specific information.
    """

    # somtimes we get "No results found. Please, try your search again!"
    # Even thoug the page should exist.
    # There it is necessary to retry the download
    retries = 5  # Number of retries
    while True:
        for attempt in range(retries):
            response = down_page(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # In HTML `id` must be unique where as `class` can be applied to many things.
            # Just in case that there are multiple `"search-results-list"` we look for
            # `"search"` id at first, so we get the right part.

            # Even if we get "No results found" found message. This part is still present
            id_search = soup.find("div", id="search")

            # This one can be empty
            # need to check for that
            cl_search_results_list = id_search.find("section", {"class": "search-results-list"})
            # rewrite as `id_search.find("section", class_="search-results-list")`?

            if cl_search_results_list is None:
                if attempt < retries - 1:
                    print(f"Retry {attempt}: Section cl_search_results_list not found")
                    print(f"Retrying (Retry {attempt + 2}/{retries})...")
            #        print(f"{id_search}\n\n")
                else:
                    print("Max retries exceeded. Exiting. Restarting the session.")
                    #global session
                    #session.close()  # Close the existing session
                    #session = requests.Session()  # Create a new session
            else:
                break

    search_list = cl_search_results_list.find_all("li", class_="search-result-wrapper mt-4")
    last_page = check_page(id_search)
    return search_list, last_page


def process_list(search_list):
    """
    Processes the list of beautifulsoup elements representing
    individual search results, extracting basic information about each listed boat.

    Args:
        search_list (list):
           A list of beautifulsoup elements representing individual search results.
           Each element corresponds to a boat listing on the search page.
    Returns:
        page_data (list):
        A list of dictionaries, each containing the following information about a boat:
            - 'link': The href value of the boat's listing.
            - 'charter_name': The charter name extracted from the alt text of the charter's logo.
            - 'boat_name': The name of the boat extracted from the text
            of the 'span' with class 'mr-2'.
            - 'boat_length': The length of the boat extracted from
            the second 'li' in 'ul' with class 'search-result-middle__params-value'.
            - 'price': The price of the boat extracted from
            the text of the 'span' with class 'price-box__price ml-2'.
            - 'check_in': The check-in date extracted
            from the 'checkIn' query parameter in the boat's link.
            - 'check_out': The check-out date extracted
            from the 'checkOut' query parameter in the boat's link.
    """
    page_data = []

    for item in search_list:
        # Find the 'a' element within each 'li'
        anchor_tag = item.find('a')

        # Extract the 'href' value from the 'a' element
        href_value = anchor_tag.get('href', '')
        print(href_value)

        # Extract checkIn and checkOut values from href_value
        parsed_url = urlparse(href_value)
        query_params = parse_qs(parsed_url.query)
        check_in = query_params.get('checkIn', [''])[0]
        check_out = query_params.get('checkOut', [''])[0]

        # Extract text from the 'span' with class 'mr-2'
        span_mr_2_text = item.find('span', class_='mr-2').text.strip()

        # Extract text from the 'span' with class 'price-box__price ml-2'
        price_text = item.find('span', class_='price-box__price ml-2').text.strip()

        # simple but less robust
        # second_li_value = item.find_all(
        #         'div', class_='d-flex')[1].select_one(
        #                 'ul.search-result-middle__params-value li:nth-of-type(2)').text.strip()

       # get boat lengths

        d_flex_divs = item.find_all('div', class_='d-flex')

        # Iterate through the 'div' elements and select the one without 'pr-4'
        for div in d_flex_divs:
            length_item = div.find(
                    'ul', class_='search-result-middle__params-name').find(
                            "li", string=lambda text: "Length" in text)
#            print(f"\n\nlength item: {length_item}")
#            print(f"\n{div}")
            if length_item:
                # Get the index of the "Length" item in the list
                index_of_length = len(list(length_item.find_previous_siblings('li')))

                # Get the corresponding value from the adjacent ul
                # with class="search-result-middle__params-value"
                params_value_ul = length_item.find_next('ul',
                                                        class_='search-result-middle__params-value')

                # Get the value from the li inside params_value_ul based on the index
                if params_value_ul:
                    params_values = params_value_ul.find_all('li')
                    if 0 <= index_of_length < len(params_values):
                        length_value = params_values[index_of_length].get_text(strip=True)
                        break
                    print("Index out of range")
                else:
                    print("No value found")


            # div.select_one('li:nth-of-type(2)').text.strip():
                params_value_ul = div.find('ul', class_='search-result-middle__params-value')
                break

        ## Iterate through the 'div' elements and select the one without 'pr-4'
        #params_value_ul = None
        #for div in d_flex_divs:
        #    print(f"\n\n{div}")
        #    if 'Length' in div.select_one(
        #            'ul.search-result-middle__params-name li:nth-of-type(2)').text.strip():
        #    # div.select_one('li:nth-of-type(2)').text.strip():
        #        params_value_ul = div.find('ul', class_='search-result-middle__params-value')
        #        break

        ## Extract the value from the second 'li' inside 'ul'
        ## with class 'search-result-middle__params-value'
        #second_li_value = params_value_ul.select_one(
        #        'li:nth-of-type(2)').text.strip() if params_value_ul else ''

        # Get charter name

        # Find the 'div' with class 'search-result-right__charter'
        d_picture = item.find_all('div', class_='search-result-right__charter')

        # Extract the 'alt' text from the 'img' tag
#        img_alt = d_picture[0].find('img').get('alt', '')

        # Append the extracted values to the page_data list
        page_data.append({
            'link': href_value,
#            'charter_name': img_alt,
            'boat_name': span_mr_2_text,
            'boat_length': length_value,
            'price': price_text,
            'check_in': check_in,
            'check_out': check_out,
        })

    return page_data

def all_pages_scraping(url):
    """
    Given a URL with search results, it iterates through all pages of
    the search results and downloads them.

    Args:
        url (str): The URL of the search page on bt2stag.boataround.com.
            The expected format of the URL is:
            f"https://bt2stag.boataround.com/search?" \
            f"destinations={destination_name}-1&checkin={yyyy-mm-dd}&checkout={yyyy-mm-dd}"


    Returns:
    page_data (list):
    a list of dictionaries, each containing the information about available boats.
    """
    date_data = []
    last_page = False
    page_number = 1

    while not last_page:
        search_list, last_page = single_page_scraping(url + "&page=" + str(page_number))
        page_data = process_list(search_list)
        date_data.extend(page_data)
        print(f"page number: {page_number}, last page: {last_page}")
        page_number = page_number + 1

    return date_data

def gen_dates(start_date_str, end_date_str):
    """
    Generates list of dates.

    Args:
    start_date_str (str): Starting date in format "yyyy-mm-dd"
    end_date_str  (str): Ending date in format "yyyy-mm-dd"

    Returns:
        list: A list of dates between the start and end dates (inclusive).
    """
    # Convert input strings to datetime objects
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    # define the start and end dates
    #start_date = datetime(2024, 5, 1)
    #end_date = datetime(2024, 9, 30)

    # initialize an empty list to store the saturdays
    saturdays = []

    # iterate through the dates from start_date to end_date
    current_date = start_date
    while current_date <= end_date:
        # check if the current date is a saturday (weekday() returns 5 for saturday)
        if current_date.weekday() == 5:
            # append the formatted date to the list
            saturdays.append(current_date.strftime('%y-%m-%d'))

        # move to the next day
        current_date += timedelta(days=1)
    return saturdays



def all_dates_scraping(destination="split-1",
                       start_date_str='2024-05-01', end_date_str='2024-09-30'):
    """
    Downloads all information about available boats for give destination and time frame.

    Args:
    destination (str, optional): ID of the destination as used
    on the site `https://bt2stag.boataround.com/`
    start_date_str (str, optional): Starting date in the  format "yyyy-mm-dd".
    end_date_str  (str, optional): Ending date in the format "yyyy-mm-dd".

    Returns:
        list: A list of dictionaries, each containing information about available boats.
    """
    location_data = []
    saturdays = gen_dates(start_date_str, end_date_str)
    for nth_saturday in range(len(saturdays)-1):
        check_in_date = saturdays[nth_saturday]
        check_out_date = saturdays[nth_saturday + 1]
        url = (
                f"https://bt2stag.boataround.com/search?destinations={destination}"
                f"&checkIn={check_in_date}&checkOut={check_out_date}"
                )
        print(url)
        date_data = all_pages_scraping(url)
        location_data.extend(date_data)
    return location_data
