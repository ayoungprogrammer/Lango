Installation
=================================

Install package with pip
~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install lango

Download Stanford Models and Parser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Make sure you have Java installed for the Stanford parser to work.

`Download Stanford Parser`_

Set Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~

Set environment variables for STANFORD\_PARSER and STANFORD\_MODELS to
where you downloaded the parser.

.. code:: python

    import os
    os.environ['STANFORD_PARSER'] = 'stanford-parser-full-2015-12-09'
    os.environ['STANFORD_MODELS'] = 'stanford-parser-full-2015-12-09'

.. _Download Stanford Parser: http://nlp.stanford.edu/software/stanford-parser-full-2015-12-09.zip