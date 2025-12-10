"""
Harici API Entegrasyonları
Çevresel faktörler için API çağrıları
"""

import os
import requests
from datetime import datetime
from typing import Dict, Optional
import ephem


def get_weather_data(city: str) -> Optional[Dict]:
    """
    OpenWeatherMap API'den hava durumu verisini çek
    
    Args:
        city: Şehir adı
    
    Returns:
        dict: Hava durumu verisi veya None
    """
    api_key = os.getenv('OPENWEATHER_API_KEY')
    
    # Default environmental values (can be overridden via environment variables)
    DEFAULT_TEMP = float(os.getenv('DEFAULT_TEMPERATURE', '20'))
    DEFAULT_HUMIDITY = float(os.getenv('DEFAULT_HUMIDITY', '50'))
    DEFAULT_WEATHER_SCORE = float(os.getenv('DEFAULT_WEATHER_SCORE', '70'))
    
    if not api_key:
        # API key yoksa default değer dön
        return {
            'temperature': DEFAULT_TEMP,
            'humidity': DEFAULT_HUMIDITY,
            'weather': 'clear',
            'score': DEFAULT_WEATHER_SCORE
        }
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Hava durumu skorunu hesapla
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            weather_main = data['weather'][0]['main'].lower()
            
            # İdeal sıcaklık: 18-24°C
            temp_score = 100 if 18 <= temp <= 24 else max(0, 100 - abs(temp - 21) * 5)
            
            # İdeal nem: 40-60%
            humidity_score = 100 if 40 <= humidity <= 60 else max(0, 100 - abs(humidity - 50) * 2)
            
            # Hava durumu skoru
            weather_score = 100
            if weather_main in ['rain', 'thunderstorm', 'drizzle']:
                weather_score = 40
            elif weather_main in ['clouds', 'mist', 'fog']:
                weather_score = 60
            elif weather_main in ['clear']:
                weather_score = 100
            
            overall_score = (temp_score + humidity_score + weather_score) / 3
            
            return {
                'temperature': temp,
                'humidity': humidity,
                'weather': weather_main,
                'score': round(overall_score, 2)
            }
        else:
            return None
    except Exception as e:
        print(f"Hava durumu API hatası: {e}")
        return None


def get_air_quality(city: str) -> Optional[Dict]:
    """
    AirVisual API'den hava kalitesi verisini çek
    
    Args:
        city: Şehir adı
    
    Returns:
        dict: Hava kalitesi verisi veya None
    """
    api_key = os.getenv('AIRVISUAL_API_KEY')
    
    # Default air quality values (can be overridden via environment variables)
    DEFAULT_AQI = int(os.getenv('DEFAULT_AQI', '50'))
    DEFAULT_AIR_SCORE = float(os.getenv('DEFAULT_AIR_SCORE', '75'))
    
    if not api_key:
        # API key yoksa default değer dön
        return {
            'aqi': DEFAULT_AQI,
            'quality': 'good',
            'score': DEFAULT_AIR_SCORE
        }
    
    try:
        # AirVisual API country ve state de gerektiriyor
        # Basitleştirme için default değer dönelim
        url = f"http://api.airvisual.com/v2/city?city={city}&state=&country=&key={api_key}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            aqi = data['data']['current']['pollution']['aqius']
            
            # AQI skorunu 0-100 skalasına çevir
            if aqi <= 50:
                score = 100
                quality = 'good'
            elif aqi <= 100:
                score = 75
                quality = 'moderate'
            elif aqi <= 150:
                score = 50
                quality = 'unhealthy_sensitive'
            elif aqi <= 200:
                score = 25
                quality = 'unhealthy'
            else:
                score = 0
                quality = 'hazardous'
            
            return {
                'aqi': aqi,
                'quality': quality,
                'score': score
            }
        else:
            return None
    except Exception as e:
        print(f"Hava kalitesi API hatası: {e}")
        return None


def get_daylight_hours(city: str = "Istanbul") -> Optional[Dict]:
    """
    Gün ışığı süresi hesaplama (basitleştirilmiş)
    
    Args:
        city: Şehir adı
    
    Returns:
        dict: Gün ışığı bilgisi
    """
    try:
        # Şehir koordinatları (basitleştirilmiş)
        city_coords = {
            'istanbul': (41.0082, 28.9784),
            'ankara': (39.9334, 32.8597),
            'izmir': (38.4237, 27.1428),
            'default': (41.0082, 28.9784)
        }
        
        city_lower = city.lower()
        lat, lon = city_coords.get(city_lower, city_coords['default'])
        
        # ephem ile gün doğumu/batımı hesapla
        observer = ephem.Observer()
        observer.lat = str(lat)
        observer.lon = str(lon)
        observer.date = datetime.now()
        
        sun = ephem.Sun()
        sunrise = observer.next_rising(sun)
        sunset = observer.next_setting(sun)
        
        # Gün ışığı süresini hesapla (saat cinsinden)
        daylight_duration = (sunset - sunrise) * 24  # Gün cinsinden saat'e çevir
        
        # Skorlama: 10-14 saat ideal
        if 10 <= daylight_duration <= 14:
            score = 100
        elif 8 <= daylight_duration < 10 or 14 < daylight_duration <= 16:
            score = 75
        else:
            score = 50
        
        return {
            'daylight_hours': round(daylight_duration, 2),
            'sunrise': str(sunrise),
            'sunset': str(sunset),
            'score': score
        }
    except Exception as e:
        print(f"Gün ışığı hesaplama hatası: {e}")
        # Default değer
        return {
            'daylight_hours': 12,
            'score': 80
        }


def get_moon_phase() -> Dict:
    """
    Ay fazını hesapla (ephem kütüphanesi)
    
    Returns:
        dict: Ay fazı bilgisi
    """
    try:
        moon = ephem.Moon()
        moon.compute(datetime.now())
        
        # Ay aydınlanma yüzdesi
        illumination = moon.phase
        
        # Skorlama: Tam ay ve yeni ay uyku kalitesini etkileyebilir
        # Yarım ay daha ideal
        if 40 <= illumination <= 60:
            score = 100
        elif 20 <= illumination < 40 or 60 < illumination <= 80:
            score = 80
        else:
            score = 60
        
        # Ay fazı adı
        if illumination < 6.25:
            phase_name = 'new_moon'
        elif illumination < 25:
            phase_name = 'waxing_crescent'
        elif illumination < 43.75:
            phase_name = 'first_quarter'
        elif illumination < 56.25:
            phase_name = 'waxing_gibbous'
        elif illumination < 75:
            phase_name = 'full_moon'
        elif illumination < 93.75:
            phase_name = 'waning_gibbous'
        else:
            phase_name = 'last_quarter'
        
        return {
            'illumination': round(illumination, 2),
            'phase_name': phase_name,
            'score': score
        }
    except Exception as e:
        print(f"Ay fazı hesaplama hatası: {e}")
        return {
            'illumination': 50,
            'phase_name': 'unknown',
            'score': 70
        }


def calculate_environmental_score(city: str = "Istanbul") -> Dict:
    """
    Tüm çevresel faktörleri birleştirerek genel skor hesapla
    
    Args:
        city: Şehir adı
    
    Returns:
        dict: Çevresel skor ve detaylar
    """
    try:
        # API'lerden veri çek
        weather = get_weather_data(city)
        air_quality = get_air_quality(city)
        daylight = get_daylight_hours(city)
        moon = get_moon_phase()
        
        # Skorları birleştir (ağırlıklı ortalama)
        weather_score = weather['score'] if weather else 70
        air_score = air_quality['score'] if air_quality else 70
        daylight_score = daylight['score'] if daylight else 70
        moon_score = moon['score']
        
        environmental_score = (
            weather_score * 0.3 +
            air_score * 0.3 +
            daylight_score * 0.2 +
            moon_score * 0.2
        )
        
        return {
            'environmental_score': round(environmental_score, 2),
            'weather': weather,
            'air_quality': air_quality,
            'daylight': daylight,
            'moon': moon,
            'city': city
        }
    except Exception as e:
        print(f"Çevresel skor hesaplama hatası: {e}")
        # Hata durumunda ortalama değer dön
        return {
            'environmental_score': 50,
            'error': str(e),
            'city': city
        }
