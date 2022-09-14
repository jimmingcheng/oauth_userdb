from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='oauth_userdb',
    version='1.0.0',
    description='OAuth User DB',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='',
    author='Jimming Cheng',
    author_email='jimming@gmail.com',
    packages=['oauth_userdb'],
    install_requires=[
        'jwt',
        'oauthlib',
        'requests',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
