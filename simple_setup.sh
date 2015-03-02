#!/bin/sh

sudo apt-get install python-setuptools
sudo apt-get install pandoc
sudo apt-get install texlive-latex-base texlive-xetex texlive-latex-recommended texlive-latex-extra

sudo easy_install pip
sudo pip install -r $PWD/requirements/dev.txt

cp spec_maker/settings/local.example.py spec_maker/settings/local.py
