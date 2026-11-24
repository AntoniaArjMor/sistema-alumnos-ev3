"""Configura una base de datos y secretos exclusivos para las pruebas."""
import os
import secrets
import tempfile

from werkzeug.security import generate_password_hash

os.environ["DB_PATH"] = os.path.join(
    tempfile.mkdtemp(prefix="alumnos-test-"), "alumnos.db"
)

os.environ["APP_SECRET_KEY"] = secrets.token_hex(32)

os.environ["ADMIN_CLAVE_HASH"] = generate_password_hash(
    secrets.token_hex(32),
    method="pbkdf2:sha256:600000"
)

os.environ["APP_COOKIE_SECURE"] = "0"