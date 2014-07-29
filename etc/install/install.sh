#!/bin/bash

set -ex

# Script to set up a Django project on Vagrant.

# Installation settings

PROJECT_NAME=$1

DB_NAME=$PROJECT_NAME
VIRTUALENV_NAME=$PROJECT_NAME

PROJECT_DIR=/home/vagrant/$PROJECT_NAME
VIRTUALENV_DIR=/home/vagrant/.virtualenvs/$PROJECT_NAME

PGSQL_VERSION=9.1

if [ ! -f /home/vagrant/.locales ]; then
    # Need to fix locale so that Postgres creates databases in UTF-8
    cp -p $PROJECT_DIR/etc/install/etc-bash.bashrc /etc/bash.bashrc
    locale-gen en_GB.UTF-8
    dpkg-reconfigure locales
    touch /home/vagrant/.locales
fi

export LANGUAGE=en_GB.UTF-8
export LANG=en_GB.UTF-8
export LC_ALL=en_GB.UTF-8

# Install essential packages from Apt
apt-get update -y

if ! command python; then
    # Python dev packages
    apt-get install -y build-essential python python-dev
fi

# python-setuptools being installed manually
if [ ! -f /home/vagrant/.ez_setup ]; then
    EZ_SETUP=https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py
    wget $EZ_SETUP -O - | python
    touch /home/vagrant/.ez_setup
fi

# Dependencies for image processing with Pillow (replacement for PIL)
# supporting: jpeg, tiff, png, freetype, littlecms
# (pip install pillow to get pillow itself, not in requirements.txt)
apt-get install -y libjpeg-dev libtiff-dev zlib1g-dev libfreetype6-dev \
    liblcms2-dev

# Git (we'd rather avoid people keeping credentials for git commits
# in the repo, but sometimes we need it for pip requirements that
# aren't in PyPI)
if ! command -v git ; then
    apt-get install -y git
fi

# mcedit
if ! command -v mcedit; then
    apt-get install -y mc
fi

# create place holder for django logs
mkdir -p /var/log/django
chmod a+rw /var/log/django
chown www-data:www-data /var/log/django


# Postgresql
if ! command -v psql; then
    apt-get install -y postgresql-$PGSQL_VERSION libpq-dev

    cp $PROJECT_DIR/etc/install/pg_hba.conf \
        /etc/postgresql/$PGSQL_VERSION/main/
    /etc/init.d/postgresql reload
fi

# virtualenv global setup
if ! command -v pip; then
    easy_install -U pip
fi

if [[ ! -f /usr/local/bin/virtualenv ]]; then
    pip install virtualenv virtualenvwrapper stevedore virtualenv-clone
fi

if ! command -v nginx ; then
    apt-get install -y nginx
    cp $PROJECT_DIR/etc/install/nginx.default.conf /etc/nginx/sites-available/uwsgi.conf
    rm /etc/nginx/sites-enabled/default
    ln -s /etc/nginx/sites-available/uwsgi.conf /etc/nginx/sites-enabled/default
fi

# bash environment global setup
cp -p $PROJECT_DIR/etc/install/bashrc /home/vagrant/.bashrc
su - vagrant -c "mkdir -p /home/vagrant/.pip_download_cache"

# postgresql setup for project
DB_EXISTS=`psql -l -Upostgres | grep $DB_NAME | wc -l`
if [[ $DB_EXISTS -eq 0 ]]; then
    createdb -Upostgres $DB_NAME
fi


# virtualenv setup for project
su - vagrant -c "/usr/local/bin/virtualenv $VIRTUALENV_DIR && \
    echo $PROJECT_DIR > $VIRTUALENV_DIR/.project && \
    PIP_DOWNLOAD_CACHE=/home/vagrant/.pip_download_cache \
    $VIRTUALENV_DIR/bin/pip install -r $PROJECT_DIR/requirements.txt"

# install uwsgi system-wide
if ! command -v uwsgi ; then
    apt-get install libpcre3-dev
    pip install uwsgi==2.0.6

    mkdir -p /var/log/uwsgi/
    chmod a+rw /var/log/uwsgi/

    mkdir -p /etc/uwsgi/vassals

    cp $PROJECT_DIR/uwsgi.ini /etc/uwsgi/vassals/django.ini
    cp $PROJECT_DIR/etc/install/uwsgi.ini /etc/uwsgi/emperor.ini
    cp $PROJECT_DIR/etc/install/uwsgi.conf /etc/init/
fi

echo "workon $VIRTUALENV_NAME" >> /home/vagrant/.bashrc

# Set execute permissions on manage.py, as they get lost if we build \
# from a zip file
chmod a+x $PROJECT_DIR/manage.py

# Django project setup
su - vagrant -c "source $VIRTUALENV_DIR/bin/activate && \
   cd $PROJECT_DIR && ./manage.py syncdb --noinput && \
   ./manage.py migrate && ./manage.py collectstatic --noinput"
