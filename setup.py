import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycells",
    version="v0.1.6",
    author="Tim Fischer",
    author_email="t.fischer98@hotmail.com",
    description="A small package for simulating simple cellular automata.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tim-fi/pycells",
    packages=["pycells"],
    package_data={"pycells": ["presets/*.yml"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={'console_scripts': ['pycells = pycells.cli:cli']},
    python_requires='>=3.7',
    install_requires=[
        "Click==7.0",
        "numpy==1.18.1",
        "Pillow==7.0.0",
        "PyYAML==5.3",
    ]
)
