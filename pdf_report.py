"""
PDF Rapor Oluşturma Modülü
ReportLab kullanarak analiz raporları üretir
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime

def create_pdf_report(inputs, results):
    """
    PDF rapor oluştur
    
    Args:
        inputs: dict - Kullanıcı girdileri
        results: dict - Analiz sonuçları
    
    Returns:
        BytesIO - PDF buffer
    """
    # PDF buffer
    buffer = BytesIO()
    
    # PDF oluştur
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for elements
    story = []
    
    # Stiller
    styles = getSampleStyleSheet()
    
    # Başlık stili
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Alt başlık stili
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.grey,
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    # Bölüm başlığı
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    # Normal metin
    normal_style = styles['Normal']
    
    # Başlık
    title = Paragraph("🧠 Bulanık Mantık Uyku & Stres Analiz Raporu", title_style)
    story.append(title)
    
    # Tarih
    date_text = f"Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    date = Paragraph(date_text, subtitle_style)
    story.append(date)
    
    story.append(Spacer(1, 0.3 * inch))
    
    # GİRDİ VERİLERİ
    story.append(Paragraph("📊 Girdi Verileri", section_style))
    
    input_data = [
        ['Parametre', 'Değer', 'Birim'],
        ['Uyku Süresi', f"{inputs.get('sleep_hours', 0):.1f}", 'saat'],
        ['Kafein Tüketimi', f"{inputs.get('caffeine_mg', 0):.0f}", 'mg'],
        ['Egzersiz Süresi', f"{inputs.get('exercise_min', 0):.0f}", 'dakika'],
        ['İş Stresi Seviyesi', f"{inputs.get('work_stress', 0):.1f}", '0-10']
    ]
    
    input_table = Table(input_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    
    story.append(input_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # ANALİZ SONUÇLARI
    story.append(Paragraph("🎯 Analiz Sonuçları", section_style))
    
    # Stres seviyesi değerlendirmesi
    stress = results.get('stress', 0)
    if stress < 40:
        stress_level = "Düşük ✅"
        stress_color = colors.green
    elif stress < 70:
        stress_level = "Orta ⚠️"
        stress_color = colors.orange
    else:
        stress_level = "Yüksek ❌"
        stress_color = colors.red
    
    # Uyku kalitesi değerlendirmesi
    sleep_quality = results.get('sleep_quality', 0)
    if sleep_quality > 70:
        quality_level = "İyi ✅"
        quality_color = colors.green
    elif sleep_quality > 45:
        quality_level = "Orta ⚠️"
        quality_color = colors.orange
    else:
        quality_level = "Kötü ❌"
        quality_color = colors.red
    
    result_data = [
        ['Metrik', 'Değer', 'Durum'],
        ['Stres Seviyesi', f"{stress:.1f}/100", stress_level],
        ['Uyku Kalitesi', f"{sleep_quality:.1f}/100", quality_level]
    ]
    
    result_table = Table(result_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
    result_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    
    story.append(result_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # TAVSİYELER
    story.append(Paragraph("💡 Kişiselleştirilmiş Tavsiyeler", section_style))
    
    recommendations = results.get('recommendations', [])
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            rec_text = f"{i}. {rec}"
            story.append(Paragraph(rec_text, normal_style))
            story.append(Spacer(1, 0.1 * inch))
    else:
        story.append(Paragraph("Tavsiye bulunamadı.", normal_style))
    
    story.append(Spacer(1, 0.3 * inch))
    
    # AKTİF KURALLAR
    active_rules = results.get('active_rules', [])
    if active_rules:
        story.append(Paragraph("📋 Aktif Fuzzy Kuralları", section_style))
        rules_text = ", ".join(active_rules)
        story.append(Paragraph(f"Bu analizde şu kurallar devreye girdi: {rules_text}", normal_style))
    
    # Footer
    story.append(Spacer(1, 0.5 * inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    footer = Paragraph(
        "Bu rapor Bulanık Mantık tabanlı yapay zeka sistemi tarafından otomatik oluşturulmuştur.<br/>"
        "Profesyonel tıbbi tavsiye yerine geçmez.",
        footer_style
    )
    story.append(footer)
    
    # PDF'i oluştur
    doc.build(story)
    
    # Buffer'ı başa sar
    buffer.seek(0)
    
    return buffer

if __name__ == "__main__":
    # Test
    print("Testing PDF report generation...")
    
    test_inputs = {
        'sleep_hours': 7.5,
        'caffeine_mg': 150,
        'exercise_min': 45,
        'work_stress': 6.5
    }
    
    test_results = {
        'stress': 55.2,
        'sleep_quality': 68.5,
        'active_rules': ['R1', 'R5', 'R7'],
        'recommendations': [
            '💤 Uyku sürenizi artırın (hedef: 7-9 saat)',
            '☕ Kafein tüketimini azaltın (özellikle öğleden sonra)',
            '🏃 Günlük egzersiz sürenizi artırın'
        ]
    }
    
    pdf_buffer = create_pdf_report(test_inputs, test_results)
    
    # Test dosyası kaydet
    with open('/tmp/test_report.pdf', 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    print("✅ PDF report created: /tmp/test_report.pdf")
