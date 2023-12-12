"""
Boat Reservation Testing Module

This module performs testing of the boat reservation functionality
on the BoatAround website using the Chromium browser.

Functions:
- `wait_for_element(driver, by_attribute, value, timeout=10)`:
Waits for the specified element to be present on the webpage.
- `check_js_error(driver, screenshot_name='javascript_error_screenshot.png')`:
Check for JavaScript errors and general browser logs in the console and capture a screenshot.
- `close_overlay(driver)`:
Closes an overlay on the website if present; otherwise, continues script execution.
- `dates_from_url(url)`: Extracts check-in and check-out values from the URL.
- `dates_from_list(date_listed)`:
Extracts check-in and check-out dates from a string in the format 'DD/MM/YYYY - DD/MM/YYYY'.
- date_conversion(check_in, check_out):
        Convert date strings in format 'YYYY-MM-DD' to a formatted of '1 Dec 2023'.
- `web_test(destinations="Croatia",
             check_in="2024-06-01", check_out="2024-06-08", nth_boat_from_list = 2)`:
        Executes the entire website testing process.

Dependencies:
- `time`: Provides time-related functions for introducing delays in the script.
- `datetime`: Supports date and time manipulation.
- `urllib.parse`: Parses URLs and extracts components.
- `selenium.webdriver`: Provides a WebDriver implementation for browser automation.
- `selenium.webdriver.common.keys`: Defines keys used for simulating keyboard input.
- `selenium.webdriver.common.by`: Provides mechanisms for locating elements on a webpage.
- `selenium.webdriver.support.ui.WebDriverWait`: Implements waiting mechanisms for element presence.
- `selenium.webdriver.support.expected_conditions`: Defines expected conditions for waiting.
"""

import sys
import platform
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def wait_for_element(driver, by_attribute, value, timeout=15):
    """
    `wait_for_element(driver, by_attribute, value, timeout=10)`: 
        Waits for the specified element to be present on the webpage.

        Parameters:
        - `driver` (selenium.webdriver.Chrome): The Selenium WebDriver instance.
        - `by_attribute` (selenium.webdriver.common.by):
        The method of locating the element (e.g., By.ID).
        - `value` (str): The value of the attribute to search for.
        - `timeout` (int, optional): Maximum time to wait for the element to be present
        (default is 10 seconds).

    Returns:
    - selenium.webdriver.remote.webelement.WebElement: The located element.
    waits for element
    """
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by_attribute, value))
    )

def check_js_error(driver, screenshot_name='javascript_error_screenshot.png'):
    """
    Check for JavaScript errors and general browser logs in the console and capture a screenshot.

    Args:
        driver (WebDriver): The Selenium WebDriver instance representing the browser session.
        screenshot_name (str, optional): The name of the screenshot file to be saved.
            Defaults to 'javascript_error_screenshot.png'.

    Returns:
        None

    Notes:
        This function retrieves both JavaScript errors and general browser logs
        from the browser console using the provided WebDriver.
        For each log entry, it prints the message, saves a screenshot,
        and can be extended for further error handling or logging.
    """
    error_logs = driver.get_log('browser')
    for entry in error_logs:
        print(f"JavaScript Error: {entry['message']}")
        driver.save_screenshot(screenshot_name)
        #    if entry['level'] == 'SEVERE':

def close_overlay(driver):
    """
    `close_overlay(driver)`: 
        Closes an overlay on the website if present; otherwise, continues script execution.

    Parameters:
        - `driver` (selenium.webdriver.Chrome): The Selenium WebDriver instance.
    Closes overlay on website if presents. Otherwise catches the error and let's script
    continue.
    """
    try:
        close_overlay_btn = wait_for_element(driver, By.CLASS_NAME, "overlay-modal__close")
        close_overlay_btn.click()
    except (TimeoutException, NoSuchElementException):
        # Handle the case where the overlay did not appear within the specified time
        print("Overlay did not appear or close button not found. Continuing further.")

def dates_from_url(url):
    """
    `dates_from_url(url)`: 
        Extracts check-in and check-out values from the URL.

        Parameters:
        - `url` (str): The URL containing check-in and check-out parameters.

        Returns:
        - Tuple[str, str]: A tuple containing check-in and check-out date strings.
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    check_in = query_params.get('checkIn', [''])[0]
    check_out = query_params.get('checkOut', [''])[0]
    return check_in, check_out

def dates_from_list(date_listed):
    """
    `dates_from_list(date_listed)`: 
        Extracts check-in and check-out dates from a string
        in the format 'DD/MM/YYYY - DD/MM/YYYY'
        to two strings both in format 'YYYY-MM-DD'
        Might cause problem if other language mutations of the website
        have different date fromating.


        Parameters:
        - `date_listed` (str): The date string in the specified format.

        Returns:
        - Tuple[str, str]: A tuple containing formatted
        check-in and check-out date strings.
    """
    # Split the string based on the '-' character
    dates = date_listed.split('-')

    # Remove leading and trailing spaces from the resulting strings
    next_check_in_listed = dates[0].strip()
    next_check_out_listed = dates[1].strip()

    # Parse the date strings
    check_in_date = datetime.strptime(next_check_in_listed, '%d/%m/%Y')
    check_out_date = datetime.strptime(next_check_out_listed, '%d/%m/%Y')

    # Format the dates in the desired format
    formatted_check_in = check_in_date.strftime('%Y-%m-%d')
    formatted_check_out = check_out_date.strftime('%Y-%m-%d')
    return formatted_check_in, formatted_check_out

def date_conversion(check_in, check_out):
    """
    Convert date strings to a formatted representation based on the operating system.

    Args:
        check_in (str): The check-in date string in the format 'yyyy-mm-dd'.
        check_out (str): The check-out date string in the format 'yyyy-mm-dd'.

    Returns:
        Tuple[str, str]: A tuple containing the formatted check-in and check-out dates
        in format '1 Dec 2024'.

    Notes:
        This function parses the input date strings, determines the operating system,
        and formats the dates accordingly.
        The format specifier is chosen based on the operating system.
        On Windows, leading zeroes in the day are omitted ('%#d'),
        while on UNIX-like systems, leading zeroes are preserved ('%-d').
        The formatted dates are then returned as a tuple.
    """
    # Parse the date strings
    check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
    check_out_date = datetime.strptime(check_out, '%Y-%m-%d')

    # Syntax for omitting leading zeroes works differently
    # on Windows than on other platforms
    current_os = platform.system()

    # Choose the appropriate format specifier based on the operating system
    if current_os == 'Windows':
        format_specifier = '%#d %b %Y'
    else:  # Assume UNIX-like systems
        format_specifier = '%-d %b %Y'

    # Format the dates using the chosen format specifier
    formatted_check_in = check_in_date.strftime(format_specifier)
    formatted_check_out = check_out_date.strftime(format_specifier)
    return formatted_check_in, formatted_check_out

def web_test(destinations="Croatia",
             check_in="2024-06-01", check_out="2024-06-08", nth_boat_from_list = 2):
    """
    Execute the entire website testing process.

    This function performs a series of actions, including opening the website,
    interacting with elements, and validating results.

    Parameters:
        destinations (str): The destination to search for available boats (default is "Croatia").
        check_in (str): The check-in date in the format 'YYYY-MM-DD' (default is "2024-06-01").
        check_out (str): The check-out date in the format 'YYYY-MM-DD' (default is "2024-06-08").
        nth_boat_from_list (int): The index of the boat to select from
        the search results list (default is 2).

    Returns:
        None

    Notes:
        This function automates the testing process on the Boataround website. It interacts with
        various elements, performs searches, validates results, and captures screenshots on errors.
        The function uses the Chrome webdriver for testing.

    Raises:
        SystemExit: If the specified nth_boat_from_list is out of bounds.
    """
    driver = webdriver.Chrome()

    try:
        driver.get("https://bt2stag.boataround.com") # Code to interact with the page
    except Exception as general_exception:
        # Take a screenshot on error
        driver.save_screenshot('homepage_error_screenshot.png')
        print(f"An error occurred on homepage: {str(general_exception)}")

    check_js_error(driver, 'homepage_javascript_error_screenshot.png')

    # there is overlay prompting user to subscribe to newsletter
    # real user would close it, this simulate this behavour
    # might not be always present on the website
    close_overlay(driver)

    time.sleep(1)

    destination_input = wait_for_element(driver, By.ID, "elastic-autocomplete")
    destination_input.send_keys(destinations)

    time.sleep(1)

    calendar_input =  wait_for_element(driver, By.ID, 'calendar-3-input')
    calendar_input.click()

    # current calendar month has index zero, later
    # for other month, month that is displayed in the calendar
    # on the left has index 1
    # on the right has index 2
    month_index = 0
    max_next = 60 # user is unlikely to reserve more than 5 years in advance
    for _ in range(max_next):
        all_month_elements = driver.find_elements(By.CLASS_NAME, 'calendar-3__month')
        current_month = all_month_elements[month_index].find_element(
                By.CLASS_NAME, 'calendar-3__month-year').get_attribute("innerText")
        if 'June, 2024' in current_month:
            break  # exit the loop if the condition is met
        next_month_btn = wait_for_element(driver, By.CLASS_NAME, 'calendar-3__btn--next')
        next_month_btn.click()
        if month_index == 0:
            month_index = 1
        time.sleep(1)

    check_in_date, check_out_date = date_conversion(check_in, check_out)

    time.sleep(1)
    table = all_month_elements[0].find_element(By.CLASS_NAME, 'calendar-3__dates')
    check_in_date_btn = table.find_elements(
            By.XPATH,'//td[button[@title="' + check_in_date + '"]]//button')
    check_in_date_btn[1].click()

    time.sleep(1)
    check_in_out_btn = table.find_elements(
            By.XPATH,'//td[button[@title="' + check_out_date + '"]]//button')
    check_in_out_btn[1].click()

    time.sleep(1)
    search_btn =  wait_for_element(driver, By.CLASS_NAME, 'basic-search__button')

    try:
        search_btn.click()
    except Exception as general_exception:
        # Take a screenshot on error
        driver.save_screenshot('searchpage_error_screenshot.png')
        print(f"An error occurred on search page: {str(general_exception)}")

    check_js_error(driver, 'searchpage_javascript_error_screenshot.png')

    time.sleep(10)

    max_retries = 5
    for attempt in range(max_retries):
        time.sleep(1)
        id_search = wait_for_element(driver, By.ID, 'search')
        cl_search_results_list = id_search.find_element(
                By.CLASS_NAME, 'search-results-list')
        search_list = cl_search_results_list.find_elements(
                By.CLASS_NAME, 'search-result-wrapper')
        if search_list == []:
            print("Search result not displayed. Refreshing current page")
            driver.save_screenshot('search_error_screenshot' + str(attempt) + '.png')
            time.sleep(2)  # Add a delay between retries
            driver.refresh()
        break

    if (nth_boat_from_list -  1 >= len(search_list)) or  (nth_boat_from_list <= - len(search_list)):
        print("nth_boat_from_list out of bound")
        print(f"Max value for current search list is {len(search_list)}")
        print("Exiting")
        sys.exit(1)

    try:
        search_list[nth_boat_from_list - 1].click()
    except Exception as general_exception:
        # Take a screenshot on error
        driver.save_screenshot('boatpage_error_screenshot.png')
        print(f"An error occurred on boat page: {str(general_exception)}")

    check_js_error(driver, 'boatpage_javascript_error_screenshot.png')

    # switching driver to a new tab
    # Get the list of all window handles
    all_handles = driver.window_handles

    # Switch to the newly opened tab
    new_tab_handle = all_handles[-1]
    driver.switch_to.window(new_tab_handle)

    time.sleep(5)
    ava_list_wrapper = wait_for_element(driver, By.CLASS_NAME, "ava-list-wrapper")
    driver.execute_script("arguments[0].scrollIntoView(true);", ava_list_wrapper)
    time.sleep(5)

    # list items 0-3 are empty, 4 is behind left arrow button
    # the selected date is 5
    # next date is 6
    # only dates 5-9 are clickable
    ava_list = ava_list_wrapper.find_elements(By.CLASS_NAME, 'ava-item')

    # Checks if product page display available booking option for the specified dates
    selected_date_url = driver.current_url
    selected_check_in_url, selected_check_out_url = dates_from_url(selected_date_url)
    selected_date_listed = ava_list[5].find_element(
            By.CLASS_NAME, 'ava-date').get_attribute("innerText")

    if not check_in == selected_check_in_url:
        print("Searched and displayed dates don't match")
        print(f"check_in: {check_in}\n"
              "selected_check_in_url: {selected_check_in_url}")

    if not check_out == selected_check_out_url:
        print("Searched and displayed dates don't match")
        print(f"check_out: {check_out}\n"
              "selected_check_out_url: {selected_check_out_url}")

    selected_check_in_listed, selected_check_out_listed = dates_from_list(selected_date_listed)
    if not selected_check_in_listed == selected_check_in_url:
        print("Selected date check in dates don't match")
        print(f"selected_check_in_listed: {selected_check_in_listed}\n"
              "selected_check_in_url: {selected_check_in_url}")

    if not selected_check_out_listed == selected_check_out_url:
        print("Selected date check out dates don't match")
        print(f"selected_check_out_listed: {selected_check_out_listed}\n"
              "selected_check_out_url: {selected_check_out_url}")

    all_reserved = False
    for a_index in range(6,10):
        availability_label = ava_list[a_index].find_element(
                By.CLASS_NAME, 'availability-label').get_attribute("innerText")
        if availability_label != 'Reserved':
            ava_index = a_index
            break
        if a_index == 9:
            print("All 4 closest dates are reserved")
            all_reserved = True
            driver.save_screenshot('boat_reserved_screenshot.png')

    # First check if first date is available and has price
    selected_availability_label = ava_list[5].find_element(
                By.CLASS_NAME, 'availability-label').get_attribute("innerText")

    if selected_availability_label == 'Reserved':
        print("Searched date is already reserved!")
        driver.save_screenshot('searched_date_reserved_screenshot.png')
        if all_reserved:
            print("All dates on the page are reserved")
            driver.save_screenshot('all_dates_reserved_screenshot.png')
            print("Exiting")
            sys.exit(1)

    if not all_reserved:
        # clicking on first available option after selected dates
        ava_list[ava_index].click()

        # save url after click operation
        # used to chcekc if The product pag has updated checkIn and checkOut params in url
        next_date_url = driver.current_url
        next_check_in_url, next_check_out_url = dates_from_url(next_date_url)

        if selected_date_url == next_date_url:
            print(f"Urls did not change.\nurl:{selected_date_url}")

        next_date_listed = ava_list[ava_index].find_element(
                By.CLASS_NAME, 'ava-date').get_attribute("innerText")
        next_check_in_listed, next_check_out_listed = dates_from_list(next_date_listed)

        if not next_check_in_listed == next_check_in_url:
            print("Next date check in dates don't match")
            print(f"next_check_in_listed: {next_check_in_listed}\n"
                  "next_check_in_url: {next_check_in_url}")

        if not next_check_out_listed == next_check_out_url:
            print("Next date check out dates don't match")
            print(f"next_check_out_listed: {next_check_out_listed}\n"
                  "next_check_out_url: {next_check_out_url}")

    # Comparing prices and clicking on the cheaper one

    if selected_availability_label != 'Reserved':
        selected_date = ava_list[5].find_element(
                By.CLASS_NAME, 'ava-price').get_attribute("innerText")
        next_date = ava_list[ava_index].find_element(
                By.CLASS_NAME, 'ava-price').get_attribute("innerText")
        selected_date_price = int(''.join(filter(str.isdigit, selected_date)))
        next_date_price = int(''.join(filter(str.isdigit, next_date)))
        if selected_date_price < next_date_price:
            ava_list[5].click()


    reserve_btn = driver.find_elements(By.CLASS_NAME, 'stateful-button__button')

    # items 0 (top of the page), 2 (bottom of the page) are 'Reserve'
    # item 1 is 'Search'
    # items 3 'Request a quote'
    reserve_btn = driver.find_elements(By.CLASS_NAME, 'stateful-button')

    # we need to scroll to the button before clicking
    # otherwise it doesn't react
    driver.execute_script("arguments[0].scrollIntoView(true);", reserve_btn[2])
    time.sleep(5)

    try:
        reserve_btn[2].click()
    except Exception as general_exception:
        # Take a screenshot on error
        driver.save_screenshot('enter_details_error_screenshot.png')
        print(f"An error occurred on enter your details page: {str(general_exception)}")

    check_js_error(driver, 'enter_details_javascript_error_screenshot.png')
