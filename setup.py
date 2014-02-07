from setuptools import setup, find_packages


setup(
    name="txtalert",
    version="0.1",
    url='http://github.com/praekelt/txtalert',
    license='GPL',
    description=("txtAlert sends automated, personalized SMS reminders "
                 "to patients on chronic medication."),
    long_description = open('README.rst', 'r').read(),
    author = 'Praekelt Foundation',
    author_email = "dev@praekeltfoundation.org",
    packages = find_packages(),
    install_requires=[
        'Django>=1.5,<1.6',
        'django-nose',
        'gdata==2.0.18',
        'xlrd==0.7.1',
        'django-dirtyfields==0.1',
        'django-historicalrecords==1.1',
        'iso8601',
        'django-piston==0.2.3',
        'south==0.7.3',
        'gunicorn==0.12.1',
        'supervisor',
        'django-geckoboard',
        'python-memcached==1.48',
        'raven',
        'pytz',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable'
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
