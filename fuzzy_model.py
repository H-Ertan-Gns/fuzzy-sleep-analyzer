"""
Manuel Fuzzy Logic Motoru
Bulanık mantık sistemi - scikit-fuzzy kullanmadan
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64


# Membership fonksiyonları

def trimf(x, abc):
    """
    Triangular membership function
    abc = [a, b, c] where a <= b <= c
    """
    a, b, c = abc
    if x <= a or x >= c:
        return 0.0
    elif x == b:
        return 1.0
    elif a < x < b:
        return (x - a) / (b - a)
    else:  # b < x < c
        return (c - x) / (c - b)


def trapmf(x, abcd):
    """
    Trapezoidal membership function
    abcd = [a, b, c, d] where a <= b <= c <= d
    """
    a, b, c, d = abcd
    if x <= a or x >= d:
        return 0.0
    elif b <= x <= c:
        return 1.0
    elif a < x < b:
        return (x - a) / (b - a)
    else:  # c < x < d
        return (d - x) / (d - c)


# Üyelik fonksiyonları tanımları

# Uyku saatleri (0-12 saat)
SLEEP_POOR = [0, 0, 4, 6]       # trapmf
SLEEP_MODERATE = [4, 6, 8]       # trimf
SLEEP_GOOD = [6, 8, 10, 12]      # trapmf

# Kafein (0-400 mg)
CAFFEINE_LOW = [0, 0, 50, 100]      # trapmf
CAFFEINE_MODERATE = [50, 150, 250]   # trimf
CAFFEINE_HIGH = [200, 350, 400, 400] # trapmf

# Egzersiz (0-120 dakika)
EXERCISE_LOW = [0, 0, 20, 40]       # trapmf
EXERCISE_MODERATE = [20, 40, 60]     # trimf
EXERCISE_HIGH = [40, 80, 120, 120]   # trapmf

# İş stresi (0-10)
STRESS_LOW = [0, 0, 2, 4]        # trapmf
STRESS_MODERATE = [2, 4, 6, 8]    # trapmf
STRESS_HIGH = [6, 8, 10, 10]      # trapmf

# Çıktı: Genel stres seviyesi (0-100)
OUTPUT_STRESS_LOW = [0, 0, 20, 40]       # trapmf
OUTPUT_STRESS_MODERATE = [20, 40, 60, 80] # trapmf
OUTPUT_STRESS_HIGH = [60, 80, 100, 100]   # trapmf

# Çıktı: Uyku kalitesi (0-100)
OUTPUT_QUALITY_POOR = [0, 0, 30, 50]      # trapmf
OUTPUT_QUALITY_MODERATE = [30, 50, 70]     # trimf
OUTPUT_QUALITY_GOOD = [50, 70, 100, 100]   # trapmf


# Fuzzy Kurallar
FUZZY_RULES = [
    # Kural 1: İyi uyku + düşük kafein + yüksek egzersiz + düşük stres → düşük stres çıktısı, iyi uyku kalitesi
    {
        'id': 1,
        'conditions': {
            'sleep': 'good',
            'caffeine': 'low',
            'exercise': 'high',
            'work_stress': 'low'
        },
        'outputs': {
            'stress': 'low',
            'quality': 'good'
        }
    },
    # Kural 2: Kötü uyku + yüksek kafein + düşük egzersiz + yüksek stres → yüksek stres, düşük kalite
    {
        'id': 2,
        'conditions': {
            'sleep': 'poor',
            'caffeine': 'high',
            'exercise': 'low',
            'work_stress': 'high'
        },
        'outputs': {
            'stress': 'high',
            'quality': 'poor'
        }
    },
    # Kural 3: Orta uyku + orta kafein + orta egzersiz + orta stres → orta stres, orta kalite
    {
        'id': 3,
        'conditions': {
            'sleep': 'moderate',
            'caffeine': 'moderate',
            'exercise': 'moderate',
            'work_stress': 'moderate'
        },
        'outputs': {
            'stress': 'moderate',
            'quality': 'moderate'
        }
    },
    # Kural 4: İyi uyku + düşük stres → iyi kalite (kafein ve egzersiz önemsiz)
    {
        'id': 4,
        'conditions': {
            'sleep': 'good',
            'work_stress': 'low'
        },
        'outputs': {
            'stress': 'low',
            'quality': 'good'
        }
    },
    # Kural 5: Kötü uyku + yüksek stres → yüksek stres çıktısı, kötü kalite
    {
        'id': 5,
        'conditions': {
            'sleep': 'poor',
            'work_stress': 'high'
        },
        'outputs': {
            'stress': 'high',
            'quality': 'poor'
        }
    },
    # Kural 6: Yüksek kafein + düşük egzersiz → yüksek stres
    {
        'id': 6,
        'conditions': {
            'caffeine': 'high',
            'exercise': 'low'
        },
        'outputs': {
            'stress': 'high',
            'quality': 'moderate'
        }
    },
    # Kural 7: Yüksek egzersiz + düşük kafein → düşük stres, iyi kalite
    {
        'id': 7,
        'conditions': {
            'exercise': 'high',
            'caffeine': 'low'
        },
        'outputs': {
            'stress': 'low',
            'quality': 'good'
        }
    },
    # Kural 8: Orta uyku + yüksek stres → orta-yüksek stres çıktısı
    {
        'id': 8,
        'conditions': {
            'sleep': 'moderate',
            'work_stress': 'high'
        },
        'outputs': {
            'stress': 'high',
            'quality': 'moderate'
        }
    },
]


# Kural açıklamaları
RULE_DESCRIPTIONS = {
    1: "İyi uyku, düşük kafein, yüksek egzersiz ve düşük iş stresi → Düşük stres, iyi uyku kalitesi",
    2: "Kötü uyku, yüksek kafein, düşük egzersiz ve yüksek iş stresi → Yüksek stres, kötü uyku kalitesi",
    3: "Orta seviye tüm parametreler → Orta stres ve uyku kalitesi",
    4: "İyi uyku ve düşük iş stresi → Düşük stres, iyi uyku kalitesi",
    5: "Kötü uyku ve yüksek iş stresi → Yüksek stres, kötü uyku kalitesi",
    6: "Yüksek kafein ve düşük egzersiz → Yüksek stres",
    7: "Yüksek egzersiz ve düşük kafein → Düşük stres, iyi kalite",
    8: "Orta uyku ve yüksek iş stresi → Yüksek stres"
}


def fuzzify(value, membership_funcs):
    """
    Bir girdi değerini fuzzy setlere dönüştür
    Returns: dict with membership degrees
    """
    result = {}
    for name, params in membership_funcs.items():
        if len(params) == 3:
            result[name] = trimf(value, params)
        elif len(params) == 4:
            result[name] = trapmf(value, params)
    return result


def evaluate_rule(rule, fuzzy_inputs):
    """
    Bir kuralın aktivasyon derecesini hesapla (AND operatörü: minimum)
    """
    activations = []
    
    for input_name, fuzzy_value in rule['conditions'].items():
        if input_name in fuzzy_inputs:
            activations.append(fuzzy_inputs[input_name].get(fuzzy_value, 0.0))
    
    if not activations:
        return 0.0
    
    # AND operatörü: minimum
    return min(activations)


def defuzzify_centroid(output_memberships):
    """
    Centroid (ağırlık merkezi) yöntemi ile defuzzification
    """
    # 0-100 aralığında örnekle
    x_range = np.linspace(0, 100, 1000)
    
    # Tüm kuralların çıktı membership fonksiyonlarını birleştir
    aggregated = np.zeros_like(x_range)
    
    for mf_name, activation in output_memberships.items():
        if activation > 0:
            # Her x değeri için membership derecesini hesapla
            if mf_name == 'low':
                params = OUTPUT_STRESS_LOW
            elif mf_name == 'moderate':
                params = OUTPUT_STRESS_MODERATE
            elif mf_name == 'high':
                params = OUTPUT_STRESS_HIGH
            elif mf_name == 'poor':
                params = OUTPUT_QUALITY_POOR
            elif mf_name == 'good':
                params = OUTPUT_QUALITY_GOOD
            else:
                continue
            
            if len(params) == 3:
                mf_values = np.array([trimf(x, params) for x in x_range])
            elif len(params) == 4:
                mf_values = np.array([trapmf(x, params) for x in x_range])
            
            # Mamdani implication: minimum
            clipped = np.minimum(mf_values, activation)
            
            # Aggregation: maximum
            aggregated = np.maximum(aggregated, clipped)
    
    # Centroid hesapla
    if np.sum(aggregated) == 0:
        return 50.0  # Default value
    
    centroid = np.sum(x_range * aggregated) / np.sum(aggregated)
    return centroid


def defuzzify_quality_centroid(output_memberships):
    """
    Uyku kalitesi için centroid defuzzification
    """
    x_range = np.linspace(0, 100, 1000)
    aggregated = np.zeros_like(x_range)
    
    for mf_name, activation in output_memberships.items():
        if activation > 0:
            if mf_name == 'poor':
                params = OUTPUT_QUALITY_POOR
            elif mf_name == 'moderate':
                params = OUTPUT_QUALITY_MODERATE
            elif mf_name == 'good':
                params = OUTPUT_QUALITY_GOOD
            else:
                continue
            
            if len(params) == 3:
                mf_values = np.array([trimf(x, params) for x in x_range])
            elif len(params) == 4:
                mf_values = np.array([trapmf(x, params) for x in x_range])
            
            clipped = np.minimum(mf_values, activation)
            aggregated = np.maximum(aggregated, clipped)
    
    if np.sum(aggregated) == 0:
        return 50.0
    
    centroid = np.sum(x_range * aggregated) / np.sum(aggregated)
    return centroid


def analyze(inputs):
    """
    Ana fuzzy analiz fonksiyonu
    
    Args:
        inputs: dict with keys: sleep_hours, caffeine_mg, exercise_min, work_stress
    
    Returns:
        dict with analysis results
    """
    try:
        # Girdileri al
        sleep_hours = float(inputs.get('sleep_hours', 7))
        caffeine_mg = float(inputs.get('caffeine_mg', 100))
        exercise_min = float(inputs.get('exercise_min', 30))
        work_stress = float(inputs.get('work_stress', 5))
        
        # Fuzzification
        sleep_fuzzy = fuzzify(sleep_hours, {
            'poor': SLEEP_POOR,
            'moderate': SLEEP_MODERATE,
            'good': SLEEP_GOOD
        })
        
        caffeine_fuzzy = fuzzify(caffeine_mg, {
            'low': CAFFEINE_LOW,
            'moderate': CAFFEINE_MODERATE,
            'high': CAFFEINE_HIGH
        })
        
        exercise_fuzzy = fuzzify(exercise_min, {
            'low': EXERCISE_LOW,
            'moderate': EXERCISE_MODERATE,
            'high': EXERCISE_HIGH
        })
        
        work_stress_fuzzy = fuzzify(work_stress, {
            'low': STRESS_LOW,
            'moderate': STRESS_MODERATE,
            'high': STRESS_HIGH
        })
        
        fuzzy_inputs = {
            'sleep': sleep_fuzzy,
            'caffeine': caffeine_fuzzy,
            'exercise': exercise_fuzzy,
            'work_stress': work_stress_fuzzy
        }
        
        # Kural değerlendirmesi
        stress_outputs = {'low': 0, 'moderate': 0, 'high': 0}
        quality_outputs = {'poor': 0, 'moderate': 0, 'good': 0}
        active_rules = []
        
        for rule in FUZZY_RULES:
            activation = evaluate_rule(rule, fuzzy_inputs)
            
            if activation > 0.01:  # Threshold
                active_rules.append(rule['id'])
                
                # Çıktı üyelik derecelerini güncelle (max aggregation)
                stress_out = rule['outputs'].get('stress')
                if stress_out:
                    stress_outputs[stress_out] = max(stress_outputs[stress_out], activation)
                
                quality_out = rule['outputs'].get('quality')
                if quality_out:
                    quality_outputs[quality_out] = max(quality_outputs[quality_out], activation)
        
        # Defuzzification
        stress_level = defuzzify_centroid(stress_outputs)
        sleep_quality = defuzzify_quality_centroid(quality_outputs)
        
        return {
            'stress_level': round(stress_level, 2),
            'sleep_quality': round(sleep_quality, 2),
            'active_rules': active_rules,
            'fuzzy_memberships': {
                'sleep': sleep_fuzzy,
                'caffeine': caffeine_fuzzy,
                'exercise': exercise_fuzzy,
                'work_stress': work_stress_fuzzy
            },
            'stress_outputs': stress_outputs,
            'quality_outputs': quality_outputs
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'stress_level': 50,
            'sleep_quality': 50,
            'active_rules': []
        }


def get_membership_plots():
    """
    Üyelik fonksiyonlarının görselleştirmesi
    Returns: base64 encoded PNG
    """
    fig, axes = plt.subplots(3, 2, figsize=(14, 12))
    fig.suptitle('Bulanık Mantık Üyelik Fonksiyonları', fontsize=16, fontweight='bold')
    
    # Uyku saatleri
    ax = axes[0, 0]
    x_sleep = np.linspace(0, 12, 300)
    ax.plot(x_sleep, [trapmf(x, SLEEP_POOR) for x in x_sleep], 'r-', linewidth=2, label='Kötü')
    ax.plot(x_sleep, [trimf(x, SLEEP_MODERATE) for x in x_sleep], 'y-', linewidth=2, label='Orta')
    ax.plot(x_sleep, [trapmf(x, SLEEP_GOOD) for x in x_sleep], 'g-', linewidth=2, label='İyi')
    ax.set_title('Uyku Saatleri', fontweight='bold')
    ax.set_xlabel('Saat')
    ax.set_ylabel('Üyelik Derecesi')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Kafein
    ax = axes[0, 1]
    x_caffeine = np.linspace(0, 400, 300)
    ax.plot(x_caffeine, [trapmf(x, CAFFEINE_LOW) for x in x_caffeine], 'g-', linewidth=2, label='Düşük')
    ax.plot(x_caffeine, [trimf(x, CAFFEINE_MODERATE) for x in x_caffeine], 'y-', linewidth=2, label='Orta')
    ax.plot(x_caffeine, [trapmf(x, CAFFEINE_HIGH) for x in x_caffeine], 'r-', linewidth=2, label='Yüksek')
    ax.set_title('Kafein (mg)', fontweight='bold')
    ax.set_xlabel('mg')
    ax.set_ylabel('Üyelik Derecesi')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Egzersiz
    ax = axes[1, 0]
    x_exercise = np.linspace(0, 120, 300)
    ax.plot(x_exercise, [trapmf(x, EXERCISE_LOW) for x in x_exercise], 'r-', linewidth=2, label='Düşük')
    ax.plot(x_exercise, [trimf(x, EXERCISE_MODERATE) for x in x_exercise], 'y-', linewidth=2, label='Orta')
    ax.plot(x_exercise, [trapmf(x, EXERCISE_HIGH) for x in x_exercise], 'g-', linewidth=2, label='Yüksek')
    ax.set_title('Egzersiz (dakika)', fontweight='bold')
    ax.set_xlabel('Dakika')
    ax.set_ylabel('Üyelik Derecesi')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # İş stresi
    ax = axes[1, 1]
    x_stress = np.linspace(0, 10, 300)
    ax.plot(x_stress, [trapmf(x, STRESS_LOW) for x in x_stress], 'g-', linewidth=2, label='Düşük')
    ax.plot(x_stress, [trapmf(x, STRESS_MODERATE) for x in x_stress], 'y-', linewidth=2, label='Orta')
    ax.plot(x_stress, [trapmf(x, STRESS_HIGH) for x in x_stress], 'r-', linewidth=2, label='Yüksek')
    ax.set_title('İş Stresi', fontweight='bold')
    ax.set_xlabel('Seviye (0-10)')
    ax.set_ylabel('Üyelik Derecesi')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Çıktı: Stres seviyesi
    ax = axes[2, 0]
    x_out = np.linspace(0, 100, 300)
    ax.plot(x_out, [trapmf(x, OUTPUT_STRESS_LOW) for x in x_out], 'g-', linewidth=2, label='Düşük')
    ax.plot(x_out, [trapmf(x, OUTPUT_STRESS_MODERATE) for x in x_out], 'y-', linewidth=2, label='Orta')
    ax.plot(x_out, [trapmf(x, OUTPUT_STRESS_HIGH) for x in x_out], 'r-', linewidth=2, label='Yüksek')
    ax.set_title('Çıktı: Genel Stres Seviyesi', fontweight='bold')
    ax.set_xlabel('Seviye (0-100)')
    ax.set_ylabel('Üyelik Derecesi')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Çıktı: Uyku kalitesi
    ax = axes[2, 1]
    ax.plot(x_out, [trapmf(x, OUTPUT_QUALITY_POOR) for x in x_out], 'r-', linewidth=2, label='Kötü')
    ax.plot(x_out, [trimf(x, OUTPUT_QUALITY_MODERATE) for x in x_out], 'y-', linewidth=2, label='Orta')
    ax.plot(x_out, [trapmf(x, OUTPUT_QUALITY_GOOD) for x in x_out], 'g-', linewidth=2, label='İyi')
    ax.set_title('Çıktı: Uyku Kalitesi', fontweight='bold')
    ax.set_xlabel('Kalite (0-100)')
    ax.set_ylabel('Üyelik Derecesi')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Base64 encode
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    return img_base64
