class AppSidebar extends HTMLElement {
    connectedCallback() {
        // 1. Dapatkan nama file saat ini di URL (contoh: "prediction.html")
        // Jika kosong (hanya "/"), kita asumsikan itu "index.html"
        const currentPath = window.location.pathname.split('/').pop() || 'index.html';

        // 2. Fungsi pintar untuk mengatur warna menu yang sedang aktif
        const getLinkClass = (path) => {
            const isActive = currentPath === path;
            if (isActive) {
                // Style jika menu sedang Aktif (Warna Biru)
                return "flex items-center gap-3 p-3 text-blue-600 bg-blue-50 rounded-lg font-medium transition-all pointer-events-auto";
            } else {
                // Style jika menu Tidak Aktif (Warna Abu-abu biasa)
                return "flex items-center gap-3 p-3 text-slate-600 hover:bg-slate-50 rounded-lg transition-all pointer-events-auto";
            }
        };

        // 3. Render HTML dengan z-50 dan href yang sudah diperbaiki
        this.innerHTML = `
            <aside class="w-64 min-h-screen bg-white border-r border-slate-200 flex flex-col fixed left-0 top-0 z-50">
                <div class="p-6">
                    <h2 class="text-xs font-semibold text-slate-400 uppercase tracking-widest">App Navigation</h2>
                </div>
                <nav class="flex-1 px-4 space-y-2">
                    <!-- Perhatikan href sudah menunjuk ke file HTML yang benar -->
                    <a href="index.html" class="${getLinkClass('index.html')}">
                        <span>📊</span> Dashboard
                    </a>
                    <a href="about.html" class="${getLinkClass('about.html')}">
                        <span>ℹ️</span> About
                    </a>
                    <a href="prediction.html" class="${getLinkClass('prediction.html')}">
                        <span>🤖</span> Prediction
                    </a>
                    <a href="analysis.html" class="${getLinkClass('analysis.html')}">
                        <span>🔍</span> Analysis
                    </a>
                    <a href="revenue.html" class="${getLinkClass('revenue.html')}">
                        <span>💰</span> Revenue
                    </a>
                    <a href="actor.html" class="${getLinkClass('actor.html')}">
                        <span>🎭</span> Actor
                    </a>
                    <a href="ai.html" class="${getLinkClass('ai.html')}">
                        <span>🧠</span> AI Analyst
                    </a>
                </nav>
                <div class="p-4 border-t border-slate-100">
                    <p class="text-xs text-slate-400 text-center">v1.0.4 - Adrian M.</p>
                </div>
            </aside>
        `;
    }
}
customElements.define('app-sidebar', AppSidebar);