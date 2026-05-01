import streamlit as st
import requests

# Web sitesinin başlığı ve açıklaması
st.set_page_config(page_title="Global YouTube Trend Avcısı", page_icon="🌍")
st.title("🌍 Global YouTube Trend Avcısı")
st.write("Hedef ülkeyi seçin, trend olan videoları ve potansiyel fırsatları anında keşfedin.")

# API ANAHTARINIZI BURAYA YAPIŞTIRIN
API_KEY = "BURAYA_API_ANAHTARINIZI_YAPISTIRIN"

# Güncellenmiş Hedef Ülkeler Listesi
countries = {
    "Amerika Birleşik Devletleri": "US", 
    "Birleşik Krallık": "GB",
    "Almanya": "DE", 
    "Türkiye": "TR", 
    "İtalya": "IT",     # Yeni eklendi
    "İspanya": "ES"     # Yeni eklendi
}

# Web sitesindeki açılır menü (Dropdown)
selected_country_name = st.selectbox("Analiz Etmek İstediğiniz Ülkeyi Seçin:", list(countries.keys()))
selected_country_code = countries[selected_country_name]

# Butona basıldığında çalışacak kısım
if st.button("🚀 Trendleri Analiz Et"):
    url = f"https://www.googleapis.com/youtube/v3/videos"
    params = {
        'part': 'snippet,contentDetails,statistics',
        'chart': 'mostPopular',
        'regionCode': selected_country_code,
        'maxResults': 20,
        'key': API_KEY
    }
    
    with st.spinner("YouTube veritabanı taranıyor..."):
        response = requests.get(url, params=params)
        
    if response.status_code == 200:
        data = response.json()
        st.success(f"{selected_country_name} için güncel veriler başarıyla çekildi!")
        
        for video in data.get('items', []):
            title = video['snippet']['title']
            views = video['statistics'].get('viewCount', '0')
            duration = video['contentDetails']['duration']
            channel = video['snippet']['channelTitle']
            video_id = video['id']
            
            # Format belirleme
            if 'H' not in duration and 'M' not in duration:
                video_format = "📱 Shorts (Dikey)"
            else:
                video_format = "📺 Uzun Video (Yatay)"
            
            # Ekrana yazdırma
            st.subheader(title)
            st.write(f"**Kanal:** {channel} | **Format:** {video_format} | **İzlenme:** {int(views):,}")
            st.markdown(f"[Videoyu İzle](https://www.youtube.com/watch?v={video_id})")
            st.markdown("---")
    else:
        st.error("Bir hata oluştu! Lütfen API anahtarınızı kontrol edin.")
