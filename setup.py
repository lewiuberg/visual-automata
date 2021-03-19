import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="visual-automata",
    version="1.0.1",
    description="Visual Automata is a Python 3 library built as a wrapper for Caleb Evans' Automata library to add more visualization features.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/lewiuberg/visual-automata",
    author="Lewi Lie Uberg",
    author_email="lewi@uberg.me",
    license="MIT",
    keywords='automata',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=[
        "visual_automata",
        "visual_automata.fa"
    ],
    include_package_data=True,
    install_requires=[
        "automata-lib",
        "pandas",
        "graphviz",
        "colormath",
        "jupyterlab"
    ],
    entry_points={},
)
