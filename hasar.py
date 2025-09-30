import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json

# Sayfa yapılandırması
st.set_page_config(
    page_title="Yapay Zeka Destekli Hasar Paneli",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Veri hazırlama
incidents_data = [
    {"id": 63, "tarih": "28.09.2025", "il": "Erzurum", "ilce": "Aziziye", "konum": "Erzurum 1. OSB", "tesisAdi": "Şahika Boya Üretim Tesisleri", "sektor": "Kimya / Boya", "olayTuru": "Yangın", "etkiSeviyesi": "Yüksek", "dogrulamaYontemi": "A", "dogrulukOrani": 95, "lat": 39.9510, "lng": 41.1920, "ozet": "Boya üretim tesisinin depo bölümünde çıkan yangın, bitişikte bulunan terlik hammaddesi (EVA) deposuna da sıçradı. İki tesis de büyük hasar gördü.", "etki": "Boya ve kimya tesisleri, solvent gibi yanıcı ve parlayıcı maddeler nedeniyle yangın riski en yüksek sektörlerdendir.", "haberler": ["AA: 'Erzurum OSB'de boya fabrikasında yangın.'", "Erzurum Günebakış: 'Yangın yandaki depoya da sıçradı.'"]},
    {"id": 62, "tarih": "28.09.2025", "il": "Adana", "ilce": "Yüreğir", "konum": "Zağarlı Mahallesi", "tesisAdi": "FBY Enerji Üretim (Yüreğir BES)", "sektor": "Enerji / Biyokütle", "olayTuru": "Yangın", "etkiSeviyesi": "Orta", "dogrulamaYontemi": "A", "dogrulukOrani": 90, "lat": 36.9535, "lng": 35.4182, "ozet": "Tarımsal atıklardan enerji üreten biyokütle santralinin açık alandaki atık depolama sahasında büyük bir yangın çıktı.", "etki": "Santralin yakıt stoğu önemli ölçüde yanmıştır.", "haberler": ["İHA: 'Adana'da biyokütle enerji santralinde yangın.'"]},
    {"id": 61, "tarih": "28.09.2025", "il": "Karabük", "ilce": "Safranbolu", "konum": "Safranbolu Sanayi Sitesi", "tesisAdi": "Ahmet Sevigen Kereste Atölyesi", "sektor": "Kereste", "olayTuru": "Yangın", "etkiSeviyesi": "Orta", "dogrulamaYontemi": "B", "dogrulukOrani": 85, "lat": 41.2580, "lng": 32.6715, "ozet": "Kereste atölyesinde yangın çıktı.", "etki": "Atölye için total hasar.", "haberler": ["BirGün: 'Safranbolu sanayi sitesinde kereste atölyesi yandı.'"]},
    {"id": 60, "tarih": "29.09.2025", "il": "Karaman", "ilce": "Merkez", "konum": "Karaman OSB", "tesisAdi": "Sosyete Un Gıda Sanayi", "sektor": "Gıda / Un", "olayTuru": "Yangın", "etkiSeviyesi": "Düşük", "dogrulamaYontemi": "B", "dogrulukOrani": 75, "lat": 37.2050, "lng": 33.2590, "ozet": "Un fabrikasının atık depolama alanında yangın çıktı.", "etki": "Düşük şiddetli hasar.", "haberler": ["Karamandan.com: 'OSB'de fabrikanın hurdalığında yangın paniği.'"]},
    {"id": 59, "tarih": "25.09.2025", "il": "Zonguldak", "ilce": "Kilimli", "konum": "Çatalağzı, ZETES Santrali", "tesisAdi": "Eren Enerji Termik Santrali", "sektor": "Enerji / Termik Santral", "olayTuru": "Kazan/Boiler Patlağı", "etkiSeviyesi": "Yüksek", "dogrulamaYontemi": "A", "dogrulukOrani": 96, "lat": 41.5167, "lng": 31.9, "ozet": "Termik santralin buhar hattında patlama sonucu 3 işçi ağır yaralandı.", "etki": "Ciddi iş durması ve kar kaybı.", "haberler": ["Z Haber: 'Eren Enerji'de buhar kazanı patladı.'"]}
]

# HTML içeriği
html_content = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Yapay Zeka Destekli Hasar Paneli</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f0f2f5;
            margin: 0;
            padding: 0;
        }
        .main-grid {
            display: grid;
            grid-template-columns: 380px 1fr;
            height: calc(100vh - 200px);
            gap: 1rem;
            padding: 1rem;
        }
        #incident-list-container {
            background: white;
            border-radius: 0.5rem;
            padding: 1rem;
            overflow-y: auto;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .incident-item {
            padding: 0.75rem;
            border-left: 4px solid;
            background: white;
            margin-bottom: 0.5rem;
            border-radius: 0 0.375rem 0.375rem 0;
            cursor: pointer;
            transition: all 0.15s;
        }
        .incident-item:hover {
            background-color: #eef2ff;
            transform: translateX(-2px);
        }
        .active-item {
            background-color: #eef2ff !important;
            border-left-color: #4f46e5 !important;
        }
        #map {
            height: 450px;
            width: 100%;
            border-radius: 0.75rem;
        }
        .chart-container {
            height: 350px;
        }
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="bg-white shadow-sm p-4 mb-4">
        <div class="max-w-screen-2xl mx-auto flex items-center gap-3">
            <svg class="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
                <h1 class="text-2xl font-bold text-gray-800">Yapay Zeka Destekli Hasar Paneli</h1>
                <p class="text-sm text-gray-500">Türkiye: Son 3 Aylık Endüstriyel & Enerji Hasarları Analizi</p>
            </div>
        </div>
    </div>

    <div class="bg-white/80 backdrop-blur-sm p-3 shadow-md mb-4">
        <div class="max-w-screen-2xl mx-auto flex items-center gap-2">
            <span class="font-semibold text-gray-600">Filtreler:</span>
            <select id="il-filter" class="p-2 border rounded-md text-sm">
                <option value="all">Tüm İller</option>
            </select>
            <select id="sektor-filter" class="p-2 border rounded-md text-sm">
                <option value="all">Tüm Sektörler</option>
            </select>
            <select id="olay-filter" class="p-2 border rounded-md text-sm">
                <option value="all">Tüm Olay Türleri</option>
            </select>
            <select id="etki-filter" class="p-2 border rounded-md text-sm">
                <option value="all">Tüm Etki Seviyeleri</option>
                <option value="Yüksek">Yüksek</option>
                <option value="Orta">Orta</option>
                <option value="Düşük">Düşük</option>
            </select>
            <button id="reset-filters" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-2 px-4 rounded-md text-sm">
                Filtreleri Temizle
            </button>
            <div id="result-count" class="ml-auto text-sm font-medium text-gray-600"></div>
        </div>
    </div>

    <div class="main-grid">
        <aside id="incident-list-container">
            <h2 class="text-lg font-bold mb-3 pb-2 border-b">📋 Hasar Listesi (En Yeni)</h2>
            <div id="incident-list"></div>
        </aside>

        <div id="main-content-area">
            <div id="details-panel" class="hidden bg-white p-6 rounded-lg shadow-lg"></div>
            <div id="analysis-panel">
                <div class="bg-white rounded-lg shadow-lg p-4 mb-4">
                    <h3 class="font-bold text-gray-700 text-lg mb-2">🗺️ Hasar Konumları Haritası</h3>
                    <div id="map"></div>
                </div>
                <div class="grid grid-cols-4 gap-4 mb-4" id="metric-cards"></div>
                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-white rounded-lg shadow-lg p-4">
                        <h3 class="font-semibold text-center mb-2 text-gray-600">Sektörlere Göre Hasar</h3>
                        <div class="chart-container">
                            <canvas id="sektorChart"></canvas>
                        </div>
                    </div>
                    <div class="bg-white rounded-lg shadow-lg p-4">
                        <h3 class="font-semibold text-center mb-2 text-gray-600">Etki Seviyesi Dağılımı</h3>
                        <div class="chart-container">
                            <canvas id="etkiChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const incidentsData = """ + json.dumps(incidents_data) + """;
        let map, currentFilteredData = incidentsData;
        let currentIncident = null;
        
        function init() {
            populateFilters();
            initMap();
            renderAll(incidentsData);
            addEventListeners();
        }

        function populateFilters() {
            const iller = [...new Set(incidentsData.map(item => item.il))].sort();
            const sektorler = [...new Set(incidentsData.map(item => item.sektor.split(' / ')[0]))].sort();
            const olaylar = [...new Set(incidentsData.map(item => item.olayTuru))].sort();
            
            iller.forEach(il => {
                document.getElementById('il-filter').innerHTML += `<option value="${il}">${il}</option>`;
            });
            sektorler.forEach(sektor => {
                document.getElementById('sektor-filter').innerHTML += `<option value="${sektor}">${sektor}</option>`;
            });
            olaylar.forEach(olay => {
                document.getElementById('olay-filter').innerHTML += `<option value="${olay}">${olay}</option>`;
            });
        }

        function renderIncidentList(data) {
            const listEl = document.getElementById('incident-list');
            listEl.innerHTML = '';
            
            if (data.length === 0) {
                listEl.innerHTML = '<p class="text-gray-500 text-center p-4">Sonuç bulunamadı.</p>';
                return;
            }
            
            data.forEach(item => {
                const colors = {
                    'Yüksek': 'border-red-500',
                    'Orta': 'border-yellow-500',
                    'Düşük': 'border-green-500'
                };
                const borderColor = colors[item.etkiSeviyesi] || 'border-gray-300';
                
                const itemDiv = document.createElement('div');
                itemDiv.className = `incident-item ${borderColor}`;
                itemDiv.dataset.id = item.id;
                itemDiv.innerHTML = `
                    <div class="flex justify-between items-start">
                        <div class="font-bold text-gray-800">${item.tesisAdi}</div>
                        <div class="text-xs text-gray-500">${item.tarih}</div>
                    </div>
                    <div class="text-sm text-gray-600 mt-1">${item.il}, ${item.ilce}</div>
                    <div class="text-xs text-gray-500 mt-1">${item.olayTuru}</div>
                `;
                itemDiv.onclick = () => showDetails(item);
                listEl.appendChild(itemDiv);
            });
            
            document.getElementById('result-count').textContent = `${data.length} sonuç bulundu`;
        }

        function showDetails(incident) {
            currentIncident = incident;
            document.querySelectorAll('.incident-item').forEach(el => el.classList.remove('active-item'));
            document.querySelector(`[data-id="${incident.id}"]`).classList.add('active-item');
            
            const detailsPanel = document.getElementById('details-panel');
            const analysisPanel = document.getElementById('analysis-panel');
            
            detailsPanel.innerHTML = `
                <button onclick="closeDetails()" class="float-right text-2xl text-gray-500 hover:text-gray-800">&times;</button>
                <h2 class="text-2xl font-bold text-gray-800 mb-4">${incident.tesisAdi}</h2>
                <div class="grid grid-cols-2 gap-4 mb-4">
                    <div class="bg-gray-50 p-3 rounded">
                        <div class="text-sm text-gray-500">Tarih</div>
                        <div class="font-semibold">${incident.tarih}</div>
                    </div>
                    <div class="bg-gray-50 p-3 rounded">
                        <div class="text-sm text-gray-500">Olay Türü</div>
                        <div class="font-semibold">${incident.olayTuru}</div>
                    </div>
                    <div class="bg-gray-50 p-3 rounded">
                        <div class="text-sm text-gray-500">Sektör</div>
                        <div class="font-semibold">${incident.sektor}</div>
                    </div>
                    <div class="bg-gray-50 p-3 rounded">
                        <div class="text-sm text-gray-500">Doğruluk Oranı</div>
                        <div class="font-semibold">%${incident.dogrulukOrani}</div>
                    </div>
                </div>
                <div class="bg-blue-50 p-4 rounded mb-4">
                    <h4 class="font-semibold text-blue-900 mb-2">Olay Özeti</h4>
                    <p class="text-sm">${incident.ozet}</p>
                </div>
                <div class="mb-4">
                    <h4 class="font-semibold text-gray-700 mb-2">Hasar Etkisi</h4>
                    <p class="text-sm">${incident.etki}</p>
                </div>
            `;
            
            detailsPanel.classList.remove('hidden');
            analysisPanel.classList.add('hidden');
            
            map.setView([incident.lat, incident.lng], 14);
        }

        function closeDetails() {
            document.getElementById('details-panel').classList.add('hidden');
            document.getElementById('analysis-panel').classList.remove('hidden');
            document.querySelectorAll('.incident-item').forEach(el => el.classList.remove('active-item'));
            currentIncident = null;
            map.setView([39.0, 35.0], 6);
        }

        function initMap() {
            map = L.map('map').setView([39.0, 35.0], 6);
            L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png').addTo(map);
        }

        function updateMapMarkers(data) {
            map.eachLayer(layer => {
                if (layer instanceof L.Marker) {
                    map.removeLayer(layer);
                }
            });
            
            data.forEach(item => {
                const colors = {
                    'Yüksek': 'red',
                    'Orta': 'orange',
                    'Düşük': 'green'
                };
                const color = colors[item.etkiSeviyesi] || 'gray';
                
                const icon = L.divIcon({
                    html: `<div style="color: ${color}; font-size: 20px;"><i class="fa fa-fire"></i></div>`,
                    className: 'custom-div-icon',
                    iconSize: [30, 30]
                });
                
                L.marker([item.lat, item.lng], {icon: icon})
                    .bindPopup(`<b>${item.tesisAdi}</b><br>${item.olayTuru}`)
                    .addTo(map);
            });
        }

        function updateCharts(data) {
            // Metrik kartları
            const metricsHtml = `
                <div class="bg-blue-50 p-4 rounded-lg text-center">
                    <div class="text-3xl font-bold text-blue-900">${data.length}</div>
                    <div class="text-sm text-blue-700">Toplam Vaka</div>
                </div>
                <div class="bg-red-50 p-4 rounded-lg text-center">
                    <div class="text-3xl font-bold text-red-900">${data.filter(d => d.etkiSeviyesi === 'Yüksek').length}</div>
                    <div class="text-sm text-red-700">Yüksek Etkili</div>
                </div>
                <div class="bg-yellow-50 p-4 rounded-lg text-center">
                    <div class="text-3xl font-bold text-yellow-900">${data.filter(d => d.etkiSeviyesi === 'Orta').length}</div>
                    <div class="text-sm text-yellow-700">Orta Etkili</div>
                </div>
                <div class="bg-green-50 p-4 rounded-lg text-center">
                    <div class="text-3xl font-bold text-green-900">${data.filter(d => d.etkiSeviyesi === 'Düşük').length}</div>
                    <div class="text-sm text-green-700">Düşük Etkili</div>
                </div>
            `;
            document.getElementById('metric-cards').innerHTML = metricsHtml;
            
            // Sektör grafiği
            const sektorCounts = {};
            data.forEach(item => {
                const sektor = item.sektor.split(' / ')[0];
                sektorCounts[sektor] = (sektorCounts[sektor] || 0) + 1;
            });
            
            const ctx1 = document.getElementById('sektorChart').getContext('2d');
            new Chart(ctx1, {
                type: 'bar',
                data: {
                    labels: Object.keys(sektorCounts),
                    datasets: [{
                        data: Object.values(sektorCounts),
                        backgroundColor: '#6366f1'
                    }]
                },
                options: {
                    indexAxis: 'y',
                    plugins: { legend: { display: false } }
                }
            });
            
            // Etki seviyesi grafiği
            const etkiCounts = {
                'Yüksek': data.filter(d => d.etkiSeviyesi === 'Yüksek').length,
                'Orta': data.filter(d => d.etkiSeviyesi === 'Orta').length,
                'Düşük': data.filter(d => d.etkiSeviyesi === 'Düşük').length
            };
            
            const ctx2 = document.getElementById('etkiChart').getContext('2d');
            new Chart(ctx2, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(etkiCounts),
                    datasets: [{
                        data: Object.values(etkiCounts),
                        backgroundColor: ['#ef4444', '#f59e0b', '#22c55e']
                    }]
                }
            });
        }

        function renderAll(data) {
            renderIncidentList(data);
            updateMapMarkers(data);
            updateCharts(data);
        }

        function addEventListeners() {
            ['il-filter', 'sektor-filter', 'olay-filter', 'etki-filter'].forEach(id => {
                document.getElementById(id).addEventListener('change', applyFilters);
            });
            document.getElementById('reset-filters').addEventListener('click', () => {
                ['il-filter', 'sektor-filter', 'olay-filter', 'etki-filter'].forEach(id => {
                    document.getElementById(id).value = 'all';
                });
                applyFilters();
            });
        }

        function applyFilters() {
            const filters = {
                il: document.getElementById('il-filter').value,
                sektor: document.getElementById('sektor-filter').value,
                olay: document.getElementById('olay-filter').value,
                etki: document.getElementById('etki-filter').value
            };
            
            currentFilteredData = incidentsData.filter(item => {
                return (filters.il === 'all' || item.il === filters.il) &&
                       (filters.sektor === 'all' || item.sektor.startsWith(filters.sektor)) &&
                       (filters.olay === 'all' || item.olayTuru === filters.olay) &&
                       (filters.etki === 'all' || item.etkiSeviyesi === filters.etki);
            });
            
            renderAll(currentFilteredData);
        }

        // Başlat
        init();
    </script>
</body>
</html>
"""

# HTML'i render et
components.html(html_content, height=900, scrolling=True)
