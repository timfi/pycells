import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycells",
    version="0.1",
    author="Tim Fischer",
    author_email="t.fischer98@hotmail.com",
    description="A small package for simulating simple cellular automata",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tim-fi/pycells",
    packages=["pycells"],
    package_dir={"pycells": "src"},
    package_data={"pycells": ["presets/*.yml"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
