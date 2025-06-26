from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md')) as f:
    long_description = f.read()


setup(
    name='swimrankingsscraper',
    version='0.1.5',
    description='A scraper for swimrankings.net',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://swimrankingsscraper.readthedocs.io/',
    author='Bas Neeleman',
    author_email='bas@neeleman-mail.nl',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
    ],
    packages=find_packages(include=['swimrankingsscraper']),
    include_package_data=True,
    install_requires=['requests', 'beautifulsoup4', 'lxml'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==8.0.0'],
    test_suite='tests',
)