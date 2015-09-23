

Spec_Maker
========================

Below you will find basic setup instructions for the spec_maker
project. To begin you should have the following requirements::

- Python >= 2.7

Optional::
- `virtualenv >= 1.7 <http://www.virtualenv.org/>`_
- `virtualenvwrapper >= 3.0 <http://pypi.python.org/pypi/virtualenvwrapper>`_

Getting Started
------------------------

You have two setup choices: Simple or Virtualenv.
If you don't know virtualenv, just check the `Simple Setup` section.
Here we use `Ubuntu` as the OS environment.

Simple Setup
************

::

    ./simple_setup.sh

You should now be able to run the development server::

    ./run.sh

Then open your browser and connect to `http://localhost:7788`

Virtualenv Setup
*****************

::

    sudo apt-get install python-setuptools
    sudo apt-get install pandoc
    sudo apt-get install texlive-latex-base texlive-xetex texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended

    sudo easy_install pip

    sudo pip install virtualenvwrapper

To setup your local environment you should create a virtualenv and install the
necessary requirements(maybe you need to source /urs/local/bin/virtualenvwrapper.sh manually)::

    mkvirtualenv spec_maker
    $VIRTUAL_ENV/bin/pip install -r $PWD/requirements/dev.txt

    sed -i "s/pdflatex/xelatex/g" $VIRTUAL_ENV/local/lib/python2.7/site-packages/sphinx/texinputs/Makefile

Then create a local settings file and set your ``DJANGO_SETTINGS_MODULE`` to use it::

    cp spec_maker/settings/local.example.py spec_maker/settings/local.py
    echo "export DJANGO_SETTINGS_MODULE=spec_maker.settings.local" >> $VIRTUAL_ENV/bin/postactivate
    echo "unset DJANGO_SETTINGS_MODULE" >> $VIRTUAL_ENV/bin/postdeactivate

Exit the virtualenv and reactivate it to activate the settings just changed::

    deactivate
    workon spec_maker

You should now be able to run the development server::

    ./run.sh

Then open your browser and connect to `http://localhost:7788`

