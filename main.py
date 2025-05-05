import time
import csv
import os
import argparse
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def setup_driver():
    """Set up and return a configured Chrome webdriver."""
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    
    # Uncomment the line below to run in headless mode
    # options.add_argument("--headless")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def login_to_site(driver):
    """Login to ExpiredDomains.net."""
    driver.get("https://www.expireddomains.net/login/")
    
    print("Please log in manually. Press Enter after logging in...")
    input()
    
    # Check if login was successful
    if "member.expireddomains.net" in driver.current_url:
        print("Login successful!")
        return True
    else:
        print("Login failed. Please check credentials and try again.")
        return False

def search_for_term(driver, term):
    """Search for a specific term on ExpiredDomains.net."""
    # Replace spaces with + for multi-word terms
    search_term = term.replace(" ", "+")
    
    # Navigate to the search URL
    search_url = f"https://member.expireddomains.net/domain-name-search/?o=bl&r=d&q={search_term}#listing"
    driver.get(search_url)
    
    # Wait for the listing to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "listing"))
        )
        
        # Click on the "Show Filter" link
        try:
            show_filter_link = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".showfilter a"))
            )
            show_filter_link.click()
            
            # Wait for the filter options to appear and select "only available Domains"
            available_domains_checkbox = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input#fwhois[value='22']"))
            )
            
            # Check if it's not already checked
            if not available_domains_checkbox.is_selected():
                available_domains_checkbox.click()
                
                # Wait for page to reload with the filter applied
                time.sleep(2)
                
                # Click the filter button to apply
                filter_button = driver.find_element(By.CSS_SELECTOR, "input.btn.btn-primary[value='Apply Filter']")
                filter_button.click()
                
                # Wait for filtered results to load
                time.sleep(3)
            
            print(f"Filter applied for available domains only.")
        except Exception as e:
            print(f"Could not apply filter: {e}")
        
        return True
    except Exception as e:
        print(f"Error loading search results: {e}")
        return False

def extract_available_domains(html_content):
    """Extract available domains from the page HTML.
    Note: We're already filtering for available domains on the site,
    but we'll double-check for availability here as well."""
    soup = BeautifulSoup(html_content, 'html.parser')
    listing_div = soup.find("div", id="listing")
    
    if not listing_div:
        print("No listing found on the page.")
        return []
    
    domains_data = []
    table = listing_div.find("table")
    if not table:
        print("No table found in listing.")
        return []
        
    rows = table.find_all("tr")
    available_count = 0
    total_rows = 0
    
    for row in rows:
        # Skip if no proper tr element or header row
        if not row or ('class' in row.attrs and 'thead' in row['class']):
            continue
            
        total_rows += 1
            
        # Find domain cell
        domain_cell = row.find("td", class_="field_domain")
        if not domain_cell:
            continue
            
        # Skip if no domain link found
        domain_link = domain_cell.find("a", class_="namelinks")
        if not domain_link:
            continue
            
        # Get domain name
        domain_name = domain_link.get('title', domain_link.text.strip())
        
        # Find status cell (double-checking for Available domains)
        whois_cell = row.find("td", class_="field_whois2")
        if not whois_cell:
            continue
            
        # Check if it contains "Available" text
        status_link = whois_cell.find("a")
        if not status_link or "Available" not in status_link.text:
            continue
        
        available_count += 1
        
        # Create domain data dictionary
        domain_data = {"domain": domain_name}
        
        # Extract all available fields
        # Length
        length_cell = row.find("td", class_="field_length")
        if length_cell:
            domain_data["length"] = length_cell.text.strip()
        
        # Backlinks (BL)
        bl_cell = row.find("td", class_="field_bl")
        if bl_cell and bl_cell.find("a"):
            domain_data["backlinks"] = bl_cell.find("a").get("title", bl_cell.find("a").text.strip())
        
        # Domain Popularity
        pop_cell = row.find("td", class_="field_domainpop")
        if pop_cell and pop_cell.find("a"):
            domain_data["domainpop"] = pop_cell.find("a").text.strip()
        
        # Creation Date
        creation_cell = row.find("td", class_="field_creationdate")
        if creation_cell and creation_cell.find("a"):
            domain_data["creation_date"] = creation_cell.find("a").get("title", creation_cell.find("a").text.strip())
        
        # Archive Birth
        abirth_cell = row.find("td", class_="field_abirth")
        if abirth_cell and abirth_cell.find("a"):
            domain_data["archive_birth"] = abirth_cell.find("a").get("title", abirth_cell.find("a").text.strip())
        
        # Archive Entries
        aentries_cell = row.find("td", class_="field_aentries")
        if aentries_cell and aentries_cell.find("a"):
            domain_data["archive_entries"] = aentries_cell.find("a").get("title", aentries_cell.find("a").text.strip())
        
        # Majestic Global Rank
        rank_cell = row.find("td", class_="field_majestic_globalrank")
        if rank_cell and rank_cell.find("a"):
            domain_data["majestic_rank"] = rank_cell.find("a").text.strip()
        
        # DMOZ
        dmoz_cell = row.find("td", class_="field_dmoz")
        if dmoz_cell:
            domain_data["dmoz"] = dmoz_cell.text.strip()
        
        # TLD Status
        tld_cell = row.find("td", class_="field_statustld_registered")
        if tld_cell and tld_cell.find("a"):
            domain_data["tld_status"] = tld_cell.find("a").text.strip()
        
        # COM Status
        com_cell = row.find("td", class_="field_statuscom")
        if com_cell and com_cell.find("a"):
            domain_data["com_status"] = com_cell.find("a").get("title", "").replace(".com ", "")
        
        # NET Status
        net_cell = row.find("td", class_="field_statusnet")
        if net_cell and net_cell.find("a"):
            domain_data["net_status"] = net_cell.find("a").get("title", "").replace(".net ", "")
        
        # ORG Status
        org_cell = row.find("td", class_="field_statusorg")
        if org_cell and org_cell.find("a"):
            domain_data["org_status"] = org_cell.find("a").get("title", "").replace(".org ", "")
        
        # BIZ Status
        biz_cell = row.find("td", class_="field_statusbiz")
        if biz_cell and biz_cell.find("a"):
            domain_data["biz_status"] = biz_cell.find("a").get("title", "").replace(".biz ", "")
        
        # INFO Status
        info_cell = row.find("td", class_="field_statusinfo")
        if info_cell and info_cell.find("a"):
            domain_data["info_status"] = info_cell.find("a").get("title", "").replace(".info ", "")
        
        # DE Status
        de_cell = row.find("td", class_="field_statusde")
        if de_cell and de_cell.find("a"):
            domain_data["de_status"] = de_cell.find("a").get("title", "").replace(".de ", "")
        
        # Add Date
        adddate_cell = row.find("td", class_="field_adddate")
        if adddate_cell:
            domain_data["add_date"] = adddate_cell.text.strip()
        
        # Related CNOBI
        related_cell = row.find("td", class_="field_related_cnobi")
        if related_cell:
            domain_data["related_cnobi"] = related_cell.text.strip()
        
        # Wikipedia Links
        wiki_cell = row.find("td", class_="field_wikipedia_links")
        if wiki_cell:
            domain_data["wikipedia_links"] = wiki_cell.text.strip()
        
        # Domain List Status
        domainlist_cell = row.find("td", class_="field_domainlist")
        if domainlist_cell:
            domain_data["domain_list"] = domainlist_cell.text.strip()
        
        # WHOIS Status
        if status_link:
            title = status_link.get("title", "")
            domain_data["whois_status"] = status_link.text.strip()
            domain_data["whois_details"] = title
        
        domains_data.append(domain_data)
    
    print(f"Found {available_count} available domains out of {total_rows} total domains in the listing.")
    return domains_data

def save_to_csv(domains_data, output_file="available_domains.csv"):
    """Save the extracted domain data to a CSV file."""
    if not domains_data:
        print("No available domains found to save.")
        return
    
    # Check if the file exists to determine if we need to append
    file_exists = os.path.isfile(output_file)
    
    # Get all possible fieldnames from all domain data
    all_fields = set()
    for domain in domains_data:
        all_fields.update(domain.keys())
    
    # Convert to sorted list for consistent column order
    fieldnames = sorted(list(all_fields))
    
    # If the file exists, read the header to ensure compatibility
    if file_exists:
        with open(output_file, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            existing_headers = next(reader, [])
            # Add any new fields found in the current data
            for field in fieldnames:
                if field not in existing_headers:
                    existing_headers.append(field)
            fieldnames = existing_headers
    
    mode = 'a' if file_exists else 'w'
    with open(output_file, mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        for domain in domains_data:
            writer.writerow(domain)
    
    print(f"{'Added' if file_exists else 'Saved'} {len(domains_data)} domains to {output_file}")

def process_terms_file(driver, terms_file, output_file):
    """Process each term in the terms file."""
    with open(terms_file, 'r', encoding='utf-8') as file:
        terms = [line.strip() for line in file if line.strip()]
        
    for term in terms:
        print(f"Searching for term: {term}")
        if search_for_term(driver, term):
            time.sleep(2)  # Give page time to fully load
            domains = extract_available_domains(driver.page_source)
            print(f"Found {len(domains)} available domains for term '{term}'")
            if domains:
                save_to_csv(domains, output_file)
            time.sleep(1)  # Avoid rate limiting

def main():
    parser = argparse.ArgumentParser(description="Scrape available domains from ExpiredDomains.net")
    parser.add_argument("--terms", default="terms.txt", help="Path to text file with search terms (one per line), defaults to terms.txt")
    parser.add_argument("--output", default="available_domains.csv", help="Output CSV file path")
    
    args = parser.parse_args()
    
    terms_file = args.terms
    if not os.path.exists(terms_file):
        print(f"Terms file '{terms_file}' not found. Creating empty file...")
        with open(terms_file, 'w', encoding='utf-8') as f:
            pass
        print(f"Please add search terms to '{terms_file}' and run the program again.")
        return
        
    if os.path.getsize(terms_file) == 0:
        print(f"Terms file '{terms_file}' is empty. Please add search terms and run the program again.")
        return
    
    driver = setup_driver()
    try:
        if login_to_site(driver):
            process_terms_file(driver, terms_file, args.output)
    finally:
        print("Closing browser...")
        driver.quit()

if __name__ == "__main__":
    main() 