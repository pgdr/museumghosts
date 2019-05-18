import os
import setuptools


def src(x):
    root = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(root, x))


def _read_file(fname, op):
    with open(src(fname), "r") as fin:
        return op(fin.readlines())


def readme():
    return _read_file("README.md", lambda lines: "".join(lines))


def requirements():
    return _read_file("requirements.txt", lambda lines: "".join(lines))


setuptools.setup(
    name="museumghosts",
    version="0.0.2",
    author="pgdr",
    packages=["museumghosts"],
    long_description=readme(),
    long_description_content_type="text/markdown",
    install_requires=requirements(),
    entry_points={"console_scripts": ["museumghosts=museumghosts:main"]},
)
