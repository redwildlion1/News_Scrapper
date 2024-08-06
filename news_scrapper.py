import subprocess
import zipfile
from datetime import datetime, timedelta
import time
import re
import chromedriver_binary
import requests
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions as selenium_exceptions
import pandas as pd


# def check_and_install_chrome():
#     try:
#         result = subprocess.run(["google-chrome", "--version"], check=True, capture_output=True, text=True)
#         if "127.0.6533.88" not in result.stdout:
#             raise FileNotFoundError("Incorrect Chrome version")
#     except (FileNotFoundError, subprocess.CalledProcessError):
#         print("Google Chrome 127.0.6533.88 not found. Installing...")
#         try:
#             update_result = subprocess.run(["sudo", "-S", "apt-get", "update"], input="L@urentiu2003\n", text=True,
#                                            capture_output=True)
#             print(update_result.stdout)
#             print(update_result.stderr)
#         except subprocess.CalledProcessError as e:
#             print(f"Failed to update package list: {e}")
#             print(e.stdout)
#             print(e.stderr)
#
#         try:
#             url = "https://storage.googleapis.com/chrome-for-testing-public/127.0.6533.88/linux64/chrome-linux64.zip"
#             zip_path = "/tmp/chrome-linux64.zip"
#             extract_path = "/tmp/chrome-linux64"
#
#             # Download the zip file
#             response = requests.get(url)
#             with open(zip_path, 'wb') as file:
#                 file.write(response.content)
#
#             # Unpack the zip file
#             with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#                 zip_ref.extractall(extract_path)
#
#             # Create the directory if it does not exist
#             subprocess.run(["sudo", "-S", "mkdir", "-p", "/opt/google/chrome/bin"], input="L@urentiu2003\n", text=True)
#             subprocess.run(["sudo", "-S", "chmod", "-R", "755", "/opt/google/chrome"], input="L@urentiu2003\n",
#                            text=True)
#             subprocess.run(["sudo", "-S", "chown", "-R", "root:root", "/opt/google/chrome"], input="L@urentiu2003\n",
#                            text=True)
#             subprocess.run(["sudo", "-S", "chmod", "755", f"{extract_path}/chrome-linux64/chrome"],
#                            input="L@urentiu2003\n", text=True)
#
#             # Install Chrome
#             install_result = subprocess.run(
#                 ["sudo", "-S", "cp", f"{extract_path}/chrome-linux64/chrome", "/opt/google/chrome/bin/"],
#                 input="L@urentiu2003\n", text=True, capture_output=True)
#             print(install_result.stdout)
#             print(install_result.stderr)
#
#             # Create a symlink
#             subprocess.run(["sudo", "-S", "ln", "-sf", "/opt/google/chrome/bin/chrome", "/usr/bin/google-chrome"],
#                            input="L@urentiu2003\n", text=True)
#
#             # Reload systemd units
#             subprocess.run(["sudo", "-S", "systemctl", "daemon-reload"], input="L@urentiu2003\n", text=True)
#         except subprocess.CalledProcessError as e:
#             print(f"Failed to install Chrome: {e}")
#             print(e.stdout)
#             print(e.stderr)
#         except Exception as e:
#             print(f"Error: {e}")
#
#
# def check_and_install_chromedriver():
#     try:
#         # Check if chromedriver is installed and matches the required version
#         result = subprocess.run(["chromedriver", "--version"], check=True, capture_output=True, text=True)
#         if "127.0.6533.88" not in result.stdout:
#             raise FileNotFoundError("Incorrect ChromeDriver version")
#     except (FileNotFoundError, subprocess.CalledProcessError):
#         print("ChromeDriver 127.0.6533.88 not found. Installing...")
#         try:
#             url = "https://chromedriver.storage.googleapis.com/127.0.6533.88/chromedriver_linux64.zip"
#             zip_path = "/tmp/chromedriver_linux64.zip"
#             extract_path = "/tmp/chromedriver_linux64"
#
#             # Download the zip file
#             response = requests.get(url)
#             with open(zip_path, 'wb') as file:
#                 file.write(response.content)
#
#             # Unpack the zip file
#             with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#                 zip_ref.extractall(extract_path)
#
#             # Move chromedriver to /usr/local/bin
#             subprocess.run(["sudo", "-S", "mv", f"{extract_path}/chromedriver", "/usr/local/bin/"],
#                            input="L@urentiu2003\n", text=True)
#             subprocess.run(["sudo", "-S", "chmod", "755", "/usr/local/bin/chromedriver"], input="L@uretiu2003\n",
#                            text=True)
#         except subprocess.CalledProcessError as e:
#             print(f"Failed to install ChromeDriver: {e}")
#             print(e.stdout)
#             print(e.stderr)
#         except Exception as e:
#             print(f"Error: {e}")


def create_excel_file_type(file_name, headers, data):
    # Create a DataFrame with the headers and data
    df = pd.DataFrame(data, columns=headers)
    # Write the DataFrame to an Excel file
    df.to_excel(file_name, index=False)


def wait_for_text_change(driver, by, value, initial_text, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.find_element(by, value).text != initial_text
        )
    except Exception as e:
        print(f"Error: {e}")
        driver.quit()


def find_element_by_class(driver, class_name):
    try:
        # Wait until the element is visible
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, class_name))
        )
        return element
    except selenium_exceptions.TimeoutException as e:
        print(f"Error: {e}")
        driver.quit()


def extract_big_number(text):
    # Use regular expression to find the number in the string
    match = re.search(r'of\s([\d,]+)', text)
    if match:
        # Remove commas and convert to integer
        big_number = int(match.group(1).replace(',', ''))
        return big_number
    return None


class NewsScrapper:
    def __init__(self, search_query="example", category="California", num_months=1):
        self.all_articles_data = []
        self.current_page = 1
        self.max_pages = 10
        self.continue_search = True
        self.search_query = search_query
        self.category = category
        self.num_months = num_months
        self.url = "https://www.latimes.com/search?q=" + self.search_query + "&s=1"
        path = chromedriver_binary
        self.options = Options()
        self.options.add_argument("--headless=new")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        try:
            self.driver = webdriver.Chrome(options=self.options)
            self.driver.get(self.url)
            self.driver.maximize_window()
        except Exception as e:
            print(e)
            self.driver.quit()
            print("Driver closed like a bitch")

    @staticmethod
    def create_excel_file(data):
        file_name = 'articles.xlsx'
        headers = ['Image', 'Headline', 'Description', 'Date']
        create_excel_file_type(file_name, headers, data)

    def get_max_pages(self):
        page_count_full = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'search-results-module-page-counts'))
        ).text
        max_page_count = extract_big_number(page_count_full)
        self.max_pages = min(self.max_pages, max_page_count)

    def select_category(self):
        input_value = ''
        input_type = ''
        see_all_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'see-all-button'))
        )
        see_all_button.click()
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'search-filter-input'))
        )
        topics = self.driver.find_elements(By.CLASS_NAME, 'checkbox-input')
        print(len(topics))
        for topic in topics:
            print(topic.text)
            if topic.text == self.category:
                input_value = topic.find_element(By.CLASS_NAME, 'checkbox-input-element').get_attribute('value')
                input_type = topic.find_element(By.CLASS_NAME, 'checkbox-input-element').get_attribute('name')
                print(input_value)
                break
        self.driver.get(
            'https://latimes.com/search?q=' + self.search_query + '&' + input_type + '=' + input_value + '&s=1')
        time.sleep(3)

    def get_articles_on_page(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'search-results-module-main'))
            )
            articles = self.driver.find_elements(By.CLASS_NAME, 'promo-wrapper')
            print(len(articles))
            for article in articles:
                self.driver.execute_script("arguments[0].scrollIntoView();", article)
                image = article.find_element(By.CLASS_NAME, 'image')
                img_src = image.get_attribute('src')
                headline = article.find_element(By.CLASS_NAME, 'promo-title')
                print(headline.text)
                description = article.find_element(By.CLASS_NAME, 'promo-description')
                print(description.text)
                date = article.find_element(By.CLASS_NAME, 'promo-timestamp').text
                print(date)
                if '.' in date:
                    formated_date = datetime.strptime(date, '%b. %d, %Y')
                else:
                    formated_date = datetime.strptime(date, '%B %d, %Y')
                print(formated_date)
                self.all_articles_data.append([img_src, headline.text, description.text, date])
                if formated_date + timedelta(days=30) * self.num_months < datetime.now():
                    self.continue_search = False
                    print("Reached the end of the search by date")
                    break
        except Exception as e:
            print(f"Error: {e}")
            self.driver.quit()
            print("Driver closed")

    def get_next_page(self):
        if self.current_page <= self.max_pages:
            try:
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'search-results-module-next-page'))
                )
                next_button.click()
                self.current_page += 1
                print(f"Page: {self.current_page}")
                time.sleep(3)
            except Exception as e:
                print(f"Error: {e}")
                self.driver.quit()
                print("Driver closed")
        else:
            self.continue_search = False
            print("Reached the end of the search by page")


if __name__ == "__main__":
    # check_and_install_chrome()
    # check_and_install_chromedriver()
    news_scrapper = NewsScrapper()
    news_scrapper.select_category()
    news_scrapper.get_max_pages()
    while news_scrapper.continue_search:
        news_scrapper.get_articles_on_page()
        news_scrapper.get_next_page()
    news_scrapper.create_excel_file(news_scrapper.all_articles_data)
