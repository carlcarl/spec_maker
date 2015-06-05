#!/bin/sh

sudo apt-get install python-setuptools
sudo apt-get install pandoc
sudo apt-get install texlive-latex-base texlive-xetex texlive-latex-recommended texlive-latex-extra

sudo easy_install pip
sudo pip install -r $PWD/requirements/dev.txt

# Relace pdflatex with xelatex in sphinx
sudo sed -i "s/pdflatex/xelatex/g" /usr/local/lib/python2.7/dist-packages/sphinx/texinputs/Makefile

cp spec_maker/settings/local.example.py spec_maker/settings/local.py
