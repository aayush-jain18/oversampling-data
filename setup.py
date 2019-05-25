from setuptools import setup
from setuptools import find_packages
import os


def read_file(filename):
    filepath = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), filename)
    if os.path.exists(filepath):
        return open(filepath).read()
    else:
        return ''


about = {}
with open(os.path.join(os.path.dirname(__file__), 'synthetic-data',
                       '__version__.py')) as f:
    exec(f.read(), about)

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    about['__long_description__'] = f.read()


setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=about['__long_description__'],
    long_description_content_type="text/markdown",
    author=about['__author__'],
    author_email=about['__author_email__'],
    maintainer=about['__maintainer__'],
    maintainer_email=about['__maintainer_email__'],
    license=about['__license__'],
    url=about['__url__'],
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'sklearn',
        'scipy',
        'matplotlib',
        'seaborn',
        'openpyxl',
        'imblearn',
        'sqlalchemy',
        'oyaml',
        'Click',
    ],
    entry_points='''
    [console_scripts]
    synthetic_data_generation=synthetic_data_generation:cli
    ''',
)