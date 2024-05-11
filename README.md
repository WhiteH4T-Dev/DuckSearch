## Introduction
DuckSearch is a command-line tool designed to scrape URLs from DuckDuckGo search results effortlessly. DuckDuckGo is known for its privacy-focused approach to internet searches, and this tool provides a convenient way to extract URLs while respecting users' privacy preferences. Whether you're conducting research, gathering data, or analyzing search trends, this tool streamlines the process of obtaining relevant URLs from DuckDuckGo's search engine.

## Usage

| Option       | Value           | Function                                          |
|--------------|-----------------|---------------------------------------------------|
| --query      | query           | Search query to execute (not with --dorks)        |
| --pages      | number          | Maximum number of pages to fetch                  |
| --headless   | null            | Run browser in headless mode                      |
| --driver     | path            | Path to Chromedriver                              |
| --export     | format          | Export format for the results (text, json, csv)   |
| --domain     | domain          | Specify a domain to scan (example.com)            |
| --dorks      | exposed_docs    | Publicly exposed documents                        |
| --dorks      | dir_listing     | Directory listing vulnerabilities                 |
| --dorks      | config_files    | Configuration files exposed                       |
| --dorks      | database_files  | Database files exposed                            |
| --dorks      | log_files       | Log files exposed                                 |
| --dorks      | backup_files    | Backup and old files                              |
| --dorks      | login_pages     | Login pages                                       |
| --dorks      | sql_errors      | SQL errors                                        |
| --dorks      | php_errors      | PHP errors / warning                              |
| --dorks      | phpinfo         | phpinfo()                                         |
| --dorks      | pastebin        | Search pastebin.com / pasting sites               |
| --dorks      | github_gitlab   | Search github.com and gitlab.com                  |
| --dorks      | stackoverflow   | Search stackoverflow.com                          |
| --dorks      | signup_pages    | Signup pages                                      |
| --dorks      | find_subdomains | Find Subdomains                                   |
| --dorks      | find_sub_subdomains | Find Sub-Subdomains                           |
| --dorks      | wayback_machine | Search in Wayback Machine                         |
| --dorks      | show_ips        | Show only IP addresses                            |

![image](https://github.com/WhiteH4T-Dev/DuckSearch/assets/83751620/74d165b9-b369-4116-b43a-3e3c2314d0a6)

