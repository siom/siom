#!/bin/bash
set -e
echo "Setting up database"
mysql -h db -P 3306 -u root --password=root -e 'ALTER DATABASE siom CHARACTER SET utf8'
python manage.py migrate
echo "Starting celery worker"
nohup python manage.py celery worker -l info -c 1 </dev/null &> /home/www/siom/logs/celery.txt &
echo "Starting web server"
nohup python manage.py runserver </dev/null &> /home/www/siom/logs/server.txt &