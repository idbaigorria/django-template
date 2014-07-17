# Introduction

Baigorria django template

This project is a basic django template for application we make at I+D Baigorria,
the template includes support for a few features like:

* ngnix + uwsgi
* pip installation through requirements.txt
* emacs django-mode support

# Usage

This is a usage guide for I+D Baigorria, may not match your setup, first create
a new project under https://github.com/idbaigorria, we will reference it's name
as [project_name].


Then execute the following (remember to replace [project_name] with the name you
gave to your github project):

    $ git clone git@github.com:idbaigorria/django-template.git [project_name]
    $ cd project_name
    $ git remote set-url origin git@github.com:idbaigorria/[project_name].git
    $ sed -i "s/django_template/[project_name]/g" Vagrantfile
    $ sed -i "s/django_template/[project_name]/g" project/settings/base.py
    $ django-admin.py startapp [project_name]

Now you are ready to start Vagrant, this will take a while, get coffe

    $ vagrant up
