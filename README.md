# 🧠 Fuzzy Sleep & Stress Analyzer

Yapay zeka destekli bulanık mantık tabanlı uyku ve stres analiz sistemi. Scikit-fuzzy'ye ihtiyaç duymadan, manuel fuzzy logic implementasyonu ile Render.com'da ve localhost'ta çalışır.

## 🌟 Özellikler

- ✅ **Manuel Fuzzy Logic Motoru**: Scikit-fuzzy olmadan çalışır (Render uyumlu)
- ✅ **7 Fuzzy Kural**: Detaylı stres ve uyku kalitesi analizi
- ✅ **SQLite Veritabanı**: Analiz geçmişi ve trend takibi
- ✅ **PDF Rapor**: Detaylı analiz raporları oluşturma
- ✅ **Responsive Dashboard**: Modern web arayüzü
- ✅ **REST API**: Kolay entegrasyon için API endpoints
- ✅ **Model Doğrulama**: Kaggle dataset ile test edilmiş

## 🚀 Hızlı Başlangıç

### Gereksinimler

- Python 3.11+
- pip

### Kurulum

1. **Depoyu klonlayın:**
```bash
git clone https://github.com/H-Ertan-Gns/fuzzy-sleep-analyzer.git
cd fuzzy-sleep-analyzer
```

2. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Uygulamayı başlatın:**
```bash
# Development mode (debug açık)
FLASK_ENV=development python app.py

# Production mode (debug kapalı - önerilir)
python app.py
```

4. **Tarayıcıda açın:**
```
http://localhost:5000/dashboard
```

## 📁 Proje Yapısı

```
fuzzy-sleep-analyzer/
├── app.py                          # Ana Flask uygulaması
├── fuzzy_model.py                  # Manuel fuzzy logic motoru
├── database.py                     # SQLite veritabanı işlemleri
├── pdf_report.py                   # PDF rapor oluşturma
├── validate_model_Version2.py      # Model doğrulama scripti
├── requirements.txt                # Python bağımlılıkları
├── runtime.txt                     # Python sürümü (Render için)
├── templates/
│   └── dashboard.html              # Web arayüzü
├── data/                           # Veritabanı ve veri dosyaları
└── static/                         # Statik dosyalar (grafikler, raporlar)
```

## 🎯 Kullanım

### Web Arayüzü

1. Dashboard'u açın: `http://localhost:5000/dashboard`
2. Form alanlarını doldurun:
   - 💤 Uyku Süresi (0-12 saat)
   - ☕ Kafein Tüketimi (0-500 mg)
   - 🏃 Egzersiz Süresi (0-120 dakika)
   - 💼 İş Stresi Seviyesi (0-10)
3. "Analiz Et" butonuna tıklayın
4. Sonuçları görün:
   - Stres seviyesi (0-100)
   - Uyku kalitesi (0-100)
   - Kişiselleştirilmiş tavsiyeler
   - Aktif fuzzy kuralları

### API Kullanımı

#### Analiz Yap
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "sleep_hours": 7.5,
    "caffeine_mg": 120,
    "exercise_min": 45,
    "work_stress": 6
  }'
```

#### Geçmiş Kayıtları Getir
```bash
curl http://localhost:5000/history?user_id=anonymous&limit=10
```

#### Trend Analizi
```bash
curl http://localhost:5000/trends?user_id=anonymous&days=7
```

## 📊 API Endpoints

| Endpoint | Metod | Açıklama |
|----------|-------|----------|
| `/` | GET | Ana sayfa |
| `/dashboard` | GET | Dashboard arayüzü |
| `/analyze` | POST | Yeni analiz yap |
| `/history` | GET | Geçmiş kayıtları getir |
| `/trends` | GET | Trend analizi |
| `/download-report` | POST | PDF rapor indir |
| `/membership-plots` | GET | Üyelik fonksiyonları görselleştirme |
| `/rules` | GET | Fuzzy kuralları listele |
| `/validation-report` | GET | Model doğrulama raporu |
| `/api-docs` | GET | API dökümanı |

## 🧮 Fuzzy Logic Kuralları

Sistem 7 fuzzy kural kullanır:

1. **R1**: Az uyku VEYA çok kafein → Stres YÜKSEK
2. **R2**: Az uyku VE (az egzersiz VEYA yüksek iş) → Stres YÜKSEK
3. **R3**: Çok uyku VE çok egzersiz VE düşük iş → Stres DÜŞÜK
4. **R4**: Az uyku VEYA çok kafein VEYA yüksek iş → Uyku KÖTÜ
5. **R5**: Orta uyku VE orta egzersiz → Uyku ORTA
6. **R6**: Çok uyku VE çok egzersiz VE az kafein → Uyku İYİ
7. **R7**: Yüksek iş VE orta uyku → Stres ORTA

## 🔧 Geliştirme

### Test Etme

```bash
# Fuzzy model test
python -c "from fuzzy_model import analyze; print(analyze({'sleep_hours': 7.5, 'caffeine_mg': 120, 'exercise_min': 45, 'work_stress': 6}))"

# Database test
python database.py

# PDF test
python pdf_report.py
```

### Model Doğrulama

Kaggle Sleep Health Dataset ile model performansını test etmek için:

```bash
# Dataset'i data/ klasörüne ekleyin
# Kaggle: https://www.kaggle.com/datasets/uom190346a/sleep-health-and-lifestyle-dataset

python validate_model_Version2.py
```

## 🚢 Deployment

### Render.com

1. GitHub repository'nizi Render'a bağlayın
2. Environment variables ayarlayın:
   - `FLASK_ENV`: `production`
3. Build komutları otomatik algılanır
4. `gunicorn app:app` komutu ile başlatılır

### Docker (Opsiyonel)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data static

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
```

## 🔒 Güvenlik

- ✅ Flask debug mode sadece development ortamında aktif
- ✅ Environment variable ile kontrol edilen debug modu
- ✅ CodeQL güvenlik taraması yapılmış
- ✅ Güvenlik açığı bulunmamaktadır

## 📈 Performans Metrikleri

Model doğrulama sonuçları (Kaggle dataset):

- **Stres Tahmini MAE**: ~15-25 / 100
- **Uyku Kalitesi MAE**: ~15-25 / 100
- **R² Score**: 0.6-0.8 (değişken özelliklere bağlı)

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 👨‍💻 Geliştirici

H. Ertan Güneş

## 🙏 Teşekkürler

- Flask framework
- ReportLab PDF generation
- Scikit-learn (model validation)
- Matplotlib & Seaborn (visualizations)
- Kaggle Sleep Health Dataset

## 📞 İletişim

Sorularınız için issue açabilir veya pull request gönderebilirsiniz.

---

**Not**: Bu sistem profesyonel tıbbi tavsiye yerine geçmez. Sadece bilgilendirme amaçlıdır.
