#!/bin/bash
set -e

echo "Setting up database"
echo "... Waiting for database to spin up"
sleep 5
echo "... Ensuring correct database encoding"
mysql -h db -P 3306 -u root --password=root -e 'ALTER DATABASE siom CHARACTER SET utf8'
echo "... Applying migrations"
python manage.py migrate
echo "... Seeding data"
python manage.py loaddata .devcontainer/seed_data/db.json

echo "Collecting static files"
python manage.py collectstatic --no-input

echo "Starting celery worker"
nohup python manage.py celery worker -l info -c 1 </dev/null &> /home/www/siom/logs/celery.txt &

echo "Starting web server"
nohup python manage.py runserver </dev/null &> /home/www/siom/logs/server.txt &

echo "Creating required folders"
mkdir -p /home/www/siom/web/latex_tmp
