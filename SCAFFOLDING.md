ok, so now create two, complementary scaffoldings:

## projects/django-api: 

- there are already some files
- the idea is that it bootstraps whole django project, create base app and is ready for scaffolding apps that extends via convention
- have configured structlog and json logs as default
- dockerfile and pyproject.toml, .env - everything is tailored to the project
- django settings.py use dotenv at the very top

# modules/django-api-app: 

- asks for app name and model name, models and admin are packages with model_name as file name and Model inside, 
- api is django-ninja-extra controller model class pointing to models
- also a package with model_name as subpackage and controller.py and schemas.py with ninja controller class and Api Schema classes
- scaffold uses convention that adding next files automatically "sees" the files
- always one management command is created (only when app is created)
- convention also takes big care about careful api desscription, so generated client has concise and consistent naming