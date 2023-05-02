from os import path
from setuptools import find_packages
from setuptools import setup


# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

version = "1.6"

install_requires = [
    "requests",
    "geopandas",
    "pandas",
    "hdsr-pygithub",
    "pathlib",
    "typing",
    "validators",
]

tests_require = ["pytest", "pytest-cov"]

setup(
    name="hdsr_fewspy",
    packages=find_packages(include=["hdsr_fewspy", "hdsr_fewspy.*"]),
    version=version,
    license="MIT",
    description="A python project to request data (locations, timeseries, etc.) from a HDSR FEWS PiWebService",
    long_description_content_type="text/markdown",
    long_description=long_description,
    author="Renier Kramer",
    author_email="renier.kramer@hdsr.nl",
    url="https://github.com/hdsr-mid/hdsr_fewspy",
    download_url=f"https://github.com/hdsr-mid/hdsr_fewspy/archive/v{version}.tar.gz",
    keywords=["hdsr", "fews", "api", "fewspy", "wis"],
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={"test": tests_require},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
