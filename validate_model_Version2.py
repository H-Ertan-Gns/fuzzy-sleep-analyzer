"""
Kaggle Sleep Health Dataset ile fuzzy model doğrulaması
- Gerçek veri vs fuzzy tahmin karşılaştırması
- Doğruluk metrikleri (MAE, RMSE, R²)
- Görselleştirme ve HTML rapor
"""

import pandas as pd
import numpy as np
from fuzzy_model import analyze
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# Veri yolu
CSV_PATH = 'data/Sleep_health_and_lifestyle_dataset.csv'
RESULTS_PATH = 'data/model_validation_results.csv'
REPORT_PATH = 'static/validation_report.html'

def load_and_prepare_data():
    """Kaggle CSV'sini yükle ve fuzzy model formatına dönüştür"""
    print("📂 Kaggle verisi yükleniyor...")
    
    if not os.path.exists(CSV_PATH):
        print(f"❌ HATA: {CSV_PATH} bulunamadı!")
        print("📥 Lütfen Kaggle'dan veriyi indirin:")
        print("   https://www.kaggle.com/datasets/uom190346a/sleep-health-and-lifestyle-dataset")
        return None
    
    df = pd.read_csv(CSV_PATH)
    
    print(f"✅ Veri yüklendi: {len(df)} kayıt")
    print(f"\n📊 Sütunlar: {df.columns.tolist()}\n")
    
    # İlk 3 satırı göster
    print("📋 Örnek veri:")
    print(df. head(3))
    
    return df

def map_to_fuzzy_inputs(row):
    """
    Kaggle verisini fuzzy model girdi formatına çevir
    
    Kaggle Sütunları → Fuzzy Model Girdileri:
    - 'Sleep Duration' → sleep_hours (saat)
    - 'Stress Level' → work_stress (0-10) 
    - 'Physical Activity Level' → exercise_min (dakika, 20-90 arası tahmini)
    - Kafein verisi yok → ortalama 100mg varsayıyoruz
    """
    
    # Sleep Duration zaten saat cinsinden
    sleep_hours = row. get('Sleep Duration', 7.0)
    
    # Stress Level zaten 0-10 arası
    work_stress = row.get('Stress Level', 5.0)
    
    # Physical Activity Level genelde 30-90 arası dakika olarak varsayalım
    # Eğer farklı bir formattaysa (örn.  0-100 skoru) dönüştür
    physical_activity = row.get('Physical Activity Level', 30.0)
    
    # Eğer 0-100 arası skorsa, 0-120 dakikaya çevir
    if physical_activity <= 100:
        exercise_min = (physical_activity / 100) * 120  # 0-120 dakika
    else:
        exercise_min = physical_activity
    
    # Kafein verisi genelde yok, varsayılan değer
    # BMI veya yaş gibi proxy kullanabilirsin
    caffeine_mg = 100. 0  # Ortalama tüketim
    
    return {
        'sleep_hours': float(sleep_hours),
        'caffeine_mg': float(caffeine_mg),
        'exercise_min': float(exercise_min),
        'work_stress': float(work_stress)
    }

def validate_model(df):
    """Model doğrulaması yap"""
    print("\n🔍 Model doğrulaması başlıyor...")
    
    results = []
    
    for idx, row in df.iterrows():
        # Fuzzy model girdilerini hazırla
        inputs = map_to_fuzzy_inputs(row)
        
        # Fuzzy analiz yap
        output = analyze(inputs)
        
        # Gerçek değerler (Kaggle'dan)
        # Stress Level 0-10 arası → 0-100'e çevir
        actual_stress = row.get('Stress Level', 5) * 10
        
        # Quality of Sleep 0-10 arası → 0-100'e çevir
        actual_sleep_quality = row.get('Quality of Sleep', 5) * 10
        
        # Tahmin edilen değerler
        predicted_stress = output['stress']
        predicted_sleep_quality = output['sleep_quality']
        
        results.append({
            'person_id': row. get('Person ID', idx),
            'actual_stress': actual_stress,
            'predicted_stress': predicted_stress,
            'actual_sleep_quality': actual_sleep_quality,
            'predicted_sleep_quality': predicted_sleep_quality,
            'sleep_hours': inputs['sleep_hours'],
            'exercise_min': inputs['exercise_min'],
            'work_stress': inputs['work_stress'],
            'active_rules': ','.join(output. get('active_rules', []))
        })
        
        if (idx + 1) % 50 == 0:
            print(f"   ✓ {idx + 1}/{len(df)} kayıt işlendi")
    
    results_df = pd.DataFrame(results)
    
    # CSV olarak kaydet
    results_df.to_csv(RESULTS_PATH, index=False)
    print(f"\n💾 Sonuçlar kaydedildi: {RESULTS_PATH}")
    
    return results_df

def calculate_metrics(results_df):
    """Doğruluk metriklerini hesapla"""
    print("\n📊 PERFORMANS METRİKLERİ")
    print("=" * 70)
    
    # STRES TAHMİNİ
    mae_stress = mean_absolute_error(
        results_df['actual_stress'], 
        results_df['predicted_stress']
    )
    rmse_stress = np. sqrt(mean_squared_error(
        results_df['actual_stress'], 
        results_df['predicted_stress']
    ))
    r2_stress = r2_score(
        results_df['actual_stress'], 
        results_df['predicted_stress']
    )
    
    print(f"\n🔴 STRES SEVİYESİ TAHMİNİ:")
    print(f"   MAE (Ortalama Mutlak Hata):     {mae_stress:.2f} / 100")
    print(f"   RMSE (Kök Ortalama Kare Hata):  {rmse_stress:.2f}")
    print(f"   R² Score (Açıklanan Varyans):   {r2_stress:.3f}")
    
    # UYKU KALİTESİ
    mae_sleep = mean_absolute_error(
        results_df['actual_sleep_quality'], 
        results_df['predicted_sleep_quality']
    )
    rmse_sleep = np.sqrt(mean_squared_error(
        results_df['actual_sleep_quality'], 
        results_df['predicted_sleep_quality']
    ))
    r2_sleep = r2_score(
        results_df['actual_sleep_quality'], 
        results_df['predicted_sleep_quality']
    )
    
    print(f"\n🔵 UYKU KALİTESİ TAHMİNİ:")
    print(f"   MAE:      {mae_sleep:.2f} / 100")
    print(f"   RMSE:     {rmse_sleep:.2f}")
    print(f"   R² Score: {r2_sleep:.3f}")
    
    # Yorumlama
    print(f"\n💡 YORUM:")
    
    if mae_stress < 15:
        print("   ✅ Stres tahmini MÜKEMMEL!")
    elif mae_stress < 25:
        print("   ⚠️  Stres tahmini İYİ, ancak iyileştirilebilir")
    else:
        print("   ❌ Stres tahmini ZAYIF - fuzzy kuralları gözden geçirilmeli")
    
    if mae_sleep < 15:
        print("   ✅ Uyku kalitesi tahmini MÜKEMMEL!")
    elif mae_sleep < 25:
        print("   ⚠️  Uyku kalitesi tahmini İYİ")
    else:
        print("   ❌ Uyku kalitesi tahmini ZAYIF")
    
    print("=" * 70)
    
    return {
        'mae_stress': mae_stress,
        'rmse_stress': rmse_stress,
        'r2_stress': r2_stress,
        'mae_sleep': mae_sleep,
        'rmse_sleep': rmse_sleep,
        'r2_sleep': r2_sleep
    }

def create_visualizations(results_df, metrics):
    """Görselleştirme grafikleri oluştur"""
    print("\n📈 Görselleştirmeler oluşturuluyor...")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Fuzzy Model Doğrulama Sonuçları', fontsize=18, fontweight='bold')
    
    # 1. Stres: Gerçek vs Tahmin (Scatter)
    ax = axes[0, 0]
    ax.scatter(results_df['actual_stress'], results_df['predicted_stress'], 
               alpha=0.5, s=30, color='#dc3545')
    ax.plot([0, 100], [0, 100], 'k--', lw=2, label='Mükemmel Tahmin')
    ax.set_xlabel('Gerçek Stres', fontsize=12)
    ax.set_ylabel('Tahmin Edilen Stres', fontsize=12)
    ax. set_title(f'Stres Tahmini (MAE: {metrics["mae_stress"]:.2f})', fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 2.  Uyku Kalitesi: Gerçek vs Tahmin
    ax = axes[0, 1]
    ax.scatter(results_df['actual_sleep_quality'], results_df['predicted_sleep_quality'], 
               alpha=0.5, s=30, color='#28a745')
    ax.plot([0, 100], [0, 100], 'k--', lw=2, label='Mükemmel Tahmin')
    ax.set_xlabel('Gerçek Uyku Kalitesi', fontsize=12)
    ax.set_ylabel('Tahmin Edilen Uyku Kalitesi', fontsize=12)
    ax. set_title(f'Uyku Kalitesi Tahmini (MAE: {metrics["mae_sleep"]:.2f})', fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 3. Hata Dağılımı - Stres
    ax = axes[1, 0]
    errors_stress = results_df['predicted_stress'] - results_df['actual_stress']
    ax. hist(errors_stress, bins=30, color='#dc3545', alpha=0.7, edgecolor='black')
    ax.axvline(0, color='black', linestyle='--', linewidth=2)
    ax.set_xlabel('Tahmin Hatası', fontsize=12)
    ax.set_ylabel('Frekans', fontsize=12)
    ax.set_title('Stres Tahmin Hatası Dağılımı', fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 4. Hata Dağılımı - Uyku
    ax = axes[1, 1]
    errors_sleep = results_df['predicted_sleep_quality'] - results_df['actual_sleep_quality']
    ax.hist(errors_sleep, bins=30, color='#28a745', alpha=0.7, edgecolor='black')
    ax.axvline(0, color='black', linestyle='--', linewidth=2)
    ax.set_xlabel('Tahmin Hatası', fontsize=12)
    ax.set_ylabel('Frekans', fontsize=12)
    ax. set_title('Uyku Kalitesi Tahmin Hatası Dağılımı', fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Kaydet
    viz_path = 'static/validation_plots.png'
    os.makedirs('static', exist_ok=True)
    plt.savefig(viz_path, dpi=150, bbox_inches='tight')
    print(f"   ✓ Grafikler kaydedildi: {viz_path}")
    plt.close()
    
    return viz_path

def generate_html_report(results_df, metrics, viz_path):
    """HTML doğrulama raporu oluştur"""
    print("\n📄 HTML rapor oluşturuluyor...")
    
    # İlk 10 örnek
    sample_html = results_df.head(10).to_html(
        classes='table table-striped',
        index=False,
        float_format=lambda x: f'{x:.1f}'
    )
    
    html = f"""
    <! DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Model Doğrulama Raporu</title>
        <style>
            body {{ 
                font-family: 'Segoe UI', sans-serif; 
                max-width: 1200px; 
                margin: 40px auto; 
                padding: 20px;
                background: #f5f5f5;
            }}
            . container {{
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }}
            h1 {{ 
                color: #667eea; 
                text-align: center;
                margin-bottom: 10px;
            }}
            . subtitle {{
                text-align: center;
                color: #666;
                margin-bottom: 40px;
            }}
            . metrics {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                margin: 30px 0;
            }}
            .metric-card {{
                background: #f8f9fa;
                padding: 25px;
                border-radius: 8px;
                border-left: 5px solid #667eea;
            }}
            .metric-card h2 {{
                color: #667eea;
                margin-bottom: 15px;
            }}
            . metric-row {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #e0e0e0;
            }}
            .metric-row:last-child {{
                border-bottom: none;
            }}
            .metric-label {{
                font-weight: 600;
                color: #555;
            }}
            .metric-value {{
                font-weight: bold;
                color: #333;
                font-size: 1.1em;
            }}
            .plot {{
                text-align: center;
                margin: 40px 0;
            }}
            .plot img {{
                max-width: 100%;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }}
            .table {{
                width: 100%;
                border-collapse: collapse;
                margin: 30px 0;
            }}
            .table th {{
                background: #667eea;
                color: white;
                padding: 12px;
                text-align: left;
            }}
            .table td {{
                padding: 10px;
                border-bottom: 1px solid #e0e0e0;
            }}
            .table tr:hover {{
                background: #f8f9fa;
            }}
            . badge {{
                display: inline-block;
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 0. 9em;
                font-weight: 600;
            }}
            .badge-success {{ background: #d4edda; color: #155724; }}
            .badge-warning {{ background: #fff3cd; color: #856404; }}
            .badge-danger {{ background: #f8d7da; color: #721c24; }}
            .back-btn {{
                display: inline-block;
                padding: 12px 24px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                margin-top: 30px;
            }}
            . back-btn:hover {{
                background: #5568d3;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 Fuzzy Model Doğrulama Raporu</h1>
            <p class="subtitle">Kaggle Sleep Health Dataset ile Model Performans Analizi</p>
            <p class="subtitle" style="font-size: 0.9em; color: #999;">
                Oluşturma Tarihi: {datetime.now().strftime('%d. %m.%Y %H:%M')} | 
                Toplam Kayıt: {len(results_df)}
            </p>
            
            <div class="metrics">
                <div class="metric-card" style="border-left-color: #dc3545;">
                    <h2 style="color: #dc3545;">🔴 Stres Seviyesi Tahmini</h2>
                    <div class="metric-row">
                        <span class="metric-label">MAE (Ortalama Mutlak Hata):</span>
                        <span class="metric-value">{metrics['mae_stress']:. 2f} / 100</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">RMSE (Kök Ort. Kare Hata):</span>
                        <span class="metric-value">{metrics['rmse_stress']:.2f}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">R² Score:</span>
                        <span class="metric-value">{metrics['r2_stress']:.3f}</span>
                    </div>
                    <div style="margin-top: 15px;">
                        <span class="badge {'badge-success' if metrics['mae_stress'] < 15 else 'badge-warning' if metrics['mae_stress'] < 25 else 'badge-danger'}">
                            {'Mükemmel' if metrics['mae_stress'] < 15 else 'İyi' if metrics['mae_stress'] < 25 else 'Zayıf'}
                        </span>
                    </div>
                </div>
                
                <div class="metric-card" style="border-left-color: #28a745;">
                    <h2 style="color: #28a745;">🔵 Uyku Kalitesi Tahmini</h2>
                    <div class="metric-row">
                        <span class="metric-label">MAE:</span>
                        <span class="metric-value">{metrics['mae_sleep']:.2f} / 100</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">RMSE:</span>
                        <span class="metric-value">{metrics['rmse_sleep']:.2f}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">R² Score:</span>
                        <span class="metric-value">{metrics['r2_sleep']:.3f}</span>
                    </div>
                    <div style="margin-top: 15px;">
                        <span class="badge {'badge-success' if metrics['mae_sleep'] < 15 else 'badge-warning' if metrics['mae_sleep'] < 25 else 'badge-danger'}">
                            {'Mükemmel' if metrics['mae_sleep'] < 15 else 'İyi' if metrics['mae_sleep'] < 25 else 'Zayıf'}
                        </span>
                    </div>
                </div>
            </div>
            
            <div class="plot">
                <h2 style="color: #667eea; margin-bottom: 20px;">📊 Görselleştirmeler</h2>
                <img src="/{viz_path}" alt="Validation Plots">
            </div>
            
            <h2 style="color: #667eea; margin-top: 50px;">📋 Örnek Tahminler (İlk 10)</h2>
            {sample_html}
            
            <p style="text-align: center; color: #666; margin-top: 30px; font-style: italic;">
                💡 Tam sonuçlar için: <code>data/model_validation_results.csv</code>
            </p>
            
            <div style="text-align: center;">
                <a href="/dashboard" class="back-btn">← Dashboard'a Dön</a>
                <a href="/api-docs" class="back-btn" style="background: #28a745;">📖 API Dökümanı</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    os.makedirs('static', exist_ok=True)
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"   ✓ HTML rapor oluşturuldu: {REPORT_PATH}")
    print(f"   🌐 Tarayıcıda aç: http://localhost:5000/validation-report")

def main():
    """Ana doğrulama fonksiyonu"""
    print("="*70)
    print("🧠 FUZZY MODEL DOĞRULAMA SİSTEMİ")
    print("="*70)
    
    # 1. Veriyi yükle
    df = load_and_prepare_data()
    if df is None:
        return
    
    # 2.  Model doğrulama
    results_df = validate_model(df)
    
    # 3. Metrikleri hesapla
    metrics = calculate_metrics(results_df)
    
    # 4. Görselleştir
    viz_path = create_visualizations(results_df, metrics)
    
    # 5. HTML rapor
    generate_html_report(results_df, metrics, viz_path)
    
    print("\n" + "="*70)
    print("✅ DOĞRULAMA TAMAMLANDI!")
    print("="*70)
    print(f"\n📁 Oluşturulan dosyalar:")
    print(f"   • {RESULTS_PATH}")
    print(f"   • {viz_path}")
    print(f"   • {REPORT_PATH}")
    print(f"\n🚀 Flask uygulamasını çalıştırın:")
    print(f"   python app.py")
    print(f"\n🌐 Raporu görüntüleyin:")
    print(f"   http://localhost:5000/validation-report")
    print("="*70)

if __name__ == "__main__":
    main()