#!/usr/bin/env python3

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

packages = setuptools.find_packages()
package_data = {"condiga_utils": ["condiga_utils/*"]}

data_files = [(".", ["LICENSE", "README.md"])]

setuptools.setup(
    name="condiga",
    version="0.2.2",
    zip_safe=True,
    author="Vijini Mallawaarachchi and Yu Lin",
    author_email="viji.mallawaarachchi@gmail.com",
    description="ConDiGA: Contigs directed gene annotation for accurate protein sequence database construction in metaproteomics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/metagentools/ConDiGA",
    license="MIT",
    packages=packages,
    package_data=package_data,
    data_files=data_files,
    include_package_data=True,
    scripts=["condiga"],
    entry_points={
        "console_scripts": [
            "convert=condiga_utils.support.convert:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Operating System :: OS Independent",
    ],
    install_requires=["biopython", "tqdm", "XlsxWriter", "click"],
    python_requires=">=3.8",
)
