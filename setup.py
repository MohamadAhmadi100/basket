import os

from setuptools import setup

requirements_dir = f"{os.getcwd()}/requirements.txt"
with open(requirements_dir, "r") as f:
    file = f.readlines()
    requirements = [line.rstrip() for line in file]

setup(
    name='basket',
    version='0.1.0',
    license='None',
    author='Mohamad',
    author_email='mohammadahmadidezhnet@gmail.com',
    load_description=open('README.md').read(),
    packages=["source"],
    install_requires=requirements,
    zip_safe=False
)