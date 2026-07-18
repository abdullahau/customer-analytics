# setup.py
from setuptools import setup, find_packages

setup(
    name="nbddirichlet",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python implementation of the NBD-Dirichlet model",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/MuniNate/nbddirichlet",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "pandas",
        "matplotlib",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
)