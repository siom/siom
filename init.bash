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
sudo pip install -r /vagrant/requirements.txt

## mysql
sudo debconf-set-selections <<< "mysql-server-14 mysql-server/root_password password ${MYSQL_PASS}"
sudo debconf-set-selections <<< "mysql-server-14 mysql-server/root_password_again password ${MYSQL_PASS}"
sudo apt-get -y install mysql-server
mysql --user=root "--password=${MYSQL_PASS}" <<< "create database siom character set utf8"
mysql --user=root "--password=${MYSQL_PASS}" <<< "create user 'siom'@'localhost' identified by 'neisvengiama'"
mysql --user=root "--password=${MYSQL_PASS}" <<< "use siom; grant all privileges on siom.* to 'siom'@'%' identified by 'neisvengiama' with grant option"
sudo apt-get -y install libapache2-mod-auth-mysql
sudo apachectl restart

mkdir -p "${GENERATED_DIR}/tasks"
mkdir -p "${GENERATED_DIR}/sys"
mkdir -p "${GENERATED_DIR}/run"
mkdir -p "${GENERATED_DIR}/latex"

# comile box
sudo updatedb
mkdir -p /tmp/box
cp -r /vagrant/grader/box/* /tmp/box/
cd /tmp/box
chmod a+x mk-syscall-table
sed -i'' -e "s/autoconf.h/$(locate autoconf.h | head -n 1 | sed -e 's/[\/&]/\\&/g')/g" mk-syscall-table box.c
sed -i'' -e 's/"box\/syscall-table.h"/"syscall-table.h"/' box.c
make o=../ s=../ 'CC=gcc -std=c99'
cp box "${GENERATED_DIR}/sys/"
cp /vagrant/grader/checker.py "${GENERATED_DIR}/sys"
cd

# initialize database
cd /vagrant/
cp settings.py.tmpl settings.py
( echo 'use siom;' && python manage.py sqlall siom ) > /tmp/siom.sql
mysql --user=root "--password=${MYSQL_PASS}" < /tmp/siom.sql
sudo rm -rf /tmp/siom.sql
echo -e 'yes\nsiom\n\nsiom\nsiom' | python manage.py syncdb
python manage.py migrate kombu.transport.django
python manage.py migrate djcelery
cd

# start server on startup
cat <<EOF > /etc/init.d/siom
#!/bin/bash
# =========================================================
#  siom - start siom server
# =========================================================
#
# :Usage: /etc/init.d/siom {start|stop|restart}

### BEGIN INIT INFO
# Provides:          siom
# Required-Start:    \$network \$local_fs \$remote_fs
# Required-Stop:     \$network \$local_fs \$remote_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: siom servers startup script
### END INIT INFO

start_siom() {
	nohup python /vagrant/manage.py celeryd -E -l info -c 1 &
	nohup python /vagrant/manage.py runserver 0.0.0.0:8000 &
}
stop_siom() {

}

case "\$1" in
	start)
		start_siom
		;;
	stop)
		stop_siom
		;;
	restart)
		stop_siom
		start_siom
		;;
	*)
	echo "Usage: \$0 {start|stop|restart}"
	exit 1
esac

exit 0
EOF
chmod a+x /etc/init.d/siom
sudo update-rc.d siom defaults
