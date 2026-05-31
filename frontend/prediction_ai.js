// frontend/prediction_ai.js
document.addEventListener('DOMContentLoaded', () => {
    const chatToggleBtn = document.getElementById('chat-toggle-btn');
    const chatContainer = document.getElementById('chat-container');
    const closeChat = document.getElementById('close-chat');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatMessages = document.getElementById('chat-messages');

    // --- 1. TOGGLE CHAT UI ---
    if (chatToggleBtn && chatContainer && closeChat) {
        chatToggleBtn.addEventListener('click', () => {
            chatContainer.classList.toggle('hidden');
            if (!chatContainer.classList.contains('hidden')) chatInput.focus();
        });
        closeChat.addEventListener('click', () => chatContainer.classList.add('hidden'));
    }

    // --- 2. SCRAPER LENGKAP: MEMBACA SEMUA DATA DI HALAMAN ---
    function getFullContext() {
        // A. Input form yang diisi user
        const inputs = {
            genre: document.getElementById('genre')?.value || "",
            rating: document.getElementById('rating')?.value || "",
            rental_rate_usd: document.getElementById('rate')?.value || "",
            rental_duration_days: document.getElementById('duration')?.value || "",
            film_length_minutes: document.getElementById('length')?.value || "",
            replacement_cost_usd: document.getElementById('cost')?.value || ""
        };

        // B. Hasil prediksi ML (label + confidence + probabilitas donut)
        const predictLabel = document.getElementById('predict-label')?.innerText || "Belum ada prediksi";
        const confidenceVal = document.getElementById('confidence-val')?.innerText || "0%";
        
        const ml_result = {
            status: predictLabel,
            confidence: confidenceVal,
            sudah_diprediksi: !document.getElementById('result-display')?.classList.contains('hidden')
        };

        // C. Baca konten analisis "Mengapa Demikian?" dan "Rekomendasi Strategis"
        const whyContent = document.getElementById('why-content')?.innerText || "Belum ada analisis";
        const actionContent = document.getElementById('action-content')?.innerText || "Belum ada rekomendasi";

        // D. Baca data chart dari Plotly (yang sudah ter-render di layar)
        let chartData = {};
        try {
            // Rating Distribution Chart
            const ratingChartEl = document.getElementById('ratingChart');
            if (ratingChartEl && ratingChartEl.data && ratingChartEl.data.length > 0) {
                const rTrace = ratingChartEl.data[0];
                chartData.rating_distribution = [];
                if (rTrace.x && rTrace.y) {
                    for (let i = 0; i < rTrace.x.length; i++) {
                        chartData.rating_distribution.push({
                            rating: rTrace.x[i],
                            jumlah_film: rTrace.y[i]
                        });
                    }
                }
            }

            // Winner Genre Chart
            const winnerChartEl = document.getElementById('winnerChart');
            if (winnerChartEl && winnerChartEl.data && winnerChartEl.data.length > 0) {
                const wTrace = winnerChartEl.data[0];
                chartData.top_genre_laris = [];
                if (wTrace.x && wTrace.y) {
                    for (let i = 0; i < wTrace.y.length; i++) {
                        chartData.top_genre_laris.push({
                            genre: wTrace.y[i],
                            total_sewa: wTrace.x[i]
                        });
                    }
                }
            }

            // Loser Genre Chart
            const loserChartEl = document.getElementById('loserChart');
            if (loserChartEl && loserChartEl.data && loserChartEl.data.length > 0) {
                const lTrace = loserChartEl.data[0];
                chartData.top_genre_sepi = [];
                if (lTrace.x && lTrace.y) {
                    for (let i = 0; i < lTrace.y.length; i++) {
                        chartData.top_genre_sepi.push({
                            genre: lTrace.y[i],
                            total_sewa: lTrace.x[i]
                        });
                    }
                }
            }

            // Donut Chart (Confidence)
            const donutChartEl = document.getElementById('donutChart');
            if (donutChartEl && donutChartEl.data && donutChartEl.data.length > 0) {
                const dTrace = donutChartEl.data[0];
                chartData.donut_probabilitas = {
                    labels: dTrace.labels,
                    values: dTrace.values
                };
            }
        } catch (e) {
            console.warn("Gagal membaca chart data:", e);
        }

        // E. Baca summary strategy (rekomendasi manajerial historis)
        const summaryStrategy = document.getElementById('summary-strategy')?.innerText || "";

        return {
            inputs,
            ml_result,
            analisis_model: {
                mengapa_demikian: whyContent,
                rekomendasi_strategis: actionContent
            },
            data_chart_di_layar: chartData,
            rekomendasi_manajerial_historis: summaryStrategy
        };
    }

    // --- 3. APPEND MESSAGE HELPER ---
    function appendMessage(role, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'} mb-4`;

        // Render markdown-like formatting untuk AI response
        let formattedText = text;
        if (role === 'ai') {
            // Bold: **text** → <b>text</b>
            formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
            // Bullet points: - item → • item
            formattedText = formattedText.replace(/^- /gm, '• ');
            // Line breaks
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

    // --- 4. CHAT LOGIC ---
    async function handleChat() {
        const prompt = chatInput.value.trim();
        if (!prompt) return;

        appendMessage('user', prompt);
        chatInput.value = '';

        // Loading indicator
        const loadingId = 'loading-' + Date.now();
        const loadingDiv = document.createElement('div');
        loadingDiv.id = loadingId;
        loadingDiv.className = 'text-xs text-slate-400 italic mb-4 ml-2 animate-pulse';
        loadingDiv.innerText = 'Predict AI sedang menganalisis data dan chart...';
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const res = await fetch('/api/chat-prediction', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt, page_context: getFullContext() })
            });

            const data = await res.json();
            document.getElementById(loadingId)?.remove();

            console.log("Raw AI Response:", data);

            if (data.message) {
                appendMessage('ai', data.message);
            }



        } catch (e) {
            document.getElementById(loadingId)?.remove();
            console.error("Error Detail:", e);
            appendMessage('ai', '❌ Gagal terhubung ke server. Pastikan backend FastAPI berjalan di port 8000.');
        }
    }

    sendBtn.addEventListener('click', handleChat);
    chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleChat(); });
});