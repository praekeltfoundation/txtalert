from setuptools import setup, find_packages

def listify(filename):
    return filter(None, open(filename,'r').readlines())

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
    install_requires = listify('requirements.pip'),
    classifiers = listify('CLASSIFIERS.txt')
)

