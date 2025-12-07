"""
SQLite Veritabanı İşlemleri
Analiz geçmişi ve trend verileri yönetimi
"""

import sqlite3
import json
from datetime import datetime, timedelta
import os

# Veritabanı yolu
DB_PATH = 'data/history.db'

def get_connection():
    """Veritabanı bağlantısı oluştur"""
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Dict-like access
    return conn

def init_db():
    """Veritabanı tablosunu oluştur"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            sleep_hours REAL,
            caffeine_mg REAL,
            exercise_min REAL,
            work_stress REAL,
            stress_result REAL,
            sleep_quality_result REAL,
            active_rules TEXT,
            recommendations TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized: {DB_PATH}")

def save_analysis(inputs, results, user_id='anonymous'):
    """
    Yeni analiz kaydını veritabanına kaydet
    
    Args:
        inputs: dict - Kullanıcı girdileri
        results: dict - Analiz sonuçları
        user_id: str - Kullanıcı kimliği
    
    Returns:
        int - Kayıt ID'si
    """
    # Veritabanını başlat (yoksa oluştur)
    init_db()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO analysis_history (
            user_id, sleep_hours, caffeine_mg, exercise_min, work_stress,
            stress_result, sleep_quality_result, active_rules, recommendations
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        inputs.get('sleep_hours'),
        inputs.get('caffeine_mg'),
        inputs.get('exercise_min'),
        inputs.get('work_stress'),
        results.get('stress'),
        results.get('sleep_quality'),
        json.dumps(results.get('active_rules', [])),
        json.dumps(results.get('recommendations', []))
    ))
    
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return record_id

def get_history(user_id='anonymous', limit=10):
    """
    Kullanıcının geçmiş analiz kayıtlarını getir
    
    Args:
        user_id: str - Kullanıcı kimliği
        limit: int - Maksimum kayıt sayısı
    
    Returns:
        list - Analiz kayıtları
    """
    # Veritabanını başlat (yoksa oluştur)
    init_db()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM analysis_history
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (user_id, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dicts
    records = []
    for row in rows:
        records.append({
            'id': row['id'],
            'timestamp': row['timestamp'],
            'sleep_hours': row['sleep_hours'],
            'caffeine_mg': row['caffeine_mg'],
            'exercise_min': row['exercise_min'],
            'work_stress': row['work_stress'],
            'stress_result': row['stress_result'],
            'sleep_quality_result': row['sleep_quality_result'],
            'active_rules': row['active_rules'],
            'recommendations': row['recommendations']
        })
    
    return records

def get_trend_data(user_id='anonymous', days=7):
    """
    Trend analizi için veri getir
    
    Args:
        user_id: str - Kullanıcı kimliği
        days: int - Kaç günlük veri
    
    Returns:
        list - Trend verileri
    """
    # Veritabanını başlat (yoksa oluştur)
    init_db()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Son X günlük veri
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        SELECT 
            DATE(timestamp) as date,
            AVG(sleep_hours) as avg_sleep,
            AVG(stress_result) as avg_stress,
            AVG(sleep_quality_result) as avg_sleep_quality,
            AVG(exercise_min) as avg_exercise,
            AVG(caffeine_mg) as avg_caffeine,
            AVG(work_stress) as avg_work_stress,
            COUNT(*) as count
        FROM analysis_history
        WHERE user_id = ? AND timestamp >= ?
        GROUP BY DATE(timestamp)
        ORDER BY date ASC
    ''', (user_id, cutoff_date))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dicts
    trends = []
    for row in rows:
        trends.append({
            'date': row['date'],
            'avg_sleep': round(row['avg_sleep'], 2) if row['avg_sleep'] else None,
            'avg_stress': round(row['avg_stress'], 2) if row['avg_stress'] else None,
            'avg_sleep_quality': round(row['avg_sleep_quality'], 2) if row['avg_sleep_quality'] else None,
            'avg_exercise': round(row['avg_exercise'], 2) if row['avg_exercise'] else None,
            'avg_caffeine': round(row['avg_caffeine'], 2) if row['avg_caffeine'] else None,
            'avg_work_stress': round(row['avg_work_stress'], 2) if row['avg_work_stress'] else None,
            'count': row['count']
        })
    
    return trends

def delete_old_records(days=30):
    """
    Eski kayıtları sil (GDPR uyumu için)
    
    Args:
        days: int - Kaç günden eski kayıtlar silinsin
    
    Returns:
        int - Silinen kayıt sayısı
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        DELETE FROM analysis_history
        WHERE timestamp < ?
    ''', (cutoff_date,))
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted_count

if __name__ == "__main__":
    # Test
    print("Testing database operations...")
    init_db()
    
    # Test kayıt
    test_inputs = {
        'sleep_hours': 7.5,
        'caffeine_mg': 120,
        'exercise_min': 45,
        'work_stress': 6
    }
    
    test_results = {
        'stress': 55.2,
        'sleep_quality': 68.5,
        'active_rules': ['R1', 'R5'],
        'recommendations': ['Test recommendation']
    }
    
    record_id = save_analysis(test_inputs, test_results, 'test_user')
    print(f"✅ Test record saved with ID: {record_id}")
    
    # Geçmişi getir
    history = get_history('test_user', 5)
    print(f"✅ Retrieved {len(history)} records")
    
    # Trend verisi
    trends = get_trend_data('test_user', 7)
    print(f"✅ Retrieved trend data: {len(trends)} days")
    
    print("\n✅ Database tests completed!")
