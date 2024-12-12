import logging
import os
import time

from typing import Optional, Any
from espo_request import (
    get_all_entities,
    alis_client,
    aledo_client,
    update_entity,
    delete_entity,
)
from searching_service import (
    generate_email_variants,
    get_possible_emails,
    get_company_email,
    validate_email,
)


def setup_logging() -> None:
    """
    Configures the logging system. Logs are saved to both console
    and a log file. Creates the necessary directories if they do not exist.
    """
    os.makedirs('/home/admin/web/pythonScripts/lead_finder', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                '/home/admin/web/pythonScripts/lead_finder/loger.log'
            )
        ]
    )


def update_prospect_data(
    prospect_id: str, email: str, client: Any
) -> None:
    """
    Updates the email information and status of a prospect.

    Args:
        prospect_id (str): The ID of the prospect to update.
        email (str): The email to assign to the prospect.
        client (Any): The client used for API interaction.
    """
    update_entity("Prospect", prospect_id, email, "emailAddress", client)
    update_entity("Prospect", prospect_id, email, "emailDb", client)
    update_entity("Prospect", prospect_id, True, "isChecked", client)


def get_prospect(name: str, email: str, client: Any = alis_client) -> str:
    """
    Retrieves a prospect's ID based on the name and email.

    Args:
        name (str): The name of the prospect.
        email (str): The email of the prospect.
        client (Any): The client used for API interaction. Defaults to
            alis_client.

    Returns:
        str: The ID of the matching prospect.
    """
    params = {
        "select": "name, emailDb",
        "where": [
            {"type": "equals", "attribute": "name", "value": name},
            {"type": "equals", "attribute": "isChecked", "value": False},
            {"type": "equals", "attribute": "emailDb", "value": email},
        ],
    }
    response = client.request("GET", "Prospect", params)
    logging.info(response["list"][0])
    return response["list"][0]["id"]


def main() -> None:
    """
    Main function to process prospects and update their email information
    or delete them if necessary.
    """
    setup_logging()
    
    prospects = get_all_entities("Prospect")
    for prospect in prospects:
        alis_name = prospect["name"]
        alis_email = prospect["emailDb"]
        alis_email_address = prospect["emailAddress"]
        alis_prospect_id = prospect["id"]
        is_checked = prospect["isChecked"]

        if alis_email and not is_checked:
            domain = alis_email.split("@")[-1]
            email: Optional[str] = None
            result: Optional[str] = None
            emails = generate_email_variants(alis_name, domain)
            logging.info(f"\n{len(emails)} EMAILS: {emails}")
            ai_emails = get_possible_emails(alis_name, domain)
            logging.info(f"\n{len(ai_emails)} AI_EMAILS: {ai_emails}")

            for pre_email in ai_emails:
                if pre_email not in emails:
                    emails.append(pre_email)

            if alis_email_address not in emails:
                emails.append(alis_email_address)

            logging.info(f"\n{len(emails)} RESULT EMAILS: {emails}")

            for possible_email in emails:
                name_part = possible_email.split("@")[0]

                if len(name_part) > 3:
                    result = validate_email(possible_email)
                    logging.info(f"Validation result => {result}")

                if result == "delete":
                    break

                if result:
                    email = possible_email
                    break
                else:
                    time.sleep(1)

            logging.info(f"Email: {email}")
            company_email = get_company_email(domain, email)

            if email or company_email:
                if company_email:
                    email = company_email

                logging.info(f"\nOLD EMAIL => {alis_email}")
                logging.info(f"NEW EMAIL => {email}")

                aledo_prospect_id = get_prospect(
                    alis_name, alis_email, aledo_client
                )
                update_prospect_data(alis_prospect_id, email, alis_client)
                update_prospect_data(aledo_prospect_id, email, aledo_client)

            elif result == "delete" or not email:
                delete_entity("Prospect", alis_prospect_id, alis_client)
                aledo_prospect_id = get_prospect(
                    alis_name, alis_email, aledo_client
                )
                delete_entity("Prospect", aledo_prospect_id, aledo_client)
                logging.info(f"Prospect {alis_name} Deleted.")
                continue


if __name__ == "__main__":
    main()
