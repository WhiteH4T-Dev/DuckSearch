import os
import argparse
import json
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from typing import List, Dict, Optional

class DuckDuckGoSearch:
    def __init__(self, driver_path: Optional[str] = None, headless: bool = True):
        self.driver_path = driver_path or os.getenv('CHROMEDRIVER_PATH', '')
        self.headless = headless
        self.driver = self._init_driver()

    def _init_driver(self) -> webdriver.Chrome:
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        service = Service(executable_path=self.driver_path)
        return webdriver.Chrome(service=service, options=options)

    def fetch_search_results(self, query: str, pages: int) -> List[Dict[str, str]]:
        results = []
        try:
            url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'article[data-testid="result"]')))
            for _ in range(pages):
                self._extract_results_on_page(results)
                if not self._navigate_to_next_page(wait):
                    break

        except (TimeoutException, WebDriverException) as e:
            self.driver.save_screenshot('error_screenshot.png')
        finally:
            self.driver.quit()
        return results

    def _extract_results_on_page(self, results: List[Dict[str, str]]):
        search_items = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="result"]')
        for item in search_items:
            results.append({
                'title': item.find_element(By.CSS_SELECTOR, 'h2 a[data-testid="result-title-a"]').text,
                'link': item.find_element(By.CSS_SELECTOR, 'h2 a[data-testid="result-title-a"]').get_attribute('href'),
                'description': item.find_element(By.CSS_SELECTOR, 'div[data-result="snippet"]').text
            })

    def _navigate_to_next_page(self, wait: WebDriverWait) -> bool:
        try:
            more_results_button = wait.until(EC.element_to_be_clickable((By.ID, "more-results")))
            more_results_button.click()
            wait.until(EC.staleness_of(more_results_button))
            return True
        except TimeoutException:
            return False

def parse_arguments():
    parser = argparse.ArgumentParser(description='Search DuckDuckGo from the command line.')
    parser.add_argument('--query', type=str, help='Search query to execute')
    parser.add_argument('--pages', type=int, help='Max number of pages to fetch')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--driver', type=str, default='', help='Path to Chromedriver')
    parser.add_argument('--export', type=str, choices=['text', 'json', 'csv'], help='Export format for the results')
    args = parser.parse_args()
    return args, parser

def export_results(results, format_type):
    if format_type == 'text':
        for result in results:
            print(f"Title: {result['title']}\nLink: {result['link']}\nDescription: {result['description']}\n")
    elif format_type == 'json':
        with open('results.json', 'w') as file:
            json.dump(results, file, indent=4)
    elif format_type == 'csv':
        keys = results[0].keys()
        with open('results.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(results)

if __name__ == "__main__":
    args, parser = parse_arguments()
    if not args.query or not args.pages:
        parser.print_help()
    else:
        searcher = DuckDuckGoSearch(driver_path=args.driver, headless=args.headless)
        results = searcher.fetch_search_results(args.query, args.pages)
        if args.export:
            export_results(results, args.export)
        else:
            export_results(results, 'text')
