"""Initialiser SQLite-databasen med brukere og historikkdata."""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), "scada.db")

def init():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.executescript("""
    DROP TABLE IF EXISTS users;
    DROP TABLE IF EXISTS historian_archive;

    CREATE TABLE users (
        id       INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        role     TEXT NOT NULL,
        password TEXT NOT NULL
    );

    INSERT INTO users VALUES (1, 'admin',    'ADMINISTRATOR', 'Adm1nPl4tform!');
    INSERT INTO users VALUES (2, 'operator', 'OPERATOR',      'Op3r4t0r#42');
    INSERT INTO users VALUES (3, 'viewer',   'VIEWER',        'V1ewer_only');

    CREATE TABLE historian_archive (
        id        INTEGER PRIMARY KEY,
        ts        TEXT NOT NULL,
        sensor_id TEXT NOT NULL,
        event     TEXT NOT NULL
    );

    INSERT INTO historian_archive VALUES (1,  '2026-01-14 06:12:03', 'TEMP-001', 'Temperature nominal at 68.4 C');
    INSERT INTO historian_archive VALUES (2,  '2026-01-14 07:45:19', 'PRES-002', 'Pressure spike detected: 214 bar');
    INSERT INTO historian_archive VALUES (3,  '2026-01-14 08:02:55', 'VALVE-01', 'Manual override executed by operator');
    INSERT INTO historian_archive VALUES (4,  '2026-01-14 09:33:41', 'PUMP-003', 'Flow rate adjusted to 51.2 m3/h');
    INSERT INTO historian_archive VALUES (5,  '2026-01-14 11:17:08', 'ESD-MAIN', 'CTF{uni0n_b4sed_sc4d4_pwn3d}');
    INSERT INTO historian_archive VALUES (6,  '2026-01-14 12:44:22', 'TEMP-001', 'Temperature back to normal: 69.1 C');
    INSERT INTO historian_archive VALUES (7,  '2026-01-14 14:05:37', 'PRES-002', 'Pressure stable at 199 bar');
    INSERT INTO historian_archive VALUES (8,  '2026-01-14 15:28:11', 'VALVE-01', 'Valve closed successfully');
    """)

    conn.commit()
    conn.close()
    print(f"[+] Database initialisert: {DB}")

if __name__ == "__main__":
    init()
