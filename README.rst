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

    $ dnf install libyaml-devel
    $ pip install -r test-requirements.txt
    $ nosetests

Check test suite coverage::

    $ pip install coverage
    $ nosetests --with-coverage --cover-package=pdcupdater

If the test suite is failing, one thing to try is to remove the VCR cassette
data before re-running the tests::

    $ rm -rf pdcupdater/tests/vcr-request-data/
    $ nosetests

Getting an authentication token
-------------------------------

...from https://pdc.fedoraproject.org/

- go to https://pdc.fedoraproject.org/ in your browser and login.
- go to https://pdc.fedoraproject.org/rest_api/v1/auth/token/obtain/
- open up the devtools console in your browser, and find the request for the current page.
- right click to open a context menu and select 'copy as cURL'
- paste that into a terminal.  It should have your saml cookie.
- before hitting enter, edit the command to add the following option:

  - ``-H 'Accept: application/json'``, to tell the API you want data

- the command should print out your token.

Copy ``fedmsg.d/pdcupdater-example.py`` to ``fedmsg.d/pdcupdater.py`` and fill
in your token there.

Running the fedmsg-hub
----------------------

Run it for real::

    $ fedmsg-hub

Finally, you can take the dev instructions from `the-new-hotness
<https://github.com/fedora-infra/the-new-hotness#hacking>`_ and learn how to
set up a local fedmsg-relay so you can replay production messages and more
fully test out pdc-updater.
