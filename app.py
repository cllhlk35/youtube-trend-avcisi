import streamlit as st
import requests
from datetime import datetime, timedelta

# Arayüz ayarları
st.set_page_config(page_title="Global YouTube Fırsat Avcısı", page_icon="🎯", layout="wide")
st.title("🎯 Global YouTube Fırsat Avcısı (Pro)")
st.write("Belirlediğiniz anahtar kelime ve kategoride **son 30 günün** gizli fırsatlarını (Düşük Rekabet / Yüksek Hacim) bulun.")

# API ANAHTARINIZI AŞAĞIDAKİ TIRNAKLARIN İÇİNE YAPIŞTIRIN
API_KEY = "AIzaSyCT5pvnI5IpLI4gffjLjL8pTQgodjuG_HY"

countries = {
    "Amerika Birleşik Devletleri": "US", 
    "Birleşik Krallık": "GB",
    "Almanya": "DE", 
    "Türkiye": "TR", 
    "İtalya": "IT",     
    "İspanya": "ES"     
}

# "Tüm Kategoriler" seçeneği eklendi, böylece YouTube'un kısıtlamaları aşıldı!
categories = {
    "Tüm Kategoriler (Önerilen)": "", 
    "Eğitim": "27",
    "Eğlence": "24",
    "Oyun": "20",
    "Kişiler ve Bloglar": "22",
    "Nasıl Yapılır ve Stil": "26",
    "Bilim ve Teknoloji": "28",
    "Komedi": "23"
}

# 1. Satır: Ülke, Kategori ve YENİ Anahtar Kelime Kutusu
col1, col2, col3 = st.columns(3)
with col1:
    selected_country_name = st.selectbox("🌍 Hedef Ülke:", list(countries.keys()))
    selected_country_code = countries[selected_country_name]

with col2:
    selected_category_name = st.selectbox("📂 İçerik Kategorisi:", list(categories.keys()))
    selected_category_id = categories[selected_category_name]

with col3:
    # YENİ ÖZELLİK: Anahtar Kelime Arama Kutusu
    search_query = st.text_input("🔑 Anahtar Kelime:", placeholder="Örn: yapay zeka, vlog, podcast...")

st.markdown("---")
st.subheader("⚙️ Fırsat Filtreleri")

# 2. Satır: Kullanıcı Kontrolündeki Kaydırıcılar
col4, col5 = st.columns(2)
with col4:
    min_views = st.slider("Minimum İzlenme Sayısı:", min_value=1000, max_value=500000, value=5000, step=1000)
with col5:
    min_score = st.slider("Minimum Fırsat Puanı (İzlenme/Abone Oranı):", min_value=0.0, max_value=5.0, value=0.1, step=0.1)

st.markdown("---")

if st.button("🚀 Fırsatları Analiz Et"):
    
    # Kullanıcı anahtar kelime yazmazsa küçük bir ipucu göster
    if not search_query and selected_category_id != "":
        st.info("💡 İpucu: YouTube bazı kategorilerde anahtar kelime yazılmadan sonuç vermeyebilir. Arama kutusuna bir kelime yazmayı veya 'Tüm Kategoriler' seçeneğini kullanmayı deneyin.")
        
    thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat() + "Z"
    
    search_url = "https://www.googleapis.com/youtube/v3/search"
    search_params = {
        'part': 'snippet',
        'type': 'video',
        'regionCode': selected_country_code,
        'order': 'viewCount', 
        'publishedAfter': thirty_days_ago, 
        'maxResults': 50, 
        'key': API_KEY
    }
    
    # Kategori seçiliyse parametrelere ekle
    if selected_category_id != "":
        search_params['videoCategoryId'] = selected_category_id
        
    # Anahtar kelime yazılmışsa parametrelere ekle (YouTube'un kilit noktasını açan kod)
    if search_query:
        search_params['q'] = search_query
    
    with st.spinner("YouTube derinlikleri taranıyor..."):
        search_res = requests.get(search_url, params=search_params)
        
        if search_res.status_code == 200:
            search_data = search_res.json().get('items', [])
            
            if not search_data:
                st.warning("Bu kriterlere uygun taze video bulunamadı. Lütfen anahtar kelimenizi değiştirin.")
            else:
                video_ids = [item['id']['videoId'] for item in search_data]
                video_ids_str = ",".join(video_ids)
                
                video_url = f"https://www.googleapis.com/youtube/v3/videos"
                video_params = {
                    'part': 'snippet,contentDetails,statistics',
                    'id': video_ids_str,
                    'key': API_KEY
                }
                vid_res = requests.get(video_url, params=video_params)
                video_details = vid_res.json().get('items', []) if vid_res.status_code == 200 else []
                
                channel_ids = [v['snippet']['channelId'] for v in video_details]
                channel_ids_str = ",".join(list(set(channel_ids))) 
                
                channel_url = f"https://www.googleapis.com/youtube/v3/channels"
                channel_params = {
                    'part': 'statistics',
                    'id': channel_ids_str,
                    'key': API_KEY
                }
                chan_res = requests.get(channel_url, params=channel_params)
                
                if chan_res.status_code == 200 and video_details:
                    chan_data = chan_res.json().get('items', [])
                    sub_counts = {c['id']: int(c['statistics'].get('subscriberCount', 1)) for c in chan_data}
                    
                    analyzed_videos = []
                    for video in video_details:
                        title = video['snippet']['title']
                        views = int(video['statistics'].get('viewCount', 0))
                        duration = video['contentDetails']['duration']
                        channel_title = video['snippet']['channelTitle']
                        channel_id = video['snippet']['channelId']
                        video_id = video['id']
                        
                        subs = sub_counts.get(channel_id, 1)
                        if subs == 0: subs = 1
                        
                        opportunity_score = views / subs
                        
                        if opportunity_score >= min_score and views >= min_views: 
                            video_format = "📱 Shorts (Dikey)" if ('H' not in duration and 'M' not in duration) else "📺 Uzun Video (Yatay)"
                                
                            analyzed_videos.append({
                                'title': title,
                                'channel': channel_title,
                                'views': views,
                                'subs': subs,
                                'score': opportunity_score,
                                'format': video_format,
                                'link': f"https://www.youtube.com/watch?v={video_id}"
                            })
                    
                    analyzed_videos.sort(key=lambda x: x['score'], reverse=True)
                    
                    if analyzed_videos:
                        st.success(f"Analiz Tamamlandı! {len(analyzed_videos)} Adet Altın Fırsat Bulundu 🏆")
                        for idx, v in enumerate(analyzed_videos): 
                            st.subheader(f"#{idx+1} {v['title']}")
                            st.write(f"**Format:** {v['format']} | **Kanal:** {v['channel']} ({v['subs']:,} Abone)")
                            st.write(f"**İzlenme:** {v['views']:,} | **🔥 Fırsat Puanı:** {v['score']:.2f}")
                            st.markdown(f"[Videoyu ve Başlığı İncele]({v['link']})")
                            st.markdown("---")
                    else:
                        st.warning("Seçtiğiniz filtreleri geçen video bulunamadı. Lütfen 'Minimum Fırsat Puanı' kaydırıcısını biraz düşürerek tekrar deneyin.")
                else:
                     st.error("Kanal detayları alınırken bir sorun oluştu.")
        else:
            st.error("Arama verileri çekilirken YouTube bir hata fırlattı.")
