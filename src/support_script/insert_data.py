import json
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from src.db_tables import events, event_tag, organizations  # Adjust import according to your structure
from src.core import config
from pydantic import PostgresDsn
import os
from sqlalchemy.dialects.postgresql import insert as pg_insert
import requests
import ast

script_dir = os.path.dirname(os.path.abspath(__file__))

PG_URL = PostgresDsn.build(
    scheme="postgresql",    
    user=config.settings.POSTGRES_USER,
    password=config.settings.POSTGRES_PASSWORD,
    host=config.settings.POSTGRES_HOST,
    port=config.settings.DB_PORT,
    path=f"/{config.settings.POSTGRES_DB}",
)


engine = create_engine(PG_URL)
Session = sessionmaker(bind=engine)
session = Session()

base_url = 'http://127.0.0.1:8001'

response = (requests.get(f"{base_url}/metadata/org")).json()

countries = {entry["label"]: entry["value"] for entry in response["data"]["countries"]}


def load_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)
    
def load_data(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        # Safely evaluate the string representation of tuples
        data = ast.literal_eval(f"[{content}]")  # Convert to a list of tuples
    return data

def edit_vendor_data(vendor):

    
    # Prompt the user for new values (leave blank to keep current value)
    address = vendor[1]

    split_addr = address.split(",")
    city = split_addr[1].strip()
    country = split_addr[2].strip()

    country_id = countries[country]

    response = (requests.get(f"{base_url}/metadata/cities/{country_id}")).json()
    cities = {entry["label"]: entry["value"] for entry in response["data"]["cities"]}

    city_id = cities[city]


    return {
        "organization_name": vendor[0],
        "contact_address": split_addr[0].strip(),
        "contact_phone": vendor[2],
        "organization_type": "VENDOR",
        "email": vendor[4],
        "size": vendor[5],
        "years_of_operation": vendor[6],
        "country": country_id,
        "city": city_id
    }

def insert_vendor_data():
    file_path = os.path.join(script_dir, 'vendors.txt')
    vendor_data = load_data(file_path)

    # Iterate through the vendor data and allow editing
    for vendor in vendor_data:
        data = edit_vendor_data(vendor)
        session.execute(organizations.insert().values(data))

def insert_events_from_json(json_data):
    for event in json_data:
        new_event = {
            "organizer_id": event["organizer_id"],
            "event_name": event["event_name"],
            "street_addr": event["street_addr"],
            "description": event["description"],
            "phone_contact": event["phone_contact"],
            "pictures": event.get(
                "pictures"
            ),  # Use .get() to avoid KeyError if key doesn't exist
            "details": event.get("details"),
            "status": event["status"],
            "start_date": event["start_date"],
            "end_date": event["end_date"],
            "country": event["country"],
            "city": event["city"],
        }

        # Create an event instance and add it to the session
        inserted_id = (session.execute(events.insert().values(new_event).returning(events.c.id))).scalar()

        session.execute(
            pg_insert(event_tag).values(event_id=inserted_id),
            [{"tag_id": tag_id} for tag_id in event["tags"]],
        )

    


if __name__ == "__main__":
    # Load the JSON data from a file
    insert_vendor_data()

    file_path = os.path.join(script_dir, "processed_data.json")
    json_data = load_json(file_path)

    # Insert events into the database
    insert_events_from_json(json_data)

    
    # Commit the transaction
    session.commit()

    # Close the session
    session.close()
