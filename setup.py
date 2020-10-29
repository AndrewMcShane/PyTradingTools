from setuptools import find_packages, setup

# Subject to change as project progresses.

setup(
    name='pytradingtools',
    license='GPL 3.0',
    version='0.6',
    packages=find_packages(exclude=('test',)),
    include_package_data=True,
    long_description=open('README.md').read()
)
