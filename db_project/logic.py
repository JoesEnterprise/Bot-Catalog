"""Database manager module
Provides a DatabaseManager class that can create the project's tables.
"""
from typing import List
import sqlite3
from .config import DATABASE

class DatabaseManager:
    """Simple SQLite database manager for creating and inspecting tables."""

    def __init__(self, database: str = DATABASE):
        self.database = database

    def create_tables(self) -> None:
        """Create application tables according to the project schema.

        Tables created:
        - users (user_id PK, username, email, joined_at)
        - status (status_id PK, name)
        - projects (project_id PK, user_id FK -> users(user_id), status_id FK -> status(status_id))

        Foreign key behaviors:
        - Deleting a user cascades and deletes their projects.
        - Deleting a status sets the project's status_id to NULL.
        """
        sql_users = """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                email TEXT,
                joined_at TEXT
            );
        """

        sql_status = """
            CREATE TABLE IF NOT EXISTS status (
                status_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            );
        """

        sql_projects = """
            CREATE TABLE IF NOT EXISTS projects (
                project_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                project_name TEXT NOT NULL,
                description TEXT,
                url TEXT,
                status_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY(status_id) REFERENCES status(status_id) ON DELETE SET NULL
            );
        """

        # Use a connection context manager (commits on success, rollbacks on exception)
        with sqlite3.connect(self.database) as conn:
            # Enable foreign key support in SQLite
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute(sql_users)
            conn.execute(sql_status)
            conn.execute(sql_projects)

    def list_tables(self) -> List[str]:
        """Return a list of table names present in the database."""
        with sqlite3.connect(self.database) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            return [row[0] for row in cur.fetchall()]

    # ------------------------------------------------------------------
    # Generic helpers for executing queries
    # ------------------------------------------------------------------
    def execute(self, sql: str, params: tuple = (), commit: bool = True):
        """Execute a single SQL statement. Returns the cursor."""
        with sqlite3.connect(self.database) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()
            cur.execute(sql, params)
            if commit:
                conn.commit()
            return cur

    def executemany(self, sql: str, seq_of_params: list):
        """Execute a statement against many parameter sets."""
        with sqlite3.connect(self.database) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()
            cur.executemany(sql, seq_of_params)
            conn.commit()

    def fetchall(self, sql: str, params: tuple = ()): 
        """Execute a SELECT and return all rows."""
        cur = self.execute(sql, params, commit=False)
        return cur.fetchall()

    def create_youtube_table(self) -> None:
        """Create a youtube_videos table used by the example script."""
        sql = """
            CREATE TABLE IF NOT EXISTS youtube_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul_video TEXT NOT NULL,
                tautan_video TEXT NOT NULL,
                kreator_video TEXT,
                tanggal_rilis TEXT,
                deskripsi_video TEXT
            );
        """
        # Reuse execute helper which commits by default
        self.execute(sql)


if __name__ == "__main__":
    dm = DatabaseManager()
    dm.create_tables()
    print("Created tables:", dm.list_tables())
    
import sqlite3
from config import DATABASE

class DB_Manager:
    def __init__(self, database):
        self.database = database 
        
    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE projects (
                            project_id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            project_name TEXT NOT NULL,
                            description TEXT,
                            url TEXT,
                            status_id INTEGER,
                            FOREIGN KEY(status_id) REFERENCES status(status_id)
                        )''') 
            conn.execute('''CREATE TABLE skills (
                            skill_id INTEGER PRIMARY KEY,
                            skill_name TEXT
                        )''')
            conn.execute('''CREATE TABLE project_skills (
                            project_id INTEGER,
                            skill_id INTEGER,
                            FOREIGN KEY(project_id) REFERENCES projects(project_id),
                            FOREIGN KEY(skill_id) REFERENCES skills(skill_id)
                        )''')
            conn.execute('''CREATE TABLE status (
                            status_id INTEGER PRIMARY KEY,
                            status_name TEXT
                        )''')
            conn.commit()

if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.create_tables()

import sqlite3
from config import DATABASE

skills = [ (_,) for _ in (['Python', 'SQL', 'API', 'Discord'])]
statuses = [ (_,) for _ in (['Pembuatan Prototipe', 'Dalam Pengembangan', 'Selesai, siap digunakan', 'Diperbarui', 'Selesai, tapi tidak sedang dilanjutkan'])]

class DB_Manager:
    def __init__(self, database):
        self.database = database
        
    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE projects (
                            project_id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            project_name TEXT NOT NULL,
                            description TEXT,
                            url TEXT,
                            status_id INTEGER,
                            FOREIGN KEY(status_id) REFERENCES status(status_id)
                        )''') 
            conn.execute('''CREATE TABLE skills (
                            skill_id INTEGER PRIMARY KEY,
                            skill_name TEXT
                        )''')
            conn.execute('''CREATE TABLE project_skills (
                            project_id INTEGER,
                            skill_id INTEGER,
                            FOREIGN KEY(project_id) REFERENCES projects(project_id),
                            FOREIGN KEY(skill_id) REFERENCES skills(skill_id)
                        )''')
            conn.execute('''CREATE TABLE status (
                            status_id INTEGER PRIMARY KEY,
                            status_name TEXT
                        )''')
            conn.commit()

    def __executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()
    
    def __select_data(self, sql, data = tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()
        
    def default_insert(self):
        sql = 'INSERT OR IGNORE INTO skills (skill_name) values(?)'
        data = skills
        self.__executemany(sql, data)
        sql = 'INSERT OR IGNORE INTO status (status_name) values(?)'
        data = statuses
        self.__executemany(sql, data)


    def insert_project(self, data):
        # data should be an iterable of tuples: (user_id, project_name, description, url, status_id)
        sql = 'INSERT INTO projects (user_id, project_name, description, url, status_id) VALUES (?, ?, ?, ?, ?)'
        self.__executemany(sql, data)


    def insert_skill(self, user_id, project_name, skill):
        sql = 'SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?'
        res = self.__select_data(sql, (project_name, user_id))
        if not res:
            raise ValueError("Project not found")
        project_id = res[0][0]
        res = self.__select_data('SELECT skill_id FROM skills WHERE skill_name = ?', (skill,))
        if not res:
            raise ValueError("Skill not found")
        skill_id = res[0][0]
        data = [(project_id, skill_id)]
        sql = 'INSERT OR IGNORE INTO project_skills (project_id, skill_id) VALUES(?, ?)'
        self.__executemany(sql, data)


    def get_statuses(self):
        sql = 'SELECT status_id, status_name FROM status'
        return self.__select_data(sql)
        

    def get_status_id(self, status_name):
        sql = 'SELECT status_id FROM status WHERE status_name = ?'
        res = self.__select_data(sql, (status_name,))
        if res: return res[0][0]
        else: return None

    def get_projects(self, user_id):
        sql = '''
SELECT projects.project_id, projects.project_name, projects.description, projects.url, status.status_name
FROM projects
LEFT JOIN status ON projects.status_id = status.status_id
WHERE projects.user_id = ?
'''
        return self.__select_data(sql, data = (user_id,))
        
    def get_project_id(self, project_name, user_id):
        res = self.__select_data(sql='SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?  ', data = (project_name, user_id,))
        if not res:
            raise ValueError("Project not found")
        return res[0][0]
        
    def get_skills(self):
        return self.__select_data(sql='SELECT * FROM skills')
    
    def get_project_skills(self, project_name):
        res = self.__select_data(sql='''SELECT skill_name FROM projects 
JOIN project_skills ON projects.project_id = project_skills.project_id 
JOIN skills ON skills.skill_id = project_skills.skill_id 
WHERE project_name = ?''', data = (project_name,) )
        return ', '.join([x[0] for x in res])
    
    def get_project_info(self, user_id, project_name):
        sql = """
SELECT projects.project_name, projects.description, projects.url, status.status_name
FROM projects
LEFT JOIN status ON status.status_id = projects.status_id
WHERE projects.user_id = ? AND projects.project_name = ?
"""
        return self.__select_data(sql=sql, data = (user_id, project_name))


    def update_projects(self, param, data):
        allowed = {'project_name', 'description', 'url', 'status_id'}
        if param not in allowed:
            raise ValueError("Invalid column")
        sql = f'UPDATE projects SET {param} = ? WHERE user_id = ? AND project_id = ?'
        self.__executemany(sql, [data])


    def delete_project(self, user_id, project_id):
        sql = 'DELETE FROM projects WHERE user_id = ? AND project_id = ?'
        self.__executemany(sql, [(user_id, project_id)])
    
    def delete_skill(self, project_id, skill_id):
        sql = 'DELETE FROM project_skills WHERE project_id = ? AND skill_id = ?'
        self.__executemany(sql, [(project_id, skill_id)])


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)