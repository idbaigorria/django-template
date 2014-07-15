# Introduction

Baigorria public lights control software

# Execution

## Setup

In order to run this project you will need to install Vagrant, check
online on how to do it, the process to setup a devel machine is:

    $ git clone https://github.com/idbaigorria/light-control.git
    ....
    $ vagrant up
    ....
    $ vagrant ssh
    $ ./manage.py createsuperuser
    $ exit


## Running

After you have follow the Setup process you can start the web server by
running:

    $ vagrant ssh
    $ ./manage.py runserver 0:8000

After that you can open 127.0.0.1:8111 to get into our site


## SMS Bridge

The application was initially designed in a way where a SMS message was going to
be received under certain events, the system was tested with a ZTE MF193, using
Claro as telephony provider, the initial security features are rather simple. You
will need to stop the VM with the VirtualBox manager and add a filter that matches
your USB Modem device if you want to use it.

You may want to modify /etc/kannel/kannel.conf if you want to enhance your security

If you don't want to use the bridge then it's best to remove kannel:

    $ sudo apt-get purge kannel

# Developing

Developing is similar in a sense to execution:

    $ git clone https://github.com/idbaigorria/light-control.git
    ...
    $ cd light-control
    $ virtualenv .venv
    $ source .venv/bin/activate
    $ pip install -r requirements.txt
    $ sudo apt-get install libgeos-c1 libgdal1h gdal-bin python-gdal
    ....

We need the following lines so emacs or other editors can be used
    $ echo "names = ['$HOSTNAME',]" >> project/settings/local_hostnames.py


Now check you can get into the shell
    $ python manage.py shell
    $ exit()

If you could get into the shell without any exception been thrown then your
ready to use emacs or what ever editor you want to use with this project.

Now you can use emacs for development, I recommend you get python-django-mode
and python-mode enabled, you can use my own configuration if you want, this
configuration is based on Fabian Gallina's configuration, only I disabled a
few modules I don't like:


    $ git clone https://github.com/manuelnaranjo/dotemacs.git ~/.emacs.d



# Software Architecture

TODO: Describe here which pieces are involved in the project


# URLs: /

This is a list of urls that's relevant for this project

* /admin : Admin panel
* /httptester : SMS interface testing page
* /messagelog : SMS log
* /backend/kannel-usb0-smsc : internal URL used by kannel for message
  handling.
* /lights : main project


## URLs: /lights/


# Deployment

TODO: write here how to change default password and such things
