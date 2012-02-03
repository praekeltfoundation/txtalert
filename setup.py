from setuptools import setup, find_packages

def listify(filename, filter_callable=None):
    return filter(filter_callable, open(filename,'r').readlines())

setup(
    name = "txtalert",
    version = "0.1",
    url = 'http://github.com/smn/txtalert',
    license = 'GPL',
    description = "txtAlert sends automated, personalized SMS reminders to patients on chronic medication.",
    long_description = open('README.rst', 'r').read(),
    author = 'Praekelt Foundation',
    author_email = "dev@praekeltfoundation.org",
    packages = find_packages(),
    dependency_links = [
        'https://github.com/smn/vumi-client/tarball/master#egg=vumi-client',
    ],
    install_requires = [
        'vumi-client',
        ] + listify('requirements.pip', lambda x: 'git+git' not in x),
    classifiers = listify('CLASSIFIERS.txt')
)

