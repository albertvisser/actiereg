========
ActieReg
========

The name stands for Actie Registratie (action registration),
it is the web version of `ProbReg </albertvisser/probreg/>`_ -
that itself should have been called ActieReg
because it does more than register (the progress on) just problems.

For using it in the web browser, I added user support and changed the data storage
to an SQL database instead of XML files.

There's also the possibility to communicate with another web app of mine,
a `software project administration </albertvisser/myprojects/>`_,
to provide some context to the activity.

I was a bit embarrassed about not using this myself, 
so after my Trac installation failed me on switching to Python 3.14
I dusted off this app, changed it a bit and started using it for real.

Usage
-----

Use manage.py or the provided asgi or wsgi script to start the django app, and
configure your web server to communicate with it.

WARNING: the texts in the details page are currently marked as safe, to provide an easy way
to show code fragments and unformatted code. This implies that the application is intended
for trusted users only (i.e. myself in my own environment).

Requirements
------------

- Python
- Django
