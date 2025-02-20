from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='watch-calibration',
    version='0.0.1',
    license='MIT,',
    description='Basic example implemeting the SHREW.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Sabar Dasgupta',
    author_email='s@bardasgupta.com',
    install_requires=[],
    packages=['watch_calibration'],
    python_requires='>=3.8'
)
