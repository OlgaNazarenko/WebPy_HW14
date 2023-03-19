## WebPy_HW14
For this project it was used poetry, which is designed for dependency management and packaging in this project. It allowed declaring the libraries of this project depends on and manages (install/update) them for you. Kindly activate it.

REST API for storing and managing contacts 1. For the start need to initialize Docker through "Docker Compose" in order to initialize all services and databases used in this project, like Postgres and Redis:
        
    docker-compose up

Then, run the following command to start the FastAPI server in folder "REST":

    python3 (py) main.py

For this project was done the following:

- verification of the registered user's e-mail; 
- added the limit of requests to the contact routes along with the rate at which contacts are created:
- CORS for your REST API; 
- the option to update the user's avatar. For this purpose was used the Cloudinary service; 
- all sensitive info is stored in the ".env" file; 
- Docker Compose to run all services and databases in the application (Postgres and Redis)[^1]
------------------------------------------------------------------------------------------------
- the documentation for this project was completed with the help of **Sphinx**. It was applied in the functions and methods of the classes in the main modules:
   * *repository/contacts* & */users*
   * *routes/auth* & */contacts* & */users*
   * *services/auth* [^2]
- the repository modules are covered with unit tests using the **Unittest** framework.[^3] 
- scr/routes is covered with functional tests using the **PyTest** framework.
- the test coverage report was generated with **PyTest-Cov** [^4]




[^1]: You need to run docker-compose using the command *docker-compose up*
[^2]: You can find it: *docs/_build/html/index.html*
[^3]: A separate folder, *tests*, was created for storing files for this test purpose. To run the tests the following command should be done: *pytest "name_of_the_file".py*.
[^4]: *REST/htmlov/index.html* or to run/refresh manually : *pytest --cov=src tests/*
