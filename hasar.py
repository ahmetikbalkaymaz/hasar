import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
from datetime import datetime

# Sayfa yapılandırması
st.set_page_config(
    page_title="Yapay Zeka Destekli Hasar Paneli",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS stilleri
st.markdown("""
<style>
    .main {
        padding: 0;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0;
    }
    div[data-testid="stSidebarNav"] {
        display: none;
    }
    .incident-item {
        padding: 12px;
        border-left: 4px solid;
        background: white;
        margin-bottom: 8px;
        border-radius: 0 6px 6px 0;
        cursor: pointer;
        transition: all 0.2s;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .incident-item:hover {
        background-color: #eef2ff;
        transform: translateX(-2px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.15);
    }
    .incident-high { border-left-color: #dc3545; }
    .incident-medium { border-left-color: #ffc107; }
    .incident-low { border-left-color: #28a745; }
    .incident-active {
        background-color: #eef2ff !important;
        border-left-color: #4f46e5 !important;
    }
    .stButton > button {
        text-align: left;
        width: 100%;
        background: transparent;
        border: none;
        padding: 0;
        font-weight: normal;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
        height: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Session state
if 'selected_id' not in st.session_state:
    st.session_state.selected_id = None
if 'show_details' not in st.session_state:
    st.session_state.show_details = False

# Veri yükleme
@st.cache_data
def load_data():
    data = [
        {
            "id": 1, "tarih": "28.09.2025", "il": "Erzurum", "ilce": "Aziziye", 
            "konum": "Erzurum 1. OSB", "tesisAdi": "Şahika Boya Üretim Tesisleri", 
            "sektor": "Kimya / Boya", "olayTuru": "Yangın", "etkiSeviyesi": "Yüksek",
            "dogrulamaYontemi": "A", "dogrulukOrani": 95, "lat": 39.9510, "lng": 41.1920,
            "ozet": "Boya üretim tesisinin depo bölümünde çıkan yangın, bitişikte bulunan terlik hammaddesi deposuna da sıçradı. İki tesis de büyük hasar gördü.",
            "etki": "İki farklı riskin (kimyasal ve plastik) birleştiği büyük ve komplike bir hasar dosyasıdır. Yangının komşu bir tesise sıçraması, Üçüncü Şahıs Sorumluluk poliçesini doğrudan devreye sokar.",
            "haberler": ["AA: 'Erzurum OSB'de boya fabrikasında yangın.'", "Erzurum Günebakış: 'Yangın yandaki depoya da sıçradı.'"]
        },
        {
            "id": 2, "tarih": "28.09.2025", "il": "Adana", "ilce": "Yüreğir",
            "konum": "Zağarlı Mahallesi", "tesisAdi": "FBY Enerji Üretim (Yüreğir BES)",
            "sektor": "Enerji / Biyokütle", "olayTuru": "Yangın", "etkiSeviyesi": "Orta",
            "dogrulamaYontemi": "A", "dogrulukOrani": 90, "lat": 36.9535, "lng": 35.4182,
            "ozet": "Tarımsal atıklardan enerji üreten biyokütle santralinin açık alandaki atık depolama sahasında büyük bir yangın çıktı. Yangının santralin ana ünitelerine sıçraması önlendi.",
            "etki": "Santralin yakıt stoğu önemli ölçüde yanmıştır. Enerji üretiminde aksama yaşanması ve buna bağlı bir İş Durması hasarı oluşması kaçınılmazdır.",
            "haberler": ["İHA: 'Adana'da biyokütle enerji santralinde yangın.'", "Habertürk: 'Santralin atık depolama alanı alev alev yandı.'"]
        },
        {
            "id": 3, "tarih": "28.09.2025", "il": "Karabük", "ilce": "Safranbolu",
            "konum": "Safranbolu Sanayi Sitesi", "tesisAdi": "Ahmet Sevigen Kereste Atölyesi",
            "sektor": "Kereste", "olayTuru": "Yangın", "etkiSeviyesi": "Orta",
            "dogrulamaYontemi": "B", "dogrulukOrani": 85, "lat": 41.2580, "lng": 32.6715,
            "ozet": "Sanayi sitesi içerisinde faaliyet gösteren bir kereste atölyesinde, depolanan ahşap malzemelerin ve talaşların tutuşmasıyla yangın çıktı.",
            "etki": "Kereste ve ahşap işleme tesisleri, yanıcı toz ve malzeme birikimi nedeniyle yangın frekansı en yüksek sektörler arasındadır. Atölye için total bir hasar söz konusudur.",
            "haberler": ["BirGün: 'Safranbolu sanayi sitesinde kereste atölyesi yandı.'", "İHA: 'Yangın güçlükle kontrol altına alındı.'"]
        },
        {
            "id": 4, "tarih": "25.09.2025", "il": "Zonguldak", "ilce": "Kilimli",
            "konum": "Çatalağzı, ZETES Santrali", "tesisAdi": "Eren Enerji Termik Santrali",
            "sektor": "Enerji / Termik Santral", "olayTuru": "Kazan/Boiler Patlağı",
            "etkiSeviyesi": "Yüksek", "dogrulamaYontemi": "A", "dogrulukOrani": 96,
            "lat": 41.5167, "lng": 31.9,
            "ozet": "Termik santralin ana kazanlarından birine giden yüksek basınçlı buhar hattında meydana gelen patlama sonucu 3 işçi ağır yaralandı. Üretim kısmen durduruldu.",
            "etki": "Patlama sonucu 3 işçinin ağır yaralanması, İşveren Sorumluluk poliçesi kapsamında yüksek tutarlı tazminat taleplerini gündeme getirmektedir.",
            "haberler": ["Z Haber: 'Eren Enerji'de buhar kazanı patladı: 3 ağır yaralı.'", "Enerji Günlüğü: 'ZETES'te üretim aksadı.'"]
        },
        {
            "id": 5, "tarih": "29.09.2025", "il": "Karaman", "ilce": "Merkez",
            "konum": "Karaman OSB", "tesisAdi": "Sosyete Un Gıda Sanayi",
            "sektor": "Gıda / Un", "olayTuru": "Yangın", "etkiSeviyesi": "Düşük",
            "dogrulamaYontemi": "B", "dogrulukOrani": 75, "lat": 37.2050, "lng": 33.2590,
            "ozet": "Bir un fabrikasının üretim tesisinden ayrı, arka bölümde bulunan hurda ve atık depolama alanında yangın çıktı. Yangın, ana tesise sıçramadan söndürüldü.",
            "etki": "Üretimi doğrudan etkilemeyen, düşük şiddetli bir hasar. Maddi hasar sınırlıdır.",
            "haberler": ["Karamandan.com: 'OSB'de fabrikanın hurdalığında yangın paniği.'"]
        }
    ]
    return pd.DataFrame(data)

def create_map(df, selected_id=None):
    """Harita oluştur"""
    if df.empty:
        m = folium.Map(location=[39.0, 35.0], zoom_start=6, tiles='CartoDB positron')
    else:
        m = folium.Map(location=[39.0, 35.0], zoom_start=6, tiles='CartoDB positron')
        
        for _, row in df.iterrows():
            color_map = {'Yüksek': 'red', 'Orta': 'orange', 'Düşük': 'green'}
            color = color_map.get(row['etkiSeviyesi'], 'gray')
            
            # Seçili öğeyi vurgula
            if selected_id and row['id'] == selected_id:
                folium.CircleMarker(
                    [row['lat'], row['lng']],
                    radius=15,
                    color='blue',
                    fill=False,
                    weight=3
                ).add_to(m)
            
            icon_html = f"""
            <div style="font-size: 20px; color: {color};">
                <i class="fa fa-fire"></i>
            </div>
            """
            
            folium.Marker(
                [row['lat'], row['lng']],
                popup=folium.Popup(f"""
                    <b>{row['tesisAdi']}</b><br>
                    {row['olayTuru']}<br>
                    <i>{row['tarih']}</i>
                """, max_width=300),
                tooltip=row['tesisAdi'],
                icon=folium.Icon(color=color, icon='fire', prefix='fa')
            ).add_to(m)
    
    return m

# Ana başlık
st.markdown("""
<div style="background: white; padding: 1rem 2rem; margin: -2rem -3rem 1rem -3rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    <div style="display: flex; align-items: center; gap: 1rem;">
        <span style="font-size: 2rem;">⚠️</span>
        <div>
            <h1 style="margin: 0; font-size: 1.5rem;">Yapay Zeka Destekli Hasar Paneli</h1>
            <p style="margin: 0; color: #6b7280; font-size: 0.875rem;">Türkiye: Son 3 Aylık Endüstriyel & Enerji Hasarları Analizi</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Veri yükle
df = load_data()

# Filtreler
with st.container():
    st.markdown("**Filtreler:**")
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 0.5])
    
    with col1:
        il_filter = st.selectbox("", ["Tüm İller"] + sorted(df['il'].unique().tolist()), key="il")
    with col2:
        sectors = df['sektor'].str.split(' / ').str[0].unique()
        sektor_filter = st.selectbox("", ["Tüm Sektörler"] + sorted(sectors.tolist()), key="sektor")
    with col3:
        olay_filter = st.selectbox("", ["Tüm Olay Türleri"] + sorted(df['olayTuru'].unique().tolist()), key="olay")
    with col4:
        etki_filter = st.selectbox("", ["Tüm Etki Seviyeleri", "Yüksek", "Orta", "Düşük"], key="etki")
    with col5:
        if st.button("🔄 Temizle"):
            for key in ['il', 'sektor', 'olay', 'etki']:
                st.session_state[key] = list(st.session_state[key + '_options'])[0] if key + '_options' in st.session_state else None
            st.rerun()

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

st.info(f"📊 {len(filtered_df)} sonuç bulundu.")

# Ana içerik - 2 kolon
col_left, col_right = st.columns([1, 3])

# Sol panel - Liste
with col_left:
    st.markdown("### 📋 Hasar Listesi (En Yeni)")
    
    if filtered_df.empty:
        st.write("Filtre kriterlerine uygun sonuç bulunamadı.")
    else:
        for _, row in filtered_df.iterrows():
            impact_colors = {
                'Yüksek': '#dc3545',
                'Orta': '#ffc107', 
                'Düşük': '#28a745'
            }
            border_color = impact_colors.get(row['etkiSeviyesi'], '#6c757d')
            
            is_active = st.session_state.selected_id == row['id']
            active_style = "background-color: #eef2ff; border-left-color: #4f46e5;" if is_active else ""
            
            # Tıklanabilir kart
            card_html = f"""
            <div class="incident-item" style="border-left-color: {border_color}; {active_style}">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <strong style="color: #1f2937; font-size: 14px;">{row['tesisAdi']}</strong>
                    <span style="color: #6b7280; font-size: 12px;">{row['tarih']}</span>
                </div>
                <div style="color: #6b7280; font-size: 13px;">
                    {row['il']}, {row['ilce']}
                </div>
                <div style="color: #9ca3af; font-size: 12px; margin-top: 2px;">
                    {row['olayTuru']}
                </div>
            </div>
            """
            
            if st.button(card_html, key=f"card_{row['id']}", help=f"Detayları görmek için tıklayın", use_container_width=True):
                st.session_state.selected_id = row['id']
                st.session_state.show_details = True
                st.rerun()
            
            st.markdown(card_html, unsafe_allow_html=True)

# Sağ panel
with col_right:
    if st.session_state.show_details and st.session_state.selected_id:
        # Detay görünümü
        selected = filtered_df[filtered_df['id'] == st.session_state.selected_id]
        
        if not selected.empty:
            selected = selected.iloc[0]
            
            # Kapat butonu
            col_close, _ = st.columns([1, 10])
            with col_close:
                if st.button("✖ Kapat"):
                    st.session_state.show_details = False
                    st.session_state.selected_id = None
                    st.rerun()
            
            # Detay içeriği
            impact_badges = {
                'Yüksek': '<span style="background: #fee2e2; color: #991b1b; padding: 4px 12px; border-radius: 9999px; font-size: 14px; font-weight: 600;">🔴 Yüksek Etki</span>',
                'Orta': '<span style="background: #fef3c7; color: #92400e; padding: 4px 12px; border-radius: 9999px; font-size: 14px; font-weight: 600;">🟡 Orta Etki</span>',
                'Düşük': '<span style="background: #d1fae5; color: #065f46; padding: 4px 12px; border-radius: 9999px; font-size: 14px; font-weight: 600;">🟢 Düşük Etki</span>'
            }
            
            st.markdown(f"""
            <div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                {impact_badges.get(selected['etkiSeviyesi'], '')}
                <h2 style="margin-top: 1rem; color: #111827;">{selected['tesisAdi']}</h2>
                <p style="color: #6b7280;">📍 {selected['konum']}, {selected['ilce']}/{selected['il']}</p>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1.5rem 0;">
                    <div style="background: #f9fafb; padding: 1rem; border-radius: 8px;">
                        <p style="color: #6b7280; font-size: 0.875rem; margin: 0;">Tarih</p>
                        <p style="font-size: 1.25rem; font-weight: bold; margin: 4px 0;">{selected['tarih']}</p>
                    </div>
                    <div style="background: #f9fafb; padding: 1rem; border-radius: 8px;">
                        <p style="color: #6b7280; font-size: 0.875rem; margin: 0;">Olay Türü</p>
                        <p style="font-size: 1.25rem; font-weight: bold; margin: 4px 0;">{selected['olayTuru']}</p>
                    </div>
                    <div style="background: #f9fafb; padding: 1rem; border-radius: 8px;">
                        <p style="color: #6b7280; font-size: 0.875rem; margin: 0;">Sektör</p>
                        <p style="font-size: 1.25rem; font-weight: bold; margin: 4px 0;">{selected['sektor']}</p>
                    </div>
                    <div style="background: #f9fafb; padding: 1rem; border-radius: 8px;">
                        <p style="color: #6b7280; font-size: 0.875rem; margin: 0;">Doğruluk Oranı</p>
                        <div style="margin-top: 8px;">
                            <div style="background: #e5e7eb; border-radius: 9999px; height: 8px;">
                                <div style="background: #6366f1; width: {selected['dogrulukOrani']}%; height: 100%; border-radius: 9999px;"></div>
                            </div>
                            <p style="text-align: right; font-size: 0.75rem; margin: 4px 0;">%{selected['dogrulukOrani']}</p>
                        </div>
                    </div>
                </div>
                
                <div style="background: #eff6ff; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                    <h4 style="color: #1e40af;">📝 Olay Özeti</h4>
                    <p style="color: #1f2937;">{selected['ozet']}</p>
                </div>
                
                <div>
                    <h4 style="color: #111827;">💥 Direkt Hasar Etkisi</h4>
                    <p style="color: #4b5563;">{selected['etki']}</p>
                </div>
                
                <div style="margin-top: 1.5rem;">
                    <h4 style="color: #111827;">📰 Haber Alıntıları</h4>
                    <ul style="color: #4b5563;">
                        {"".join([f"<li>{haber}</li>" for haber in selected['haberler']])}
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Detay haritası
            st.markdown("#### 📍 Konum Detayı")
            detail_map = create_map(pd.DataFrame([selected]), selected['id'])
            folium_static(detail_map, height=400)
    
    else:
        # Normal görünüm - Harita ve analizler
        tabs = st.tabs(["🗺️ Hasar Konumları Haritası", "📊 Öne Çıkan Analizler"])
        
        with tabs[0]:
            m = create_map(filtered_df, st.session_state.selected_id)
            folium_static(m, height=500)
        
        with tabs[1]:
            # Metrikler
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                    <div style="font-size: 0.875rem; opacity: 0.9;">Toplam Vaka</div>
                    <div style="font-size: 2.5rem; font-weight: bold; margin: 8px 0;">{len(filtered_df)}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                high_count = len(filtered_df[filtered_df['etkiSeviyesi'] == 'Yüksek'])
                st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white;">
                    <div style="font-size: 0.875rem; opacity: 0.9;">Yüksek Etkili</div>
                    <div style="font-size: 2.5rem; font-weight: bold; margin: 8px 0;">{high_count}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                most_freq = filtered_df['olayTuru'].mode()[0] if not filtered_df.empty else "-"
                st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white;">
                    <div style="font-size: 0.875rem; opacity: 0.9;">En Sık Olay</div>
                    <div style="font-size: 1.5rem; font-weight: bold; margin: 8px 0;">{most_freq}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                most_sector = filtered_df['sektor'].str.split(' / ').str[0].mode()[0] if not filtered_df.empty else "-"
                st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #333;">
                    <div style="font-size: 0.875rem; opacity: 0.8;">En Riskli Sektör</div>
                    <div style="font-size: 1.5rem; font-weight: bold; margin: 8px 0;">{most_sector}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Grafikler
            if not filtered_df.empty:
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📊 Sektörlere Göre Hasar Sayısı")
                    sector_counts = filtered_df['sektor'].value_counts()
                    fig1 = px.bar(
                        x=sector_counts.values,
                        y=sector_counts.index,
                        orientation='h',
                        color_discrete_sequence=['#6366f1']
                    )
                    fig1.update_layout(
                        height=350,
                        showlegend=False,
                        xaxis_title="Hasar Sayısı",
                        yaxis_title="",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
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
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig2, use_container_width=True)
