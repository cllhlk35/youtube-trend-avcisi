import streamlit as st
import requests

# Web sitesinin başlığı ve arayüz ayarları
st.set_page_config(page_title="Global YouTube Fırsat Avcısı", page_icon="🎯", layout="wide")
st.title("🎯 Global YouTube Fırsat Avcısı")
st.write("Bu araç sadece trendleri değil, küçük kanalların devasa izlenmeler aldığı **'Düşük Rekabet / Yüksek Hacim'** fırsatlarını bulur.")

# API ANAHTARINIZI BURAYA YAPIŞTIRIN
API_KEY = "AIzaSyCT5pvnI5IpLI4gffjLjL8pTQgodjuG_HY"

# Hedef Ülkeler
countries = {
    "Amerika Birleşik Devletleri": "US", 
    "Birleşik Krallık": "GB",
    "Almanya": "DE", 
    "Türkiye": "TR", 
    "İtalya": "IT",     
    "İspanya": "ES"     
}

selected_country_name = st.selectbox("Analiz Etmek İstediğiniz Ülkeyi Seçin:", list(countries.keys()))
selected_country_code = countries[selected_country_name]

if st.button("🚀 Fırsatları Analiz Et"):
    
    video_url = f"https://www.googleapis.com/youtube/v3/videos"
    video_params = {
        'part': 'snippet,contentDetails,statistics',
        'chart': 'mostPopular',
        'regionCode': selected_country_code,
        'maxResults': 50, # Veri havuzunu büyüttük
        'key': API_KEY
    }
    
    with st.spinner(f"{selected_country_name} pazarındaki trendler taranıyor ve rekabet analizi yapılıyor..."):
        vid_res = requests.get(video_url, params=video_params)
        
        if vid_res.status_code == 200:
            video_data = vid_res.json().get('items', [])
            
            # 1. Adım: Trend olan kanalların ID'lerini topla
            channel_ids = [v['snippet']['channelId'] for v in video_data]
            channel_ids_str = ",".join(list(set(channel_ids))) 
            
            # 2. Adım: Bu kanalların abone sayılarını bul
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
                    # Abonesi gizli olanları 1 kabul ediyoruz ki sistem çökmesin
                    sub_counts[c['id']] = int(c['statistics'].get('subscriberCount', 1)) 
                
                # 3. Adım: Fırsat Puanı Hesaplama ve Filtreleme
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
                    
                    # FIRSAT ALGORİTMASI: İzlenme / Abone Sayısı
                    opportunity_score = views / subs
                    
                    # Sadece belirli bir fırsat puanının üzerindeki "gerçek" fırsatları al
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
                
                # En yüksek fırsat puanından en düşüğe doğru sırala
                analyzed_videos.sort(key=lambda x: x['score'], reverse=True)
                
                st.success("Altın Fırsatlar Başarıyla Bulundu! 🏆")
                st.info("💡 **Nasıl Okunmalı?** Aşağıdaki liste sıradan bir trend listesi değildir. En üstteki videolar, abone sayısı çok az olmasına rağmen kendi çapından katbekat fazla izlenme almayı başarmış (Düşük Rekabet / Yüksek Hacim) gizli potansiyellerdir. Bu videoların başlık (anahtar kelime) ve formatlarını inceleyerek kendi stratejinizi kurabilirsiniz.")
                
                # En iyi 15 fırsatı ekrana yazdır
                for idx, v in enumerate(analyzed_videos[:15]): 
                    st.subheader(f"#{idx+1} {v['title']}")
                    st.write(f"**Format:** {v['format']} | **Kanal:** {v['channel']} ({v['subs']:,} Abone)")
                    st.write(f"**İzlenme:** {v['views']:,} | **🔥 Fırsat Puanı:** {v['score']:.1f}")
                    st.markdown(f"[Videoyu ve Başlığı İncele]({v['link']})")
                    st.markdown("---")
            else:
                 st.error("Kanal verileri çekilirken hata oluştu.")
        else:
            st.error("Video verileri çekilirken hata oluştu.")
