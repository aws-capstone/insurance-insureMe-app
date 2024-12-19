import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run headless Chrome
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Path to your ChromeDriver
service = Service('/usr/local/bin/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)

# Retrieve the hostname from the environment variable 
#hostname = os.getenv('EC2_PUBLIC_IP', 'localhost') 
hostname = os.getenv('EC2_PUBLIC_IP') 
#webapp_url = f"http://{hostname}:8081"
webapp_url = f"http://localhost:8080"

test_results = []

def run_test_case(test_name, test_function):
    try:
        test_function()
        test_results.append(f"{test_name}: PASSED")
    except Exception as e:
        test_results.append(f"{test_name}: FAILED - {e}")

try:
    # Test Case 1: Check if the website is loading
    def test_case_1():
        print("Running Test Case 1: Check website loading")
        driver.get(webapp_url)
        driver.implicitly_wait(10)  # Wait up to 10 seconds for elements to become available
        print("Website loaded successfully.")

    run_test_case("Test Case 1", test_case_1)
    
    # Test Case 2: Validate the title of the website
    def test_case_2():
        print("Running Test Case 2: Validate title of website")
        expected_title = "Insure-me"  # Replace with the actual expected title
        assert expected_title in driver.title, f"Title does not match: {driver.title}"
        print("Title validated successfully.")
        
    run_test_case("Test Case 2", test_case_2)
    
    # Test Case 3: Look for the string "WELCOME TO CUSTOMER BANKING SERVICES"
    def test_case_3():
        print('Running Test Case 3: Look for the string "Best insurance for your family"')
        time.sleep(2)  # Give some time to ensure the page content is fully loaded
        specific_string = "Best insurance for your family"
        assert specific_string in driver.page_source, f'The string "{specific_string}" is not found on the webpage.'
        print(f'The string "{specific_string}" is present on the webpage.')
        
    run_test_case("Test Case 3", test_case_3)
    
except Exception as e:
    print(f"An error occurred during test setup: {e}")

finally:
    # Close the browser
    driver.quit()
    # Print all test results
    print("\nTest Results:")
    all_passed = True
    for result in test_results:
        print(result)
        if "FAILED" in result:
            all_passed = False
    
    # Exit with code 0 if all tests passed, 1 otherwise
    if all_passed:
        sys.exit(0)
    else:
        sys.exit(1)
