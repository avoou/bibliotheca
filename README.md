# bibliotheca
Used Python3.9.1, Debian 9.5
Clone the git repository:
    git clone https://github.com/avoou/bibliotheca.git
To make a virtual environment:
    cd bibliotheca
    python3 -m venv env
    source env/bin/activate
Install any necessary dependencies for Python:
    pip install -r pip_requirements.txt
If there is a problem installing psycopg2:
    sudo apt install libpq-dev python-dev
    pip install -r pip_requirements.txt
Install Postgresql:
    sudo apt install postgresql postgresql-contrib
Run postgresql if necessary:
    sudo service postgresql start
Create a user named biblioth with password 123:
    sudo -u postgres -i
    createuser -P biblioth
    Enter password 123
Create a database named biblioth_db
    createdb biblioth_db -O biblioth
These parameters are in the file bibliotheca/database.py, in the line SQLALCHEMY_DATABASE_URL = "postgresql://biblioth:123@localhost/biblioth_db"
Then do the initial database migrations:
    alembic init --template generic ./alembic
Then edit files alembic.ini and env.py.
In alembic.ini add:
    script_location = ./alembic
    sqlalchemy.url = postgresql://biblioth:123@localhost/biblioth_db
In alembic/env.py add:
    import os
    import sys
    current_path = os.path.dirname(os.path.abspath(__file__))
    root_path = os.path.join(current_path, '.')
    sys.path.append(root_path)
    from bibliotheca.database import engine, Base
    from bibliotheca.models import *
    target_metadata = Base.metadata
To create a migration do:
    alembic revision --autogenerate -m "Your comments"
To apply migration:
    alembic upgrade head
In the directory dibliotheca where the file app.py is located:
    uvicorn app:app --reload --host 127.0.0.1
