"""
Manuel Fuzzy Logic Motoru - Python 3.9 Uyumlu
Bulanık mantık sistemi - scikit-fuzzy kullanmadan
README.md'de belirtilen 10 kural tam implementasyonu
"""

from typing import Dict, List, Tuple, Optional
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64


# Üyelik fonksiyonları

def trapmf(x: float, params: List[float]) -> float:
    """
    Trapezoidal membership function
    params = [a, b, c, d] where a <= b <= c <= d
    """
    a, b, c, d = params
    if x <= a or x >= d:
        return 0.0
    elif b <= x <= c:
        return 1.0
    elif a < x < b:
        return (x - a) / (b - a)
    else:  # c < x < d
        return (d - x) / (d - c)


def trimf(x: float, params: List[float]) -> float:
    """
    Triangular membership function
    params = [a, b, c] where a <= b <= c
    """
    a, b, c = params
    if x <= a or x >= c:
        return 0.0
    elif x == b:
        return 1.0
    elif a < x < b:
        return (x - a) / (b - a)
    else:  # b < x < c
        return (c - x) / (c - b)


# Girdi değişkenleri tanımları (README'ye göre)

# sleep_hours (0-12): low(0-6), medium(5-9), high(8-12)
SLEEP_LOW = [0, 0, 4, 6]          # trapmf
SLEEP_MEDIUM = [5, 6.5, 8, 9]     # trapmf  
SLEEP_HIGH = [8, 9, 12, 12]       # trapmf

# caffeine_mg (0-500): low(0-150), medium(100-300), high(250-500)
CAFFEINE_LOW = [0, 0, 100, 150]        # trapmf
CAFFEINE_MEDIUM = [100, 175, 225, 300] # trapmf
CAFFEINE_HIGH = [250, 350, 500, 500]   # trapmf

# exercise_min (0-120): low(0-30), medium(20-70), high(60-120)
EXERCISE_LOW = [0, 0, 20, 30]         # trapmf
EXERCISE_MEDIUM = [20, 40, 55, 70]    # trapmf
EXERCISE_HIGH = [60, 80, 120, 120]    # trapmf

# work_stress (0-10): low(0-4), medium(3-7), high(6-10)
WORK_LOW = [0, 0, 2, 4]           # trapmf
WORK_MEDIUM = [3, 4.5, 5.5, 7]    # trapmf
WORK_HIGH = [6, 7.5, 10, 10]      # trapmf

# environmental_score (0-100): bad(0-50), medium(40-80), good(70-100)
ENV_BAD = [0, 0, 30, 50]          # trapmf
ENV_MEDIUM = [40, 55, 65, 80]     # trapmf
ENV_GOOD = [70, 85, 100, 100]     # trapmf

# Çıktı değişkenleri tanımları (README'ye göre)

# stress (0-100): low(0-35), medium(30-70), high(60-100)
OUTPUT_STRESS_LOW = [0, 0, 20, 35]       # trapmf
OUTPUT_STRESS_MEDIUM = [30, 45, 55, 70]  # trapmf
OUTPUT_STRESS_HIGH = [60, 75, 100, 100]  # trapmf

# sleep_quality (0-100): poor(0-40), average(30-70), good(60-100)
OUTPUT_QUALITY_POOR = [0, 0, 25, 40]      # trapmf
OUTPUT_QUALITY_AVERAGE = [30, 45, 55, 70] # trapmf
OUTPUT_QUALITY_GOOD = [60, 75, 100, 100]  # trapmf


# 10 Fuzzy Kurallar (README'ye göre)
RULE_DESCRIPTIONS = {
    'R1': 'IF (sleep = low) OR (caffeine = high) THEN stress = high',
    'R2': 'IF (sleep = low) AND ((exercise = low) OR (work = high)) THEN stress = high',
    'R3': 'IF (sleep = high) AND (exercise = high) AND (work = low) THEN stress = low',
    'R4': 'IF (sleep = low) OR (caffeine = high) OR (work = high) THEN sleep_quality = poor',
    'R5': 'IF (sleep = medium) AND (exercise = medium) THEN sleep_quality = average',
    'R6': 'IF (sleep = high) AND (exercise = high) AND (caffeine = low) THEN sleep_quality = good',
    'R7': 'IF (work = high) AND (sleep = medium) THEN stress = medium',
    'R8': 'IF (environmental_score = bad) THEN stress = high',
    'R9': 'IF (environmental_score = bad) THEN sleep_quality = poor',
    'R10': 'IF (environmental_score = good) THEN stress = low'
}


def fuzzify(value: float, variable_name: str) -> Dict[str, float]:
    """
    Üyelik derecelerini hesapla (fuzzification)
    
    Args:
        value: Girdi değeri
        variable_name: Değişken adı ('sleep', 'caffeine', 'exercise', 'work', 'environmental')
    
    Returns:
        dict: Üyelik dereceleri
    """
    memberships = {}
    
    if variable_name == 'sleep':
        memberships['low'] = trapmf(value, SLEEP_LOW)
        memberships['medium'] = trapmf(value, SLEEP_MEDIUM)
        memberships['high'] = trapmf(value, SLEEP_HIGH)
    
    elif variable_name == 'caffeine':
        memberships['low'] = trapmf(value, CAFFEINE_LOW)
        memberships['medium'] = trapmf(value, CAFFEINE_MEDIUM)
        memberships['high'] = trapmf(value, CAFFEINE_HIGH)
    
    elif variable_name == 'exercise':
        memberships['low'] = trapmf(value, EXERCISE_LOW)
        memberships['medium'] = trapmf(value, EXERCISE_MEDIUM)
        memberships['high'] = trapmf(value, EXERCISE_HIGH)
    
    elif variable_name == 'work':
        memberships['low'] = trapmf(value, WORK_LOW)
        memberships['medium'] = trapmf(value, WORK_MEDIUM)
        memberships['high'] = trapmf(value, WORK_HIGH)
    
    elif variable_name == 'environmental':
        memberships['bad'] = trapmf(value, ENV_BAD)
        memberships['medium'] = trapmf(value, ENV_MEDIUM)
        memberships['good'] = trapmf(value, ENV_GOOD)
    
    return memberships


def apply_rules(memberships: Dict[str, Dict[str, float]]) -> Tuple[Dict[str, float], Dict[str, float], List[str]]:
    """
    10 kuralı uygula ve aktif kuralları belirle
    
    Args:
        memberships: Tüm girdiler için üyelik dereceleri
    
    Returns:
        tuple: (stress_outputs, quality_outputs, active_rules)
    """
    sleep = memberships['sleep']
    caffeine = memberships['caffeine']
    exercise = memberships['exercise']
    work = memberships['work']
    env = memberships.get('environmental', {'bad': 0, 'medium': 0, 'good': 0})
    
    stress_outputs = {'low': 0.0, 'medium': 0.0, 'high': 0.0}
    quality_outputs = {'poor': 0.0, 'average': 0.0, 'good': 0.0}
    active_rules = []
    
    # R1: IF (sleep = low) OR (caffeine = high) THEN stress = high
    r1_activation = max(sleep['low'], caffeine['high'])
    if r1_activation > 0.01:
        active_rules.append('R1')
        stress_outputs['high'] = max(stress_outputs['high'], r1_activation)
    
    # R2: IF (sleep = low) AND ((exercise = low) OR (work = high)) THEN stress = high
    r2_activation = min(sleep['low'], max(exercise['low'], work['high']))
    if r2_activation > 0.01:
        active_rules.append('R2')
        stress_outputs['high'] = max(stress_outputs['high'], r2_activation)
    
    # R3: IF (sleep = high) AND (exercise = high) AND (work = low) THEN stress = low
    r3_activation = min(sleep['high'], exercise['high'], work['low'])
    if r3_activation > 0.01:
        active_rules.append('R3')
        stress_outputs['low'] = max(stress_outputs['low'], r3_activation)
    
    # R4: IF (sleep = low) OR (caffeine = high) OR (work = high) THEN sleep_quality = poor
    r4_activation = max(sleep['low'], caffeine['high'], work['high'])
    if r4_activation > 0.01:
        active_rules.append('R4')
        quality_outputs['poor'] = max(quality_outputs['poor'], r4_activation)
    
    # R5: IF (sleep = medium) AND (exercise = medium) THEN sleep_quality = average
    r5_activation = min(sleep['medium'], exercise['medium'])
    if r5_activation > 0.01:
        active_rules.append('R5')
        quality_outputs['average'] = max(quality_outputs['average'], r5_activation)
    
    # R6: IF (sleep = high) AND (exercise = high) AND (caffeine = low) THEN sleep_quality = good
    r6_activation = min(sleep['high'], exercise['high'], caffeine['low'])
    if r6_activation > 0.01:
        active_rules.append('R6')
        quality_outputs['good'] = max(quality_outputs['good'], r6_activation)
    
    # R7: IF (work = high) AND (sleep = medium) THEN stress = medium
    r7_activation = min(work['high'], sleep['medium'])
    if r7_activation > 0.01:
        active_rules.append('R7')
        stress_outputs['medium'] = max(stress_outputs['medium'], r7_activation)
    
    # R8: IF (environmental_score = bad) THEN stress = high
    r8_activation = env['bad']
    if r8_activation > 0.01:
        active_rules.append('R8')
        stress_outputs['high'] = max(stress_outputs['high'], r8_activation)
    
    # R9: IF (environmental_score = bad) THEN sleep_quality = poor
    r9_activation = env['bad']
    if r9_activation > 0.01:
        active_rules.append('R9')
        quality_outputs['poor'] = max(quality_outputs['poor'], r9_activation)
    
    # R10: IF (environmental_score = good) THEN stress = low
    r10_activation = env['good']
    if r10_activation > 0.01:
        active_rules.append('R10')
        stress_outputs['low'] = max(stress_outputs['low'], r10_activation)
    
    return stress_outputs, quality_outputs, active_rules


def defuzzify(rule_outputs: Dict[str, float], output_type: str = 'stress') -> float:
    """
    Centroid defuzzification yöntemi
    
    Args:
        rule_outputs: Kural çıktıları (örn: {'low': 0.5, 'medium': 0.3, 'high': 0.8})
        output_type: 'stress' veya 'quality'
    
    Returns:
        float: Defuzzified değer (0-100)
    """
    # 0-100 aralığında örnekle
    x_range = np.linspace(0, 100, 1000)
    aggregated = np.zeros_like(x_range)
    
    # Output membership fonksiyonlarını birleştir
    for level, activation in rule_outputs.items():
        if activation > 0:
            # Membership fonksiyonunu seç
            if output_type == 'stress':
                if level == 'low':
                    params = OUTPUT_STRESS_LOW
                elif level == 'medium':
                    params = OUTPUT_STRESS_MEDIUM
                else:  # high
                    params = OUTPUT_STRESS_HIGH
            else:  # quality
                if level == 'poor':
                    params = OUTPUT_QUALITY_POOR
                elif level == 'average':
                    params = OUTPUT_QUALITY_AVERAGE
                else:  # good
                    params = OUTPUT_QUALITY_GOOD
            
            # Her x için membership değerini hesapla
            mf_values = np.array([trapmf(x, params) for x in x_range])
            
            # Mamdani implication: minimum
            clipped = np.minimum(mf_values, activation)
            
            # Aggregation: maximum
            aggregated = np.maximum(aggregated, clipped)
    
    # Centroid hesapla
    if np.sum(aggregated) == 0:
        return 50.0  # Default value
    
    centroid = np.sum(x_range * aggregated) / np.sum(aggregated)
    return float(centroid)


def analyze(
    sleep_hours: float,
    caffeine_mg: float,
    exercise_min: float,
    work_stress: float,
    environmental_score: float = 50.0
) -> Dict:
    """
    Ana fuzzy analiz fonksiyonu
    
    Args:
        sleep_hours: Uyku saatleri (0-12)
        caffeine_mg: Kafein miktarı (0-500)
        exercise_min: Egzersiz dakikası (0-120)
        work_stress: İş stresi (0-10)
        environmental_score: Çevresel skor (0-100), opsiyonel
    
    Returns:
        dict: Analiz sonuçları
    """
    try:
        # Fuzzification
        memberships = {
            'sleep': fuzzify(sleep_hours, 'sleep'),
            'caffeine': fuzzify(caffeine_mg, 'caffeine'),
            'exercise': fuzzify(exercise_min, 'exercise'),
            'work': fuzzify(work_stress, 'work'),
            'environmental': fuzzify(environmental_score, 'environmental')
        }
        
        # Kuralları uygula
        stress_outputs, quality_outputs, active_rules = apply_rules(memberships)
        
        # Defuzzification
        stress_result = defuzzify(stress_outputs, 'stress')
        quality_result = defuzzify(quality_outputs, 'quality')
        
        return {
            'stress': round(stress_result, 2),
            'sleep_quality': round(quality_result, 2),
            'active_rules': active_rules,
            'memberships': {
                'sleep': memberships['sleep'],
                'caffeine': memberships['caffeine'],
                'exercise': memberships['exercise'],
                'work': memberships['work'],
                'environmental': memberships['environmental']
            }
        }
    
    except Exception as e:
        return {
            'error': str(e),
            'stress': 50.0,
            'sleep_quality': 50.0,
            'active_rules': []
        }


def plot_membership_functions() -> str:
    """
    Üyelik fonksiyonlarını görselleştir
    
    Returns:
        str: Base64 encoded PNG
    """
    fig, axes = plt.subplots(3, 3, figsize=(16, 12))
    fig.suptitle('Bulanık Mantık Üyelik Fonksiyonları', fontsize=16, fontweight='bold')
    
    # Uyku saatleri
    ax = axes[0, 0]
    x = np.linspace(0, 12, 300)
    ax.plot(x, [trapmf(v, SLEEP_LOW) for v in x], 'r-', linewidth=2, label='Low (0-6)')
    ax.plot(x, [trapmf(v, SLEEP_MEDIUM) for v in x], 'y-', linewidth=2, label='Medium (5-9)')
    ax.plot(x, [trapmf(v, SLEEP_HIGH) for v in x], 'g-', linewidth=2, label='High (8-12)')
    ax.set_title('Sleep Hours (0-12)', fontweight='bold')
    ax.set_xlabel('Hours')
    ax.set_ylabel('Membership')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Kafein
    ax = axes[0, 1]
    x = np.linspace(0, 500, 300)
    ax.plot(x, [trapmf(v, CAFFEINE_LOW) for v in x], 'g-', linewidth=2, label='Low (0-150)')
    ax.plot(x, [trapmf(v, CAFFEINE_MEDIUM) for v in x], 'y-', linewidth=2, label='Medium (100-300)')
    ax.plot(x, [trapmf(v, CAFFEINE_HIGH) for v in x], 'r-', linewidth=2, label='High (250-500)')
    ax.set_title('Caffeine (0-500 mg)', fontweight='bold')
    ax.set_xlabel('mg')
    ax.set_ylabel('Membership')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Egzersiz
    ax = axes[0, 2]
    x = np.linspace(0, 120, 300)
    ax.plot(x, [trapmf(v, EXERCISE_LOW) for v in x], 'r-', linewidth=2, label='Low (0-30)')
    ax.plot(x, [trapmf(v, EXERCISE_MEDIUM) for v in x], 'y-', linewidth=2, label='Medium (20-70)')
    ax.plot(x, [trapmf(v, EXERCISE_HIGH) for v in x], 'g-', linewidth=2, label='High (60-120)')
    ax.set_title('Exercise (0-120 min)', fontweight='bold')
    ax.set_xlabel('Minutes')
    ax.set_ylabel('Membership')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # İş stresi
    ax = axes[1, 0]
    x = np.linspace(0, 10, 300)
    ax.plot(x, [trapmf(v, WORK_LOW) for v in x], 'g-', linewidth=2, label='Low (0-4)')
    ax.plot(x, [trapmf(v, WORK_MEDIUM) for v in x], 'y-', linewidth=2, label='Medium (3-7)')
    ax.plot(x, [trapmf(v, WORK_HIGH) for v in x], 'r-', linewidth=2, label='High (6-10)')
    ax.set_title('Work Stress (0-10)', fontweight='bold')
    ax.set_xlabel('Level')
    ax.set_ylabel('Membership')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Çevresel skor
    ax = axes[1, 1]
    x = np.linspace(0, 100, 300)
    ax.plot(x, [trapmf(v, ENV_BAD) for v in x], 'r-', linewidth=2, label='Bad (0-50)')
    ax.plot(x, [trapmf(v, ENV_MEDIUM) for v in x], 'y-', linewidth=2, label='Medium (40-80)')
    ax.plot(x, [trapmf(v, ENV_GOOD) for v in x], 'g-', linewidth=2, label='Good (70-100)')
    ax.set_title('Environmental Score (0-100)', fontweight='bold')
    ax.set_xlabel('Score')
    ax.set_ylabel('Membership')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Çıktı: Stres
    ax = axes[1, 2]
    x = np.linspace(0, 100, 300)
    ax.plot(x, [trapmf(v, OUTPUT_STRESS_LOW) for v in x], 'g-', linewidth=2, label='Low (0-35)')
    ax.plot(x, [trapmf(v, OUTPUT_STRESS_MEDIUM) for v in x], 'y-', linewidth=2, label='Medium (30-70)')
    ax.plot(x, [trapmf(v, OUTPUT_STRESS_HIGH) for v in x], 'r-', linewidth=2, label='High (60-100)')
    ax.set_title('Output: Stress (0-100)', fontweight='bold')
    ax.set_xlabel('Level')
    ax.set_ylabel('Membership')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Çıktı: Uyku kalitesi
    ax = axes[2, 0]
    x = np.linspace(0, 100, 300)
    ax.plot(x, [trapmf(v, OUTPUT_QUALITY_POOR) for v in x], 'r-', linewidth=2, label='Poor (0-40)')
    ax.plot(x, [trapmf(v, OUTPUT_QUALITY_AVERAGE) for v in x], 'y-', linewidth=2, label='Average (30-70)')
    ax.plot(x, [trapmf(v, OUTPUT_QUALITY_GOOD) for v in x], 'g-', linewidth=2, label='Good (60-100)')
    ax.set_title('Output: Sleep Quality (0-100)', fontweight='bold')
    ax.set_xlabel('Quality')
    ax.set_ylabel('Membership')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Boş panelleri gizle
    axes[2, 1].axis('off')
    axes[2, 2].axis('off')
    
    plt.tight_layout()
    
    # Base64 encode
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    return img_base64


# Backward compatibility için eski fonksiyon isimleri
def get_membership_plots() -> str:
    """Backward compatibility için"""
    return plot_membership_functions()
