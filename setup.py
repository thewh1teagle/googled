from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()
with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()
setup(
    name="googled",  # How you named your package folder
    packages=['googled'],  # Chose the same as "name"
    include_package_data=False,
    version="v0.0.1",  # Start with a small number and increase it with every change you make
    license="MIT",  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description="Simple library for Google Drive in Python",  # Give a short description about your library
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="thewh1teagle",  # Type in your name
    author_email="example@gmail.com",  # Type in your E-Mail
    url="https://github.com/thewh1teagle/py-googled",  # Provide either the link to your github or to your website
    download_url="",
    keywords=[
        "drive",
        "google",
        "storage",
    ],  # Keywords that define your package best
    install_requires=requirements,  # I get to this in a second
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",  # Define that your audience are developers
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",  # Again, pick a license
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    
)
