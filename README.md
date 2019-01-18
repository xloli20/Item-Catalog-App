# Item Catalog Web App

Seconed project in Udacity Fullstack Nanodegree.
 it's an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.
 
# Installation

  - [Python](https://www.python.org/downloads/)
  - [Vagrant](https://www.vagrantup.com/downloads.html)
  - [Virtual Machine](https://www.virtualbox.org/wiki/Downloads)

## How to Run the project?
Once you get the above installed, run the following in the terminal:

you should download [FSND virtual machine](https://github.com/udacity/fullstack-nanodegree-vm). then,
```sh 
$ cd vagrant
```
to Launch Vagrant VM
```sh 
$ vagrant up
```

to login into the VM
```sh 
$ vagrant ssh
```

then,
```sh 
$ cd /vagrant
```
you should downlaod or clone the project inside the vagrant folder. then run
```sh 
$ cd item-catalog
```

you should first run the database setup,
 ```sh 
$ python database_setup.py
```
then to fill it with items. run,
 ```sh 
$ python lotsofitems.py
```
then finally to run the app,
 ```sh 
$ python application.py
```
