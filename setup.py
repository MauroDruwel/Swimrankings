#!/usr/bin/env python3
"""
Setup script for the SwimRankings library.
"""

from setuptools import setup, find_packages

setup(
    name="swimrankings",
    version="0.1.0",
    description="A modern Python library for interacting with swimrankings.net",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Mauro Druwel",
    author_email="mauro.druwel@gmail.com",
    url="https://github.com/MauroDruwel/Swimrankings",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "lxml>=4.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
    },
)
