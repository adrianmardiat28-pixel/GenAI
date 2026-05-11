// frontend/analysis_ai.js
document.addEventListener('DOMContentLoaded', () => {
    // --- 1. DEFINISIKAN SEMUA ELEMEN ---
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatMessages = document.getElementById('chat-messages');
    const chatToggleBtn = document.getElementById('chat-toggle-btn');
    const chatContainer = document.getElementById('chat-container');
    const closeChat = document.getElementById('close-chat');
    const mainContent = document.getElementById('main-content');

    // --- 2. TOGGLE UI LOGIC ---
    if (chatToggleBtn && chatContainer) {
        chatToggleBtn.onclick = () => {
            chatContainer.classList.toggle('hidden');
            if (!chatContainer.classList.contains('hidden')) chatInput.focus();
        };
    }

    if (closeChat) {
        closeChat.onclick = () => chatContainer.classList.add('hidden');
    }

    // --- 3. APPLY AI CHANGES (MODUL KONTROL UI) ---
    // frontend/analysis_ai.js (Ganti bagian applyAIChanges saja)

    // frontend/analysis_ai.js

function applyAIChanges(layout) {
    if (!layout) return;

    // 1. Warna (HANYA reload jika warna BARU berbeda dengan yang lama)
    if (layout.bg_color && layout.bg_color !== "null") {
        const currentSavedBg = localStorage.getItem('analysis_bg_color');
        
        // Cek apakah warna dari AI berbeda dengan yang sudah tersimpan
        if (layout.bg_color !== currentSavedBg) {
            localStorage.setItem('analysis_bg_color', layout.bg_color);
            console.log("Warna baru dideteksi, me-refresh halaman...");
            location.reload(); 
            return; // Berhenti di sini agar tidak bentrok dengan proses lain
        }
    }

    // 2. Tipe Diagram (Tanpa Reload, Langsung Berubah)
    if (layout.diagram_type && layout.diagram_type !== "null") {
        // AI harus mengirimkan target_chart (genre, rating, film, atau trend)
        const target = layout.target_chart || 'genre'; 
        
        localStorage.setItem(`${target}_chart_type`, layout.diagram_type);
        console.log(`Mengubah grafik ${target} menjadi ${layout.diagram_type}`);
        
        if (typeof window.refreshCharts === 'function') {
            window.refreshCharts(target);
        }
    }

    // 3. Swap Posisi Store
    if (layout.store_position && layout.store_position !== "null") {
        const currentSwap = localStorage.getItem('analysis_store_swap');
        if (layout.store_position !== currentSwap) {
            localStorage.setItem('analysis_store_swap', layout.store_position);
            if (typeof renderStorePositions === 'function') {
                renderStorePositions();
            }
        }
    }
}

    // --- 4. CHAT LOGIC ---
    async function handleChat() {
        const prompt = chatInput.value.trim();
        if (!prompt) return;

        chatMessages.innerHTML += `
            <div class="flex justify-end mb-4">
                <div class="bg-blue-600 text-white p-3 rounded-xl rounded-br-none text-sm shadow-sm max-w-[85%]">
                    ${prompt}
                </div>
            </div>`;
        
        chatInput.value = '';
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const res = await fetch('http://127.0.0.1:8000/chat-analysis', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: prompt, dashboard_context: "Halaman Analysis Store" })
            });
            const data = await res.json();
            
            chatMessages.innerHTML += `
                <div class="flex justify-start mb-4">
                    <div class="bg-white border border-slate-200 p-3 rounded-xl rounded-bl-none text-sm shadow-sm max-w-[85%] text-slate-800">
                        ${data.message}
                    </div>
                </div>`;
            
            chatMessages.scrollTop = chatMessages.scrollHeight;

            if (data.layout) applyAIChanges(data.layout);
        } catch (e) { 
            console.error("Error Chat AI:", e); 
        }
    }

    // --- 5. EVENT LISTENERS ---
    if (sendBtn) {
        sendBtn.onclick = handleChat;
    }

    if (chatInput) {
        chatInput.onkeypress = (e) => { 
            if (e.key === 'Enter') handleChat(); 
        };
    }

    // --- 6. AUTO LOAD PREFERENCES ---
    const savedBg = localStorage.getItem('analysis_bg_color');
    const savedText = localStorage.getItem('analysis_text_color');
    if (savedBg && mainContent) {
        document.body.classList.add(savedBg, savedText);
        mainContent.classList.add(savedBg);
    }
});