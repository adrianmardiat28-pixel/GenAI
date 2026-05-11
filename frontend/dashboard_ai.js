// frontend/dashboard_ai.js

document.addEventListener('DOMContentLoaded', () => {
    // --- INIT: LOAD SAVED STATE DARI LOCALSTORAGE ---
    const savedBg = localStorage.getItem('dashboard_bg_color');
    const savedText = localStorage.getItem('dashboard_text_color');
    
    if (savedBg) {
        let classes = document.body.className.split(" ").filter(c => !c.startsWith("bg-"));
        classes.push(savedBg);
        document.body.className = classes.join(" ");
    }
    if (savedText) {
        let classes = document.body.className.split(" ").filter(c => !c.startsWith("text-"));
        classes.push(savedText);
        document.body.className = classes.join(" ");
    }

    const chatToggleBtn = document.getElementById('chat-toggle-btn');
    const chatContainer = document.getElementById('chat-container');
    const closeChat = document.getElementById('close-chat');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatMessages = document.getElementById('chat-messages');

    // --- 1. TOGGLE UI ---
    if (chatToggleBtn && chatContainer && closeChat) {
        chatToggleBtn.addEventListener('click', () => {
            chatContainer.classList.toggle('hidden');
            if (!chatContainer.classList.contains('hidden')) chatInput.focus();
        });
        closeChat.addEventListener('click', () => chatContainer.classList.add('hidden'));
    }

    // --- 2. SCRAPER KHUSUS DASHBOARD (BISA BACA DETAIL FILM) ---
    function getDashboardContext() {
        let contextData = {};
        
        // Cek apakah user sedang melihat halaman Detail atau Dashboard
        const detailView = document.getElementById('detail-view');
        const isDetailActive = detailView && detailView.style.display === 'block';

        if (isDetailActive && typeof currentDetailMovie !== 'undefined' && currentDetailMovie) {
            // Jika sedang buka detail film, kirim data filmnya ke AI
            contextData = {
                halaman_aktif: "Movie Detail Page",
                film_yang_sedang_dilihat: currentDetailMovie
            };
        } else {
            // Jika di Dashboard utama
            contextData = {
                halaman_aktif: "Movie Inventory Dashboard (Utama)"
            };

            if (typeof allMovies !== 'undefined') {
                const kpis = document.querySelectorAll('.metric-card');
                contextData.susunan_kpi = Array.from(kpis).map(el => ({
                    id: el.id,
                    judul: el.querySelector('.metric-title')?.innerText || "",
                    nilai: el.querySelector('.metric-value')?.innerText || "",
                    posisi: el.style.order || "0"
                }));
                contextData.total_inventaris_ditampilkan = allMovies.length;
                
                // Beritahu AI film apa saja yang ada di halaman tabel saat ini
                if (typeof currentPage !== 'undefined' && typeof rowsPerPage !== 'undefined') {
                    const start = currentPage * rowsPerPage;
                    contextData.film_di_tabel_saat_ini = allMovies.slice(start, start + rowsPerPage).map(m => m.title);
                }
            }
        }
        return JSON.stringify(contextData);
    }

    // --- 3. BULLETPROOF UI & TABLE CHANGER ---
    function applyAIChanges(data) {
        if (!data) return;
        const layout = data.layout || data;

        // 1. GANTI WARNA (Anti Halusinasi & LocalStorage)
        const bgColor = layout.bg_color || layout.theme?.bg_color;
        const textColor = layout.text_color || layout.theme?.text_color;

        if (bgColor && typeof bgColor === 'string' && bgColor.startsWith("bg-") && bgColor !== "null") {
            let currentClasses = document.body.className.split(" ").filter(c => !c.startsWith("bg-"));
            currentClasses.push(bgColor);
            document.body.className = currentClasses.join(" ");
            
            localStorage.setItem('dashboard_bg_color', bgColor);
            
            if (!textColor || textColor === "null" || !textColor.startsWith("text-")) {
                const darkThemes = ['900', '800', '700', '600', '500', 'dark', 'black'];
                const isDark = darkThemes.some(color => bgColor.includes(color));
                const newTextColor = isDark ? 'text-slate-100' : 'text-slate-900';
                
                currentClasses = document.body.className.split(" ").filter(c => !c.startsWith("text-"));
                currentClasses.push(newTextColor);
                document.body.className = currentClasses.join(" ");
                
                localStorage.setItem('dashboard_text_color', newTextColor);
            }
        }

        if (textColor && typeof textColor === 'string' && textColor.startsWith("text-") && textColor !== "null") {
            let currentClasses = document.body.className.split(" ").filter(c => !c.startsWith("text-"));
            currentClasses.push(textColor);
            document.body.className = currentClasses.join(" ");
            localStorage.setItem('dashboard_text_color', textColor);
        }

        // 2. UBAH POSISI KPI (Disimpan di localStorage)
        const positions = layout.kpi_positions || layout.positions;
        if (positions && Array.isArray(positions) && positions.length > 0) {
            positions.forEach(item => {
                const el = document.getElementById(item.id);
                if (el && item.order !== undefined && item.order !== null) {
                    el.style.order = item.order;
                }
            });
            localStorage.setItem('dashboard_kpi_positions', JSON.stringify(positions));
        }

        // 3. UBAH POSISI DIAGRAM 
        if (layout.diagram_position && typeof layout.diagram_position === 'string' && layout.diagram_position !== "null") {
            const diagramPos = layout.diagram_position.toLowerCase();
            
            const chartSection = document.querySelector('[id="chart-container"]')?.parentElement;
            const metricsContainer = document.getElementById('metrics-container');
            
            if (chartSection && metricsContainer && chartSection.parentElement === metricsContainer.parentElement) {
                const parent = metricsContainer.parentElement;
                
                if (diagramPos === 'atas') {
                    parent.insertBefore(chartSection, metricsContainer);
                } else if (diagramPos === 'bawah') {
                    metricsContainer.parentNode.insertBefore(chartSection, metricsContainer.nextElementSibling);
                }
            }
        }

        // 4. FILTER TABEL 
        if (layout.table_filter !== undefined && layout.table_filter !== null && typeof layout.table_filter === 'string' && layout.table_filter !== "null" && typeof allMovies !== 'undefined') {
            if (typeof window.originalMovies === 'undefined') {
                window.originalMovies = [...allMovies];
            }
            
            const keyword = layout.table_filter.toLowerCase().trim();
            
            if (keyword === "") {
                allMovies = [...window.originalMovies];
            } else {
                allMovies = window.originalMovies.filter(m => 
                    (m.title && m.title.toLowerCase().includes(keyword)) ||
                    (m.genre && m.genre.toLowerCase().includes(keyword)) ||
                    (m.rating && m.rating.toLowerCase().includes(keyword))
                );
            }
            
            if (typeof currentPage !== 'undefined') currentPage = 0;
            if (typeof renderTable === 'function') {
                renderTable();
                setTimeout(() => {
                    document.getElementById('table-container').scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 100);
            }
        }

        // 5. UBAH TIPE DIAGRAM (Disimpan di localStorage)
        if (layout.diagram_type && ['bar', 'pie', 'line'].includes(layout.diagram_type.toLowerCase())) {
            localStorage.setItem('dashboard_diagram_type', layout.diagram_type.toLowerCase());
            
            if (typeof renderChart === 'function') {
                renderChart(); 
            }
        }
    }

    // --- 4. CHAT LOGIC ---
    function appendMessage(role, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'} mb-4`;
        msgDiv.innerHTML = `<div class="max-w-[85%] p-3 rounded-xl text-sm shadow-sm transition-colors ${
            role === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 'bg-white text-slate-800 border border-slate-200 rounded-bl-none'
        }">${text}</div>`;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function handleChat() {
        const prompt = chatInput.value.trim();
        if (!prompt) return;

        appendMessage('user', prompt);
        chatInput.value = '';

        const loadingId = 'loading-' + Date.now();
        const loadingDiv = document.createElement('div');
        loadingDiv.id = loadingId;
        loadingDiv.className = 'text-xs text-slate-400 italic mb-4 ml-2 animate-pulse';
        loadingDiv.innerText = 'AI Dashboard sedang menganalisis...';
        chatMessages.appendChild(loadingDiv);

        try {
            const response = await fetch('http://127.0.0.1:8000/chat-dashboard', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: prompt,
                    dashboard_context: getDashboardContext()
                })
            });

            const data = await response.json();
            document.getElementById(loadingId)?.remove();

            console.log("Raw AI Response:", data);

            if (data.message) appendMessage('ai', data.message);
            
            applyAIChanges(data.layout || data);

        } catch (error) {
            document.getElementById(loadingId)?.remove();
            console.error("Error Detail:", error);
            appendMessage('ai', "❌ Gagal terhubung ke endpoint atau terjadi error pada UI.");
        }
    }

    sendBtn.addEventListener('click', handleChat);
    chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleChat(); });
});