from setuptools import setup, Extension

module = Extension(
    "sonde_parser",
    sources=["sonde_parser.c"]
)

setup(
    name="sonde_parser",
    version="1.0",
    ext_modules=[module]
)