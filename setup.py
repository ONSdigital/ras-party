from setuptools import setup, find_packages

NAME = "ras_party"
VERSION = "0.0.2"

REQUIRES = []

setup(
    name=NAME,
    version=VERSION,
    description="Party API",
    author_email="ras@ons.gov.uk",
    url="",
    keywords=["ONS", "RAS", "Party API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    long_description="RAS Party microservice.",
)
