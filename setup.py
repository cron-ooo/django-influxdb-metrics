"""
Python setup file for the influxdb_metrics app.

In order to register your app at pypi.python.org, create an account at
pypi.python.org and login, then register your new app like so:

    python setup.py register

If your name is still free, you can now make your first release but first you
should check if you are uploading the correct files:

    python setup.py sdist

Inspect the output thoroughly. There shouldn't be any temp files and if your
app includes staticfiles or templates, make sure that they appear in the list.
If something is wrong, you need to edit MANIFEST.in and run the command again.

If all looks good, you can make your first release:

    python setup.py sdist upload

For new releases, you need to bump the version number in
influxdb_metrics/__init__.py and re-run the above command.

For more information on creating source distributions, see
https://docs.python.org/3/distutils/sourcedist.html

"""
import os

from setuptools import find_packages, setup

import influxdb_metrics as app


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ""


setup(
    name="django-influxdb-metrics",
    version=app.__version__,
    description=("A reusable Django app that sends metrics "
                 "about your project to InfluxDB"),
    long_description_content_type="text/markdown",
    long_description=read("README.md"),
    license="The MIT License",
    platforms=["OS Independent"],
    keywords="django, app, reusable, metrics, influxdb",
    author="Martin Brochhaus",
    author_email="mbrochh@gmail.com",
    url="https://github.com/bitmazk/django-influxdb-metrics",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "django>=2.2",
        "influxdb>=2.9.1",
        "tld",
    ],
    extras_require={
        "celery": ["celery>=4"],
        "postgresql": ["python-server-metrics>=0.1.9"],
    },
    classifiers=[
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
