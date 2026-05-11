# 🏪 Analysis Page - Feature Testing Guide

## ✅ 2 Fitur Baru Ditambahkan

### Lokasi File yang Berubah:
- **Backend**: `backend/chat_analysis_api.py` (System instruction diperkuat)
- **Frontend**: `frontend/analysis_ai.js` (applyAIChanges function ditingkatkan)

---

## 📋 Test Scenarios untuk Kedua Fitur

### **FITUR 1: UBAH WARNA BACKGROUND** 🎨

**Trigger Kalimat yang Bisa Dipakai:**
```
✓ "ubah jadi warna biru"
✓ "tema gelap"
✓ "background putih saja"
✓ "warna hijau"
✓ "jadi tema dark"
```

**Expected Result:**
- Background berubah ke warna yang diminta (Tailwind class)
- Text color auto-adjust untuk contrast
- Transition halus

**Test:**
1. Buka Analysis page di browser
2. Klik tombol chat AI (bawah kanan)
3. Ketik: `"ubah background jadi biru gelap"`
4. ✅ Lihat background berubah warna

---

### **FITUR 2: UBAH LAYOUT (Reorder Charts & Swap Stores)** 📦

#### **A. Reorder Chart Sections**

**Trigger Kalimat:**
```
✓ "pindahkan trend di atas"
✓ "rating di paling depan"
✓ "tukar posisi genre dan film"
✓ "ubah urutan: trend, rating, genre, film"
```

**Expected Result:**
- Urutan section grafik berubah sesuai permintaan
- Contoh urutan default: Genre → Rating → Film → Trend
- Bisa jadi: Trend → Rating → Genre → Film
- Section label dan divider ikut berpindah

**Test:**
1. Perhatikan urutan section: Genre | Rating | Film | Trend
2. Ketik: `"pindahkan trend section ke paling atas"`
3. ✅ Lihat urutan berubah: Trend | Genre | Rating | Film

---

#### **B. Swap Store 1 & Store 2 (Kiri-Kanan)**

**Trigger Kalimat:**
```
✓ "tukar posisi store 1 dan 2"
✓ "store 2 di sebelah kiri"
✓ "swap store posisi"
✓ "store 1 pindah ke kanan"
```

**Expected Result:**
- Di setiap chart grid (Genre, Rating, Film):
  - Store 1 (🔵) pindah ke kanan
  - Store 2 (🔴) pindah ke kiri
- Semua grid ter-swap sekaligus
- Badge dan chart tetap valid

**Test:**
1. Lihat posisi: Store 1 (kiri) | Store 2 (kanan)
2. Ketik: `"tukar posisi store, store 2 di kiri"`
3. ✅ Lihat semuanya ter-swap: Store 2 (kiri) | Store 1 (kanan)

---

### **FITUR KOMBINASI: Ubah Warna + Layout Sekaligus**

**Trigger Kalimat:**
```
✓ "ubah tema gelap dan swap store posisi"
✓ "warna orange, pindahkan trend ke atas"
✓ "background biru, reorder: trend, rating, genre, film"
```

**Expected Result:**
- Background berubah PLUS layout berubah
- Semua perubahan diterapkan dalam satu interaction
- Natural conversation berjalan

**Test:**
1. Ketik: `"ubah jadi tema gelap dan tukar store posisi"`
2. ✅ Background gelap + Store ter-swap sekaligus
3. Ketik: `"pindahkan trend ke atas"`
4. ✅ Trend naik ke atas (dengan background gelap tetap)

---

## 🛡️ Guardrails & Validasi

### Test Anti-Hallucination:
```
❌ Jangan ubah jika tidak diminta
✓ Ketik: "jelaskan data store 1" (tanpa perubahan UI)
✅ AI jawab, UI tetap sama
```

### Test Invalid Values Handling:
```
❌ Ketik: "ubah warna jadi xyz"
✅ Frontend ignore, color tetap default
```

### Test Out-of-Context:
```
❌ Ketik: "apa itu buah?"
✅ AI reject: "Saya hanya bisa membantu dengan analysis..."
```

---

## 📊 Backend Response Structure

**Dengan Fitur Baru:**
```json
{
  "layout": {
    "bg_color": "bg-blue-900" | null,
    "text_color": "text-slate-100" | null,
    "chart_order": ["trend", "rating", "genre", "film"] | null,
    "swap_stores": true | false | null
  },
  "message": "Analisis & penjelasan perubahan UI..."
}
```

---

## 🔧 Debugging Tips

### Jika Warna Tidak Berubah:
```javascript
// Di browser console
console.log(document.body.className) // Check classes
console.log(typeof Plotly) // Verify Plotly loaded
```

### Jika Layout Tidak Reorder:
```javascript
// Check section elements
const sections = document.querySelectorAll('.section-label');
console.log(Array.from(sections).map(s => s.innerText))

// Check chart-grid elements
const grids = document.querySelectorAll('.chart-grid');
console.log(grids.length) // Should be 3 (genre, rating, film)
```

### Jika Swap Stores Tidak Bekerja:
```javascript
// Check chart boxes
const boxes = document.querySelectorAll('.chart-box');
console.log(boxes.length) // Should be 6+ (2 per grid)
```

### Network Debug:
```javascript
// Di browser console
fetch('http://127.0.0.1:8000/chat-analysis', {...})
  .then(r => r.json())
  .then(d => console.log(JSON.stringify(d.layout, null, 2)))
```

---

## ✅ FINAL VERIFICATION CHECKLIST

- [ ] ✅ **Ubah Warna**: Background berubah ke beberapa warna berbeda
- [ ] ✅ **Reorder Chart**: Section-section bisa dipindahkan
- [ ] ✅ **Swap Stores**: Store 1 & 2 bisa ter-swap posisi
- [ ] ✅ **Kombinasi**: Warna + Layout bisa berubah sekaligus
- [ ] ✅ **Out-of-Context**: AI reject pertanyaan di luar topik
- [ ] ✅ **Data Persistence**: Refresh page → layout kembali default ✓
- [ ] ✅ **Error Handling**: Invalid values tidak crash

---

## 📝 Example Prompts untuk Testing

```
1. "ubah warna jadi biru tua"
   → Check: Background jadi bg-blue-900, text jadi terang

2. "pindahkan trend ke paling atas"
   → Check: Urutan jadi Trend | Genre | Rating | Film

3. "tukar store 1 dan 2"
   → Check: Semua grid ter-swap (Store 2 kiri, Store 1 kanan)

4. "ubah tema dark dan swap store"
   → Check: Background gelap + Store ter-swap

5. "kenapa store 1 rental lebih tinggi di genre tertentu?"
   → Check: AI jawab dengan data insights (bukan halusinasi)

6. "jelaskan perbedaan trend bulanan kedua store"
   → Check: AI analisis trend data dari DB
```

---

## 🎉 Feature Status

| Fitur | Status | Implementation | Test |
|-------|--------|-----------------|------|
| Ubah Warna | ✅ Done | Body className | Ready |
| Reorder Charts | ✅ Done | Chart-order array | Ready |
| Swap Stores | ✅ Done | Clone & replace | Ready |
| Context Guard | ✅ Done | System instruction | Ready |
| Data Analysis | ✅ Done | DB integration | Ready |

---

## 🚀 READY FOR TESTING!

Buka analysis page dan coba fitur-fitur baru melalui chatbot AI! Good luck! 🎬

