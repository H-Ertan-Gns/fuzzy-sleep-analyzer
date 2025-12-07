"""
SQLite Database işlemleri
Analiz kayıtları ve trend verileri
"""

import sqlite3
import json
from datetime import datetime, timedelta
import os


DB_PATH = 'data/history.db'


def init_db():
    """
    Veritabanını başlat, gerekli tabloları oluştur
    """
    # data klasörünü oluştur
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Analiz kayıtları tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            sleep_hours REAL,
            caffeine_mg REAL,
            exercise_min REAL,
            work_stress REAL,
            stress_level REAL,
            sleep_quality REAL,
            active_rules TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Index oluştur
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_user_timestamp 
        ON analysis_history(user_id, timestamp DESC)
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Veritabanı hazır: {DB_PATH}")


def save_analysis(inputs, results, user_id='anonymous'):
    """
    Analiz sonucunu veritabanına kaydet
    
    Args:
        inputs: dict - girdi parametreleri
        results: dict - analiz sonuçları
        user_id: str - kullanıcı kimliği
    
    Returns:
        int - kayıt ID'si
    """
    # DB yoksa oluştur
    if not os.path.exists(DB_PATH):
        init_db()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Active rules'ı JSON string'e çevir
    active_rules_json = json.dumps(results.get('active_rules', []))
    
    cursor.execute('''
        INSERT INTO analysis_history 
        (user_id, sleep_hours, caffeine_mg, exercise_min, work_stress, 
         stress_level, sleep_quality, active_rules, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        inputs.get('sleep_hours'),
        inputs.get('caffeine_mg'),
        inputs.get('exercise_min'),
        inputs.get('work_stress'),
        results.get('stress_level'),
        results.get('sleep_quality'),
        active_rules_json,
        datetime.now().isoformat()
    ))
    
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return record_id


def get_history(user_id='anonymous', limit=10):
    """
    Kullanıcının analiz geçmişini getir
    
    Args:
        user_id: str - kullanıcı kimliği
        limit: int - maksimum kayıt sayısı
    
    Returns:
        list of dict - analiz kayıtları
    """
    if not os.path.exists(DB_PATH):
        init_db()
        return []
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Dict gibi erişim için
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            id, user_id, timestamp, 
            sleep_hours, caffeine_mg, exercise_min, work_stress,
            stress_level, sleep_quality, active_rules
        FROM analysis_history
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (user_id, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Row objelerini dict'e çevir
    records = []
    for row in rows:
        records.append({
            'id': row['id'],
            'user_id': row['user_id'],
            'timestamp': row['timestamp'],
            'inputs': {
                'sleep_hours': row['sleep_hours'],
                'caffeine_mg': row['caffeine_mg'],
                'exercise_min': row['exercise_min'],
                'work_stress': row['work_stress']
            },
            'results': {
                'stress_level': row['stress_level'],
                'sleep_quality': row['sleep_quality']
            },
            'active_rules': row['active_rules']  # JSON string olarak
        })
    
    return records


def get_trend_data(user_id='anonymous', days=7):
    """
    Son N günün trend verilerini getir
    
    Args:
        user_id: str - kullanıcı kimliği
        days: int - kaç günlük veri
    
    Returns:
        list of dict - günlük ortalama veriler
    """
    if not os.path.exists(DB_PATH):
        init_db()
        return []
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Son N günün başlangıç tarihi
    start_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    cursor.execute('''
        SELECT 
            DATE(timestamp) as date,
            AVG(sleep_hours) as avg_sleep,
            AVG(caffeine_mg) as avg_caffeine,
            AVG(exercise_min) as avg_exercise,
            AVG(work_stress) as avg_work_stress,
            AVG(stress_level) as avg_stress_level,
            AVG(sleep_quality) as avg_sleep_quality,
            COUNT(*) as count
        FROM analysis_history
        WHERE user_id = ? AND timestamp >= ?
        GROUP BY DATE(timestamp)
        ORDER BY date ASC
    ''', (user_id, start_date))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Sonuçları formatla
    trends = []
    for row in rows:
        trends.append({
            'date': row['date'],
            'avg_sleep': round(row['avg_sleep'], 2) if row['avg_sleep'] else 0,
            'avg_caffeine': round(row['avg_caffeine'], 2) if row['avg_caffeine'] else 0,
            'avg_exercise': round(row['avg_exercise'], 2) if row['avg_exercise'] else 0,
            'avg_work_stress': round(row['avg_work_stress'], 2) if row['avg_work_stress'] else 0,
            'avg_stress_level': round(row['avg_stress_level'], 2) if row['avg_stress_level'] else 0,
            'avg_sleep_quality': round(row['avg_sleep_quality'], 2) if row['avg_sleep_quality'] else 0,
            'count': row['count']
        })
    
    return trends


# Database is initialized when needed (on first save_analysis or explicit init_db call)
# This avoids side effects during module import
