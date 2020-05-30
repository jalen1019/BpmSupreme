from setuptools import setup, find_namespace_packages

setup(
    name="bpm_supreme", 
    version="0.1",
    package_dir={"":"src"},

    scripts=["src/bpm_supreme/download.py"],
    install_requires=["selenium>=3.141.0"]
)