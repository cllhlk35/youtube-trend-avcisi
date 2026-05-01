import streamlit as st
import requests

st.set_page_config(page_title="Global YouTube Fırsat Avcısı", page_icon="🎯", layout="wide")
st.title("🎯 Global YouTube Fırsat Avcısı")
st.write("Müzik kliplerinden arındırılmış, sadece hedeflediğiniz kategorilerdeki **'Düşük Rekabet / Yüksek Hacim'** fırsatlarını bulur.")

# API ANAHTARINIZI BURAYA YAPIŞTIRIN
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

col1, col2 = st.columns(2)
with col1:
    selected_country_name = st.selectbox("🌍 Hedef Ülke:", list(countries.keys()))
    selected_country_code = countries[selected_country_name]

with col2:
    selected_category_name = st.selectbox("📂 İçerik Kategorisi:", list(categories.keys()))
    selected_category_id = categories[selected_category_name]

if st.button("🚀 Fırsatları Analiz Et"):
    
    video_url = f"https://www.googleapis.com/youtube/v3/videos"
    video_params = {
        'part': 'snippet,contentDetails,statistics',
        'chart': 'mostPopular',
        'regionCode': selected_country_code,
        'videoCategoryId': selected_category_id, 
        'maxResults': 50,
        'key': API_KEY
    }
    
    with st.spinner(f"{selected_country_name} pazarında {selected_category_name} kategorisi taranıyor..."):
        vid_res = requests.get(video_url, params=video_params)
        
        if vid_res.status_code == 200:
            video_data = vid_res.json().get('items', [])
            
            if not video_data:
                st.warning("Bu kategoride şu an yeterli trend veri bulunamadı. Lütfen başka bir kategori veya ülke deneyin.")
            else:
                channel_ids = [v['snippet']['channelId'] for v in video_data]
                channel_ids_str = ",".join(list(set(channel_ids))) 
                
                channel_url = f"https://www.googleapis.com/youtube/v3/channels"
                channel_params = {
                    'part': 'statistics',
                    'id': channel_ids_str,
                    'key': API_KEY
                }
                chan_res = requests.get(channel_url, params=channel_params)
                
                if chan_res.status_code == 200:
                    chan_data = chan_res.json().get('items', [])
                    sub_counts = {}
                    for c in chan_data:
                        sub_counts[c['id']] = int(c['statistics'].get('subscriberCount', 1)) 
                    
                    analyzed_videos = []
                    for video in video_data:
                        title = video['snippet']['title']
                        views = int(video['statistics'].get('viewCount', 0))
                        duration = video['contentDetails']['duration']
                        channel_title = video['snippet']['channelTitle']
                        channel_id = video['snippet']['channelId']
                        video_id = video['id']
                        
                        subs = sub_counts.get(channel_id, 1)
                        if subs == 0: subs = 1
                        
                        opportunity_score = views / subs
                        
                        if opportunity_score > 0.5: 
                            if 'H' not in duration and 'M' not in duration:
                                video_format = "📱 Shorts (Dikey)"
                            else:
                                video_format = "📺 Uzun Video (Yatay)"
                                
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
                        st.success(f"{selected_category_name} İçin Altın Fırsatlar Bulundu! 🏆")
                        st.info("💡 **Nasıl Okunmalı?** Aşağıdaki videolar abone sayısına oranla devasa izlenmiş (Düşük Rekabet / Yüksek Hacim) potansiyellerdir. Müzik videoları filtrelenmiştir.")
                        
                        for idx, v in enumerate(analyzed_videos[:15]): 
                            st.subheader(f"#{idx+1} {v['title']}")
                            st.write(f"**Format:** {v['format']} | **Kanal:** {v['channel']} ({v['subs']:,} Abone)")
                            st.write(f"**İzlenme:** {v['views']:,} | **🔥 Fırsat Puanı:** {v['score']:.1f}")
                            st.markdown(f"[Videoyu ve Başlığı İncele]({v['link']})")
                            st.markdown("---")
                    else:
                        st.warning("Bu kategoride şu an için belirlediğimiz fırsat puanını aşan video bulunamadı. Daha niş kategorilere bakabilirsiniz.")
                else:
                     st.error("Kanal verileri çekilirken hata oluştu.")
                     st.code(chan_res.text)
        else:
            st.error(f"YouTube bir hata fırlattı! Hata Kodu: {vid_res.status_code}")
            st.code(vid_res.text) # İşte YouTube'un gerçek itirafı burada yazacak
