"""
Boat Reservation Testing Module

This module performs testing of the boat reservation functionality on the BoatAround website using the Chromium browser.

Functions:
- `wait_for_element(driver, by_attribute, value, timeout=10)`: Waits for the specified element to be present on the webpage.
- `close_overlay(driver)`: Closes an overlay on the website if present; otherwise, continues script execution.
- `dates_from_url(url)`: Extracts check-in and check-out values from the URL.
- `dates_from_list(date_listed)`: Extracts check-in and check-out dates from a string in the format 'DD/MM/YYYY - DD/MM/YYYY'.
- `web_test()`: Executes the entire website testing process.

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

import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def wait_for_element(driver, by_attribute, value, timeout=10):
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


def web_test():
    """
    Executes the entire website testing process.

    This function performs a series of actions, including opening the website,
    interacting with elements, and validating results.

    Parameters:
    - None

    Returns:
    - None
    """
    driver = webdriver.Chrome()
    driver.get("https://bt2stag.boataround.com")
    assert "Boataround" in driver.title

    # there is overlay prompting user to subscribe to newsletter
    # real user would close it, this simulate this behavour
    # might not be always present on the website
    close_overlay(driver)

    time.sleep(1)

    destination_input = wait_for_element(driver, By.ID, "elastic-autocomplete")
    destination_input.send_keys("Croatia")

    time.sleep(1)

    calendar_input =  wait_for_element(driver, By.ID, 'calendar-3-input')
    calendar_input.click()

    # current calendar month has index zero, later
    # for other month, month that is displayed in the calendar
    # on the left has index 1
    # on the right has index 2
    month_index = 0
    while True:
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

    time.sleep(1)
    table = all_month_elements[0].find_element(By.CLASS_NAME, 'calendar-3__dates')
    check_in_date = table.find_elements(By.XPATH,'//td[button[@title="1 Jun 2024"]]//button')
    check_in_date[1].click()

    time.sleep(1)
    check_in_out = table.find_elements(By.XPATH,'//td[button[@title="8 Jun 2024"]]//button')
    check_in_out[1].click()


    time.sleep(1)
    search_btn =  wait_for_element(driver, By.CLASS_NAME, 'basic-search__button')
    search_btn.click()

    time.sleep(10)

    id_search = wait_for_element(driver, By.ID, 'search')
    cl_search_results_list = id_search.find_element(By.CLASS_NAME, 'search-results-list')

    search_list = cl_search_results_list.find_elements(By.CLASS_NAME, 'search-result-wrapper')

    if search_list == []:
        print("Search result not displayed. Refreshing current page")
        driver.refresh()

    # opens new tab with individual boat information
    search_list[1].click()

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
    ava_list = ava_list_wrapper.find_elements(By.CLASS_NAME, 'ava-item')

    ava_list[6].find_elements(By.CLASS_NAME, 'ava-price')

    # save current url
    selected_date_url = driver.current_url

    # clicking on first available option after selected dates
    ava_list[6].click()

    # save url after click operation
    # used to chcekc if The product pag has updated checkIn and checkOut params in url
    next_date_url = driver.current_url
    next_check_in_url, next_check_out_url = dates_from_url(next_date_url)

    if selected_date_url == next_date_url:
        print(f"Urls did not change.\nurl:{selected_date_url}")

    next_date_listed = ava_list[6].find_element(
            By.CLASS_NAME, 'ava-date').get_attribute("innerText")
    next_check_in_listed, next_check_out_listed = dates_from_list(next_date_listed)

    if not next_check_in_listed == next_check_in_url:
        print("Next date chcek in dates don't match")
        print(f"next_check_in_listed: {next_check_in_listed}\n"
              "next_check_in_url: {next_check_in_url}")

    if not next_check_out_listed == next_check_out_url:
        print("Next date chcek out dates don't match")
        print(f"next_check_out_listed: {next_check_out_listed}\n"
              "next_check_out_url: {next_check_out_url}")


    # Comparing prices and clicking on the cheaper one
    selected_date = ava_list[5].find_element(By.CLASS_NAME, 'ava-price').get_attribute("innerText")
    next_date = ava_list[6].find_element(By.CLASS_NAME, 'ava-price').get_attribute("innerText")

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
    reserve_btn[2].click()
    time.sleep(5)
