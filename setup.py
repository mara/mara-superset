from setuptools import setup, find_packages
import re

def get_long_description():
    with open('README.md') as f:
        return re.sub('!\[(.*?)\]\(docs/(.*?)\)', r'![\1](https://github.com/mara/mara-pipelines/raw/master/docs/\2)', f.read())

about = {}
with open('mara_superset/_version.py') as f:
    exec(f.read(), about)

setup(
    name='mara-superset',
    version=about['__version__'],

    description='Opinionated lightweight ELT pipeline framework',

    long_description=get_long_description(),
    long_description_content_type='text/markdown',

    url = 'https://github.com/leo-schick/mara-superset',

    install_requires=[
        'mara-db>=4.7.1',
        'mara-page>=1.3.0',
        'click',
        'requests'
    ],
    extras_require={
        'dev': ['apache-superset>=1.3.2']
    },

    python_requires='>=3.6',

    packages=find_packages(),

    author='Mara contributors',
    license='MIT',

    entry_points={},
)