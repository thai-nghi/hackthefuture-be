import ast
import json
import requests

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from src.db_tables import organizations
from src.core import config
from pydantic import PostgresDsn
import os

PG_URL = PostgresDsn.build(
    scheme="postgresql",
    user=config.settings.POSTGRES_USER,
    password=config.settings.POSTGRES_PASSWORD,
    host=config.settings.POSTGRES_HOST,
    port=config.settings.DB_PORT,
    path=f"/{config.settings.POSTGRES_DB}",
)


script_dir = os.path.dirname(os.path.abspath(__file__))

engine = create_engine(PG_URL)
Session = sessionmaker(bind=engine)
session = Session()

base_url = 'http://192.168.31.115:8001'

response = (requests.get(f"{base_url}/metadata/org")).json()

countries = {entry["label"]: entry["value"] for entry in response["data"]["countries"]}

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


    # Return the edited vendor data as a tuple
    #return (name, address, phone, vendor_type, email, size, vendor_id)

def main():
    # Load data from the text file

    file_path = os.path.join(script_dir, 'vendors.txt')
    vendor_data = load_data(file_path)

    # Iterate through the vendor data and allow editing
    for vendor in vendor_data:
        data = edit_vendor_data(vendor)
        session.execute(organizations.insert().values(data))

    session.commit()
    session.close()


if __name__ == "__main__":
    main()