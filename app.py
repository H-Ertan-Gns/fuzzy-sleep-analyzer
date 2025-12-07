"""
Gelişmiş Flask API + Dashboard + Model Doğrulama
"""
from flask import (
    Flask, request, jsonify, send_file, 
    render_template, send_from_directory
)
from fuzzy_model import analyze, get_membership_plots, RULE_DESCRIPTIONS
from database import save_analysis, get_history, get_trend_data
from pdf_report import create_pdf_report
from datetime import datetime
import json
import os

app = Flask(__name__)

@app.route("/")
def index():
    return """
    <html>
    <head>
        <title>Fuzzy Sleep & Stress Analyzer</title>
        <style>
            body { 
                font-family: 'Segoe UI', sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0; padding: 50px; text-align: center; 
            }
            .container {
                background: white; max-width: 700px; margin: 0 auto;
                padding: 40px; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            }
            h1 { color: #667eea; margin-bottom: 10px; }
            .btn {
                display: inline-block; margin: 10px; padding: 15px 30px;
                background: #667eea; color: white; text-decoration: none;
                border-radius: 6px; font-weight: 600; transition: 0.3s;
            }
            .btn:hover { background: #5568d3; transform: translateY(-2px); }
            .btn-success { background: #28a745; }
            .btn-success:hover { background: #218838; }
            .btn-warning { background: #ffc107; color: #333; }
            .btn-warning:hover { background: #e0a800; }
            .api-list { text-align: left; margin: 30px 0; }
            .api-list li { margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 Bulanık Mantık Uyku & Stres Analiz Sistemi</h1>
            <p style="color: #666; margin-bottom: 30px;">
                Yapay zeka destekli kişiselleştirilmiş sağlık analizi<br>
                <small>Kaggle Dataset ile doğrulanmış fuzzy logic model</small>
            </p>
            
            <a href="/dashboard" class="btn">📊 Dashboard</a>
            <a href="/validation-report" class="btn btn-success">✅ Model Doğrulama Raporu</a>
            <a href="/api-docs" class="btn btn-warning">📖 API Dökümanı</a>
            
            <div class="api-list">
                <h3>🔌 API Endpoints:</h3>
                <ul>
                    <li><b>POST /analyze</b> → Yeni analiz yap</li>
                    <li><b>GET /history</b> → Geçmiş kayıtları getir</li>
                    <li><b>GET /trends</b> → Trend analizi</li>
                    <li><b>POST /download-report</b> → PDF rapor indir</li>
                    <li><b>GET /membership-plots</b> → Üyelik fonksiyonları</li>
                    <li><b>GET /validation-report</b> → ✨ Model doğrulama raporu</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """

@app.route("/analyze", methods=["POST"])
def analyze_route():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({'error': 'JSON body expected'}), 400

    result = analyze(data)
    if result.get('error'):
        return jsonify({'error': result['error']}), 500

    result['active_rule_descriptions'] = [
        {'id': r, 'description': RULE_DESCRIPTIONS[r]} 
        for r in result.get('active_rules', [])
    ]

    user_id = data.get('user_id', 'anonymous')
    record_id = save_analysis(data, result, user_id)
    result['record_id'] = record_id

    return jsonify({
        'input': data,
        'result': result,
        'timestamp': datetime.now().isoformat()
    })

@app.route("/history")
def history():
    user_id = request.args.get('user_id', 'anonymous')
    limit = int(request.args.get('limit', 10))
    
    records = get_history(user_id, limit)
    
    for record in records:
        if record.get('active_rules'):
            record['active_rules'] = json.loads(record['active_rules'])
    
    return jsonify({
        'total': len(records),
        'records': records
    })

@app.route("/trends")
def trends():
    user_id = request.args.get('user_id', 'anonymous')
    days = int(request.args.get('days', 7))
    
    trend_data = get_trend_data(user_id, days)
    
    return jsonify({
        'period_days': days,
        'data_points': len(trend_data),
        'trends': trend_data
    })

@app.route("/download-report", methods=["POST"])
def download_report():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({'error': 'JSON body expected'}), 400
    
    inputs = data.get('inputs', {})
    results = data.get('results', {})
    
    pdf_buffer = create_pdf_report(inputs, results)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'analiz_raporu_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    )

@app.route("/membership-plots")
def membership_plots():
    img_data = get_membership_plots()
    html = f"""
    <html>
    <head>
        <title>Üyelik Fonksiyonları</title>
        <style>
            body {{ background: #f5f5f5; padding: 20px; font-family: Arial; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; }}
            h2 {{ color: #667eea; text-align: center; }}
            img {{ max-width: 100%; border: 2px solid #667eea; border-radius: 8px; }}
            .back-btn {{ 
                display: inline-block; margin: 20px 0; padding: 10px 20px; 
                background: #667eea; color: white; text-decoration: none; border-radius: 6px; 
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/dashboard" class="back-btn">← Dashboard'a Dön</a>
            <h2>📈 Bulanık Mantık Üyelik Fonksiyonları</h2>
            <p style="text-align: center; color: #666;">
                Bu grafikler sistemin karar verme mekanizmasını gösterir. 
            </p>
            <div style="text-align: center; margin-top: 30px;">
                <img src="data:image/png;base64,{img_data}">
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route("/rules")
def rules():
    return jsonify({
        'total_rules': len(RULE_DESCRIPTIONS),
        'rules': [{'id': k, 'description': v} for k, v in RULE_DESCRIPTIONS.items()]
    })

@app.route("/validation-report")
def validation_report():
    """Model doğrulama HTML raporunu göster"""
    report_path = 'static/validation_report.html'
    
    if not os.path.exists(report_path):
        return """
        <html>
        <body style="font-family: Arial; padding: 50px; text-align: center;">
            <h1 style="color: #dc3545;">⚠️ Doğrulama Raporu Bulunamadı</h1>
            <p>Lütfen önce model doğrulaması yapın:</p>
            <pre style="background: #f5f5f5; padding: 20px; display: inline-block; text-align: left;">
python validate_model.py
            </pre>
            <p><a href="/" style="color: #667eea;">← Ana Sayfaya Dön</a></p>
        </body>
        </html>
        """, 404
    
    with open(report_path, 'r', encoding='utf-8') as f:
        return f.read()

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

@app.route("/api-docs")
def api_docs():
    return """
    <html>
    <head><title>API Documentation</title>
    <style>
        body { font-family: monospace; max-width: 900px; margin: 50px auto; padding: 20px; }
        h1 { color: #667eea; }
        .endpoint { background: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 6px; border-left: 4px solid #667eea; }
        code { background: #e0e0e0; padding: 2px 6px; border-radius: 3px; }
    </style>
    </head>
    <body>
        <h1>📖 API Documentation</h1>
        
        <div class="endpoint">
            <h3>POST /analyze</h3>
            <p>Yeni analiz yapar ve sonuçları döner</p>
            <b>Request Body:</b>
            <pre>{
  "sleep_hours": 7.5,
  "caffeine_mg": 120,
  "exercise_min": 30,
  "work_stress": 5,
  "user_id": "optional_user_id"
}</pre>
        </div>

        <div class="endpoint">
            <h3>GET /validation-report</h3>
            <p>Kaggle dataset ile model doğrulama raporunu gösterir</p>
            <p><b>Not:</b> Önce <code>python validate_model.py</code> çalıştırılmalı</p>
        </div>

        <a href="/" style="display: inline-block; margin-top: 30px; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 6px;">← Ana Sayfa</a>
    </body>
    </html>
    """

# Static dosyalar için route
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    # data/ klasörünü oluştur
    os.makedirs('data', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("="*70)
    print("🧠 FUZZY SLEEP & STRESS ANALYZER")
    print("="*70)
    print("\n📊 Dashboard: http://localhost:5000/dashboard")
    print("✅ Doğrulama Raporu: http://localhost:5000/validation-report")
    print("\n💡 Model doğrulaması için:")
    print("   python validate_model.py")
    print("="*70 + "\n")
    
    # Debug mode should be disabled in production
    # Set via environment variable: FLASK_DEBUG=1 for development
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)