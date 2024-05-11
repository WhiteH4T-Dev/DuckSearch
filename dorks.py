import os
import argparse
import json
import csv
from prettytable import PrettyTable
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
            wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'article[data-testid="result"]')))
            current_page = 1
            while current_page <= pages:
                self._extract_results_on_page(results)
                if not self._navigate_to_next_page(wait):
                    break
                current_page += 1
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
            more_results_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#more-results")))
            more_results_button.click()
            wait.until(EC.staleness_of(more_results_button))
            wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'article[data-testid="result"]')))
            return True
        except TimeoutException:
            return False

class CustomHelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog):
        super().__init__(prog, max_help_position=50)

    def format_help(self):
        table = PrettyTable()
        table.field_names = ["Option", "Value", "Function"]
        table.align = "l"
        table.add_row(["--query", "query", "Search query to execute (not with --dorks)"])
        table.add_row(["--pages", "number", "Maximum number of pages to fetch"])
        table.add_row(["--headless", "null", "Run browser in headless mode"])
        table.add_row(["--driver", "path", "Path to Chromedriver"])
        table.add_row(["--export", "format", "Export format for the results (text, json, csv)"])
        table.add_row(["--domain", "domain", "Specify a domain to scan (example.com)"])
        dork_types = [
            ('exposed_docs', 'Publicly exposed documents'), 
            ('dir_listing', 'Directory listing vulnerabilities'), 
            ('config_files', 'Configuration files exposed'), 
            ('database_files', 'Database files exposed'),
            ('log_files', 'Log files exposed'), 
            ('backup_files', 'Backup and old files'), 
            ('login_pages', 'Login pages'), 
            ('sql_errors', 'SQL errors'),
            ('php_errors', 'PHP errors / warning'), 
            ('phpinfo', 'phpinfo()'), 
            ('pastebin', 'Search pastebin.com / pasting sites'), 
            ('github_gitlab', 'Search github.com and gitlab.com'), 
            ('stackoverflow', 'Search stackoverflow.com'), 
            ('signup_pages', 'Signup pages'), 
            ('find_subdomains', 'Find Subdomains'),
            ('find_sub_subdomains', 'Find Sub-Subdomains'), 
            ('wayback_machine', 'Search in Wayback Machine'), 
            ('show_ips', 'Show only IP addresses')
        ]
        for dork_type, description in dork_types:
            table.add_row(["--dorks", f"{dork_type}", description])

        return str(table)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Search DuckDuckGo from the command line using advanced search techniques.', formatter_class=CustomHelpFormatter)
    parser.add_argument('--pages', type=int, help='Max number of pages to fetch')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--driver', type=str, default='', help='Path to Chromedriver')
    parser.add_argument('--export', type=str, choices=['text', 'json', 'csv'], help='Export format for the results')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--query', type=str, help='Search query to execute')
    group.add_argument('--dorks', type=str, choices=[
        'exposed_docs', 'dir_listing', 'config_files', 'database_files', 'log_files', 'backup_files',
        'login_pages', 'sql_errors', 'php_errors', 'phpinfo', 'pastebin', 'github_gitlab',
        'stackoverflow', 'signup_pages', 'find_subdomains', 'find_sub_subdomains',
        'wayback_machine', 'show_ips'
    ], help='Choose a predefined Google Dork search')
    parser.add_argument('--domain', type=str, default='', help='Specify a domain to focus the dork search, e.g., "cia.gov"')

    args = parser.parse_args()
    return args, parser

def apply_dork(dork, domain):
    dorks = {
        'exposed_docs': "site:{} ext:doc | ext:docx | ext:odt | ext:rtf | ext:sxw | ext:psw | ext:ppt | ext:pptx | ext:pps | ext:csv",
        'dir_listing': "site:{} intitle:index.of",
        'config_files': "site:{} ext:xml | ext:conf | ext:cnf | ext:reg | ext:inf | ext:rdp | ext:cfg | ext:txt | ext:ora | ext:ini | ext:env",
        'database_files': "site:{} ext:sql | ext:dbf | ext:mdb",
        'log_files': "site:{} ext:log",
        'backup_files': "site:{} ext:bkf | ext:bkp | ext:bak | ext:old | ext:backup",
        'login_pages': "site:{} inurl:login | inurl:signin | intitle:Login | intitle:'sign in' | inurl:auth",
        'sql_errors': "site:{} intext:'sql syntax near' | intext:'syntax error has occurred' | intext:'incorrect syntax near' | intext:'unexpected end of SQL command' | intext:'Warning: mysql_connect()' | intext:'Warning: mysql_query()' | intext:'Warning: pg_connect()'",
        'php_errors': "site:{} 'PHP Parse error' | 'PHP Warning' | 'PHP Error'",
        'phpinfo': "site:{} ext:php intitle:phpinfo 'published by the PHP Group'",
        'pastebin': "site:pastebin.com | site:paste2.org | site:pastehtml.com | site:slexy.org | site:snipplr.com | site:snipt.net | site:textsnip.com | site:bitpaste.app | site:justpaste.it | site:heypasteit.com | site:hastebin.com | site:dpaste.org | site:dpaste.com | site:codepad.org | site:jsitor.com | site:codepen.io | site:jsfiddle.net | site:dotnetfiddle.net | site:phpfiddle.org | site:ide.geeksforgeeks.org | site:repl.it | site:ideone.com | site:paste.debian.net | site:paste.org | site:paste.org.ru | site:codebeautify.org | site:codeshare.io | site:trello.com",
        'github_gitlab': "site:github.com | site:gitlab.com",
        'stackoverflow': "site:stackoverflow.com",
        'signup_pages': "site:{} inurl:signup | inurl:register | intitle:Signup",
        'find_subdomains': "site:*.*.{}",
        'find_sub_subdomains': "site:*.*.*.{}",
        'wayback_machine': "https://web.archive.org/web/*/{}./*",
        'show_ips': "({}) (site:*.*.{0}.* | site:*.*.{1}.* | site:*.*.{2}.* | site:*.*.{3}.* | site:*.*.{4}.* | site:*.*.{5}.* | site:*.*.{6}.* | site:*.*.{7}.* | site:*.*.{8}.* | site:*.*.{9}.* | site:*.*.{10}.* | site:*.*.{11}.* | site:*.*.{12}.* | site:*.*.{13}.* | site:*.*.{14}.* | site:*.*.{15}.* | site:*.*.{16}.* | site:*.*.{17}.* | site:*.*.{18}.* | site:*.*.{19}.* | site:*.*.{20}.* | site:*.*.{21}.* | site:*.*.{22}.* | site:*.*.{23}.* | site:*.*.{24}.* | site:*.*.{25}.* | site:*.*.{26}.* | site:*.*.{27}.* | site:*.*.{28}.* | site:*.*.{29}.* |)"
    }
    domain = domain if domain else 'example.com'
    return dorks[dork].format(domain)

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
    if args.dorks:
        query = apply_dork(args.dorks, args.domain if args.domain else 'example.com')
    else:
        query = args.query if not args.domain else f"site:{args.domain} {args.query}"

    searcher = DuckDuckGoSearch(driver_path=args.driver, headless=args.headless)
    results = searcher.fetch_search_results(query, args.pages or 1)  # Default to 1 page if not specified
    if args.export:
        export_results(results, args.export)
    else:
        export_results(results, 'text')
