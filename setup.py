import os
import ast
from io import open
from setuptools import find_packages, setup

AUTHOR_NAME = 'John Andersen'
AUTHOR_EMAIL = 'johnandersenpdx@gmail.com'
ORG = 'pdxjohnny'
NAME = 'twothings'
DESCRIPTION = 'You want me to do two things?'
INSTALL_REQUIRES = [
    'keyring>=19.0.1',
    'exchangelib[kerberos]>=1.12.3',
    ]

IMPORT_NAME = NAME.replace('-', '_')
SELF_PATH = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(SELF_PATH, IMPORT_NAME, 'version.py'), 'r') as f:
    for line in f:
        if line.startswith('VERSION'):
            version = ast.literal_eval(line.strip().split('=')[-1].strip())
            break

with open(os.path.join(SELF_PATH, 'README.md'), 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name=NAME,
    version=version,
    description=DESCRIPTION,
    long_description=readme,
    long_description_content_type='text/markdown',
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR_NAME,
    maintainer_email=AUTHOR_EMAIL,
    url='https://github.com/' + ORG + '/' + NAME,
    license='MIT',
    keywords=[
        '',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    entry_points={
        'console_scripts': [
            NAME + '-calendar-sync = ' + IMPORT_NAME + '.calendar.sync:CalendarSync.cli',
        ],
    },
)
