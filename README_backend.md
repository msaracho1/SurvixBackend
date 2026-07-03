# Survix — Backend

API REST del proyecto Survix, una plataforma digital para estimular la vida outdoor. Provee los endpoints consumidos por el frontend web y la app mobile: actividades, guías, tips de supervivencia, usuarios, autenticación y contenido editorial.

## Tecnologías

- **Python 3.10+** — lenguaje principal
- **FastAPI / Flask / Django** — framework web (ver `app/main.py`)
- **Base de datos relacional** — configurada via `DATABASE_URL`
- **JWT** — autenticación stateless
- **Google OAuth** — autenticación social

## Requisitos previos

- Python 3.10+
- pip

## Instalación

```bash
git clone https://github.com/msaracho1/SurvixBackend.git
cd SurvixBackend
python3 -m venv venv

# macOS / Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

pip install -r app/requirements.txt
```

## Variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```
DATABASE_URL=tu_cadena_de_conexion
SECRET_KEY=tu_clave_secreta_jwt
GOOGLE_CLIENT_ID=tu_google_client_id
FIREBASE_API_KEY=tu_firebase_api_key
FIREBASE_PROJECT_ID=tu_firebase_project_id
```

> ⚠️ Nunca subir el archivo `.env` al repositorio.

## Cómo correr el proyecto

```bash
# FastAPI:
uvicorn app.main:app --reload --port 8000

# Flask:
flask run --port 8000

# Django:
python manage.py runserver 8000
```

La API queda disponible en `http://localhost:8000`.
Si usás FastAPI, la documentación interactiva está en `http://localhost:8000/docs`.

## Arquitectura técnica

El backend sigue una estructura por capas:

```
SurvixBackend/
├── app/
│   ├── main.py       ← punto de entrada de la API
│   ├── routes/       ← endpoints REST
│   ├── models/       ← modelos de datos
│   └── requirements.txt
├── .env              ← variables de entorno (no subir a git)
└── .gitignore
```

El backend es completamente independiente del cliente. Expone una API REST consumida tanto por el frontend web como por la app mobile.

## Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| POST | /auth/login | Login con email y contraseña |
| POST | /auth/google | Login con Google OAuth |
| POST | /auth/register | Registro de nuevo usuario |
| GET | /activities | Listado de actividades outdoor |
| GET | /guides | Listado de guías |
| GET | /tips | Tips de supervivencia |
| GET | /blog | Posts del blog |
| GET | /admin/users | Gestión de usuarios (admin) |

> Los endpoints exactos pueden variar. Consultar la documentación en `/docs` con el servidor corriendo.

## Librerías principales

| Librería | Uso |
|---|---|
| fastapi / flask / django | Framework web |
| uvicorn | Servidor ASGI (si FastAPI) |
| sqlalchemy / django ORM | ORM para base de datos |
| pyjwt | Generación y validación de tokens JWT |
| python-dotenv | Carga de variables de entorno |
| google-auth | Validación de tokens de Google OAuth |

## Autores

- **Michael Saracho** — Backend
- **Priscila Gómez** — Colaboración en Backend
