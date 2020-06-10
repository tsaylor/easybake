import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="easybake",
    version="0.0.2",
    author="Tim Saylor",
    author_email="tim.saylor@gmail.com",
    description="A static site builder",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tsaylor/easybake",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "Jinja2",
        "markdown",
        "PyYAML",
    ],
)
