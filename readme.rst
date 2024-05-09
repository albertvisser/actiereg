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


Usage
-----

Use manage.py or the provided asgi or wsgi script to start the django app, and
configure your web server to communicate with it.


Requirements
------------

- Python
- Django
