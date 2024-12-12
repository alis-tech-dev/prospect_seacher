import time
from typing import Any

import requests
import json
from openai import OpenAI

from requests.exceptions import ConnectTimeout, HTTPError, RequestException
from data.data import ESPO_API_KEY, ESPO_URL, PAD_URL, OPENAI_API_KEY, ALEDO_URL
from espo_api_client import EspoAPI
from bs4 import BeautifulSoup

alis_client = EspoAPI(ESPO_URL, ESPO_API_KEY)
aledo_client = EspoAPI(ALEDO_URL, ESPO_API_KEY)
clients = [alis_client, aledo_client]


def get_pad_name(full_name: str, pad: int = 5) -> str:
    """
    Returns the full name with a salutation based on the Czech language rules.

    Args:
        full_name (str): The full name to be processed.
        pad (int, optional): The pad to use. Defaults to 5.

    Returns:
        str: The name with the corresponding salutation.
    """
    response = requests.get(f"{PAD_URL}pad={pad}&jmeno={full_name}")
    if response.status_code == 200:
        return response.text


def get_name(pad_name: str) -> str:
    """
    Returns the name without the salutation.

    Args:
        pad_name (str): The name with a salutation.

    Returns:
        str: The name without the salutation.
    """
    response = requests.get(f"https://sklonuj.cz/jmeno/{pad_name}")
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find("table", {"class": "table"})

        if table:
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) == 2:
                    case = cells[0].text.strip()
                    form = cells[1].text.strip()
                    if case == "5":
                        return form


def get_declined_name(name: str) -> str:
    """
    Converts a given name to the vocative case using OpenAI's API.

    Args:
        name (str): The name to be converted.

    Returns:
        str: The name in the vocative case.
    """
    client_api = OpenAI(api_key=OPENAI_API_KEY)

    prompt = (
        f"Convert the name {name} to the vocative case in Czech. "
        f"For example, if the input name is 'Jan,' you should return 'Jane.' "
        f"Return only the name without explanation. "
        f"Use the rules of the Czech language."
        f"Name to inflect: {name}"
    )

    response = client_api.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are the best assistant in converting "
                                          "a name to the vocative case in Czech."
                                          "Return python string without any comments."},
            {"role": "user", "content": prompt}
        ]
    )
    answer = response.choices[0].message.content
    if "[" in answer and "]" in answer:
        answer = answer[answer.index("["): answer.rindex("]") + 1]
    try:
        return answer[1:-1]
    except Exception as e:
        print(f"Error: {e}")
        print(f"Raw API response: {answer}")
        return ""


def get_salutation(name: str) -> str:
    """
    Returns the appropriate salutation ("pan" or "paní") based on the last name.

    Args:
        name (str): The full name to extract the salutation from.

    Returns:
        str: The salutation ("pan" or "paní").
    """
    full_name = name.split(" ")
    if len(full_name) > 1:
        last_name = full_name[-1]
    else:
        last_name = full_name[0]

    if last_name[-3:] in ["ská", "ová", "aja", "ina"]:
        return "paní"
    else:
        return "pane"


def get_all_entities(entity: str, client: EspoAPI = alis_client, limit: int = 200) -> list:
    """
    Retrieves all entities of a specified type from the client.

    Args:
        entity (str): The type of entity to retrieve.
        client (EspoAPI, optional): The client to use for the request.
        limit (int, optional): The number of entities to fetch per request. Defaults to 200.

    Returns:
        list: A list of all entities.
    """
    all_entities = []
    offset = 0

    while True:
        params = {
            "limit": limit,
            "offset": offset
        }
        response = client.request('GET', entity, params)
        all_entities.extend(response.get('list', []))

        if offset == 0:
            print(f"Total persons: {response.get('total', 'unknown')}")

        if len(response.get('list', [])) < limit:
            break
        offset += limit

    return all_entities


def set_pad_name(entity: str = "Contact") -> None:
    """
    Sets the pad name for all entities of the specified type.

    Args:
        entity (str, optional): The type of entity to update. Defaults to "Contact".
    """
    persons = get_all_entities(entity)
    count = 0
    for person in persons:
        person_id = person["id"]
        name = person["name"]

        if name:
            salutation = get_salutation(name)
            pad_name = get_name(name)

            if not pad_name:
                pad_name = get_declined_name(name)
            pad_name = pad_name.split(" ")

            if len(pad_name) == 2:
                pad_name = " ".join([pad_name[0].capitalize(), pad_name[-1].capitalize()])
            else:
                pad_name = pad_name[0].capitalize()

            update_entity(entity, person_id, f"{salutation} {pad_name}")
            count += 1
            print(f"{count} : {salutation} {pad_name} UPDATED.")
        else:
            count += 1
            print(f"NAME IS NONE, COUNT: {count}")
            continue


def delete_prospect() -> None:
    """
    Deletes prospects that have short email addresses (3 characters or less).
    """
    prospects = get_all_entities("Prospect")
    count = 0
    for prospect in prospects:
        prospect_id = prospect["id"]
        email = prospect["emailDb"]

        name_part = email.split("@")[0]
        if len(name_part) <= 3:
            try:
                alis_client.request('DELETE', f'Prospect/{prospect_id}')
            except Exception as e:
                print(f"Error: {e}, skipping deleting.")
            count += 1
            print(f"{count} : {email} DELETED.")


def delete_entity(entity: str, entity_id: str, client: EspoAPI) -> None:
    """
    Deletes a specified entity by its ID.

    Args:
        entity (str): The type of entity to delete.
        entity_id (str): The ID of the entity to delete.
        client (EspoAPI): The client to use for the request.
    """
    try:
        client.request('DELETE', f'{entity}/{entity_id}')
    except Exception as e:
        print(f"Error: {e}, skipping deleting.")


def update_entity(entity_type: str, entity_id: str, value: Any, field: str = 'padName', client: EspoAPI = alis_client) -> None:
    """
    Updates a specified field for an entity.

    Args:
        entity_type (str): The type of entity to update.
        entity_id (str): The ID of the entity to update.
        value (str): The new value for the field.
        field (str, optional): The field to update. Defaults to 'padName'.
        client (EspoAPI, optional): The client to use for the request.
    """
    try:
        client.request('PUT', f'{entity_type}/{entity_id}', {field: value})
    except Exception as e:
        print(f"Error: {e}, skipping updating.")


def create_prospect(params: dict) -> None:
    """
    Creates a new prospect based on the provided parameters.

    Args:
        params (dict): A dictionary of parameters for the prospect.
    """
    prospect = get_prospect(params["name"], params["emailAddress"])
    if not prospect:
        try:
            for client in clients:
                client.request('POST', 'Prospect', params)
                print(f"\n ~ LEAD CREATED ~ \n")
        except Exception as e:
            print(f"Error: {e}, skipping lead.")
    else:
        print("Lead already exists.")


def get_prospect(name: str, email: str, client: EspoAPI = alis_client) -> bool:
    """
    Checks if a prospect already exists in the database.

    Args:
        name (str): The name of the prospect.
        email (str): The email address of the prospect.
        client (EspoAPI, optional): The client to use for the request.

    Returns:
        bool: True if the prospect exists, False otherwise.
    """
    params = {
        "select": "name, emailAddress",
        "where": [
            {
                "type": "equals",
                "attribute": "name",
                "value": name,
            },
            {
                "type": "equals",
                "attribute": "emailAddress",
                "value": email,
            },
        ],
    }
    response = client.request('GET', 'Prospect', params)
    return int(response["total"]) > 0


def get_lead(name: str, client: EspoAPI = alis_client) -> bool:
    """
    Checks if a lead exists in the database.

    Args:
        name (str): The name of the lead.
        client (EspoAPI, optional): The client to use for the request.

    Returns:
        bool: True if the lead exists, False otherwise.
    """
    params = {
        "select": "name",
        "where": [
            {
                "type": "equals",
                "attribute": "name",
                "value": name,
            },
        ],
    }

    retries = 5
    for attempt in range(retries):
        try:
            response = client.request('GET', 'Prospect', params)
            return int(response["total"]) > 0

        except ConnectTimeout:
            print(f"Attempt {attempt + 1} of {retries}: Connection timed out. Retrying...")
            if attempt < retries - 1:
                time.sleep(5)

        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            break

        except RequestException as req_err:
            print(f"Request error occurred: {req_err}")
            break

        except Exception as error:
            print(f"An unexpected error occurred: {error}")
            break

    return True


def get_prospects_quantity() -> int:
    """
    Retrieves the total number of prospects in the database.

    Returns:
        int: The total number of prospects.
    """
    response = alis_client.request('GET', 'Prospect')
    return int(response["total"])


def get_prospects() -> dict:
    """
    Retrieves all prospects from the database.

    Returns:
        dict: A dictionary of all prospects.
    """
    return alis_client.request('GET', 'Prospect')


def read_json_file(file: str) -> dict:
    """
    Reads a JSON file and returns the parsed data.

    Args:
        file (str): The path to the JSON file.

    Returns:
        dict: The data parsed from the JSON file.
    """
    with open(file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data


def get_email_address_for_prospect() -> dict:
    """
    Retrieves email addresses for prospects from multiple sources.

    Returns:
        dict: A dict of updated prospects with email addresses.
    """
    prospects = read_json_file("data/prospects.json")
    emails = read_json_file("emails.json")
    email_address = read_json_file("email_address.json")

    for prospect in prospects:
        prospect_id = prospect['id']
        related_email = next(
            (email for email in emails
             if email['entity_id'] == prospect_id and email['entity_type'] == "Prospect"),
            None
        )

        if related_email:
            email_address_id = related_email['email_address_id']
            related_email_address = next(
                (email_addr for email_addr in email_address if email_addr['id'] == email_address_id),
                None
            )
            if related_email_address:
                prospect['email_address'] = related_email_address['name']
            else:
                print(f"Не знайдено email_address для email_address_id: {email_address_id}")
        else:
            print(f"Не знайдено пов'язаних email для Prospect ID: {prospect_id}")

    return prospects


def create_prospect_from_json() -> None:
    """
    Creates prospects from the data in the JSON file.
    """
    updated_prospects = get_email_address_for_prospect()
    counter = 0
    for prospect in updated_prospects:
        name = prospect["name"]
        email = prospect["email_address"]
        espo_prospect = {
            "name": prospect["name"],
            "position": prospect["position"],
            "fromHunter": prospect["from_hunter"],
            "linkedIn": prospect["linked_in"],
            "emailAddress": prospect["email_address"],
            "emailDb": prospect["email_address"],
            "country": prospect["country"],
            "company": prospect["company"],
            "url": prospect["url"]
        }
        for client in clients:
            if get_lead(prospect["name"], client):
                print(f"User {name} already exists in espo database.", flush=True)
                continue
            else:
                client.request('POST', 'Prospect', espo_prospect)
                if client == alis_client:
                    counter += 1
                    print(f"{counter}\nProspect: {name}\nEmail: {email}\n")


if __name__ == "__main__":
    create_prospect_from_json()
