"""
Manuel Fuzzy Logic Motoru
scikit-fuzzy olmadan çalışır (Render uyumlu)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

# Üyelik fonksiyonları
def trimf(x, params):
    """
    Üçgen üyelik fonksiyonu
    params: [a, b, c] where a <= b <= c
    """
    a, b, c = params
    if a == b == c:
        return 1.0 if x == a else 0.0
    
    if x <= a or x >= c:
        return 0.0
    elif a < x <= b:
        return (x - a) / (b - a)
    else:  # b < x < c
        return (c - x) / (c - b)

def trapmf(x, params):
    """
    Yamuk üyelik fonksiyonu
    params: [a, b, c, d] where a <= b <= c <= d
    """
    a, b, c, d = params
    
    if x <= a or x >= d:
        return 0.0
    elif a < x < b:
        return (x - a) / (b - a)
    elif b <= x <= c:
        return 1.0
    else:  # c < x < d
        return (d - x) / (d - a)

# Üyelik fonksiyonları tanımları
MEMBERSHIP_FUNCTIONS = {
    'sleep_hours': {
        'low': lambda x: trapmf(x, [0, 0, 5, 6.5]),
        'medium': lambda x: trimf(x, [5.5, 7, 8.5]),
        'high': lambda x: trapmf(x, [7.5, 9, 12, 12])
    },
    'caffeine_mg': {
        'low': lambda x: trapmf(x, [0, 0, 50, 100]),
        'medium': lambda x: trimf(x, [80, 150, 220]),
        'high': lambda x: trapmf(x, [200, 300, 500, 500])
    },
    'exercise_min': {
        'low': lambda x: trapmf(x, [0, 0, 15, 30]),
        'medium': lambda x: trimf(x, [25, 45, 65]),
        'high': lambda x: trapmf(x, [60, 90, 120, 120])
    },
    'work_stress': {
        'low': lambda x: trapmf(x, [0, 0, 2, 4]),
        'medium': lambda x: trimf(x, [3, 5, 7]),
        'high': lambda x: trapmf(x, [6, 8, 10, 10])
    },
    'stress': {
        'low': lambda x: trapmf(x, [0, 0, 20, 40]),
        'medium': lambda x: trimf(x, [30, 50, 70]),
        'high': lambda x: trapmf(x, [60, 80, 100, 100])
    },
    'sleep_quality': {
        'poor': lambda x: trapmf(x, [0, 0, 30, 45]),
        'average': lambda x: trimf(x, [40, 55, 70]),
        'good': lambda x: trapmf(x, [65, 80, 100, 100])
    }
}

# Fuzzy Kurallar
RULE_DESCRIPTIONS = {
    'R1': 'Az uyku VEYA çok kafein → Stres YÜKSEK',
    'R2': 'Az uyku VE (az egzersiz VEYA yüksek iş) → Stres YÜKSEK',
    'R3': 'Çok uyku VE çok egzersiz VE düşük iş → Stres DÜŞÜK',
    'R4': 'Az uyku VEYA çok kafein VEYA yüksek iş → Uyku KÖTÜ',
    'R5': 'Orta uyku VE orta egzersiz → Uyku ORTA',
    'R6': 'Çok uyku VE çok egzersiz VE az kafein → Uyku İYİ',
    'R7': 'Yüksek iş VE orta uyku → Stres ORTA'
}

def evaluate_rules(inputs):
    """
    Fuzzy kuralları değerlendir ve aktivasyon derecelerini hesapla
    """
    # Girdi değişkenlerinin üyelik dereceleri
    sleep_low = MEMBERSHIP_FUNCTIONS['sleep_hours']['low'](inputs['sleep_hours'])
    sleep_medium = MEMBERSHIP_FUNCTIONS['sleep_hours']['medium'](inputs['sleep_hours'])
    sleep_high = MEMBERSHIP_FUNCTIONS['sleep_hours']['high'](inputs['sleep_hours'])
    
    caffeine_low = MEMBERSHIP_FUNCTIONS['caffeine_mg']['low'](inputs['caffeine_mg'])
    caffeine_medium = MEMBERSHIP_FUNCTIONS['caffeine_mg']['medium'](inputs['caffeine_mg'])
    caffeine_high = MEMBERSHIP_FUNCTIONS['caffeine_mg']['high'](inputs['caffeine_mg'])
    
    exercise_low = MEMBERSHIP_FUNCTIONS['exercise_min']['low'](inputs['exercise_min'])
    exercise_medium = MEMBERSHIP_FUNCTIONS['exercise_min']['medium'](inputs['exercise_min'])
    exercise_high = MEMBERSHIP_FUNCTIONS['exercise_min']['high'](inputs['exercise_min'])
    
    work_low = MEMBERSHIP_FUNCTIONS['work_stress']['low'](inputs['work_stress'])
    work_medium = MEMBERSHIP_FUNCTIONS['work_stress']['medium'](inputs['work_stress'])
    work_high = MEMBERSHIP_FUNCTIONS['work_stress']['high'](inputs['work_stress'])
    
    # Kural aktivasyonları
    rules = {}
    
    # R1: Az uyku VEYA çok kafein → Stres YÜKSEK
    rules['R1'] = {
        'activation': max(sleep_low, caffeine_high),
        'output_var': 'stress',
        'output_set': 'high'
    }
    
    # R2: Az uyku VE (az egzersiz VEYA yüksek iş) → Stres YÜKSEK
    rules['R2'] = {
        'activation': min(sleep_low, max(exercise_low, work_high)),
        'output_var': 'stress',
        'output_set': 'high'
    }
    
    # R3: Çok uyku VE çok egzersiz VE düşük iş → Stres DÜŞÜK
    rules['R3'] = {
        'activation': min(sleep_high, exercise_high, work_low),
        'output_var': 'stress',
        'output_set': 'low'
    }
    
    # R4: Az uyku VEYA çok kafein VEYA yüksek iş → Uyku KÖTÜ
    rules['R4'] = {
        'activation': max(sleep_low, caffeine_high, work_high),
        'output_var': 'sleep_quality',
        'output_set': 'poor'
    }
    
    # R5: Orta uyku VE orta egzersiz → Uyku ORTA
    rules['R5'] = {
        'activation': min(sleep_medium, exercise_medium),
        'output_var': 'sleep_quality',
        'output_set': 'average'
    }
    
    # R6: Çok uyku VE çok egzersiz VE az kafein → Uyku İYİ
    rules['R6'] = {
        'activation': min(sleep_high, exercise_high, caffeine_low),
        'output_var': 'sleep_quality',
        'output_set': 'good'
    }
    
    # R7: Yüksek iş VE orta uyku → Stres ORTA
    rules['R7'] = {
        'activation': min(work_high, sleep_medium),
        'output_var': 'stress',
        'output_set': 'medium'
    }
    
    return rules

def defuzzify(rules, output_var):
    """
    Centroid defuzzification yöntemi
    """
    # Çıkış uzayı
    x = np.linspace(0, 100, 1000)
    
    # Aggregated üyelik fonksiyonu
    aggregated = np.zeros_like(x)
    
    for rule_id, rule in rules.items():
        if rule['output_var'] == output_var and rule['activation'] > 0:
            # Her x değeri için üyelik derecesi
            mf = np.array([MEMBERSHIP_FUNCTIONS[output_var][rule['output_set']](xi) for xi in x])
            # Kural aktivasyonu ile kırp (min operatörü)
            clipped = np.minimum(mf, rule['activation'])
            # Aggregate (max operatörü)
            aggregated = np.maximum(aggregated, clipped)
    
    # Centroid hesapla
    if np.sum(aggregated) == 0:
        # Eğer hiçbir kural aktif değilse, varsayılan değer
        return 50.0
    
    centroid = np.sum(x * aggregated) / np.sum(aggregated)
    
    return centroid

def analyze(inputs):
    """
    Ana fuzzy analiz fonksiyonu
    
    inputs: {
        'sleep_hours': float (0-12),
        'caffeine_mg': float (0-500),
        'exercise_min': float (0-120),
        'work_stress': float (0-10)
    }
    
    returns: {
        'stress': float (0-100),
        'sleep_quality': float (0-100),
        'active_rules': list,
        'recommendations': list
    }
    """
    try:
        # Girdi validasyonu
        required_keys = ['sleep_hours', 'caffeine_mg', 'exercise_min', 'work_stress']
        for key in required_keys:
            if key not in inputs:
                return {'error': f'Missing required input: {key}'}
        
        # Kuralları değerlendir
        rules = evaluate_rules(inputs)
        
        # Aktif kuralları bul (aktivasyon > 0.1)
        active_rules = [rule_id for rule_id, rule in rules.items() if rule['activation'] > 0.1]
        
        # Defuzzification
        stress = defuzzify(rules, 'stress')
        sleep_quality = defuzzify(rules, 'sleep_quality')
        
        # Tavsiyeler
        recommendations = generate_recommendations(stress, sleep_quality, inputs)
        
        return {
            'stress': round(stress, 2),
            'sleep_quality': round(sleep_quality, 2),
            'active_rules': active_rules,
            'recommendations': recommendations
        }
    
    except Exception as e:
        return {'error': str(e)}

def generate_recommendations(stress, sleep_quality, inputs):
    """
    Kişiselleştirilmiş tavsiyeler üret
    """
    recommendations = []
    
    # Uyku tavsiyeleri
    if inputs['sleep_hours'] < 6:
        recommendations.append('💤 Uyku sürenizi artırın (hedef: 7-9 saat)')
    elif inputs['sleep_hours'] > 9:
        recommendations.append('⏰ Düzenli uyku saatleri belirleyin')
    
    # Kafein tavsiyeleri
    if inputs['caffeine_mg'] > 250:
        recommendations.append('☕ Kafein tüketimini azaltın (özellikle öğleden sonra)')
    
    # Egzersiz tavsiyeleri
    if inputs['exercise_min'] < 30:
        recommendations.append('🏃 Günlük egzersiz sürenizi artırın (hedef: 30-60 dakika)')
    
    # İş stresi tavsiyeleri
    if inputs['work_stress'] > 7:
        recommendations.append('🧘 Stres yönetimi teknikleri uygulayın (meditasyon, nefes egzersizleri)')
    
    # Genel öneriler
    if stress > 70:
        recommendations.append('⚠️ Yüksek stres seviyesi! Profesyonel destek düşünün')
    
    if sleep_quality < 40:
        recommendations.append('🛏️ Uyku ortamınızı iyileştirin (karanlık, sessiz, serin)')
    
    if not recommendations:
        recommendations.append('✅ Harika! Sağlıklı bir yaşam tarzı sürdürüyorsunuz')
    
    return recommendations

def get_membership_plots():
    """
    Üyelik fonksiyonlarının grafiklerini oluştur ve base64 string döner
    """
    fig, axes = plt.subplots(3, 2, figsize=(15, 12))
    fig.suptitle('Bulanık Mantık Üyelik Fonksiyonları', fontsize=16, fontweight='bold')
    
    # 1. Uyku Saatleri
    ax = axes[0, 0]
    x = np.linspace(0, 12, 300)
    ax.plot(x, [MEMBERSHIP_FUNCTIONS['sleep_hours']['low'](xi) for xi in x], 'r-', label='Düşük', linewidth=2)
    ax.plot(x, [MEMBERSHIP_FUNCTIONS['sleep_hours']['medium'](xi) for xi in x], 'g-', label='Orta', linewidth=2)
    ax.plot(x, [MEMBERSHIP_FUNCTIONS['sleep_hours']['high'](xi) for xi in x], 'b-', label='Yüksek', linewidth=2)
    ax.set_title('Uyku Saatleri', fontweight='bold')
    ax.set_xlabel('Saat')
    ax.set_ylabel('Üyelik Derecesi')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 2. Kafein
    ax = axes[0, 1]
    x = np.linspace(0, 500, 300)
    ax.plot(x, [MEMBERSHIP_FUNCTIONS['caffeine_mg']['low'](xi) for xi in x], 'r-', label='Düşük', linewidth=2)
    ax.plot(x, [MEMBERSHIP_FUNCTIONS['caffeine_mg']['medium'](xi) for xi in x], 'g-', label='Orta', linewidth=2)
    ax.plot(x, [MEMBERSHIP_FUNCTIONS['caffeine_mg']['high'](xi) for xi in x], 'b-', label='Yüksek', linewidth=2)
    ax.set_title('Kafein (mg)', fontweight='bold')
    ax.set_xlabel('Miligram')
    ax.set_ylabel('Üyelik Derecesi')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 3. Egzersiz
    ax = axes[1, 0]
    x = np.linspace(0, 120, 300)
    ax.plot(x, [MEMBERSHIP_FUNCTIONS['exercise_min']['low'](xi) for xi in x], 'r-', label='Düşük', linewidth=2)
    ax.plot(x, [MEMBERSHIP_FUNCTIONS['exercise_min']['medium'](xi) for xi in x], 'g-', label='Orta', linewidth=2)
    ax.plot(x, [MEMBERSHIP_FUNCTIONS['exercise_min']['high'](xi) for xi in x], 'b-', label='Yüksek', linewidth=2)
    ax.set_title('Egzersiz (dakika)', fontweight='bold')
    ax.set_xlabel('Dakika')
    ax.set_ylabel('Üyelik Derecesi')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 4. İş Stresi
    ax = axes[1, 1]
    x = np.linspace(0, 10, 300)
    ax.plot(x, [MEMBERSHIP_FUNCTIONS['work_stress']['low'](xi) for xi in x], 'r-', label='Düşük', linewidth=2)
    ax.plot(x, [MEMBERSHIP_FUNCTIONS['work_stress']['medium'](xi) for xi in x], 'g-', label='Orta', linewidth=2)
    ax.plot(x, [MEMBERSHIP_FUNCTIONS['work_stress']['high'](xi) for xi in x], 'b-', label='Yüksek', linewidth=2)
    ax.set_title('İş Stresi', fontweight='bold')
    ax.set_xlabel('Seviye (0-10)')
    ax.set_ylabel('Üyelik Derecesi')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 5. Stres (Çıkış)
    ax = axes[2, 0]
    x = np.linspace(0, 100, 300)
    ax.plot(x, [MEMBERSHIP_FUNCTIONS['stress']['low'](xi) for xi in x], 'r-', label='Düşük', linewidth=2)
    ax.plot(x, [MEMBERSHIP_FUNCTIONS['stress']['medium'](xi) for xi in x], 'g-', label='Orta', linewidth=2)
    ax.plot(x, [MEMBERSHIP_FUNCTIONS['stress']['high'](xi) for xi in x], 'b-', label='Yüksek', linewidth=2)
    ax.set_title('Stres Seviyesi (Çıkış)', fontweight='bold')
    ax.set_xlabel('Değer (0-100)')
    ax.set_ylabel('Üyelik Derecesi')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 6. Uyku Kalitesi (Çıkış)
    ax = axes[2, 1]
    x = np.linspace(0, 100, 300)
    ax.plot(x, [MEMBERSHIP_FUNCTIONS['sleep_quality']['poor'](xi) for xi in x], 'r-', label='Kötü', linewidth=2)
    ax.plot(x, [MEMBERSHIP_FUNCTIONS['sleep_quality']['average'](xi) for xi in x], 'g-', label='Orta', linewidth=2)
    ax.plot(x, [MEMBERSHIP_FUNCTIONS['sleep_quality']['good'](xi) for xi in x], 'b-', label='İyi', linewidth=2)
    ax.set_title('Uyku Kalitesi (Çıkış)', fontweight='bold')
    ax.set_xlabel('Değer (0-100)')
    ax.set_ylabel('Üyelik Derecesi')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Base64'e çevir
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return img_str
