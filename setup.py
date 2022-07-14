import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="reportlab-pdf-table-builder",
    version="1.1.5",
    author="Timotheos Savva",
    author_email="timotheos.savva12@gmail.com",
    description="A simple pdf table builder using the ReportLab Toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/timossavva/reportlab-pdf-table-builder",
    packages=setuptools.find_packages(),
    install_requires=[
        'reportlab>=3.6.5',
        'Pillow>=9.0.1'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True
)
