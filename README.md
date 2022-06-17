# Digital land issues datasette

## Getting started

Create a python virtualenv then run:

    make init


Create a local sqlite datbase

    make issue-db

To run the application run:

    make run


## Adding new python packages to the project

This project uses pip-tools to manage requirements files. [https://pypi.org/project/pip-tools/](https://pypi.org/project/pip-tools/)

When using fresh checkout of this repository, then make init will take care of the initial of packages from the checked
in requirements and dev-requirements files.

These instructions are only for when you add new libraries to the project.

To add a production dependency to the main aapplication, add the package to the [requirements.in](requirements.in)
file.

Then run the piptools compile command on the "in" file:

    python -m piptools compile requirements/requirements.in

That will generate a new requirements.txt file in the requirements directory.

Then to install all the packages run:

    python -m piptools sync requirements/requirements.txt requirements/dev-requirements.txt
