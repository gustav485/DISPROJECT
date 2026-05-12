#!/bin/bash

cd /code/GreenGroceries/utils

python init_db.py

# psql --username=postgres -h database -p 5432 -f users.sql
# psql --username=postgres -h database -p 5432 -f produce.sql

cd /code/GreenGroceries

flask run --host=0.0.0.0
