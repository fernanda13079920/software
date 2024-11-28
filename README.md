# LenguaStream AI.

## Introducción

ejemplo para usar git, crea tu rama con tu nombre ejmplo: franz
ahora hagamos cammbio en nuestra rama :D 
LenguaStream AI, es un software SaaS, para la Transcripcion y/o Traducción de Conferencia Presencial, Videos y Audio con Inteligencia Artificial.

<hr/>

## Estructura del proyecto

```
software/  
├── proyecto/  
│   ├── controllers/  
│       └── UserController.py  
│   ├── database/  
│       └── connection.py  
│       └── usuario_db.py  
│   ├── models/  
│       └── User.py  
│   ├── routers/  
│       └── __init__.py  
│       └── router.py  
│   ├── views/  
│       └── static/  
│       └── templates/  
│   ├── __init__.py  
├── .env.example  
├── .gitignore  
├── README.md  
├── config.py  
├── run.py  
├── requirements.txt  
├── config 

```

----

## Entorno Virtual, en caso que no tenga instalado el virtual instalar con el comando:
Para windows: C:\Users\Jenn\AppData\Local\Programs\Python\Python310\python.exe -m pip install virtualenv

`C:\Users\Jenn\AppData\Local\Programs\Python\Python310\python.exe -m virtualenv env`

`.\env\Scripts\activate.bat`

`pip install -r requirements.txt`


Para Linux(ubuntu): pip install virtualenv --break-system-packages

`python3 -m virtualenv env`   o  `virtualenv venv`
 
`source env/bin/activate`

`pip install -r requirements.txt`



Paso no necesario hacerlo porque si ya instalaste los requirements.txt : pip install Flask Flask-SQLAlchemy Flask-Migrate psycopg2 python-dotenv


----

## Migrar a la base de datos Postgres


`flask db init`

`flask db migrate -m "Crea la tabla Usuarios"`

`flask db upgrade`


----

## actualizar la base de datos


`flask db downgrade`
`flask db upgrade`
`flask db migrate -m "actualizacion"`
`flask db upgrade`
----

## Uso de Git y Github para subir sus cambios al repositorio

`git init`

`git status`

`git add .`


esto solo se hace la primera vez

git config --global user.email "aquituemail@algo.com"

git config --global user.name "aquitunombredesuario"


`git commit -m "comentario de lo que realizaste"`


subir el proyecto al repositorio github, esto solo lo realizá el que creó el proyecto en github, se hace la primera vez despues ya no.

`git remote add origin` https://nombredelrepositorio.git


subir los cambios a la rama master del proyecto de github, se recomienda que cada colaborador se creé su propia rama y envié los cambios a su rama propia para que el master confirme dichos cambios.

`git push -u origin master`



----

## Ramas del Proyecto

`git branch`

crear una rama en el repositorio, nombre_rama
`git branch nombre_rama`

cambiar de la rama nombre
`git checkout nombre_rama`


----

Si queres ver los cambios de otra rama que se haya subido al github, hacer un commit antes si esque has modificado algo.
Traer los cambios sin tener ramas,cuando solo tenes la rama Master.   
`git pull` 

Traer los cambios de una rama especifica nombre_rama
`git pull origin nombre_rama`

Unir los cambios de tu rama con tu rama master para subir al github

`git checkout master`

`git merge nombre_rama`

Subir a la rama master 
`git push -u origin master`

Subir a la rama especifica nombre_rama
`git push -u origin nombre_rama`



----

Ver los registros de los cambios realizados
`git log`

Crear un archivo para ingonar archivos especificos pones el nombre ya se de las capetas o archivos dentro

.gitignore


Revertir cambios de los archivos realizado 

`git checkout --`

