"""
PDF Rapor Oluşturma
ReportLab ile analiz sonuçlarını PDF'e dönüştürme
Python 3.9 Uyumlu
"""

from typing import Dict
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import io


def create_pdf_report(inputs: Dict, results: Dict):
    """
    Analiz sonuçlarını PDF raporuna dönüştür
    
    Args:
        inputs: dict - kullanıcı girdileri
        results: dict - analiz sonuçları
    
    Returns:
        BytesIO - PDF dosyası buffer
    """
    # PDF buffer oluştur
    buffer = io.BytesIO()
    
    # PDF dokümanı oluştur
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    # Stil tanımlamaları
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=1  # Center
    ))
    
    styles.add(ParagraphStyle(
        name='CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=12,
        spaceBefore=12
    ))
    
    # Rapor elemanları
    story = []
    
    # Başlık
    title = Paragraph("🧠 Bulanık Mantık Uyku & Stres Analiz Raporu", styles['CustomTitle'])
    story.append(title)
    story.append(Spacer(1, 0.3 * inch))
    
    # Tarih
    date_text = f"Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    story.append(Paragraph(date_text, styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))
    
    # Girdi Parametreleri
    story.append(Paragraph("📊 Girdi Parametreleri", styles['CustomHeading']))
    
    input_data = [
        ['Parametre', 'Değer'],
        ['Uyku Saatleri', f"{inputs.get('sleep_hours', 0)} saat"],
        ['Kafein Tüketimi', f"{inputs.get('caffeine_mg', 0)} mg"],
        ['Egzersiz Süresi', f"{inputs.get('exercise_min', 0)} dakika"],
        ['İş Stresi Seviyesi', f"{inputs.get('work_stress', 0)}/10"]
    ]
    
    input_table = Table(input_data, colWidths=[3 * inch, 2.5 * inch])
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    story.append(input_table)
    story.append(Spacer(1, 0.4 * inch))
    
    # Analiz Sonuçları
    story.append(Paragraph("🎯 Analiz Sonuçları", styles['CustomHeading']))
    
    stress_level = results.get('stress_level', 0)
    sleep_quality = results.get('sleep_quality', 0)
    
    # Stres seviyesi yorumu
    if stress_level < 30:
        stress_comment = "Düşük - İyi durumdasınız"
        stress_color = colors.green
    elif stress_level < 70:
        stress_comment = "Orta - Dikkat edilmeli"
        stress_color = colors.orange
    else:
        stress_comment = "Yüksek - Önlem alınmalı"
        stress_color = colors.red
    
    # Uyku kalitesi yorumu
    if sleep_quality < 40:
        quality_comment = "Kötü - İyileştirme gerekli"
        quality_color = colors.red
    elif sleep_quality < 70:
        quality_comment = "Orta - Geliştirilebilir"
        quality_color = colors.orange
    else:
        quality_comment = "İyi - Mükemmel"
        quality_color = colors.green
    
    result_data = [
        ['Metrik', 'Değer', 'Yorum'],
        ['Genel Stres Seviyesi', f"{stress_level:.1f}/100", stress_comment],
        ['Uyku Kalitesi', f"{sleep_quality:.1f}/100", quality_comment]
    ]
    
    result_table = Table(result_data, colWidths=[2 * inch, 1.5 * inch, 2 * inch])
    result_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    story.append(result_table)
    story.append(Spacer(1, 0.4 * inch))
    
    # Aktif Kurallar
    active_rules = results.get('active_rules', [])
    if active_rules:
        story.append(Paragraph("📋 Aktif Bulanık Mantık Kuralları", styles['CustomHeading']))
        
        from fuzzy_model import RULE_DESCRIPTIONS
        
        rules_text = "<br/>".join([
            f"<b>Kural {rule_id}:</b> {RULE_DESCRIPTIONS.get(rule_id, 'Açıklama yok')}"
            for rule_id in active_rules
        ])
        
        story.append(Paragraph(rules_text, styles['Normal']))
        story.append(Spacer(1, 0.4 * inch))
    
    # Öneriler
    story.append(Paragraph("💡 Öneriler", styles['CustomHeading']))
    
    recommendations = []
    
    # Uyku önerileri
    sleep_hours = inputs.get('sleep_hours', 7)
    if sleep_hours < 6:
        recommendations.append("• Uyku sürenizi artırın (hedef: 7-9 saat)")
    elif sleep_hours > 9:
        recommendations.append("• Uyku sürenizi dengeyin (ideal: 7-9 saat)")
    
    # Kafein önerileri
    caffeine = inputs.get('caffeine_mg', 0)
    if caffeine > 200:
        recommendations.append("• Kafein tüketiminizi azaltın (günlük max: 200-300mg)")
    
    # Egzersiz önerileri
    exercise = inputs.get('exercise_min', 0)
    if exercise < 30:
        recommendations.append("• Günlük egzersiz sürenizi artırın (hedef: 30-60 dakika)")
    
    # Stres önerileri
    work_stress = inputs.get('work_stress', 0)
    if work_stress > 6:
        recommendations.append("• Stres yönetimi teknikleri uygulayın (meditasyon, nefes egzersizleri)")
        recommendations.append("• İş-yaşam dengesini gözden geçirin")
    
    # Genel sonuç önerileri
    if stress_level > 60:
        recommendations.append("• Profesyonel destek alabilirsiniz (psikolog, yaşam koçu)")
    
    if sleep_quality < 50:
        recommendations.append("• Uyku hijyeni kurallarına dikkat edin")
        recommendations.append("• Yatak odası ortamını optimize edin (karanlık, sessiz, serin)")
    
    if not recommendations:
        recommendations.append("• Mevcut yaşam tarzınızı sürdürün, dengeli durumdasınız!")
    
    recommendations_text = "<br/>".join(recommendations)
    story.append(Paragraph(recommendations_text, styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))
    
    # Alt bilgi
    story.append(Spacer(1, 0.5 * inch))
    footer_text = """
    <i>Bu rapor bulanık mantık algoritmaları kullanılarak oluşturulmuştur. 
    Sonuçlar bilgilendirme amaçlıdır, tıbbi teşhis yerine geçmez.</i>
    """
    story.append(Paragraph(footer_text, styles['Normal']))
    
    # PDF'i oluştur
    doc.build(story)
    
    # Buffer'ı başa sar
    buffer.seek(0)
    
    return buffer
