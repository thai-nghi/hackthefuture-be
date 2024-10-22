import json
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from src.db_tables import events, event_tag  # Adjust import according to your structure
from src.core import config
from pydantic import PostgresDsn
import os
from sqlalchemy.dialects.postgresql import insert as pg_insert

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


def load_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


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

    # Commit the transaction
    session.commit()


if __name__ == "__main__":
    # Load the JSON data from a file
    file_path = os.path.join(script_dir, "processed_data.json")
    json_data = load_json(file_path)

    # Insert events into the database
    insert_events_from_json(json_data)

    # Close the session
    session.close()
