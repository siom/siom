#!/bin/bash

GENERATED_DIR='/vagrant/generated'
MYSQL_PASS='some password that no one will ever guess'

sudo apt-get -y update
sudo apt-get -y install moreutils vim build-essential fpc # must to have stuff
sudo apt-get -y install debconf-utils                     # for presettings apt-get parameters (like mysql password)
sudo apt-get -y install linux-headers-generic             # for autoconf.h

mkdir Build

## apache and extra modules
sudo apt-get -y install apache2 apache2-dev

## latex
sudo apt-get -y install texlive

## python
sudo apt-get -y install python python-dev python-pip
sudo pip install 'django==1.5.5'
sudo pip install django-celery
sudo pip install south
sudo pip install django-markdown
sudo pip install pygments
sudo pip install docutils
sudo pip install mysql-python

## mysql
sudo debconf-set-selections <<< "mysql-server-14 mysql-server/root_password password ${MYSQL_PASS}"
sudo debconf-set-selections <<< "mysql-server-14 mysql-server/root_password_again password ${MYSQL_PASS}"
sudo apt-get -y install mysql-server
mysql --user=root "--password=${MYSQL_PASS}" <<< "create database siom"
mysql --user=root "--password=${MYSQL_PASS}" <<< "create user 'siom'@'localhost' identified by 'neisvengiama'"
mysql --user=root "--password=${MYSQL_PASS}" <<< "use siom; grant all privileges on siom.* to 'siom'@'%' identified by 'neisvengiama' with grant option"
sudo apt-get -y install libapache2-mod-auth-mysql
sudo apachectl restart

mkdir -p "${GENERATED_DIR}/tasks"
mkdir -p "${GENERATED_DIR}/sys"
mkdir -p "${GENERATED_DIR}/run"
mkdir -p "${GENERATED_DIR}/latex"

cd /vagrant/grader/box/
chmod a+x mk-syscall-table
sed -i'' -e 's/autoconf.h/\/usr\/src\/linux-headers-3.2.0-58-generic\/include\/generated\/autoconf.h/g' mk-syscall-table box.c
make o=../ s=../ 'CC=gcc -std=c99'
cp box "${GENERATED_DIR}/sys/"
cp /vagrant/grader/checker.py "${GENERATED_DIR}/sys"
cd

cp settings.py.tmpl settings.py
cd /vagrant/
( echo 'use siom;' && python manage.py sqlall siom ) > /tmp/siom.sql
mysql --user=root "--password=${MYSQL_PASS}" < /tmp/siom.sql
sudo rm -rf /tmp/siom.sql
echo -e 'yes\nsiom\n\nsiom\nsiom' | python manage.py syncdb
python manage.py migrate kombu.transport.django
python manage.py migrate djcelery
cd

# nohup python manage.py celeryd -E -l info -c 1 &
# nohup python manage.py runserver 0.0.0.0:8000 &
