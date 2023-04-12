from distutils.util import convert_path
from os import path
from setuptools import find_packages
from setuptools import setup


# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

main_namespace = {}
version_path = convert_path("fewspy/version.py")
with open(version_path) as version_file:
    exec(version_file.read(), main_namespace)
version = main_namespace["__version__"]
maintainer_email = main_namespace["__maintainer_email__"]

install_requires = [
    "requests",
    "pandas",
    "geopandas",
    "pathlib",
    "typing",
    "validators",
]

tests_require = ["pytest", "pytest-cov", "responses"]

setup(
    name="hdsr_fewspy",
    packages=find_packages(include=["fewspy", "fewspy.*"]),
    version=version,
    license="MIT",
    description="An interface for interacting with hdsr github repos",
    long_description_content_type="text/markdown",
    long_description=long_description,
    author="Renier Kramer",
    author_email=maintainer_email,
    url="https://github.com/hdsr-mid/hdsr_pygithub",
    download_url=f"https://github.com/hdsr-mid/hdsr_pygithub/archive/v{version}.tar.gz",
    keywords=["interface", "interaction", "github", "files", "hdsr"],
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
