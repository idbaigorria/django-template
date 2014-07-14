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
