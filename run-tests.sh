#!/bin/bash
virtualenv --no-site-packages ve && \
. ve/bin/activate && \
pip install -r requirements.pip --download-cache=/var/lib/jenkins/pip-cache/ && \
./manage.py test --with-xunit --xunit-file=nosetests.xml \
    --with-coverage --cover-package=txtalert && \
(pep8 --repeat txtalert/ > pep8.txt || true) && \
coverage xml --include="txtalert/*" && \
deactivate