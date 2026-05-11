// frontend/actor_ai.js
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

    // --- 2. MODUL KONTROL UI (Warna & Grafik) ---
    function applyAIChanges(layout) {
        if (!layout) return;

        // A. Kontrol Tema Warna
        if (layout.bg_color && layout.bg_color !== "null") {
            const currentSavedBg = localStorage.getItem('actor_bg_color');
            
            if (layout.bg_color !== currentSavedBg) {
                localStorage.setItem('actor_bg_color', layout.bg_color);
                
                // Deteksi gelap/terang untuk kontras teks
                const isDark = ['900', '800', '700'].some(v => layout.bg_color.includes(v));
                localStorage.setItem('actor_text_color', isDark ? 'text-white' : 'text-slate-800');
                
                location.reload(); 
                return;
            }
        }

        // B. Kontrol Tipe Grafik (Target: 'actor' atau 'film')
        if (layout.diagram_type && layout.target_chart) {
            const target = layout.target_chart; 
            localStorage.setItem(`${target}_chart_type`, layout.diagram_type);
            
            // Memanggil fungsi refresh yang nanti kita buat di script utama actor
            if (typeof window.refreshActorCharts === 'function') {
                window.refreshActorCharts(target);
            }
        }
    }

    // --- 3. SCRAPER: MEMBACA KONTEKS HALAMAN ---
    function getActorContext() {
        const context = {
            halaman_aktif: "Actor Star Power Analysis"
        };

        // A. KPI Metrics
        context.top_actor = document.getElementById('m-top-name')?.innerText || '-';
        context.highest_revenue = document.getElementById('m-top-rev')?.innerText || '$0';
        context.total_top10_revenue = document.getElementById('m-total-top')?.innerText || '$0';

        // B. Top 10 Actors Chart
        let actorChart = {};
        try {
            const chartEl = document.getElementById('actorChart');
            if (chartEl && chartEl.data && chartEl.data.length > 0) {
                const trace = chartEl.data[0];
                const names = (trace.y || []).slice().reverse();
                const revenues = (trace.x || []).slice().reverse();
                actorChart.names = names;
                actorChart.revenues = revenues;
            }
        } catch (e) { console.warn("Gagal baca actorChart:", e); }
        context.actor_chart = actorChart;

        // C. Selected Actor & Films
        const selectEl = document.getElementById('actorSelect');
        context.selected_actor = selectEl?.options[selectEl.selectedIndex]?.text || '';

        let filmChart = {};
        try {
            const filmEl = document.getElementById('filmChart');
            if (filmEl && filmEl.data && filmEl.data.length > 0) {
                const trace = filmEl.data[0];
                filmChart.titles = (trace.y || []).slice().reverse();
                filmChart.revenues = (trace.x || []).slice().reverse();
            }
        } catch (e) { console.warn("Gagal baca filmChart:", e); }
        context.film_chart = filmChart;

        return context;
    }

    // --- 4. APPEND MESSAGE HELPER ---
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

    // --- 5. CHAT LOGIC ---
    async function handleChat() {
        const prompt = chatInput.value.trim();
        if (!prompt) return;

        appendMessage('user', prompt);
        chatInput.value = '';

        const loadingId = 'loading-' + Date.now();
        const loadingDiv = document.createElement('div');
        loadingDiv.id = loadingId;
        loadingDiv.className = 'text-xs text-slate-400 italic mb-4 ml-2 animate-pulse';
        loadingDiv.innerText = 'Actor AI sedang menganalisis star power...';
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const res = await fetch('http://127.0.0.1:8000/chat-actor', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt, page_context: getActorContext() })
            });

            const data = await res.json();
            document.getElementById(loadingId)?.remove();

            if (data.message) {
                appendMessage('ai', data.message);
            }

            // Jalankan perubahan UI jika diperintahkan AI
            if (data.layout) {
                applyAIChanges(data.layout);
            }

        } catch (e) {
            document.getElementById(loadingId)?.remove();
            console.error("Error Detail:", e);
            appendMessage('ai', '❌ Gagal terhubung ke server Actor AI.');
        }
    }

    sendBtn.addEventListener('click', handleChat);
    chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleChat(); });
});