import streamlit as st
import requests
from datetime import datetime, timedelta

# Arayüz ayarları
st.set_page_config(page_title="Global YouTube Fırsat Avcısı", page_icon="🎯", layout="wide")
st.title("🎯 Global YouTube Fırsat Avcısı (Pro)")
st.write("Seçtiğiniz nişte **son 30 günün** en çok izlenen videolarını tarar. Aşağıdaki ayarları kullanarak kendi fırsat kriterlerinizi belirleyin.")

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

categories = {
    "Eğlence (Entertainment)": "24",
    "Oyun (Gaming)": "20",
    "Eğitim (Education)": "27",
    "Kişiler ve Bloglar (People & Blogs)": "22",
    "Nasıl Yapılır ve Stil (Howto & Style)": "26",
    "Bilim ve Teknoloji (Science & Technology)": "28",
    "Komedi (Comedy)": "23",
    "Spor (Sports)": "17",
    "Evcil Hayvanlar ve Hayvanlar (Pets & Animals)": "15"
}

# 1. Satır: Ülke ve Kategori Seçimi
col1, col2 = st.columns(2)
with col1:
    selected_country_name = st.selectbox("🌍 Hedef Ülke:", list(countries.keys()))
    selected_country_code = countries[selected_country_name]

with col2:
    selected_category_name = st.selectbox("📂 İçerik Kategorisi:", list(categories.keys()))
    selected_category_id = categories[selected_category_name]

st.markdown("---")
st.subheader("⚙️ Fırsat Filtreleri")

# 2. Satır: Kullanıcı Kontrolündeki Slider'lar (Kaydırıcılar)
col3, col4 = st.columns(2)
with col3:
    # Kullanıcı minimum izlenmeyi seçecek (Varsayılan: 10.000)
    min_views = st.slider("Minimum İzlenme Sayısı:", min_value=1000, max_value=1000000, value=10000, step=5000)
with col4:
    # Kullanıcı minimum fırsat puanını seçecek (Varsayılan: 0.1)
    min_score = st.slider("Minimum Fırsat Puanı (İzlenme/Abone Oranı):", min_value=0.0, max_value=5.0, value=0.1, step=0.1)

st.markdown("---")

if st.button("🚀 Fırsatları Analiz Et"):
    
    thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat() + "Z"
    
    search_url = "https://www.googleapis.com/youtube/v3/search"
    search_params = {
        'part': 'snippet',
        'type': 'video',
        'videoCategoryId': selected_category_id,
        'regionCode': selected_country_code,
        'order': 'viewCount', 
        'publishedAfter': thirty_days_ago, 
        'maxResults': 50, # Veri havuzunu 50'ye çıkardık
        'key': API_KEY
    }
    
    with st.spinner(f"Son 30 günün {selected_category_name} verileri taranıyor..."):
        search_res = requests.get(search_url, params=search_params)
        
        if search_res.status_code == 200:
            search_data = search_res.json().get('items', [])
            
            if not search_data:
                st.warning("Bu kategoride taze video bulunamadı.")
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
                        
                        # İŞTE YENİ FİLTRE MANTIĞI: Kullanıcının belirlediği puan ve izlenmeyi geçiyorsa ekrana bas
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
                        st.success(f"{len(analyzed_videos)} Adet Fırsat Bulundu! 🏆")
                        for idx, v in enumerate(analyzed_videos): 
                            st.subheader(f"#{idx+1} {v['title']}")
                            st.write(f"**Format:** {v['format']} | **Kanal:** {v['channel']} ({v['subs']:,} Abone)")
                            st.write(f"**İzlenme:** {v['views']:,} | **🔥 Fırsat Puanı:** {v['score']:.2f}")
                            st.markdown(f"[Videoyu ve Başlığı İncele]({v['link']})")
                            st.markdown("---")
                    else:
                        st.warning("Seçtiğiniz filtreleri geçen video bulunamadı. Lütfen 'Minimum Fırsat Puanı' kaydırıcısını biraz daha sola çekerek (düşürerek) tekrar deneyin.")
                else:
                     st.error("Kanal detayları alınırken bir sorun oluştu.")
        else:
            st.error("Arama verileri çekilirken YouTube bir hata fırlattı.")
