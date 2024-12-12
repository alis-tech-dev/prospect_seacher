import ast
import base64
import os
import random
import re
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import sleep
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import requests
import smtplib
import logging
import socket
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from openai import OpenAI
from dns import resolver, exception
from unidecode import unidecode
from urllib.parse import urlparse
from data.data import (
    email_patterns,
    emails_with_middle,
    emails,
    OPENAI_API_KEY,
    URL,
    GOOGLE_API_KEY,
    CSE_ID,
    VALID_ADDRESS_REGEXP,
    FORBIDDEN_DOMAINS,
    SENDER_EMAIL,
    TOKEN_FILE,
    CREDENTIALS_FILE,
    SCOPES,
    senders
)

log = logging.getLogger(__name__)


def get_possible_emails(name: str, domain: str) -> list:
    """
    Generate possible email addresses for a given name and domain using GPT.

    Args:
        name (str): The name of the person.
        domain (str): The domain name.

    Returns:
        list: A list of possible email addresses.
    """
    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = (
        f"Generate all possible email addresses for: name {name}, "
        f"domain {domain}. Return the answer as a Python list, "
        f"where each email address is in lower_case format."
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are the best assistant for generating"
                                               " a list of all possible email addresses. "
                                               "Return python list without any comments."},
                  {"role": "user", "content": prompt}]
    )
    answer = response.choices[0].message.content
    if "[" in answer and "]" in answer:
        answer = answer[answer.index("["): answer.rindex("]") + 1]
    try:
        email_list = ast.literal_eval(answer)
        if isinstance(email_list, list):
            return email_list
    except Exception as e:
        print(f"Error: {e}")
        print(f"Raw API response: {answer}")
        return []


def google_search(company_name: str) -> str | None:
    """
    Perform a Google search to find the official site of a company.

    Args:
        company_name (str): The name of the company.

    Returns:
        str | None: The URL of the company's official site or None if not found.
    """
    query = f"{company_name} official site"
    url = URL + f"?q={query}&key={GOOGLE_API_KEY}&cx={CSE_ID}"
    latin_name = normalize_name(company_name)

    response = requests.get(url)
    if response.status_code == 200:
        results = response.json()
        items = results.get("items", [])

        for item in items[:5]:
            link = item.get("link")
            if (
                company_name.lower().split()[0] in link.lower()
                or latin_name.lower().split()[0] in link.lower()
            ):
                return link

    else:
        print(f"Error: {response.status_code}")
        return None


def get_base_domain(url: str) -> str | None:
    """
    Extract the base domain from a URL.

    Args:
        url (str): The URL from which to extract the domain.

    Returns:
        str | None: The base domain or None if it is invalid or forbidden.
    """
    parsed_url = urlparse(url)
    domain = str(parsed_url.netloc)
    if domain.count(".") > 1:
        domain = domain.split(".", 1)[-1]
    if all(
        substring not in domain.lower()
        for substring in FORBIDDEN_DOMAINS
    ) and (
        domain.lower()[-4:] != ".gov"
        or domain.lower()[:4] != "gov."
    ):
        return domain
    return None


def normalize_name(name: str) -> str:
    """
    Normalize a name by removing special characters and accent marks.

    Args:
        name (str): The name to normalize.

    Returns:
        str: The normalized name.
    """
    name = re.sub(r'\(.*?\)', '', name).strip()
    return unidecode(name)


def generate_email_variants(full_name: str, domain: str) -> list:
    """
    Generate possible email variants for a given full name and domain.

    Args:
        full_name (str): The full name of the person.
        domain (str): The domain name.

    Returns:
        list: A list of generated email variants.
    """
    full_name = normalize_name(full_name)
    full_name = re.sub(
        r'\b(Jr\.?|Sr\.?|I+|IV|VI+)\b',
        '',
        full_name,
        flags=re.IGNORECASE
    ).strip()

    name_parts = re.split(r'\s+', full_name)

    first = name_parts[0].lower()
    middle = name_parts[1].lower() if len(name_parts) > 2 else ''
    last = name_parts[-1].lower() if len(name_parts) > 1 else ''
    first_initial = first[0]
    middle_initial = middle[0] if middle else ''
    last_initial = last[0] if last else ''
    possible_emails = email_patterns
    if middle:
        possible_emails.extend(emails_with_middle)
    email_list = []
    for pattern in possible_emails:
        email = pattern.format(
            first=first,
            middle=middle,
            last=last,
            first_initial=first_initial,
            middle_initial=middle_initial,
            last_initial=last_initial
        )
        possible_email = f"{email}@{domain}"
        email_list.append(possible_email)
    return email_list


def company_emails(domain: str) -> list:
    """
    Generate a list of company email addresses based on the domain.

    Args:
        domain (str): The company's domain.

    Returns:
        list: A list of possible company emails.
    """
    return [email + "@" + domain for email in emails]


def get_company_email(domain: str, employee_email: str = None) -> str | None:
    """
    Retrieve a valid company email from a list of possible emails.

    Args:
        domain (str): The company's domain.
        employee_email (str, optional): The employee's email if known.

    Returns:
        str | None: The valid company email, or None if no valid email found.
    """
    if not employee_email:
        email_variants = company_emails(domain)
        for email in email_variants:
            validation = validate_email(email)
            if validation and validation != "delete":
                return email
            time.sleep(1)
    return None


def authenticate_gmail() -> Credentials:
    """
    Authenticate the user with Gmail API and return the credentials.

    Returns:
        Credentials: The authenticated credentials.
    """
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"Error reading token file: {e}")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds


def create_message(sender: str, to: str, subject: str, body: str) -> dict:
    """
    Create a MIME message for sending an email.

    Args:
        sender (str): The sender's email address.
        to (str): The receiver's email address.
        subject (str): The subject of the email.
        body (str): The body of the email.

    Returns:
        dict: The MIME message in a format ready to send via Gmail API.
    """
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = to
    message['Subject'] = subject
    message['Return-Receipt-To'] = sender
    message['Disposition-Notification-To'] = sender
    message.attach(MIMEText(body, 'plain'))

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}


def send_email(receiver: str, subject: str = '', body: str = '') -> bool:
    """
    Send an email through Gmail API.

    Args:
        receiver (str): The receiver's email address.
        subject (str, optional): The subject of the email. Defaults to an empty string.
        body (str, optional): The body of the email. Defaults to an empty string.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    creds = authenticate_gmail()

    try:
        service = build('gmail', 'v1', credentials=creds)

        trash = service.users().messages().list(
            userId='me', labelIds=['TRASH'], q="is:trash").execute()
        messages = trash.get('messages', [])

        sender = SENDER_EMAIL
        message = create_message(sender, receiver, subject, body)
        sent_message = service.users().messages().send(userId='me', body=message).execute()

        print(f"Message sent: {sent_message['id']}")
        return True

    except Exception as error:
        print(f"An error occurred: {error}")
        return False


def create_auth_string(email: str, access_token: str) -> str:
    """
    Create an authentication string for Gmail API.

    Args:
        email (str): The email address.
        access_token (str): The access token.

    Returns:
        str: The authentication string.
    """
    return f"user={email}\x01auth=Bearer {access_token}\x01\x01"


def is_delivered(receiver: str) -> bool:
    """
    Check if an email has been successfully delivered.

    Args:
        receiver (str): The receiver's email address.

    Returns:
        bool: True if the email was delivered, False otherwise.
    """
    if not send_email(receiver):
        return False
    check_interval = 10
    max_wait_time = 20
    try:
        elapsed_time = 0
        sleep(10)
        while elapsed_time <= max_wait_time:
            creds = authenticate_gmail()
            service = build('gmail', 'v1', credentials=creds)
            results = service.users().messages().list(
                userId='me', q='from:"mailer-daemon@googlemail.com"').execute()
            messages = results.get('messages', [])

            if messages:
                for message in messages:
                    msg = service.users().messages().get(userId='me', id=message['id']).execute()
                    if receiver in msg["snippet"]:
                        print(f"{receiver} sending failed")
                        service.users().messages().trash(
                            userId='me',
                            id=msg['id']
                        ).execute()
                        return False
                    elif "Your message was not sent" in msg["snippet"]:
                        raise RuntimeError("Message sending limit reached.")

            else:
                print("No delivery receipts found, retrying in a few seconds...")
                sleep(check_interval)
                elapsed_time += check_interval

        print("Max wait time reached. No delivery receipt found within the specified time.")
        return True

    except RuntimeError as error:
        print(f"RuntimeError: {error}")
        raise

    except Exception as e:
        print(f"Error: {e}")
        return False


def validate_email(email: str) -> bool | str:
    """
    Validate an email address by checking its format and DNS records.

    Args:
        email (str): The email address to validate.

    Returns:
        bool | str: True if the email is valid, False if invalid, or "delete" if the domain is invalid.
    """
    print(f"Validating email: {email}")
    if not re.match(VALID_ADDRESS_REGEXP, email):
        print("Invalid format.")
        return False

    local_part, domain = email.split("@")

    try:
        mx_records = resolver.resolve(domain, 'MX')
    except exception.DNSException as e:
        print(f"Invalid domain: {e}")
        return "delete"

    try:
        mx_record = str(mx_records[0].exchange).strip('.')

        server = smtplib.SMTP(timeout=10)
        server.connect(mx_record)

        sender = random.choice(senders)
        sender_domain = sender.split("@")[-1]
        try:
            server.ehlo(str(sender_domain))
        except Exception as e:
            print(e)
            server.helo(str(sender_domain))

        server.mail(str(sender))
        code, message = server.rcpt(email)
        server.quit()

        if code == 250:
            return True
        else:
            return False

    except (socket.error, smtplib.SMTPException) as e:
        print(f"SMTP validation failed: {e}")
        return False


if __name__ == "__main__":
    print(validate_email("matthiashermann@tjiko.de"))
