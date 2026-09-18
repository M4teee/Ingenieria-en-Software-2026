# Proyecto Node + Express + Postgres (local, sin Docker)

Ejemplo mínimo de un backend con Express conectado a un Postgres instalado directamente en tu máquina.

## Requisitos

- Node.js instalado
- Postgres instalado localmente (ver instrucciones de instalación abajo)

## 1. Instalar Postgres

### macOS (con Homebrew)

```bash
brew install postgresql@16
brew services start postgresql@16
```

### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install postgresql
sudo systemctl start postgresql
sudo systemctl enable postgresql   # para que arranque solo al prender la máquina
```

### Windows

Descargar el instalador desde [postgresql.org](https://www.postgresql.org/download/windows/) y seguir el asistente. Se instala como servicio, así que arranca solo. Podés administrarlo desde `services.msc` (buscar "postgresql-x64-16").

## 2. Crear la base y el usuario

Conectate como superusuario y corré el script `setup.sql` incluido:

```bash
psql -U postgres -f setup.sql
```

En Linux, si tu usuario del sistema no tiene un rol de Postgres asociado, puede que necesites:

```bash
sudo -u postgres psql -f setup.sql
```

Esto crea:

- Usuario `admin` con contraseña `admin123`
- Base de datos `mi_app_dev`, propiedad de `admin`

(Podés cambiar esos valores en `setup.sql` y en el `.env`, siempre que coincidan.)

## 3. Configurar el proyecto

```bash
npm install
cp .env.example .env
```

Revisá que `DATABASE_URL` en `.env` apunte a tu instancia local (por defecto ya está bien si usaste los valores del paso anterior):

```
DATABASE_URL=postgres://admin:admin123@localhost:5432/mi_app_dev
```

## 4. Iniciar el servidor

```bash
npm start
```

El servidor crea automáticamente la tabla `usuarios` si no existe, al arrancar.

## 5. Probar que todo funciona

- `GET http://localhost:3000/health` → chequea conexión a la base
- `GET http://localhost:3000/usuarios` → lista usuarios
- `POST http://localhost:3000/usuarios` con body JSON `{ "nombre": "Juan", "email": "juan@ejemplo.com" }` → crea un usuario

## Administrar el servicio de Postgres

| Acción | macOS (brew) | Linux (systemd) | Windows |
|---|---|---|---|
| Arrancar | `brew services start postgresql@16` | `sudo systemctl start postgresql` | `net start postgresql-x64-16` |
| Parar | `brew services stop postgresql@16` | `sudo systemctl stop postgresql` | `net stop postgresql-x64-16` |
| Estado | `brew services list` | `sudo systemctl status postgresql` | `services.msc` |

## Resetear la base desde cero

```bash
psql -U postgres -c "DROP DATABASE mi_app_dev;"
psql -U postgres -f setup.sql
```
