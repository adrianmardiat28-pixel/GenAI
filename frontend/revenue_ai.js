// frontend/revenue_ai.js
document.addEventListener('DOMContentLoaded', () => {
    // --- 1. DEFINISI ELEMEN UI ---
    const chatToggleBtn = document.getElementById('chat-toggle-btn');
    const chatContainer = document.getElementById('chat-container');
    const closeChat = document.getElementById('close-chat');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatMessages = document.getElementById('chat-messages');

    // --- 2. TOGGLE CHAT UI ---
    if (chatToggleBtn && chatContainer && closeChat) {
        chatToggleBtn.addEventListener('click', () => {
            chatContainer.classList.toggle('hidden');
            if (!chatContainer.classList.contains('hidden')) chatInput.focus();
        });
        closeChat.addEventListener('click', () => chatContainer.classList.add('hidden'));
    }

    // --- 3. MODUL KONTROL UI (Warna, Grafik, & PREDIKSI) ---
    function applyAIChanges(layout) {
        if (!layout) return;

        // A. Kontrol Tema Warna (Background)
        if (layout.bg_color && layout.bg_color !== "null") {
            const currentSavedBg = localStorage.getItem('revenue_bg_color');
            
            // Hanya reload jika warna yang diminta berbeda dari yang sekarang
            if (layout.bg_color !== currentSavedBg) {
                localStorage.setItem('revenue_bg_color', layout.bg_color);
                
                // Deteksi kegelapan warna untuk kontras teks
                const isDark = ['900', '800', '700'].some(v => layout.bg_color.includes(v));
                localStorage.setItem('revenue_text_color', isDark ? 'text-white' : 'text-slate-800');
                
                location.reload(); 
                return;
            }
        }
        const months = layout.prediction.months || 3;
        // B. Kontrol Prediksi Time Series (Transformer Forecasting)
        // TAMBAHAN BARU: Membaca array prediksi dari AI dan menggambar garis putus-putus
        if (layout.prediction && layout.prediction.future_dates) {
            console.log("[AI] Memproses data prediksi Time Series...");
            
            // 1. Ambil data historis dari variabel global (dari revenue.html)
            const histDates = globalRevenueData.daily.map(d => d.date);
            const histValues = globalRevenueData.daily.map(d => d.daily_revenue);

            // Trace 1: Data Historis (Garis Solid)
            const traceHistorical = {
                x: histDates,
                y: histValues,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Historical Revenue',
                line: { color: '#10b981', width: 3 }, // Warna hijau emerald
                marker: { size: 5 }
            };

            // Trace 2: Data Prediksi AI (Garis Putus-putus)
            let futDates = [...layout.prediction.future_dates];
            let futValues = [...layout.prediction.future_values];

            // Trik UI: Sambungkan titik terakhir historis ke titik pertama prediksi agar nyambung
            if (histDates.length > 0) {
                futDates.unshift(histDates[histDates.length - 1]);
                futValues.unshift(histValues[histValues.length - 1]);
            }

            const tracePrediction = {
                x: futDates,
                y: futValues,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'AI Forecast (Transformer)',
                line: { color: '#f59e0b', width: 3, dash: 'dashdot' }, // Warna oranye, garis putus-putus
                marker: { size: 7, symbol: 'diamond' }
            };

            // 2. Timpa chart lama (dailyChart) dengan chart gabungan ini
            Plotly.newPlot('dailyChart', [traceHistorical, tracePrediction], {
                margin: { t: 30, b: 40, l: 50, r: 20 },
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                title: { 
                    text: `📈 Revenue Forecast (Next ${months} Months)`, // Judul Dinamis!
                    font: { size: 14, color: '#334155' } 
                },
                legend: { orientation: 'h', y: -0.2 },
                // PERBAIKAN GRAFIK DI SINI:
                xaxis: { 
                    type: 'date',  // Memaksa Plotly membaca sebagai Tanggal (menghilangkan bug 1.171T)
                    tickformat: '%Y-%m-%d'
                },
                yaxis: { 
                    rangemode: 'tozero', // Mencegah sumbu Y meluncur ke angka negatif
                    tickformat: '$,.0f'
                }
            });

            return; // Hentikan fungsi di sini agar chart prediksi tidak tertimpa refresh biasa
        }

        // C. Kontrol Tipe Grafik Per Bagian
        if (layout.diagram_type && layout.target_chart) {
            const target = layout.target_chart; // 'daily', 'movie', atau 'genre'
            localStorage.setItem(`${target}_chart_type`, layout.diagram_type);
            
            // Memanggil fungsi refresh yang ada di revenue.html
            if (typeof window.refreshRevenueCharts === 'function') {
                window.refreshRevenueCharts(target);
            }
        }
    }

    // --- 4. SCRAPER: MEMBACA DATA VISUAL DI LAYAR ---
    function getRevenueContext() {
        const context = { halaman_aktif: "Revenue Dashboard" };

        context.total_revenue = document.getElementById('total-revenue-val')?.innerText || "$0.00";

        // Scrape Daily Chart
        let dailyChart = {};
        try {
            const dailyEl = document.getElementById('dailyChart');
            if (dailyEl && dailyEl.data && dailyEl.data.length > 0) {
                const trace = dailyEl.data[0];
                const allDates = trace.x || [];
                const allValues = trace.y || [];
                dailyChart.total_hari = allDates.length;

                if (allDates.length > 15) {
                    const paired = allDates.map((d, i) => ({ date: d, val: allValues[i] || 0 }));
                    paired.sort((a, b) => b.val - a.val);
                    dailyChart.dates = paired.slice(0, 10).map(p => p.date);
                    dailyChart.values = paired.slice(0, 10).map(p => p.val);
                    dailyChart.bottom_dates = paired.slice(-5).map(p => p.date);
                    dailyChart.bottom_values = paired.slice(-5).map(p => p.val);
                } else {
                    dailyChart.dates = allDates;
                    dailyChart.values = allValues;
                }
            }
        } catch (e) { console.warn("Gagal baca dailyChart:", e); }
        context.daily_chart = dailyChart;

        // Scrape Movie Chart
        let movieChart = {};
        try {
            const movieEl = document.getElementById('movieChart');
            if (movieEl && movieEl.data && movieEl.data.length > 0) {
                const trace = movieEl.data[0];
                movieChart.titles = trace.x || [];
                movieChart.revenues = trace.y || [];
            }
        } catch (e) { console.warn("Gagal baca movieChart:", e); }
        context.movie_chart = movieChart;

        // Scrape Genre Chart
        let genreChart = {};
        try {
            const genreEl = document.getElementById('genreChart');
            if (genreEl && genreEl.data && genreEl.data.length > 0) {
                const trace = genreEl.data[0];
                genreChart.labels = trace.labels || trace.x || [];
                genreChart.values = trace.values || trace.y || [];
            }
        } catch (e) { console.warn("Gagal baca genreChart:", e); }
        context.genre_chart = genreChart;

        return context;
    }

    // --- 5. APPEND MESSAGE HELPER ---
    function appendMessage(role, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'} mb-4`;

        let formattedText = text;
        if (role === 'ai') {
            formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
            formattedText = formattedText.replace(/^- /gm, '• ');
            formattedText = formattedText.replace(/\n/g, '<br>');
        }

        msgDiv.innerHTML = `<div class="max-w-[85%] p-3 rounded-xl text-sm shadow-sm transition-colors ${
            role === 'user' 
                ? 'bg-blue-600 text-white rounded-br-none' 
                : 'bg-white text-slate-800 border border-slate-200 rounded-bl-none'
        }">${formattedText}</div>`;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // --- 6. CHAT LOGIC ---
    async function handleChat() {
        const prompt = chatInput.value.trim();
        if (!prompt) return;

        appendMessage('user', prompt);
        chatInput.value = '';

        const loadingId = 'loading-' + Date.now();
        const loadingDiv = document.createElement('div');
        loadingDiv.id = loadingId;
        loadingDiv.className = 'text-xs text-slate-400 italic mb-4 ml-2 animate-pulse';
        loadingDiv.innerText = 'Revenue AI sedang menganalisis keuangan...';
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const res = await fetch('http://127.0.0.1:8000/chat-revenue', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt, page_context: getRevenueContext() })
            });

            const data = await res.json();
            document.getElementById(loadingId)?.remove();

            if (data.message) {
                appendMessage('ai', data.message);
            }

            // Jalankan perubahan UI jika ada perintah dari AI
            if (data.layout) {
                applyAIChanges(data.layout);
            }

        } catch (e) {
            document.getElementById(loadingId)?.remove();
            console.error("Chat Error:", e);
            appendMessage('ai', '❌ Gagal terhubung ke server Revenue.');
        }
    }

    sendBtn.addEventListener('click', handleChat);
    chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleChat(); });
});