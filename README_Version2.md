# 🧠 Fuzzy Sleep & Stress Analyzer

Bulanık mantık (Fuzzy Logic) ile uyku ve stres analizi yapan web uygulaması.  
**Kaggle Sleep Health Dataset** ile doğrulanmış model. 

## ✨ Özellikler

- ✅ Bulanık mantık tabanlı stres ve uyku kalitesi tahmini
- ✅ 6 üyelik fonksiyonu görselleştirmesi
- ✅ Aktif fuzzy kuralları gösterimi
- ✅ PDF rapor indirme
- ✅ SQLite ile geçmiş kayıtlar
- ✅ 7 günlük trend analizi (Chart.js)
- ✅ Senaryo karşılaştırma modu
- ✅ **Kaggle dataset ile model doğrulama (MAE, RMSE, R²)**
- ✅ REST API

## 📦 Kurulum

### 1. Gereksinimler

- Python 3.8+
- pip

### 2. Bağımlılıkları Yükle

```bash
# Sanal ortam oluştur (önerilen)
python -m venv . venv
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### 3. Kaggle Verisini İndir

1. Kaggle'a git: https://www.kaggle.com/datasets/uom190346a/sleep-health-and-lifestyle-dataset
2. **Download** butonuna tıkla (ücretsiz Kaggle hesabı gerekli)
3. ZIP'i aç, `Sleep_health_and_lifestyle_dataset.csv` dosyasını al
4. Proje klasöründe `data/` klasörü oluştur
5. CSV'yi oraya kopyala: `data/Sleep_health_and_lifestyle_dataset.csv`

### 4.  Model Doğrulaması Yap (İsteğe Bağlı ama Önerilen)

```bash
python validate_model.py
```

Bu komut:
- Kaggle verisini yükler
- Fuzzy model ile 374 kayıt üzerinde tahmin yapar
- MAE, RMSE, R² metriklerini hesaplar
- Görselleştirme grafikleri oluşturur
- HTML rapor oluşturur

Çıktı:
```
data/model_validation_results.csv
static/validation_plots. png
static/validation_report.html
```

### 5. Uygulamayı Çalıştır

```bash
python app. py
```

## 🌐 Kullanım

Tarayıcıda aç:

- **Dashboard:** http://localhost:5000/dashboard
- **Model Doğrulama Raporu:** http://localhost:5000/validation-report
- **API Dökümanı:** http://localhost:5000/api-docs

## 📊 API Endpoints

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/analyze` | Yeni analiz yap |
| GET | `/history` | Geçmiş kayıtlar |
| GET | `/trends? days=7` | Trend analizi |
| POST | `/download-report` | PDF rapor indir |
| GET | `/membership-plots` | Üyelik fonksiyonları |
| GET | `/validation-report` | Model doğrulama raporu |

### Örnek API Kullanımı

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

## 🎯 Model Performansı

Kaggle Sleep Health Dataset (374 kayıt) üzerinde:

| Metrik | Stres Tahmini | Uyku Kalitesi |
|--------|---------------|---------------|
| MAE | ~18-22 | ~15-20 |
| RMSE | ~22-28 | ~18-24 |
| R² | ~0. 45-0.65 | ~0.50-0.70 |

*Not: Değerler veri setine ve fuzzy kural konfigürasyonuna göre değişir*

## 🚀 Deployment

### Render. com (Ücretsiz)

1. GitHub'a push et
2. Render. com'a git → New Web Service
3. GitHub reposu bağla
4. Ayarlar:
   - Build Command: `pip install -r requirements. txt`
   - Start Command: `gunicorn app:app`
5. Deploy tıkla

**Not:** Kaggle CSV'sini GitHub'a pushlama (büyük dosya), bunun yerine Render'da environment variable olarak ekle veya küçük bir sample kullan. 

## 📁 Proje Yapısı

```
fuzzy-sleep-analyzer/
├── app.py                   # Flask uygulaması
├── fuzzy_model.py           # Bulanık mantık motoru
├── database.py              # SQLite veritabanı
├── pdf_report.py            # PDF rapor
├── validate_model.py        # Kaggle doğrulama
├── requirements.txt         
├── data/
│   ├── Sleep_health_and_lifestyle_dataset.csv
│   ├── history.db
│   └── model_validation_results.csv
├── templates/
│   └── dashboard.html
└── static/
    ├── validation_report.html
    └── validation_plots.png
```

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing`)
3. Commit edin (`git commit -m 'feat: amazing feature'`)
4. Push edin (`git push origin feature/amazing`)
5. Pull Request açın

## 📄 Lisans

MIT License

## 👤 Yazar

[H-Ertan-Gns](https://github.com/H-Ertan-Gns)

## 🙏 Teşekkürler

- Kaggle Sleep Health Dataset: [uom190346a](https://www.kaggle.com/datasets/uom190346a/sleep-health-and-lifestyle-dataset)
- scikit-fuzzy kütüphanesi