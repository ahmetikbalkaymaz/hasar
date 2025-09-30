import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
from datetime import datetime
import json

# Sayfa yapılandırması
st.set_page_config(
    page_title="Yapay Zeka Destekli Hasar Paneli",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS stillerini ekle - HTML versiyonuna tam uyumlu
st.markdown("""
<style>
    /* Genel stil ayarları */
    .stApp {
        background-color: #f0f2f5;
    }
    
    /* Ana grid düzeni için */
    [data-testid="stHorizontalBlock"] {
        gap: 1rem;
    }
    
    /* Sol panel (liste) için */
    .incident-list-container {
        background: white;
        border-radius: 0.5rem;
        padding: 0.5rem;
        height: calc(100vh - 200px);
        overflow-y: auto;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    
    /* Hasar kartları */
    .incident-card {
        padding: 0.75rem;
        border-left: 4px solid;
        background: white;
        margin-bottom: 0.25rem;
        border-radius: 0 0.375rem 0.375rem 0;
        cursor: pointer;
        transition: all 0.15s;
    }
    
    .incident-card:hover {
        background-color: #eef2ff;
        transform: translateX(-4px);
    }
    
    .incident-card.active-item {
        background-color: #eef2ff;
        border-left-color: #4f46e5;
        transform: translateX(-4px);
    }
    
    .incident-high { border-left-color: #ef4444; }
    .incident-medium { border-left-color: #f59e0b; }
    .incident-low { border-left-color: #22c55e; }
    
    /* Metrik kartları */
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    /* Grafik container */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Detay panel */
    .details-panel {
        background: white;
        padding: 2rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Scrollbar özelleştirme */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; }
    ::-webkit-scrollbar-thumb { 
        background: #c5c5c5; 
        border-radius: 4px; 
    }
    ::-webkit-scrollbar-thumb:hover { background: #a3a3a3; }
    
    /* Butonlar */
    .stButton > button {
        width: 100%;
        background: transparent;
        border: none;
        padding: 0;
        text-align: left;
    }
    
    /* Selectbox özelleştirme */
    .stSelectbox > div > div {
        background: white;
        border: 1px solid #d1d5db;
        border-radius: 0.375rem;
    }
    
    /* Başlık alanı */
    .header-container {
        background: white;
        padding: 1rem 2rem;
        margin: -3rem -3rem 1rem -3rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Filtre bar */
    .filter-bar {
        background: rgba(255,255,255,0.8);
        backdrop-filter: blur(10px);
        padding: 0.75rem 1rem;
        margin-bottom: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Session state
if 'selected_id' not in st.session_state:
    st.session_state.selected_id = None
if 'show_details' not in st.session_state:
    st.session_state.show_details = False

# Veri yükleme - sadece 5 örnek
@st.cache_data
def load_data():
    data = [
        {
            "id": 63, "tarih": "28.09.2025", "il": "Erzurum", "ilce": "Aziziye", 
            "konum": "Erzurum 1. OSB", "tesisAdi": "Şahika Boya Üretim Tesisleri", 
            "sektor": "Kimya / Boya", "olayTuru": "Yangın", "etkiSeviyesi": "Yüksek",
            "dogrulamaYontemi": "A", "dogrulukOrani": 95, "lat": 39.9510, "lng": 41.1920,
            "ozet": "Boya üretim tesisinin depo bölümünde çıkan yangın, bitişikte bulunan terlik hammaddesi deposuna da sıçradı.",
            "etki": "İki farklı riskin (kimyasal ve plastik) birleştiği büyük ve komplike bir hasar dosyasıdır.",
            "haberler": ["AA: 'Erzurum OSB'de boya fabrikasında yangın.'", "Erzurum Günebakış: 'Yangın yandaki depoya da sıçradı.'"]
        },
        {
            "id": 62, "tarih": "28.09.2025", "il": "Adana", "ilce": "Yüreğir",
            "konum": "Zağarlı Mahallesi", "tesisAdi": "FBY Enerji Üretim (Yüreğir BES)",
            "sektor": "Enerji / Biyokütle", "olayTuru": "Yangın", "etkiSeviyesi": "Orta",
            "dogrulamaYontemi": "A", "dogrulukOrani": 90, "lat": 36.9535, "lng": 35.4182,
            "ozet": "Tarımsal atıklardan enerji üreten biyokütle santralinin açık alandaki atık depolama sahasında büyük bir yangın çıktı.",
            "etki": "Santralin yakıt stoğu önemli ölçüde yanmıştır. İş durması kaçınılmazdır.",
            "haberler": ["İHA: 'Adana'da biyokütle enerji santralinde yangın.'"]
        },
        {
            "id": 61, "tarih": "28.09.2025", "il": "Karabük", "ilce": "Safranbolu",
            "konum": "Safranbolu Sanayi Sitesi", "tesisAdi": "Ahmet Sevigen Kereste Atölyesi",
            "sektor": "Kereste", "olayTuru": "Yangın", "etkiSeviyesi": "Orta",
            "dogrulamaYontemi": "B", "dogrulukOrani": 85, "lat": 41.2580, "lng": 32.6715,
            "ozet": "Sanayi sitesinde kereste atölyesinde yangın çıktı. Atölye kullanılamaz hale geldi.",
            "etki": "Atölye için total bir hasar söz konusudur.",
            "haberler": ["BirGün: 'Safranbolu sanayi sitesinde kereste atölyesi yandı.'"]
        },
        {
            "id": 59, "tarih": "25.09.2025", "il": "Zonguldak", "ilce": "Kilimli",
            "konum": "Çatalağzı, ZETES Santrali", "tesisAdi": "Eren Enerji Termik Santrali",
            "sektor": "Enerji / Termik Santral", "olayTuru": "Kazan/Boiler Patlağı",
            "etkiSeviyesi": "Yüksek", "dogrulamaYontemi": "A", "dogrulukOrani": 96,
            "lat": 41.5167, "lng": 31.9,
            "ozet": "Termik santralin buhar hattında meydana gelen patlama sonucu 3 işçi ağır yaralandı.",
            "etki": "Santralin bir ünitesi devre dışı. Ciddi iş durması ve kar kaybı hasarı.",
            "haberler": ["Z Haber: 'Eren Enerji'de buhar kazanı patladı: 3 ağır yaralı.'"]
        },
        {
            "id": 60, "tarih": "29.09.2025", "il": "Karaman", "ilce": "Merkez",
            "konum": "Karaman OSB", "tesisAdi": "Sosyete Un Gıda Sanayi",
            "sektor": "Gıda / Un", "olayTuru": "Yangın", "etkiSeviyesi": "Düşük",
            "dogrulamaYontemi": "B", "dogrulukOrani": 75, "lat": 37.2050, "lng": 33.2590,
            "ozet": "Un fabrikasının atık depolama alanında yangın çıktı. Ana tesise sıçramadan söndürüldü.",
            "etki": "Üretimi doğrudan etkilemeyen, düşük şiddetli bir hasar.",
            "haberler": ["Karamandan.com: 'OSB'de fabrikanın hurdalığında yangın paniği.'"]
        }
    ]
    return pd.DataFrame(data)

def create_map(df, selected_id=None):
    """Harita oluştur"""
    m = folium.Map(location=[39.0, 35.0], zoom_start=6, tiles='CartoDB positron')
    
    for _, row in df.iterrows():
        color_map = {'Yüksek': 'red', 'Orta': 'orange', 'Düşük': 'green'}
        icon_map = {'Yangın': 'fire', 'Kazan/Boiler Patlağı': 'exclamation-triangle'}
        
        color = color_map.get(row['etkiSeviyesi'], 'gray')
        icon = icon_map.get(row['olayTuru'].split('/')[0], 'info-sign')
        
        # Seçili öğeyi vurgula
        if selected_id and row['id'] == selected_id:
            folium.CircleMarker(
                [row['lat'], row['lng']],
                radius=15,
                color='blue',
                fill=False,
                weight=3
            ).add_to(m)
        
        folium.Marker(
            [row['lat'], row['lng']],
            popup=f"<b>{row['tesisAdi']}</b><br>{row['olayTuru']}<br>{row['tarih']}",
            tooltip=row['tesisAdi'],
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        ).add_to(m)
    
    return m

# Ana uygulama
def main():
    # Veri yükle
    df = load_data()
    
    # BAŞLIK
    st.markdown("""
    <div class="header-container">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="color: #4f46e5; font-size: 2rem;">⚠️</div>
            <div>
                <h1 style="margin: 0; font-size: 1.5rem; font-weight: bold;">Yapay Zeka Destekli Hasar Paneli</h1>
                <p style="margin: 0; color: #6b7280; font-size: 0.875rem;">Türkiye: Son 3 Aylık Endüstriyel & Enerji Hasarları Analizi</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # FİLTRELER
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    col1, col2, col3, col4, col5, col6 = st.columns([0.5, 1, 1, 1, 1, 0.8])
    
    with col1:
        st.markdown("**Filtreler:**")
    with col2:
        il_filter = st.selectbox("", ["Tüm İller"] + sorted(df['il'].unique().tolist()), key="il_filter")
    with col3:
        sectors = df['sektor'].str.split(' / ').str[0].unique()
        sektor_filter = st.selectbox("", ["Tüm Sektörler"] + sorted(sectors.tolist()), key="sektor_filter")
    with col4:
        olay_filter = st.selectbox("", ["Tüm Olay Türleri"] + sorted(df['olayTuru'].unique().tolist()), key="olay_filter")
    with col5:
        etki_filter = st.selectbox("", ["Tüm Etki Seviyeleri", "Yüksek", "Orta", "Düşük"], key="etki_filter")
    with col6:
        if st.button("🔄 Temizle", use_container_width=True):
            st.session_state.il_filter = "Tüm İller"
            st.session_state.sektor_filter = "Tüm Sektörler"
            st.session_state.olay_filter = "Tüm Olay Türleri"
            st.session_state.etki_filter = "Tüm Etki Seviyeleri"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filtreleme
    filtered_df = df.copy()
    if il_filter != "Tüm İller":
        filtered_df = filtered_df[filtered_df['il'] == il_filter]
    if sektor_filter != "Tüm Sektörler":
        filtered_df = filtered_df[filtered_df['sektor'].str.startswith(sektor_filter)]
    if olay_filter != "Tüm Olay Türleri":
        filtered_df = filtered_df[filtered_df['olayTuru'] == olay_filter]
    if etki_filter != "Tüm Etki Seviyeleri":
        filtered_df = filtered_df[filtered_df['etkiSeviyesi'] == etki_filter]
    
    # Sonuç sayısı
    st.info(f"📊 {len(filtered_df)} sonuç bulundu.")
    
    # ANA İÇERİK - 2 kolon (sol: liste, sağ: içerik)
    col_left, col_right = st.columns([1, 2.5])
    
    # SOL PANEL - Hasar Listesi
    with col_left:
        st.markdown("### 📋 Hasar Listesi (En Yeni)")
        st.markdown('<div class="incident-list-container">', unsafe_allow_html=True)
        
        if filtered_df.empty:
            st.write("Filtre kriterlerine uygun sonuç bulunamadı.")
        else:
            for _, row in filtered_df.iterrows():
                impact_class = {
                    'Yüksek': 'incident-high',
                    'Orta': 'incident-medium',
                    'Düşük': 'incident-low'
                }.get(row['etkiSeviyesi'], '')
                
                active_class = "active-item" if st.session_state.selected_id == row['id'] else ""
                
                if st.button(f"🏭 **{row['tesisAdi']}**", key=f"btn_{row['id']}"):
                    st.session_state.selected_id = row['id']
                    st.session_state.show_details = True
                    st.rerun()
                
                st.markdown(f"""
                <div class="incident-card {impact_class} {active_class}">
                    <div style="display: flex; justify-content: space-between;">
                        <strong>{row['tesisAdi']}</strong>
                        <small>{row['tarih']}</small>
                    </div>
                    <div style="color: #6b7280; font-size: 0.875rem;">
                        {row['il']}, {row['ilce']}<br>
                        {row['olayTuru']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # SAĞ PANEL - Harita ve Analizler
    with col_right:
        if st.session_state.show_details and st.session_state.selected_id:
            # DETAY PANELİ
            selected = filtered_df[filtered_df['id'] == st.session_state.selected_id].iloc[0]
            
            # Kapat butonu
            if st.button("✖️ Kapat", key="close_details"):
                st.session_state.show_details = False
                st.session_state.selected_id = None
                st.rerun()
            
            st.markdown(f"""
            <div class="details-panel">
                <h2>{selected['tesisAdi']}</h2>
                <p><strong>📍 Konum:</strong> {selected['konum']}, {selected['ilce']}/{selected['il']}</p>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1rem 0;">
                    <div style="background: #f9fafb; padding: 1rem; border-radius: 0.5rem;">
                        <p style="color: #6b7280; font-size: 0.875rem; margin: 0;">Tarih</p>
                        <p style="font-size: 1.25rem; font-weight: bold; margin: 0;">{selected['tarih']}</p>
                    </div>
                    <div style="background: #f9fafb; padding: 1rem; border-radius: 0.5rem;">
                        <p style="color: #6b7280; font-size: 0.875rem; margin: 0;">Olay Türü</p>
                        <p style="font-size: 1.25rem; font-weight: bold; margin: 0;">{selected['olayTuru']}</p>
                    </div>
                    <div style="background: #f9fafb; padding: 1rem; border-radius: 0.5rem;">
                        <p style="color: #6b7280; font-size: 0.875rem; margin: 0;">Sektör</p>
                        <p style="font-size: 1.25rem; font-weight: bold; margin: 0;">{selected['sektor']}</p>
                    </div>
                    <div style="background: #f9fafb; padding: 1rem; border-radius: 0.5rem;">
                        <p style="color: #6b7280; font-size: 0.875rem; margin: 0;">Doğruluk Oranı</p>
                        <p style="font-size: 1.25rem; font-weight: bold; margin: 0;">%{selected['dogrulukOrani']}</p>
                    </div>
                </div>
                <div style="background: #eff6ff; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
                    <h4>📝 Olay Özeti</h4>
                    <p>{selected['ozet']}</p>
                </div>
                <div>
                    <h4>💥 Direkt Hasar Etkisi</h4>
                    <p>{selected['etki']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Detay haritası
            st.markdown("#### 📍 Konum Detayı")
            detail_map = create_map(filtered_df[filtered_df['id'] == st.session_state.selected_id], st.session_state.selected_id)
            folium_static(detail_map, height=400)
            
        else:
            # ANALİZ PANELİ
            # Harita
            st.markdown("### 🗺️ Hasar Konumları Haritası")
            m = create_map(filtered_df, st.session_state.selected_id)
            folium_static(m, height=450)
            
            # Metrikler
            st.markdown("### 📊 Öne Çıkan Analizler")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div class="metric-container" style="background: #eff6ff;">
                    <p style="color: #3730a3; font-size: 0.875rem; font-weight: 600;">Toplam Vaka</p>
                    <p style="font-size: 2rem; font-weight: bold; color: #1e1b4b; margin: 0;">{}</p>
                </div>
                """.format(len(filtered_df)), unsafe_allow_html=True)
            
            with col2:
                high_count = len(filtered_df[filtered_df['etkiSeviyesi'] == 'Yüksek'])
                st.markdown(f"""
                <div class="metric-container" style="background: #fef2f2;">
                    <p style="color: #991b1b; font-size: 0.875rem; font-weight: 600;">Yüksek Etkili</p>
                    <p style="font-size: 2rem; font-weight: bold; color: #7f1d1d; margin: 0;">{high_count}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                most_freq = filtered_df['olayTuru'].mode()[0] if not filtered_df.empty else "-"
                st.markdown(f"""
                <div class="metric-container" style="background: #fefce8;">
                    <p style="color: #713f12; font-size: 0.875rem; font-weight: 600;">En Sık Olay</p>
                    <p style="font-size: 1.25rem; font-weight: bold; color: #78350f; margin: 0;">{most_freq}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                most_sector = filtered_df['sektor'].str.split(' / ').str[0].mode()[0] if not filtered_df.empty else "-"
                st.markdown(f"""
                <div class="metric-container" style="background: #f0fdf4;">
                    <p style="color: #14532d; font-size: 0.875rem; font-weight: 600;">En Riskli Sektör</p>
                    <p style="font-size: 1.25rem; font-weight: bold; color: #052e16; margin: 0;">{most_sector}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Grafikler
            if not filtered_df.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📊 Sektörlere Göre Hasar Sayısı")
                    sector_counts = filtered_df['sektor'].value_counts()
                    fig1 = px.bar(
                        x=sector_counts.values,
                        y=sector_counts.index,
                        orientation='h',
                        color_discrete_sequence=['#6366f1'],
                        labels={'x': 'Hasar Sayısı', 'y': 'Sektör'}
                    )
                    fig1.update_layout(
                        height=350,
                        showlegend=False,
                        plot_bgcolor='white',
                        paper_bgcolor='white'
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    st.markdown("#### 📈 Etki Seviyesi Dağılımı")
                    impact_data = filtered_df['etkiSeviyesi'].value_counts()
                    colors = {'Yüksek': '#ef4444', 'Orta': '#f59e0b', 'Düşük': '#22c55e'}
                    fig2 = px.pie(
                        values=impact_data.values,
                        names=impact_data.index,
                        color=impact_data.index,
                        color_discrete_map=colors
                    )
                    fig2.update_layout(
                        height=350,
                        showlegend=True,
                        plot_bgcolor='white',
                        paper_bgcolor='white'
                    )
                    st.plotly_chart(fig2, use_container_width=True)

if __name__ == "__main__":
    main()
