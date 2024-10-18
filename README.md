# Setup env file
First create a .dev.env file following the .example.env file. Make sure to change the credential to what you desire

# Starting for development

You should use docker to start the database so that you don't have to install it on your system.

From the root folder, simply run

```bash
docker compose --env-file .dev.env -f ./deploy/dev-compose.yml up postgres -d
```
# Virtual environment and libraries

```bash
python -m venv .venv
source ./venv/bin/activate
pip install -r requirements.txt
```


# DB Migration
On your first start of the system or after you make changes to the `db_tables.py` file, you should make a db migration.

To update the db to the latest state, simply run

```bash
alembic -x db_url="postgresql+asyncpg://<db_user>:<db_password>@127.0.0.1/<db_name>" upgrade head
```

When you make any change to the `db_tables.py` you should create a migration

```bash
alembic -x db_url="postgresql+asyncpg://<db_user>:<db_password>@127.0.0.1/<db_name>" revision --autogenerate
```

# Starting minio for development

Minio is used for object storage (similar to S3) we're using a free self-hosted version cuz we're broke.

To start it run

```bash
docker compose --env-file .dev.env -f ./deploy/dev-compose.yml up minio -d
```

# Starting server for development
```bash
uvicorn main:app --host <host_ip> --port 8000 --reload
```


# Resetting DB
In case you mess up the data, you can jump into the database and wipe it clean.

First get a shell to the database:
```bash
docker exec -it <container_id_of_db> bash
```

Then use psql to get an interactive db:
```bash
 psql -U <username> -d <db_name>
```


Then paste this block to the shell, enter
```sql
DO $$ DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
END $$;

```



