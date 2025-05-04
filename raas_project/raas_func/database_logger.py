import sqlite3
from datetime import datetime
import threading

class DatabaseLogger:
    def __init__(self, db_path="system_data.db"):
        self.lock = threading.Lock()
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        # Таблица состояний функций
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS function_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                function_name TEXT NOT NULL,
                state TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')

        # Таблица включения/выключения мультимедии
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT NOT NULL, -- 'start' или 'stop'
                timestamp TEXT NOT NULL
            )
        ''')

        # Таблица событий радаров зеркал
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mirror_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                side TEXT NOT NULL, -- 'left' или 'right'
                timestamp TEXT NOT NULL
            )
        ''')

        # Таблица экстренного торможения
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emergency_brakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                speed_kmh REAL NOT NULL,
                distance_m REAL
            )
        ''')

        # Таблица для логов круиз-контроля
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cruise_control (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,         -- 'enabled' или 'disabled'
                timestamp TEXT NOT NULL,
                speed_kmh REAL NOT NULL
            )
        ''')

        # Таблица логов смарт-парковки
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS smart_parking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,        -- 'start' или 'stop'
                timestamp TEXT NOT NULL,
                side TEXT                    -- 'left', 'right' или NULL
            )
        ''')

        # Таблица для логов аварий и экстренного вызова
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emergency_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                speed_before REAL,
                speed_after REAL,
                speed_drop REAL,
                yaw_before REAL,
                yaw_after REAL,
                yaw_change REAL,
                duration_sec REAL,
                location_x REAL,
                location_y REAL,
                location_z REAL,
                call_made INTEGER -- 1 = вызов принят, 0 = отклонён
            )
        ''')

        # Таблица логов усталости водителя
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fatigue_warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                reason TEXT NOT NULL,
                category TEXT NOT NULL
            )
        ''')

        self.conn.commit()

    def log_function_state(self, function_name, state):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO function_states (function_name, state, timestamp) VALUES (?, ?, ?)',
            (function_name, state, datetime.now().isoformat())
        )
        self.conn.commit()

    def log_system_event(self, event):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO system_sessions (event, timestamp) VALUES (?, ?)',
            (event, datetime.now().isoformat())
        )
        self.conn.commit()

    def log_mirror_alert(self, side):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO mirror_alerts (side, timestamp) VALUES (?, ?)',
            (side, datetime.now().isoformat())
        )
        self.conn.commit()

    def log_emergency_brake(self, speed_kmh, distance_m):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO emergency_brakes (timestamp, speed_kmh, distance_m) VALUES (?, ?, ?)',
                (datetime.now().isoformat(), speed_kmh, distance_m)
            )
            self.conn.commit()

    def log_cruise_control(self, action, speed_kmh):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO cruise_control (action, timestamp, speed_kmh) VALUES (?, ?, ?)',
                (action, datetime.now().isoformat(), speed_kmh)
            )
            self.conn.commit()

    def log_smart_parking(self, action, side=None):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO smart_parking (action, timestamp, side) VALUES (?, ?, ?)',
                (action, datetime.now().isoformat(), side)
            )
            self.conn.commit()

    def log_emergency_call(self, speed_before, speed_after, speed_drop,
                        yaw_before, yaw_after, yaw_change,
                        duration_sec, location, call_made):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute(
                '''INSERT INTO emergency_calls (
                    timestamp, speed_before, speed_after, speed_drop,
                    yaw_before, yaw_after, yaw_change,
                    duration_sec, location_x, location_y, location_z, call_made
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    datetime.now().isoformat(),
                    speed_before, speed_after, speed_drop,
                    yaw_before, yaw_after, yaw_change,
                    duration_sec,
                    location.x, location.y, location.z,
                    1 if call_made else 0
                )
            )
            self.conn.commit()

    def log_fatigue_warning(self, reason, category):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO fatigue_warnings (timestamp, reason, category) VALUES (?, ?, ?)',
                (datetime.now().isoformat(), reason, category)
            )
            self.conn.commit()


    def get_last_states(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT function_name, state FROM (
                SELECT function_name, state, MAX(timestamp) as max_time
                FROM function_states
                GROUP BY function_name
            )
        ''')
        return {row[0]: row[1] for row in cursor.fetchall()}
