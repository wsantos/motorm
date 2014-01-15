motorm
======

Async Motor ORM

.. image:: https://coveralls.io/repos/wsantos/motorm/badge.png?branch=master
  :target: https://coveralls.io/r/wsantos/motorm?branch=master
  :alt: Coverage

.. code-block:: python

    class Person(AsyncModel):
         name = StringType(required=True)
         website = URLType()


    >>> person = Person()
    >>> person.name = "Jonny Bravo"
    >>> person.website = "http://google.com"
    
    >>> person = yield person.save()

