-- Ejecutar este script conectado como superusuario (por ejemplo con: psql -U postgres)
-- Crea el usuario y la base que usa el proyecto en desarrollo local.

CREATE USER admin WITH PASSWORD 'admin123';
CREATE DATABASE mi_app_dev OWNER admin;
GRANT ALL PRIVILEGES ON DATABASE mi_app_dev TO admin;
