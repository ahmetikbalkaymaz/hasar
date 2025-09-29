import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium, folium_static
from datetime import datetime
import json

# Sayfa yapılandırması
st.set_page_config(
    page_title="Yapay Zeka Destekli Hasar Paneli",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS stillerini ekle
st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }
    .stButton > button {
        width: 100%;
    }
    .incident-card {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        background-color: #f8f9fa;
        border-left: 4px solid;
        cursor: pointer;
        transition: all 0.3s;
    }
    .incident-card:hover {
        background-color: #e9ecef;
        transform: translateX(2px);
    }
    .high-impact {
        border-left-color: #dc3545;
    }
    .medium-impact {
        border-left-color: #ffc107;
    }
    .low-impact {
        border-left-color: #28a745;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Veri hazırlama fonksiyonu
@st.cache_data
def load_data():
    """Hasar verilerini yükle"""
    data = [
        {"id": 63, "tarih": "28.09.2025", "il": "Erzurum", "ilce": "Aziziye", "konum": "Erzurum 1. OSB", 
         "tesisAdi": "Şahika Boya Üretim Tesisleri", "sektor": "Kimya / Boya", "olayTuru": "Yangın", 
         "etkiSeviyesi": "Yüksek", "dogrulamaYontemi": "A", "dogrulukOrani": 95, "lat": 39.9510, "lng": 41.1920, 
         "ozet": "Boya üretim tesisinin depo bölümünde çıkan yangın, bitişikte bulunan terlik hammaddesi (EVA) deposuna da sıçradı."},
        {"id": 62, "tarih": "28.09.2025", "il": "Adana", "ilce": "Yüreğir", "konum": "Zağarlı Mahallesi", 
         "tesisAdi": "FBY Enerji Üretim (Yüreğir BES)", "sektor": "Enerji / Biyokütle", "olayTuru": "Yangın", 
         "etkiSeviyesi": "Orta", "dogrulamaYontemi": "A", "dogrulukOrani": 90, "lat": 36.9535, "lng": 35.4182, 
         "ozet": "Tarımsal atıklardan enerji üreten biyokütle santralinin açık alandaki atık depolama sahasında büyük bir yangın çıktı."},
        {"id": 61, "tarih": "28.09.2025", "il": "Karabük", "ilce": "Safranbolu", "konum": "Safranbolu Sanayi Sitesi", 
         "tesisAdi": "Ahmet Sevigen Kereste Atölyesi", "sektor": "Kereste", "olayTuru": "Yangın", 
         "etkiSeviyesi": "Orta", "dogrulamaYontemi": "B", "dogrulukOrani": 85, "lat": 41.2580, "lng": 32.6715, 
         "ozet": "Sanayi sitesi içerisinde faaliyet gösteren bir kereste atölyesinde, depolanan ahşap malzemelerin ve talaşların tutuşmasıyla yangın çıktı."},
        {"id": 60, "tarih": "29.09.2025", "il": "Karaman", "ilce": "Merkez", "konum": "Karaman OSB", 
         "tesisAdi": "Sosyete Un Gıda Sanayi", "sektor": "Gıda / Un", "olayTuru": "Yangın", 
         "etkiSeviyesi": "Düşük", "dogrulamaYontemi": "B", "dogrulukOrani": 75, "lat": 37.2050, "lng": 33.2590, 
         "ozet": "Bir un fabrikasının üretim tesisinden ayrı, arka bölümde bulunan hurda ve atık depolama alanında yangın çıktı."},
        {"id": 59, "tarih": "25.09.2025", "il": "Zonguldak", "ilce": "Kilimli", "konum": "Çatalağzı, ZETES Santrali", 
         "tesisAdi": "Eren Enerji Termik Santrali", "sektor": "Enerji / Termik Santral", 
         "olayTuru": "Kazan/Boiler Buhar Hattı Patlağı", "etkiSeviyesi": "Yüksek", "dogrulamaYontemi": "A", 
         "dogrulukOrani": 96, "lat": 41.5167, "lng": 31.9, 
         "ozet": "Termik santralin ana kazanlarından birine giden yüksek basınçlı buhar hattında meydana gelen patlama sonucu 3 işçi ağır yaralandı."}
    ]
    
    # Daha fazla veri eklenebilir, örnek olarak kısa tuttum
    return pd.DataFrame(data)

def create_map(df, selected_id=None):
    """Folium haritası oluştur"""
    m = folium.Map(location=[39.0, 35.0], zoom_start=6, tiles='CartoDB positron')
    
    for idx, row in df.iterrows():
        color = {'Yüksek': 'red', 'Orta': 'orange', 'Düşük': 'green'}.get(row['etkiSeviyesi'], 'gray')
        icon = {'Yangın': 'fire', 'Patlama': 'bomb'}.get(row['olayTuru'].split('/')[0].strip(), 'info-sign')
        
        is_selected = selected_id and row['id'] == selected_id
        
        folium.Marker(
            location=[row['lat'], row['lng']],
            popup=folium.Popup(
                f"<b>{row['tesisAdi']}</b><br>"
                f"{row['olayTuru']}<br>"
                f"<i>{row['tarih']}</i>",
                max_width=300
            ),
            tooltip=row['tesisAdi'],
            icon=folium.Icon(color=color, icon=icon, prefix='glyphicon' if icon != 'fire' else 'fa'),
        ).add_to(m)
        
        if is_selected:
            folium.CircleMarker(
                location=[row['lat'], row['lng']],
                radius=20,
                color='blue',
                fill=False,
                weight=3,
                opacity=0.8
            ).add_to(m)
    
    return m

def main():
    # Başlık
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <h1>⚠️ Yapay Zeka Destekli Hasar Paneli</h1>
        <p style='color: #666;'>Türkiye: Son 3 Aylık Endüstriyel & Enerji Hasarları Analizi</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Veri yükleme
    df = load_data()
    
    # Sidebar - Filtreler
    with st.sidebar:
        st.markdown("## 🔍 Filtreler")
        
        # İl filtresi
        selected_il = st.selectbox(
            "İl", 
            options=["Tümü"] + sorted(df['il'].unique().tolist()),
            key="il_filter"
        )
        
        # Sektör filtresi
        sectors = df['sektor'].str.split(' / ').str[0].unique()
        selected_sektor = st.selectbox(
            "Sektör",
            options=["Tümü"] + sorted(sectors.tolist()),
            key="sektor_filter"
        )
        
        # Olay türü filtresi
        selected_olay = st.selectbox(
            "Olay Türü",
            options=["Tümü"] + sorted(df['olayTuru'].unique().tolist()),
            key="olay_filter"
        )
        
        # Etki seviyesi filtresi
        selected_etki = st.selectbox(
            "Etki Seviyesi",
            options=["Tümü", "Yüksek", "Orta", "Düşük"],
            key="etki_filter"
        )
        
        # Filtreleri temizle butonu
        if st.button("🔄 Filtreleri Temizle", use_container_width=True):
            st.session_state.il_filter = "Tümü"
            st.session_state.sektor_filter = "Tümü"
            st.session_state.olay_filter = "Tümü"
            st.session_state.etki_filter = "Tümü"
            st.rerun()
    
    # Filtreleme
    filtered_df = df.copy()
    if selected_il != "Tümü":
        filtered_df = filtered_df[filtered_df['il'] == selected_il]
    if selected_sektor != "Tümü":
        filtered_df = filtered_df[filtered_df['sektor'].str.startswith(selected_sektor)]
    if selected_olay != "Tümü":
        filtered_df = filtered_df[filtered_df['olayTuru'] == selected_olay]
    if selected_etki != "Tümü":
        filtered_df = filtered_df[filtered_df['etkiSeviyesi'] == selected_etki]
    
    # Sonuç sayısı
    st.info(f"📊 {len(filtered_df)} sonuç bulundu.")
    
    # Ana içerik alanı
    tab1, tab2, tab3, tab4 = st.tabs(["📍 Harita", "📋 Liste", "📊 İstatistikler", "🔎 Detaylar"])
    
    with tab1:
        st.markdown("### 🗺️ Hasar Konumları Haritası")
        m = create_map(filtered_df)
        folium_static(m, width=None, height=500)
    
    with tab2:
        st.markdown("### 📋 Hasar Listesi (En Yeni)")
        
        # Liste görünümü
        for idx, row in filtered_df.iterrows():
            impact_class = {
                'Yüksek': 'high-impact',
                'Orta': 'medium-impact',
                'Düşük': 'low-impact'
            }.get(row['etkiSeviyesi'], '')
            
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    if st.button(f"🏭 {row['tesisAdi']}", key=f"btn_{row['id']}", use_container_width=True):
                        st.session_state.selected_incident = row['id']
                with col2:
                    st.write(f"📅 {row['tarih']}")
                with col3:
                    impact_emoji = {'Yüksek': '🔴', 'Orta': '🟡', 'Düşük': '🟢'}.get(row['etkiSeviyesi'], '⚪')
                    st.write(f"{impact_emoji} {row['etkiSeviyesi']}")
                
                st.caption(f"📍 {row['il']}, {row['ilce']} | {row['olayTuru']}")
                st.divider()
    
    with tab3:
        st.markdown("### 📊 Öne Çıkan Analizler")
        
        # Metrikler
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Toplam Vaka", len(filtered_df))
        with col2:
            high_impact = len(filtered_df[filtered_df['etkiSeviyesi'] == 'Yüksek'])
            st.metric("Yüksek Etkili", high_impact)
        with col3:
            most_freq = filtered_df['olayTuru'].mode()[0] if not filtered_df.empty else "-"
            st.metric("En Sık Olay", most_freq)
        with col4:
            most_sector = filtered_df['sektor'].str.split(' / ').str[0].mode()[0] if not filtered_df.empty else "-"
            st.metric("En Riskli Sektör", most_sector)
        
        # Grafikler
        if not filtered_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Sektöre göre dağılım
                sector_counts = filtered_df['sektor'].value_counts().head(10)
                fig1 = px.bar(
                    x=sector_counts.values, 
                    y=sector_counts.index, 
                    orientation='h',
                    title="Sektörlere Göre Hasar Sayısı (Top 10)",
                    labels={'x': 'Hasar Sayısı', 'y': 'Sektör'},
                    color_discrete_sequence=['#6366f1']
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # Etki seviyesine göre dağılım
                impact_counts = filtered_df['etkiSeviyesi'].value_counts()
                fig2 = px.pie(
                    values=impact_counts.values,
                    names=impact_counts.index,
                    title="Etki Seviyelerine Göre Dağılım",
                    color_discrete_map={'Yüksek': '#ef4444', 'Orta': '#f59e0b', 'Düşük': '#22c55e'}
                )
                st.plotly_chart(fig2, use_container_width=True)
    
    with tab4:
        st.markdown("### 🔎 Olay Detayları")
        
        if 'selected_incident' in st.session_state:
            selected = filtered_df[filtered_df['id'] == st.session_state.selected_incident].iloc[0]
            
            # Detay kartı
            st.markdown(f"""
            <div style='background: #f8f9fa; padding: 2rem; border-radius: 0.75rem; border-left: 5px solid 
                {"#dc3545" if selected['etkiSeviyesi'] == 'Yüksek' else "#ffc107" if selected['etkiSeviyesi'] == 'Orta' else "#28a745"};'>
                <h2>{selected['tesisAdi']}</h2>
                <p><strong>📍 Konum:</strong> {selected['konum']}, {selected['ilce']}/{selected['il']}</p>
                <p><strong>📅 Tarih:</strong> {selected['tarih']}</p>
                <p><strong>⚠️ Olay Türü:</strong> {selected['olayTuru']}</p>
                <p><strong>🏭 Sektör:</strong> {selected['sektor']}</p>
                <p><strong>📊 Etki Seviyesi:</strong> {selected['etkiSeviyesi']}</p>
                <p><strong>✅ Doğruluk Oranı:</strong> %{selected['dogrulukOrani']}</p>
                <hr>
                <p><strong>📝 Olay Özeti:</strong></p>
                <p>{selected['ozet']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Detay haritası
            st.markdown("#### 📍 Konum Detayı")
            detail_map = create_map(filtered_df[filtered_df['id'] == st.session_state.selected_incident], 
                                  selected_id=st.session_state.selected_incident)
            folium_static(detail_map, width=None, height=400)
        else:
            st.info("📌 Detayları görüntülemek için Liste sekmesinden bir olay seçin.")

if __name__ == "__main__":
    main()