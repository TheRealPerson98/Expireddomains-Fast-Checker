<div align="center">
  <img src="assets/banner.png" alt="ExpiredDomains Fast Checker" width="800">
</div>

<div align="center">
  
  # ExpiredDomains Fast Checker

  [![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/downloads/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
  [![Selenium](https://img.shields.io/badge/Selenium-WebDriver-43B02A.svg)](https://selenium-python.readthedocs.io/)
  [![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4-orange.svg)](https://www.crummy.com/software/BeautifulSoup/)
  
  A tool to automatically search for available expired domains on ExpiredDomains.net based on search terms.
</div>

## ✨ Features

- 🔍 Searches ExpiredDomains.net for available domains matching your keywords
- 🔗 Extracts domain names and backlink counts
- 📊 Saves results to a CSV file for easy analysis
- 📝 Processes multiple search terms from a text file
- 🌐 Built-in web server to view results in a browser

## 📋 Prerequisites

- Python 3.6 or higher
- Chrome browser installed

## 🚀 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/thejacedev/expireddomains_fast_checker.git
   cd expireddomains_fast_checker
   ```

2. Install Python requirements:
   ```bash
   pip install -r requirements.txt
   ```

## 🛠️ Usage

1. Create a `terms.txt` file with search terms (one term per line)
2. Run the script:

   ```bash
   python main.py
   ```

3. When prompted, manually log in to your ExpiredDomains.net account, then press Enter to continue
4. Results will be automatically saved to `available_domains.csv`

5. To view the results in a browser:
   ```bash
   python server.py
   ```
   This will open a web interface where you can explore and filter the domains.


## 📝 Notes

- The script requires manual login to ExpiredDomains.net as the site may have CAPTCHA or other anti-bot measures
- After running the script, check the output CSV file for available domains and their backlink counts
- Use the built-in web server to visualize and filter your results

## 📄 License

Apache License 2.0 - See [LICENSE](LICENSE) for details