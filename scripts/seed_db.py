import os
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def seed_database():
    DATABASE_URL = "mysql+pymysql://root:@localhost:3306"
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("Mempersiapkan database...")
        conn.execute(text("CREATE DATABASE IF NOT EXISTS akademik_ai;"))
        conn.execute(text("USE akademik_ai;"))
        
        base_dir = os.path.dirname(os.path.dirname(__file__))
        schema_path = os.path.join(base_dir, 'database', 'schema.sql')
        
        with open(schema_path, 'r') as f:
            sql_script = f.read()
            
        print("Menjalankan schema.sql...")
        for statement in sql_script.split(';'):
            if statement.strip():
                conn.execute(text(statement + ";"))
        
        print("Membuat user admin...")
        result = conn.execute(text("SELECT id FROM users WHERE username = 'admin'"))
        if not result.fetchone():
            admin_hash = get_password_hash("admin123")
            conn.execute(
                text("INSERT INTO users (username, password_hash, role) VALUES ('admin', :hash, 'admin')"),
                {"hash": admin_hash}
            )
            print("=> Admin user created (admin / admin123)")
            
        print("Membuat user mahasiswa (responden)...")
        result = conn.execute(text("SELECT id FROM users WHERE username = 'mahasiswa'"))
        if not result.fetchone():
            mhs_hash = get_password_hash("mahasiswa123")
            conn.execute(
                text("INSERT INTO users (username, password_hash, role) VALUES ('mahasiswa', :hash, 'mahasiswa')"),
                {"hash": mhs_hash}
            )
            print("=> Mahasiswa user created (mahasiswa / mahasiswa123)")
        
        conn.commit()
    print("\n✅ Setup database selesai!")

if __name__ == "__main__":
    seed_database()
