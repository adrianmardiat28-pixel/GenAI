// frontend/ai_chat.js
// AI Data Analyst — Chart Generator + Deep Analysis + Color Persistence

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const chatInput = document.getElementById('ai-chat-input');
    const sendBtn = document.getElementById('ai-send-btn');
    const chatMessages = document.getElementById('ai-chat-messages');
    const chartsGrid = document.getElementById('ai-charts-grid');
    const emptyState = document.getElementById('ai-empty-state');
    const clearBtn = document.getElementById('ai-clear-charts');

    // Storage Keys
    const STORAGE_KEY = 'ai_page_charts';
    const HISTORY_KEY = 'ai_page_chat_history';
    const THEME_KEY = 'ai_page_theme';

    // ==========================================
    // 1. STORAGE UTILITIES (localStorage)
    // ==========================================
    function saveCharts(charts) {
        try { localStorage.setItem(STORAGE_KEY, JSON.stringify(charts)); } 
        catch (e) { console.warn('localStorage save failed:', e); }
    }

    function loadCharts() {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            return stored ? JSON.parse(stored) : [];
        } catch (e) { return []; }
    }

    function saveChatHistory(messages) {
        try { localStorage.setItem(HISTORY_KEY, JSON.stringify(messages.slice(-30))); } 
        catch (e) { console.warn('Chat history save failed:', e); }
    }

    function loadChatHistory() {
        try {
            const stored = localStorage.getItem(HISTORY_KEY);
            return stored ? JSON.parse(stored) : [];
        } catch (e) { return []; }
    }

    function savePageTheme(theme) {
        try { localStorage.setItem(THEME_KEY, JSON.stringify(theme)); } 
        catch (e) { console.warn('Theme save failed:', e); }
    }

    function loadPageTheme() {
        try {
            const stored = localStorage.getItem(THEME_KEY);
            return stored ? JSON.parse(stored) : null;
        } catch (e) { return null; }
    }

    // ==========================================
    // 2. THEME HANDLER
    // ==========================================
    function applyPageTheme(theme) {
        if (!theme) return;

        const root = document.documentElement;
        const body = document.body;

        if (theme.bg_color) {
            body.style.background = theme.bg_color;
            const header = document.querySelector('.ai-header');
            if (header) {
                header.style.background = theme.bg_color === '#ffffff' 
                    ? 'rgba(255, 255, 255, 0.8)' 
                    : theme.bg_color;
            }
            const chatPanel = document.querySelector('.ai-chat-panel');
            if (chatPanel) {
                chatPanel.style.background = theme.bg_color === '#ffffff' 
                    ? 'rgba(255, 255, 255, 0.9)' 
                    : theme.bg_color;
            }
        }

        if (theme.text_color) {
            body.style.color = theme.text_color;
            root.style.setProperty('--text-color', theme.text_color);
        }

        if (theme.accent_color) {
            root.style.setProperty('--accent-color', theme.accent_color);
        }

        console.log('[AI Page] Theme applied:', theme);
        savePageTheme(theme);
    }

    // ==========================================
    // 3. CHART HELPERS (Icons & Colors)
    // ==========================================
    function getChartIcon(type) {
        const icons = {
            'bar': '📊', 'line': '📈', 'pie': '🥧', 'scatter': '🔵',
            'histogram': '📉', 'box': '📦', 'heatmap': '🌡️',
            'funnel': '🔽', 'treemap': '🌳'
        };
        return icons[type] || '📊';
    }

    function generateDefaultColors(count) {
        const palette = [
            '#6366f1', '#8b5cf6', '#a78bfa', '#c084fc',
            '#e879f9', '#f472b6', '#fb7185', '#f87171',
            '#fb923c', '#fbbf24', '#a3e635', '#34d399',
            '#2dd4bf', '#22d3ee', '#38bdf8', '#60a5fa'
        ];
        const colors = [];
        for (let i = 0; i < count; i++) {
            colors.push(palette[i % palette.length]);
        }
        return colors;
    }

    function hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    // ==========================================
    // 4. OLD GRID CHART LOGIC (Kept for compatibility)
    // ==========================================
    function renderChart(chartSpec, index) {
        if (!chartsGrid) return; // Prevent error if grid is removed from HTML
        const containerId = `ai-chart-${index}`;

        const card = document.createElement('div');
        card.className = 'ai-chart-card';
        card.id = `ai-chart-card-${index}`;
        card.innerHTML = `
            <div class="ai-chart-header">
                <div class="ai-chart-title-row">
                    <span class="ai-chart-icon">${getChartIcon(chartSpec.type)}</span>
                    <h3 class="ai-chart-title">${chartSpec.title || 'Chart'}</h3>
                </div>
                <div class="ai-chart-actions">
                    <span class="ai-chart-type-badge">${chartSpec.type || 'bar'}</span>
                    <button class="ai-chart-delete-btn" onclick="deleteChart(${index})" title="Hapus chart">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M18 6L6 18M6 6l12 12"/>
                        </svg>
                    </button>
                </div>
            </div>
            <div id="${containerId}" class="ai-chart-body"></div>
        `;
        chartsGrid.appendChild(card);
        // Rendering logic...
        renderPlotlyInline(containerId, chartSpec); 
    }

    function renderAllCharts() {
        if (!chartsGrid) return;
        const charts = loadCharts();
        chartsGrid.innerHTML = '';

        if (charts.length === 0) {
            if(emptyState) emptyState.style.display = 'flex';
            if(clearBtn) clearBtn.style.display = 'none';
            return;
        }

        if(emptyState) emptyState.style.display = 'none';
        if(clearBtn) clearBtn.style.display = 'inline-flex';

        charts.forEach((chart, i) => renderChart(chart, i));
    }

    window.deleteChart = function(index) {
        const charts = loadCharts();
        charts.splice(index, 1);
        saveCharts(charts);
        renderAllCharts();
    };

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            if (confirm('Hapus semua chart?')) {
                saveCharts([]);
                renderAllCharts();
            }
        });
    }

    function applyChartUpdates(updates) {
        if (!updates || !Array.isArray(updates) || updates.length === 0) return;
        const charts = loadCharts();
        let changed = false;

        updates.forEach(update => {
            const idx = update.chart_index;
            if (idx !== undefined && idx >= 0 && idx < charts.length && update.new_colors) {
                charts[idx].colors = update.new_colors;
                changed = true;
            }
        });

        if (changed) {
            saveCharts(charts);
            renderAllCharts();
        }
    }

    // ==========================================
    // 5. INLINE CHAT MESSAGES & PLOTLY
    // ==========================================
    function renderPlotlyInline(containerId, chartSpec) {
        const data = chartSpec.data || [];
        if (data.length === 0) return;

        const xCol = chartSpec.x_column;
        const yCol = chartSpec.y_column;
        const type = chartSpec.type || 'bar';
        const colors = chartSpec.colors || generateDefaultColors(data.length);

        let traces = [];

        // Logika khusus untuk masing-masing tipe chart
        if (type === 'pie') {
            traces = [{
                labels: data.map(d => d[xCol]), // Pie wajib pakai labels
                values: data.map(d => d[yCol]), // Pie wajib pakai values
                type: 'pie',
                hole: 0.45, // Membuatnya jadi Donut chart agar lebih elegan
                marker: { colors: colors },
                textinfo: 'label+percent',
                textposition: 'outside'
            }];
        } else if (type === 'line') {
            traces = [{
                x: data.map(d => d[xCol]),
                y: data.map(d => d[yCol]),
                type: 'scatter',
                mode: 'lines+markers',
                line: { color: colors[0] || '#6366f1', width: 3, shape: 'spline' },
                marker: { size: 6, color: colors[0] || '#6366f1' }
            }];
        } else {
            // Default untuk Bar, Scatter biasa, dll
            traces = [{
                x: data.map(d => d[xCol]),
                y: data.map(d => d[yCol]),
                type: type === 'scatter' ? 'scatter' : 'bar',
                mode: type === 'scatter' ? 'markers' : undefined,
                marker: { color: colors.length >= data.length ? colors : colors[0] || '#6366f1' }
            }];
        }

        const layout = {
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { family: 'Inter, sans-serif', color: '#94a3b8', size: 12 },
            margin: { t: 30, b: 50, l: 50, r: 50 },
            autosize: true,
            showlegend: type === 'pie', // Tampilkan legend khusus pie chart
            legend: { orientation: 'h', y: -0.2 }
        };

        Plotly.newPlot(containerId, traces, layout, { displayModeBar: false, responsive: true });
    }
    function appendMessage(role, text, charts = []) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `ai-msg ai-msg-${role}`;

        let formattedText = text;
        if (role === 'ai') {
            formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            formattedText = formattedText.replace(/^- /gm, '• ');
            formattedText = formattedText.replace(/^(\d+)\. /gm, '<span class="ai-list-num">$1.</span> ');
            formattedText = formattedText.replace(/\n/g, '<br>');
        }

        const chatTimestamp = Date.now();
        let chartsHTML = '';
        
        if (charts && charts.length > 0) {
            charts.forEach((chart, index) => {
                const chartId = `inline-chart-${chatTimestamp}-${index}`;
                chartsHTML += `
                    <div class="ai-chart-card" style="margin-top: 1rem; width: 100%; min-width: 400px;">
                        <div class="ai-chart-header">
                            <div class="ai-chart-title-row">
                                <span class="ai-chart-icon">${getChartIcon(chart.type)}</span>
                                <h3 class="ai-chart-title">${chart.title || 'Chart'}</h3>
                            </div>
                            <span class="ai-chart-type-badge">${chart.type || 'bar'}</span>
                        </div>
                        <div id="${chartId}" class="ai-chart-body" style="min-height: 300px;"></div>
                    </div>
                `;
            });
        }

        msgDiv.innerHTML = `
            <div class="ai-msg-bubble ai-msg-bubble-${role}" style="${role === 'ai' ? 'width: 100%; max-width: 90%;' : ''}">
                ${role === 'ai' ? '<div class="ai-msg-avatar">🤖</div>' : ''}
                <div class="ai-msg-content" style="${role === 'ai' ? 'width: 100%;' : ''}">
                    <div>${formattedText}</div>
                    ${chartsHTML}
                </div>
            </div>
        `;
        
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        if (charts && charts.length > 0) {
            setTimeout(() => {
                charts.forEach((chart, index) => {
                    const chartId = `inline-chart-${chatTimestamp}-${index}`;
                    renderPlotlyInline(chartId, chart);
                });
                chatMessages.scrollTop = chatMessages.scrollHeight; 
            }, 100);
        }

        const history = loadChatHistory();
        history.push({ role, text: text, charts: charts });
        saveChatHistory(history);
    }

    // ==========================================
    // 6. MAIN CHAT HANDLER
    // ==========================================
    async function handleChat() {
        const prompt = chatInput.value.trim();
        if (!prompt) return;

        appendMessage('user', prompt);
        chatInput.value = '';
        sendBtn.disabled = true;

        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'ai-msg ai-msg-ai';
        loadingDiv.id = 'ai-loading-msg';
        loadingDiv.innerHTML = `
            <div class="ai-msg-bubble ai-msg-bubble-ai">
                <div class="ai-msg-avatar">🤖</div>
                <div class="ai-msg-content ai-loading-dots">
                    <span class="ai-dot"></span><span class="ai-dot"></span><span class="ai-dot"></span>
                    <span class="ai-loading-text">AI sedang menganalisis database...</span>
                </div>
            </div>
        `;
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const res = await fetch('/api/chat-ai', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: prompt, existing_charts: [] })
            });

            const data = await res.json();
            document.getElementById('ai-loading-msg')?.remove();
            sendBtn.disabled = false;

            if (data.message) {
                appendMessage('ai', data.message, data.charts || []);
            }
            if (data.page_theme) applyPageTheme(data.page_theme);

        } catch (e) {
            document.getElementById('ai-loading-msg')?.remove();
            sendBtn.disabled = false;
            appendMessage('ai', '❌ Gagal terhubung ke server. Pastikan backend berjalan.');
        }
    }

    // ==========================================
    // 7. EVENT LISTENERS
    // ==========================================
    
    // Kirim Chat via Tombol
    if (sendBtn) {
        sendBtn.addEventListener('click', handleChat);
    }

    // Kirim Chat via Enter Keyboard
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleChat();
            }
        });
    }

    // Suggestion Chips Click
    document.querySelectorAll('.ai-suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            chatInput.value = chip.dataset.prompt;
            chatInput.focus();
            handleChat(); // Langsung kirim saat dipencet
        });
    });

// ==========================================
    // 8. INITIALIZATION
    // ==========================================
    function restoreChatHistory() {
        const history = loadChatHistory();
        chatMessages.innerHTML = ''; // Bersihkan area chat dulu
        
        history.forEach((msg, msgIndex) => {
            const msgDiv = document.createElement('div');
            msgDiv.className = `ai-msg ai-msg-${msg.role}`;

            let formattedText = msg.text;
            if (msg.role === 'ai') {
                formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                formattedText = formattedText.replace(/^- /gm, '• ');
                formattedText = formattedText.replace(/^(\d+)\. /gm, '<span class="ai-list-num">$1.</span> ');
                formattedText = formattedText.replace(/\n/g, '<br>');
            }

            // Bikin ID unik pakai index dan waktu agar chart tidak bentrok
            const timestamp = Date.now();
            let chartsHTML = '';
            
            if (msg.charts && msg.charts.length > 0) {
                msg.charts.forEach((chart, chartIndex) => {
                    const chartId = `history-chart-${timestamp}-${msgIndex}-${chartIndex}`;
                    chartsHTML += `
                        <div class="ai-chart-card" style="margin-top: 1rem; width: 100%; min-width: 400px;">
                            <div class="ai-chart-header">
                                <div class="ai-chart-title-row">
                                    <span class="ai-chart-icon">${getChartIcon(chart.type)}</span>
                                    <h3 class="ai-chart-title">${chart.title || 'Chart'}</h3>
                                </div>
                                <span class="ai-chart-type-badge">${chart.type || 'bar'}</span>
                            </div>
                            <div id="${chartId}" class="ai-chart-body" style="min-height: 300px;"></div>
                        </div>
                    `;
                });
            }

            msgDiv.innerHTML = `
                <div class="ai-msg-bubble ai-msg-bubble-${msg.role}" style="${msg.role === 'ai' ? 'width: 100%; max-width: 90%;' : ''}">
                    ${msg.role === 'ai' ? '<div class="ai-msg-avatar">🤖</div>' : ''}
                    <div class="ai-msg-content" style="${msg.role === 'ai' ? 'width: 100%;' : ''}">
                        <div>${formattedText}</div>
                        ${chartsHTML}
                    </div>
                </div>
            `;
            
            chatMessages.appendChild(msgDiv);

            // Render chart menggunakan Plotly setelah HTML dimasukkan
            if (msg.charts && msg.charts.length > 0) {
                setTimeout(() => {
                    msg.charts.forEach((chart, chartIndex) => {
                        const chartId = `history-chart-${timestamp}-${msgIndex}-${chartIndex}`;
                        renderPlotlyInline(chartId, chart);
                    });
                }, 100); // Jeda sedikit agar DOM siap
            }
        });

        // Pastikan scroll langsung turun ke pesan paling bawah
        setTimeout(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 200);
    }
    
    // Jangan lupa panggil fungsinya di baris paling akhir file JS kamu
    restoreChatHistory();
    renderAllCharts(); // Render old charts if any still exist in UI
});