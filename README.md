![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)![Static Badge](https://img.shields.io/badge/Build-In_Progress-yellow?logo=github)

# noQ Backend (python)

![noQ](https://noq.nu/wp-content/uploads/2024/04/Logotyp_PNG-300x169.png)

## Developer Guidelines

### Create and Activate Virtual Environment

Create a virtual environment in the project directory and activate it:

    python -m venv env

    #On Windows:
    env\Scripts\activate

    #On Unix or macOS:
    source env/bin/activate

### Install Project Dependencies

Navigate to the project directory where the requirements.txt file is located and install required Python libraries listed in requirements.txt:

    pip install -r requirements.txt

This command installs all the necessary packages specified in the requirements.txt file.

### Database Initialization and Migration

Navigate to the directory containing manage.py and perform database migrations:

    python manage.py makemigrations
    python manage.py migrate
    python manage.py runscript generate_data
    python manage.py runscript generate_jobs
    python manage.py runserver

These commands set up the database schema based on the Django models defined in the project.
Qcluster is optional when testing and is used for automating periodic tasks

#### Create Local Superuser

    python manage.py createsuperuser

#### API Endpoints

Access API documentation at http://localhost:8000/api/docs.

#### General naming for all APIs

    /objects GET lists an object, with method name objects_list, can also have filter parameters
    /objects/id GET retrieves a unique instance of object(/objects/id), with method name object_detail(id)
    /objects/id POST creates an object, with method name object_add
    /objects/id PATCH updates an object, with method name object_update(id)
    /objects/id DELETE deletes an object, with method name object_delete(id)

#### Generate Random Data for Tests

    python manage.py runscript delete_all_data
    python manage.py runscript generate_data

All login credentials for generated users are stored in the fake_credentials.txt file located in the scripts folder.

#### Test Site

Access the test site at http://localhost:8000.

#### Running test cases

To run the test case for backend applications you can run following commands.

##### backend

    python manage.py test backend

##### noq_django

    python manage.py test noq_django

### Troubleshooting

#### pkg_resources Module Error

If you encounter a ModuleNotFoundError related to pkg_resources during the migration make sure all dependencies, setup tools & pip are installed and up to date.

    pip install setuptools
    pip install --upgrade pip

Then retry running the migration commands.

## Contributors

<a href="https://github.com/noQ-sweden/noq_backend_python/graphs/contributors">
    <img src="https://contrib.rocks/image?repo=noQ-sweden/noq_backend_python" />
</a>

Made with [contrib.rocks](https://contrib.rocks).
