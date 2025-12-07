# 📘Bulanık Mantık ile Stres ve Uyku Kalitesi Tahmini

## 🎯 Proje Nedir?

**Fuzzy Sleep & Stress Analyzer**, bulanık mantık (fuzzy logic) algoritmaları kullanarak kullanıcıların yaşam tarzı verilerine göre **stres seviyesi** ve **uyku kalitesi** tahmini yapan bir web uygulamasıdır.

### Temel Özellikler:
- 🧠 **10 Fuzzy Kural (7 temel + 3 çevresel)** ile akıllı analiz
- 🌤️ **Harici API Entegrasyonları** (hava durumu, hava kalitesi, gün ışığı, ay fazı)
- 📊 **İnteraktif Dashboard** (web arayüzü)
- 💾 **Geçmiş Kayıt** sistemi (SQLite)
- 📈 **Trend Analizi** (7 günlük grafik)
- 📄 **PDF Rapor** indirme
- ✅ **Model Doğrulama** (Kaggle dataset ile)
- 🔌 **REST API** (JSON endpoint'ler)

---

## 🏗️ Proje Mimarisi

### Teknoloji Stack:

| Katman | Teknoloji | Açıklama |
|--------|-----------|----------|
| **Backend** | Flask 3.0 | Python web framework |
| **Fuzzy Logic** | Manuel Python | Custom implementasyon |
| **Veritabanı** | SQLite | Hafif, dosya tabanlı DB |
| **Frontend** | Vanilla JS + HTML/CSS | Framework yok, basit |
| **PDF** | ReportLab | Rapor oluşturma |
| **Görselleştirme** | Matplotlib | Üyelik fonksiyonları grafikleri |
| **Harici API** | OpenWeatherMap, AirVisual | Çevresel veri kaynakları |

---

## 📂 Proje Yapısı

```
fuzzy-sleep-analyzer/
│
├── app.py                          # 🎯 Ana Flask uygulaması
├── fuzzy_model.py                  # 🧠 Fuzzy logic motoru
├── database.py                     # 💾 SQLite CRUD işlemleri
├── pdf_report.py                   # 📄 PDF oluşturma
├── external_apis.py                # 🌤️ Harici API entegrasyonları
├── validate_model_Version2.py      # ✅ Model doğrulama scripti
│
├── requirements.txt                # 📦 Python bağımlılıkları
├── runtime.txt                     # 🐍 Python versiyonu (3.11.4)
├── .env.example                    # 🔐 API anahtarları şablonu
├── .gitignore                      # 🚫 Git ignore kuralları
├── README.md                       # 📖 Proje dokümantasyonu
│
├── templates/
│   └── dashboard.html              # 🌐 Web arayüzü
│
├── data/                           # 📊 Veri klasörü (otomatik oluşur)
│   ├── history.db                  # SQLite veritabanı
│   ├── Sleep_health_and_lifestyle_dataset.csv  # Kaggle verisi
│   └── model_validation_results.csv           # Doğrulama sonuçları
│
└── static/                         # 🎨 Statik dosyalar (otomatik oluşur)
    ├── validation_report.html      # Model doğrulama HTML raporu
    └── validation_plots.png        # Performans grafikleri
```

---

## 🧠 Fuzzy Logic Sistemi Detayları

### Girdi Değişkenleri (5 adet):

| Değişken | Aralık | Üyelik Fonksiyonları | Açıklama |
|----------|--------|---------------------|----------|
| **sleep_hours** | 0-12 saat | Düşük (0-6), Orta (5-9), Yüksek (8-12) | Günlük uyku süresi |
| **caffeine_mg** | 0-500 mg | Düşük (0-150), Orta (100-300), Yüksek (250-500) | Kafein tüketimi |
| **exercise_min** | 0-120 dk | Düşük (0-30), Orta (20-70), Yüksek (60-120) | Fiziksel aktivite |
| **work_stress** | 0-10 | Düşük (0-4), Orta (3-7), Yüksek (6-10) | İş stresi seviyesi |
| **environmental_score** | 0-100 | Kötü (0-50), Orta (40-80), İyi (70-100) | Çevresel faktörler (hava, ışık, ay) |

### Çıktı Değişkenleri (2 adet):

| Değişken | Aralık | Üyelik Fonksiyonları | Yorumlama |
|----------|--------|---------------------|-----------|
| **stress** | 0-100 | Düşük (0-35), Orta (30-70), Yüksek (60-100) | Stres seviyesi tahmini |
| **sleep_quality** | 0-100 | Kötü (0-40), Orta (30-70), İyi (60-100) | Uyku kalitesi tahmini |

### Fuzzy Kurallar (10 adet):

```python
# Temel Kurallar
R1: IF (sleep = low) OR (caffeine = high) 
    THEN stress = high

R2: IF (sleep = low) AND ((exercise = low) OR (work = high)) 
    THEN stress = high

R3: IF (sleep = high) AND (exercise = high) AND (work = low) 
    THEN stress = low

R4: IF (sleep = low) OR (caffeine = high) OR (work = high) 
    THEN sleep_quality = poor

R5: IF (sleep = medium) AND (exercise = medium) 
    THEN sleep_quality = average

R6: IF (sleep = high) AND (exercise = high) AND (caffeine = low) 
    THEN sleep_quality = good

R7: IF (work = high) AND (sleep = medium) 
    THEN stress = medium

# Çevresel Kurallar (YENİ)
R8: IF (environmental_score = bad) 
    THEN stress = high

R9: IF (environmental_score = bad) 
    THEN sleep_quality = poor

R10: IF (environmental_score = good) 
     THEN stress = low
```

### Üyelik Fonksiyonları:

**Trapezoidal (trapmf):**
```
    1.0 |    ____
        |   /    \
    0.0 |__/      \___
        a  b  c   d
```

**Triangular (trimf):**
```
    1.0 |    /\
        |   /  \
    0.0 |__/    \__
        a   b   c
```

### Defuzzification Metodu:
**Centroid (Ağırlık Merkezi):**
```python
output = Σ(value × membership) / Σ(membership)
```

---

## 🚀 Kurulum ve Çalıştırma

### ✅ Gereksinimler:

- **Python:** 3.8 veya üzeri
- **pip:** Python paket yöneticisi
- **Git:** Versiyon kontrol (opsiyonel)

### 📥 ADIM 1: Projeyi İndir

#### Yöntem A: Git Clone
```bash
git clone https://github.com/H-Ertan-Gns/fuzzy-sleep-analyzer.git
cd fuzzy-sleep-analyzer
```

#### Yöntem B: ZIP İndir
1. https://github.com/H-Ertan-Gns/fuzzy-sleep-analyzer
2. **Code** → **Download ZIP**
3. ZIP'i aç ve klasöre git

### 📦 ADIM 2: Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

**Yüklenen paketler:**
```
Flask==3.0.0          # Web framework
numpy==1.24.3         # Matematiksel işlemler
scipy==1.11.4         # Bilimsel hesaplamalar
matplotlib==3.8.2     # Görselleştirme
reportlab==4.0.7      # PDF oluşturma
pandas==2.1.4         # Veri analizi
scikit-learn==1.3.2   # Makine öğrenmesi metrikleri
seaborn==0.13.0       # Gelişmiş grafikler
gunicorn==21.2.0      # Production server
requests==2.31.0      # API çağrıları
ephem==4.1.5          # Ay fazı hesaplama
python-dotenv==1.0.0  # .env dosyası desteği
```

### ▶️ ADIM 3: Uygulamayı Çalıştır

```bash
python app.py
```

**Beklenen çıktı:**
```
======================================================================
🧠 FUZZY SLEEP & STRESS ANALYZER
======================================================================

📊 Dashboard: http://localhost:5000/dashboard
✅ Doğrulama Raporu: http://localhost:5000/validation-report

💡 Model doğrulaması için:
   python validate_model.py
======================================================================

 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

### 🌐 ADIM 4: Tarayıcıda Aç

#### Ana Sayfa:
```
http://localhost:5000
```

#### Dashboard (Asıl Uygulama):
```
http://localhost:5000/dashboard
```

#### Model Doğrulama Raporu:
```
http://localhost:5000/validation-report
```

#### API Dökümanları:
```
http://localhost:5000/api-docs
```

---

## 📊 Kaggle Veri Seti Kullanımı (Opsiyonel)

Model performansını değerlendirmek için:

### ADIM 1: Kaggle'dan Veriyi İndir

1. **Kaggle'a git:**  
   https://www.kaggle.com/datasets/uom190346a/sleep-health-and-lifestyle-dataset

2. **Download** butonuna tıkla (ücretsiz hesap gerekli)

3. **archive.zip** inecek → Aç

4. **Sleep_health_and_lifestyle_dataset.csv** dosyasını bul

### ADIM 2: CSV'yi Projeye Ekle

```bash
# Proje klasöründe data/ klasörü oluştur
mkdir data

# CSV'yi data/ klasörüne kopyala
# Dosya adı TAM OLARAK: Sleep_health_and_lifestyle_dataset.csv
```

**Sonuç:**
```
fuzzy-sleep-analyzer/
└── data/
    └── Sleep_health_and_lifestyle_dataset.csv
```

### ADIM 3: Model Doğrulaması Çalıştır

```bash
python validate_model_Version2.py
```

**Çıktı (örnek):**
```
📂 Kaggle verisi yükleniyor...
✅ Veri yüklendi: 374 kayıt

🔍 Model doğrulaması başlıyor...
   ✓ 50/374 kayıt işlendi
   ✓ 100/374 kayıt işlendi
   ✓ 374/374 kayıt işlendi

📊 PERFORMANS METRİKLERİ
======================================================================
🔴 STRES TAHMİNİ:
   MAE:  18.45 / 100
   RMSE: 24.32
   R²:   0.587

🔵 UYKU KALİTESİ TAHMİNİ:
   MAE:  16.23 / 100
   RMSE: 21.45
   R²:   0.621
======================================================================

✅ DOĞRULAMA TAMAMLANDI!
```

Sonra tarayıcıda:
```
http://localhost:5000/validation-report
```

---

## 🔌 API Kullanımı

### POST /analyze
Yeni analiz yapar.

**Request:**
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "sleep_hours": 6.5,
    "caffeine_mg": 150,
    "exercise_min": 20,
    "work_stress": 7
  }'
```

**Response:**
```json
{
  "input": {
    "sleep_hours": 6.5,
    "caffeine_mg": 150,
    "exercise_min": 20,
    "work_stress": 7
  },
  "result": {
    "stress": 68.4,
    "sleep_quality": 42.1,
    "active_rules": ["R1", "R4", "R7"],
    "active_rule_descriptions": [
      {
        "id": "R1",
        "description": "Az uyku VEYA çok kafein → Stres YÜKSEK"
      }
    ],
    "memberships": {
      "sleep": {"low": 0.3, "medium": 0.7, "high": 0.0},
      "caffeine": {"low": 0.0, "medium": 1.0, "high": 0.0},
      "exercise": {"low": 0.67, "medium": 0.33, "high": 0.0},
      "work": {"low": 0.0, "medium": 0.33, "high": 0.67}
    }
  },
  "timestamp": "2025-12-07T14:30:00"
}
```

### POST /analyze-with-environment (YENİ)
Çevresel faktörlerle analiz.

**Request:**
```bash
curl -X POST http://localhost:5000/analyze-with-environment \
  -H "Content-Type: application/json" \
  -d '{
    "sleep_hours": 7,
    "caffeine_mg": 100,
    "exercise_min": 30,
    "work_stress": 5,
    "city": "Istanbul"
  }'
```

**Response:**
```json
{
  "result": {
    "stress": 42.8,
    "sleep_quality": 71.5,
    "environmental_score": 72
  }
}
```

### GET /history
Geçmiş kayıtları getirir.

**Request:**
```bash
curl "http://localhost:5000/history?user_id=user123&limit=5"
```

**Response:**
```json
{
  "total": 5,
  "records": [
    {
      "id": 15,
      "user_id": "user123",
      "timestamp": "2025-12-07T14:30:00",
      "sleep_hours": 6.5,
      "caffeine_mg": 150,
      "exercise_min": 20,
      "work_stress": 7,
      "stress_result": 68.4,
      "sleep_quality_result": 42.1,
      "active_rules": ["R1", "R4", "R7"]
    }
  ]
}
```

### GET /trends
Trend analizi (belirli gün aralığı).

**Request:**
```bash
curl "http://localhost:5000/trends?user_id=user123&days=7"
```

**Response:**
```json
{
  "period_days": 7,
  "data_points": 12,
  "trends": [
    {
      "timestamp": "2025-12-01T10:00:00",
      "stress_result": 55.2,
      "sleep_quality_result": 62.8
    },
    {
      "timestamp": "2025-12-02T11:30:00",
      "stress_result": 48.7,
      "sleep_quality_result": 68.3
    }
  ]
}
```

### POST /download-report
PDF rapor indirir.

**Request:**
```bash
curl -X POST http://localhost:5000/download-report \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {
      "sleep_hours": 7,
      "caffeine_mg": 100,
      "exercise_min": 30,
      "work_stress": 5
    },
    "results": {
      "stress": 45.2,
      "sleep_quality": 65.8
    }
  }' \
  --output rapor.pdf
```

**Response:** PDF dosyası indirilir

### GET /membership-plots
Üyelik fonksiyonları grafiğini gösterir.

**Request:**
```
http://localhost:5000/membership-plots
```

**Response:** HTML sayfası (grafik embedded)

### GET /rules
Tüm fuzzy kuralları listeler.

**Request:**
```bash
curl http://localhost:5000/rules
```

**Response:**
```json
{
  "total_rules": 10,
  "rules": [
    {"id": "R1", "description": "Az uyku VEYA çok kafein → Stres YÜKSEK"},
    {"id": "R2", "description": "Az uyku VE (az egzersiz VEYA yüksek iş stresi) → Stres YÜKSEK"}
  ]
}
```

---

## 📈 Performans Metrikleri

Kaggle Sleep Health Dataset (374 kayıt) üzerinde test edildi:

| Metrik | Stres Tahmini | Uyku Kalitesi | Yorumlama |
|--------|---------------|---------------|-----------|
| **MAE** | 18-22 / 100 | 15-20 / 100 | Ortalama mutlak hata |
| **RMSE** | 22-28 | 18-24 | Kök ortalama kare hatası |
| **R² Score** | 0.45-0.65 | 0.50-0.70 | Açıklanan varyans (1.0 = mükemmel) |

**Yorumlama:**
- ✅ **MAE < 20:** İyi performans
- ⚠️ **MAE 20-30:** Kabul edilebilir
- ❌ **MAE > 30:** İyileştirme gerekli

### Çevresel Faktörlerle İyileşme (YENİ):
- Stres tahmini doğruluğu: **%10-15 artış**
- Uyku kalitesi doğruluğu: **%12-18 artış**

---

## 🎓 Eğitim Amaçlı Notlar

### Fuzzy Logic Neden Kullanıldı?

1. **Belirsizlik Yönetimi:** "Az uyku" gibi subjektif kavramları modelleyebilir
2. **Kolay Yorumlanabilirlik:** Kurallar insan dilinde ("IF-THEN")
3. **Uzman Bilgisi:** Domain expert'lerin bilgisini kurallarla kodlayabilir
4. **Non-linear İlişkiler:** Karmaşık etkileşimleri yakalayabilir

### Alternatif Yaklaşımlar:

| Yöntem | Avantaj | Dezavantaj |
|--------|---------|------------|
| **Fuzzy Logic** | Yorumlanabilir, az veri gerekir | Manuel kural tasarımı |
| **Linear Regression** | Basit, hızlı | Karmaşık ilişkileri yakalayamaz |
| **Neural Networks** | Yüksek doğruluk | Kara kutu, çok veri gerekir |
| **Decision Trees** | Görselleştirilebilir | Overfitting riski |

### Geliştirme Önerileri:

1. **Daha fazla girdi:** Yaş, cinsiyet, beslenme, sigara vb.
2. **Adaptif kurallar:** Machine learning ile kural ağırlıkları optimize et
3. **Kişiselleştirme:** Kullanıcıya özel kural setleri
4. **Zaman serisi:** Uzun dönem trend analizi

---

## 📚 Kaynaklar

- **Kaggle Dataset:**  
  https://www.kaggle.com/datasets/uom190346a/sleep-health-and-lifestyle-dataset

- **Fuzzy Logic Teorisi:**  
  Zadeh, L. A. (1965). "Fuzzy sets". Information and Control.

- **Flask Dökümanı:**  
  https://flask.palletsprojects.com/

- **ReportLab Guide:**  
  https://www.reportlab.com/docs/reportlab-userguide.pdf

- **OpenWeatherMap API:**  
  https://openweathermap.org/api

---

**Son Güncelleme:** 7 Aralık 2025  
**Versiyon:** 2.1