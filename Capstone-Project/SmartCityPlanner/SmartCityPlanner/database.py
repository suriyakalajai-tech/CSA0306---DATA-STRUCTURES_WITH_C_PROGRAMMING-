import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash
from config import Config

def connect():
    Config.DATABASE.parent.mkdir(parents=True, exist_ok=True)
    db=sqlite3.connect(Config.DATABASE)
    db.row_factory=sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db

def init_db():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'admin');
        CREATE TABLE IF NOT EXISTS locations(id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, lat REAL NOT NULL, lon REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS facilities(id INTEGER PRIMARY KEY, name TEXT, category TEXT, locality TEXT, lat REAL, lon REAL);
        CREATE TABLE IF NOT EXISTS network_versions(id INTEGER PRIMARY KEY, name TEXT, utility TEXT, locality TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, parent_id INTEGER, status TEXT DEFAULT 'draft');
        CREATE TABLE IF NOT EXISTS utility_edges(id INTEGER PRIMARY KEY, version_id INTEGER, source TEXT, target TEXT, cost REAL, capacity REAL, utility TEXT, geometry TEXT, FOREIGN KEY(version_id) REFERENCES network_versions(id));
        CREATE TABLE IF NOT EXISTS analyses(id INTEGER PRIMARY KEY, module TEXT, locality TEXT, title TEXT, result_json TEXT, created_by TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS notifications(id INTEGER PRIMARY KEY, message TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, is_read INTEGER DEFAULT 0);
        """)
        if not db.execute("SELECT id FROM users LIMIT 1").fetchone():
            db.execute("INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",
                       ("admin", generate_password_hash("Admin@123"), "admin"))
        if not db.execute("SELECT id FROM locations LIMIT 1").fetchone():
            locations=[("Adyar",13.0012,80.2565),("Anna Nagar",13.0850,80.2101),("T. Nagar",13.0418,80.2341),
                       ("Velachery",12.9750,80.2210),("Mylapore",13.0368,80.2676),("Guindy",13.0067,80.2206),
                       ("Tambaram",12.9249,80.1000),("Perungudi",12.9600,80.2430),("Egmore",13.0732,80.2609)]
            db.executemany("INSERT INTO locations(name,lat,lon) VALUES(?,?,?)",locations)
            facilities=[
              ("Apollo Hospital","Hospital","Greams Road",13.0634,80.2518),("Adyar Cancer Institute","Hospital","Adyar",13.0067,80.2410),
              ("Government General Hospital","Hospital","Park Town",13.0785,80.2785),("Anna Nagar Tower School","School","Anna Nagar",13.0858,80.2105),
              ("Fire Station Adyar","Fire Station","Adyar",13.0060,80.2570),("Guindy Police Station","Police Station","Guindy",13.0064,80.2200),
              ("Guindy Metro","Transit","Guindy",13.0067,80.2206),("Airport Metro","Transit","Meenambakkam",12.9800,80.1640)]
            db.executemany("INSERT INTO facilities(name,category,locality,lat,lon) VALUES(?,?,?,?,?)",facilities)
        if not db.execute("SELECT id FROM network_versions LIMIT 1").fetchone():
            cur=db.execute("INSERT INTO network_versions(name,utility,locality,status) VALUES(?,?,?,?)",("Chennai demo baseline","All utilities","Adyar","baseline"))
            vid=cur.lastrowid
            edges=[("A","B",12,100),("B","C",8,80),("A","D",18,100),("D","C",7,60),("C","E",10,70),("B","E",20,50),("D","F",9,90),("F","E",11,60)]
            db.executemany("INSERT INTO utility_edges(version_id,source,target,cost,capacity,utility) VALUES(?,?,?,?,?,?)",
                           [(vid,*e,"Water") for e in edges])
