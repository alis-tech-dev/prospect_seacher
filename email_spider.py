import re
import json
from typing import Dict, Set
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


def get_emails_from_text(text: str) -> list:
    return re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)


def scrape_emails_from_url(
    url: str,
    driver: webdriver.Chrome,
    visited_urls: Set[str],
    emails_data: Dict[str, str],
    depth: int = 2
) -> None:
    if depth == 0 or url in visited_urls:
        return

    visited_urls.add(url)

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        for mailto in soup.select('a[href^=mailto]'):
            email = mailto.get('href').split(':')[-1]
            description = mailto.find_previous().get_text(strip=True) if mailto.find_previous() else ""
            emails_data[email] = description

        base_url = "{0.scheme}://{0.netloc}".format(urlparse(url))
        for link in soup.find_all('a', href=True):
            next_url = urljoin(base_url, link['href'])
            if urlparse(next_url).netloc == urlparse(base_url).netloc:
                scrape_emails_from_url(next_url, driver, visited_urls, emails_data, depth - 1)

    except Exception as e:
        print(f"Error while processing URL {url}: {e}")


def save_emails_to_file(emails_data: Dict[str, str], output_path: str) -> None:
    emails_by_domain = {}
    for email, description in emails_data.items():
        domain = email.split('@')[-1]
        if domain not in emails_by_domain:
            emails_by_domain[domain] = []
        emails_by_domain[domain].append({"email": email, "description": description})

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(emails_by_domain, f, indent=4, ensure_ascii=False)
    print(f"Collected email addresses saved to '{output_path}'")


if __name__ == "__main__":
    url = 'https://lumileds.com/'

    driver = webdriver.Chrome()

    emails_data = {}
    visited_urls = set()

    try:
        scrape_emails_from_url(url, driver, visited_urls, emails_data, depth=2)
    finally:
        driver.quit()

    save_emails_to_file(emails_data, 'data/emails_by_domain.json')
