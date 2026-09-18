require("dotenv").config();
const express = require("express");
const { Pool } = require("pg");

const app = express();
app.use(express.json());

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
});

// Crea la tabla si no existe, al arrancar el servidor
async function inicializarBaseDeDatos() {
    await pool.query(`
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            creado_en TIMESTAMP DEFAULT NOW()
        )
    `);
    console.log("Tabla 'usuarios' lista");
}

// Ruta de salud, para verificar que el server y la DB responden
app.get("/health", async (req, res) => {
    try {
        const resultado = await pool.query("SELECT NOW() AS hora_servidor");
        res.json({
            estado: "ok",
            hora_servidor: resultado.rows[0].hora_servidor,
        });
    } catch (error) {
        console.error("Error de conexión a la base:", error);
        res.status(500).json({ estado: "error", detalle: error.message });
    }
});

// Listar usuarios
app.get("/usuarios", async (req, res) => {
    try {
        const resultado = await pool.query(
            "SELECT * FROM usuarios ORDER BY id ASC"
        );
        res.json(resultado.rows);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Crear usuario
app.post("/usuarios", async (req, res) => {
    const { nombre, email } = req.body;

    if (!nombre || !email) {
        return res.status(400).json({ error: "Faltan 'nombre' o 'email'" });
    }

    try {
        const resultado = await pool.query(
            "INSERT INTO usuarios (nombre, email) VALUES ($1, $2) RETURNING *",
            [nombre, email]
        );
        res.status(201).json(resultado.rows[0]);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

const PORT = process.env.PORT || 3000;

inicializarBaseDeDatos()
    .then(() => {
        app.listen(PORT, () => {
            console.log(`Servidor corriendo en http://localhost:${PORT}`);
        });
    })
    .catch((error) => {
        console.error("No se pudo inicializar la base de datos:", error);
        process.exit(1);
    });
