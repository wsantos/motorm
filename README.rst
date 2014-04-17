motorm
======

Async Motor ORM

.. image:: https://coveralls.io/repos/wsantos/motorm/badge.png?branch=master
  :target: https://coveralls.io/r/wsantos/motorm?branch=master
  :alt: Coverage

.. image:: https://travis-ci.org/wsantos/motorm.png
  :target: http://travis-ci.org/wsantos/motorm
  :alt: Coverage


1. Declare model like in `Schematics <https://github.com/j2labs/schematics>`_, but use AsyncModel instead Model.

.. code-block:: python

    class Person(AsyncModel):
         name = StringType(required=True)
         website = URLType()

2. Connect to a database

.. code-block:: python

    >>> connect("MySystem_DB")

- Save (Update / Create), if the object has id it will be an update

.. code-block:: python

    >>> person = Person()
    >>> person.name = "Jonny Bravo"
    >>> person.website = "http://google.com"
    
    >>> person = yield person.save()

- Retrive from id

.. code-block:: python

    >>> person = yield Person.objects.get(id=1)
    
- Retrive from a model field

.. code-block:: python

    >>> person = yield Person.objects.get(name="Jonny Bravo")
    

- Retrive all objects from cursor database

.. code-block:: python

    >>> persons = yield Person.objects.filter({"name": {"$regex": "Jon.*"}}).all()
    
- Retrive all objects from database

.. code-block:: python

    >>> persons = yield Person.objects.all()
    
- Iterate asynchrony through cursor objects

.. code-block:: python

    >>> p_cursor = Person.objects.filter({"name": {"$regex": "Jon.*"}})
    
    >>> while (yield p_cursor.fetch_next):
    >>>     person = p_cursor.next_object()
    
    

