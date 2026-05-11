// frontend/analysis.js

document.addEventListener('DOMContentLoaded', () => {
    const STORE1_COLOR = "#4F8EF7";
    const STORE2_COLOR = "#F76E6E";
    const CHART_PALETTE = ["#4F8EF7", "#F76E6E", "#54C896", "#F7C04F", "#A78BFA", "#FB923C", "#34D399", "#F472B6"];

    window.analysisData = null;

    function loadSavedTheme() {
        const savedBg = localStorage.getItem('analysis_bg_color');
        const savedText = localStorage.getItem('analysis_text_color');
        const mainContent = document.getElementById('main-content');
        if (savedBg) {
            document.body.classList.add(savedBg);
            if (mainContent) mainContent.classList.add(savedBg);
        }
        if (savedText) document.body.classList.add(savedText);
    }

    async function fetchAnalysis() {
        try {
            const res = await fetch('http://127.0.0.1:8000/api/analysis');
            const data = await res.json();
            window.analysisData = data; 
            
            document.getElementById('loadingIndicator').style.display = 'none';
            document.getElementById('analysisContent').style.display = 'block';

            renderSummary(data.summary);
            refreshCharts('all'); 
            
            renderTrendTable(data.store1.trend, 'trendTable1');
            renderTrendTable(data.store2.trend, 'trendTable2');

        } catch (err) {
            console.error("Fetch Error:", err);
        }
    }

    window.refreshCharts = function(target = 'all') {
        const data = window.analysisData;
        if (!data) return;

        // A. BAGIAN GENRE
        if (target === 'all' || target === 'genre') {
            const genreType = localStorage.getItem('genre_chart_type') || 'bar';
            renderGenericChart(data.store1.genre, 'genreChart1', 'total_rental', 'genre', STORE1_COLOR, genreType);
            renderGenericChart(data.store2.genre, 'genreChart2', 'total_rental', 'genre', STORE2_COLOR, genreType);
        }

        // B. BAGIAN RATING
        if (target === 'all' || target === 'rating') {
            const ratingType = localStorage.getItem('rating_chart_type') || 'donut';
            renderGenericChart(data.store1.rating, 'ratingChart1', 'total_rental', 'rating', STORE1_COLOR, ratingType);
            renderGenericChart(data.store2.rating, 'ratingChart2', 'total_rental', 'rating', STORE2_COLOR, ratingType);
        }

        // C. BAGIAN FILM (DITAMBAHKAN KEMBALI)
        if (target === 'all' || target === 'film') {
            const filmType = localStorage.getItem('film_chart_type') || 'bar';
            renderGenericChart(data.store1.film, 'filmChart1', 'total_rental', 'title', STORE1_COLOR, filmType);
            renderGenericChart(data.store2.film, 'filmChart2', 'total_rental', 'title', STORE2_COLOR, filmType);
        }

        // D. BAGIAN TREND
        if (target === 'all' || target === 'trend') {
            const trendType = localStorage.getItem('trend_chart_type') || 'line';
            renderLineChart(data.store1.trend, data.store2.trend, 'trendChart', trendType);
        }
    };

    function renderGenericChart(data, el, valCol, labelCol, color, type) {
        if (!data || data.length === 0) return;
        let trace;
        let layout = {
            height: 300,
            margin: { l: 120, r: 20, t: 10, b: 40 }, // L dinaikkan agar judul film panjang tidak terpotong
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { family: 'DM Sans' }
        };

        if (type === 'donut' || type === 'pie') {
            trace = {
                labels: data.map(d => d[labelCol]),
                values: data.map(d => d[valCol]),
                type: 'pie',
                hole: type === 'donut' ? 0.55 : 0,
                marker: { colors: CHART_PALETTE },
                textinfo: 'label+percent'
            };
            layout.showlegend = false;
            layout.margin = { l: 10, r: 10, t: 10, b: 10 };
        } else {
            trace = {
                x: type === 'bar' ? data.map(d => d[valCol]) : data.map(d => d[labelCol]),
                y: type === 'bar' ? data.map(d => d[labelCol]) : data.map(d => d[valCol]),
                type: type === 'line' ? 'scatter' : 'bar',
                mode: type === 'line' ? 'lines+markers' : undefined,
                orientation: type === 'bar' ? 'h' : 'v',
                marker: { color: color },
                line: type === 'line' ? { color: color, width: 3 } : undefined
            };
            if (type === 'bar') layout.yaxis = { autorange: 'reversed' };
        }
        Plotly.newPlot(el, [trace], layout, { displayModeBar: false, responsive: true });
    }

    function renderLineChart(data1, data2, elementId, type = 'line') {
        if (!data1 || !data2) return;
        const trace1 = { 
            x: data1.map(d => d.month), y: data1.map(d => d.total_rental), 
            type: type === 'bar' ? 'bar' : 'scatter',
            mode: 'lines+markers', name: 'Store 1', line: { color: STORE1_COLOR, width: 4 } 
        };
        const trace2 = { 
            x: data2.map(d => d.month), y: data2.map(d => d.total_rental), 
            type: type === 'bar' ? 'bar' : 'scatter',
            mode: 'lines+markers', name: 'Store 2', line: { color: STORE2_COLOR, width: 4, dash: 'dot' } 
        };
        const layout = { 
            margin: { l: 40, r: 20, t: 10, b: 40 }, height: 350, 
            legend: { orientation: 'h', y: 1.1 }, 
            paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
            barmode: type === 'bar' ? 'group' : undefined
        };
        Plotly.newPlot(elementId, [trace1, trace2], layout, { displayModeBar: false, responsive: true });
    }

    function renderSummary(summaryData) {
        if (!summaryData || summaryData.length === 0) return;
        const row1 = summaryData.find(s => s.store_id === 1) || {};
        const row2 = summaryData.find(s => s.store_id === 2) || {};
        document.getElementById('summaryTable').innerHTML = `
            <tr><th>Metrik</th><th>🔵 Store 1</th><th>🔴 Store 2</th></tr>
            <tr><td>Dominant Genre</td><td class="store1-val">${row1.dominant_genre || '-'}</td><td class="store2-val">${row2.dominant_genre || '-'}</td></tr>
            <tr><td>Dominant Rating</td><td class="store1-val">${row1.dominant_rating || '-'}</td><td class="store2-val">${row2.dominant_rating || '-'}</td></tr>
            <tr><td>Top Film</td><td class="store1-val">${row1.top_film || '-'}</td><td class="store2-val">${row2.top_film || '-'}</td></tr>
            <tr><td>Top Rental</td><td class="store1-val">${row1.top_film_total_rental || 0} rental</td><td class="store2-val">${row2.top_film_total_rental || 0} rental</td></tr>
        `;
    }

    function renderTrendTable(data, elementId) {
        if (!data || data.length === 0) return;
        let html = `<tr><th>Bulan</th><th>Total Rental</th><th>Trend</th></tr>`;
        data.forEach(row => {
            let trendIcon = row.trend === 'naik' ? '<span style="color:#10B981; font-weight:bold;">▲ naik</span>' :
                            row.trend === 'turun' ? '<span style="color:#EF4444; font-weight:bold;">▼ turun</span>' :
                            '<span style="color:#6B7280;">→ tetap</span>';
            html += `<tr><td>${row.month}</td><td>${row.total_rental}</td><td>${trendIcon}</td></tr>`;
        });
        document.getElementById(elementId).innerHTML = html;
    }

    loadSavedTheme();
    fetchAnalysis();
});