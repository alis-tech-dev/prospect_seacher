import io
import sys
import requests
from typing import List, Optional

from data.data import (
    GOOGLE_API_KEY,
    CSE_ID,
    CONTACTS,
    POSITIONS,
    LOCATIONS,
)
from espo_request import get_lead, clients, create_prospect
from searching_service import (
    google_search,
    get_base_domain,
    URL,
    validate_email,
    get_company_email,
    get_possible_emails,
    generate_email_variants,
)

sys.stdout = io.TextIOWrapper(
    sys.stdout.buffer,
    encoding="utf-8",
    errors="replace",
)

LINKEDIN_PREFIX = "site:linkedin.com/in/"
LINKEDIN_SUFFIX = "| LinkedIn"
TRUNCATION_MARK = " ..."


def clean_position_and_firm(position: str, firm: str) -> (str, str):
    """
    Clean position and firm strings by removing unnecessary parts.

    Args:
        position (str): Position string.
        firm (str): Firm string.

    Returns:
        Tuple[str, str]: Cleaned position and firm.
    """
    if LINKEDIN_SUFFIX in position:
        position = position.replace(LINKEDIN_SUFFIX, "")
    if LINKEDIN_SUFFIX in firm:
        firm = firm.replace(LINKEDIN_SUFFIX, "")
    if TRUNCATION_MARK in position:
        position = position.replace(TRUNCATION_MARK, "")
    if TRUNCATION_MARK in firm:
        firm = firm.replace(TRUNCATION_MARK, "")
    return position.strip(), firm.strip()


def process_email_generation(
    name: str, domain: str
) -> Optional[str]:
    """
    Generate possible emails and validate them.

    Args:
        name (str): User's name.
        domain (str): Domain of the company.

    Returns:
        Optional[str]: Validated email or None if no valid email is found.
    """
    emails = generate_email_variants(name, domain)
    ai_emails = get_possible_emails(name, domain)
    for email in ai_emails:
        if email not in emails:
            emails.append(email)

    for possible_email in emails:
        name_part = possible_email.split("@")[0]
        if len(name_part) > 3 and validate_email(possible_email):
            return possible_email

    return get_company_email(domain)


def google_linkedin_search(
    position_type: str,
    location_type: str,
    num_pages: int = 10,
) -> List[dict]:
    """
    Perform a Google search on LinkedIn profiles.

    Args:
        position_type (str): Position to search for.
        location_type (str): Location to search in.
        num_pages (int, optional): Number of result pages to fetch. Defaults to 10.

    Returns:
        List[dict]: List of processed contacts.
    """
    for i in range(num_pages):
        start = i * 10 + 1
        query = f'{LINKEDIN_PREFIX} "{position_type}" "{location_type}"'
        url = f"{URL}?q={query}&key={GOOGLE_API_KEY}&cx={CSE_ID}&start={start}"
        print(f"Query: {query}, Page: {i + 1}")

        response = requests.get(url)
        if response.status_code == 400:
            print(f"Reached limit at start = {start}")
            break
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            break

        results = response.json()
        for item in results.get("items", []):
            title = item.get("title", "")
            link = item.get("link", "")
            if "linkedin.com/in/" not in link:
                continue

            name_parts = title.split(" – ")
            if len(name_parts) == 1:
                name_parts = title.split(" - ")
            name = name_parts[0].strip() if len(name_parts[0]) > 0 else "Unknown"
            position = name_parts[1].strip() if len(name_parts) > 1 else "Unknown"
            firm = name_parts[-1].strip() if name_parts[-1] else "Unknown"

            position, firm = clean_position_and_firm(position, firm)
            if firm == position:
                print("Company and position are identical. Skipping...")
                continue

            for client in clients:
                if get_lead(name, client):
                    print(f"User {name} already exists in Espo database.")
                    break
            else:
                print(f"User {name} not found. Checking further details...")

                site = google_search(firm)
                domain = get_base_domain(site) if site else None
                email = process_email_generation(name, domain) if domain else None

                if email:
                    print(f"Valid email found: {email}")
                    espo_lead = {
                        "name": name,
                        "position": position,
                        "fromHunter": False,
                        "linkedIn": link,
                        "emailAddress": email,
                        "emailDb": email,
                        "country": location_type,
                        "company": firm,
                        "url": site,
                    }
                    create_prospect(espo_lead)
                else:
                    print("No valid email found. Skipping user...")

    return CONTACTS


if __name__ == "__main__":
    for position_type in POSITIONS:
        for location_type in LOCATIONS:
            google_linkedin_search(position_type, location_type)
