This is a backend daemon that listens to fedmsg and updates PDC with
information about what it sees on the bus.

See https://fedoraproject.org/wiki/Changes/ProductDefinitionCenter

Development
-----------

Set up a python virtualenv::

    $ sudo dnf -y install python-virtualenvwrapper
    $ source ~/.bashrc
    $ mkvirtualenv pdc-updater

Setup pdc-updater and its dependencies::

    $ workon pdc-updater
    $ pip install -r requirements.txt
    $ python setup.py develop

Try running the test suite::

    $ pip install -r test-requirements.txt
    $ nosetests

Check test suite coverage::

    $ pip install coverage
    $ nosetests --with-coverage --cover-package=pdcupdater

Run it for real::

    $ fedmsg-hub

Finally, you can take the dev instructions from `the-new-hotness
<https://github.com/fedora-infra/the-new-hotness#hacking>`_ and learn how to
set up a local fedmsg-relay so you can replay production messages and more
fully test out pdc-updater.
