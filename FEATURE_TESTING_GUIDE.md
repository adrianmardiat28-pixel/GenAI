# 🎬 Movie Intelligence Dashboard - Feature Testing Guide

## ✅ Semua 5 Fitur Sudah Diimplementasikan

### Lokasi File yang Berubah:
- **Backend**: `backend/chat_dashboard_api.py` (System instruction diperkuat)
- **Frontend**: `frontend/dashboard_ai.js` (applyAIChanges function diperbaiki)

---

## 📋 Test Scenarios untuk Semua 5 Fitur

### **FITUR 1: GANTI WARNA BACKGROUND** 🎨

**Trigger Kalimat yang Bisa Dipakai:**
```
✓ "ubah jadi warna biru"
✓ "tema gelap"
✓ "warna orange saja"
✓ "background hitam"
✓ "jadi warna ungu"
```

**Expected Result:**
- Background berubah ke warna yang diminta (Tailwind class)
- Text color auto-adjust untuk contrast (gelap/terang)
- Transition halus (0.7s ease)

**Test:**
1. Buka dashboard di browser
2. Klik tombol chat AI (bawah kanan)
3. Ketik: `"ubah background jadi biru gelap"`
4. ✅ Lihat background berubah warna dalam 1 detik

---

### **FITUR 2: UBAH POSISI KPI (Total Film, Rata-rata Harga, Total Genre)** 📦

**Trigger Kalimat yang Bisa Dipakai:**
```
✓ "tukar posisi Total Film dan Total Genre"
✓ "pindahkan rata-rata harga ke awal"
✓ "ubah urutan kotak KPI"
✓ "genre paling kanan"
```

**Expected Result:**
- 3 kotak KPI berubah urutan sesuai `order` yang dikirim
- Animasi flex reorder terjadi
- Posisi baru permanen sampai diminta ubah lagi

**Test:**
1. Amati urutan KPI saat ini: Total Film | Rata-rata Harga | Total Genre
2. Ketik: `"tukar posisi, genre paling depan"`
3. ✅ Urutan berubah jadi: Total Genre | Total Film | Rata-rata Harga
4. Refresh halaman: posisi kembali default ✓

---

### **FITUR 3: ANALISIS DIAGRAM (Jawab Pertanyaan Tentang Chart)** 📊

**Trigger Pertanyaan yang Bisa Dipakai:**
```
✓ "kenapa durasi film berbeda-beda per rating?"
✓ "rating mana yang paling panjang?"
✓ "jelaskan diagram durasi"
✓ "film R rated berapa menit rata-rata?"
✓ "apa insight dari chart ini?"
```

**Expected Result:**
- AI jawab berdasarkan data dari database (BUKAN halusinasi)
- Referensi ke data_diagram_durasi_rating
- Natural, logis, dan akurat sesuai DB

**Test:**
1. Ketik: `"rating mana yang punya durasi paling pendek?"`
2. ✅ AI lihat DB data dan jawab dengan akurat (misal: "G-rated rata-rata...")
3. Coba tanya tentang film yang tidak ada di chart → AI bilang tidak ada data

---

### **FITUR 4: FILTER TABEL BERDASARKAN GENRE/RATING** 🔍

**Trigger Kalimat yang Bisa Dipakai:**
```
✓ "tampilkan film horor saja"
✓ "filter PG-13"
✓ "cari film drama"
✓ "yang action aja"
✓ "hapus filter" (untuk clear)
```

**Expected Result:**
- Tabel film di-filter berdasarkan keyword
- Bahasa Indonesia auto-translate ke English (horor → Horror)
- Page reset ke halaman 1
- Smooth scroll ke tabel
- Show hanya matching films

**Test:**
1. Ketik: `"tampilkan film horror saja"`
2. ✅ Tabel langsung filtered, hanya film Horror ditampilkan
3. Ketik: `"filter PG-13"`
4. ✅ Tabel berubah ke PG-13 films saja
5. Ketik: `"hapus filter"`
6. ✅ Semua film kembali ditampilkan

---

### **FITUR 5: UBAH POSISI DIAGRAM (Chart Repositioning + Explanation)** 📈

**Trigger Kalimat yang Bisa Dipakai:**
```
✓ "pindahkan diagram ke atas"
✓ "grafik di bawah KPI"
✓ "chart di atas saja"
✓ "ubah urutan diagram dan metrik"
```

**Expected Result:**
- Diagram (Plotly chart) berpindah ke atas ATAU bawah KPI cards
- AI jelaskan ALASAN (UX logic atau data insight)
- Perubahan persisten (sampai refresh)
- Message: Jelaskan apa yang berubah dan mengapa

**Test:**
1. Ketik: `"pindahkan diagram ke atas"`
2. ✅ Chart (Rata-rata Durasi) naik ke atas (di atas KPI cards)
3. AI respond: `"Diagram dipindahkan ke atas untuk visibilitas lebih baik..."`
4. Ketik: `"kenapa diagram di atas lebih baik?"`
5. ✅ AI jawab berdasarkan UX logic, bukan database

---

## 🚨 GUARDRAILS & ERROR HANDLING

### Test Out-of-Context Rejection:
```
❌ Ketik: "apa itu buah?"
✅ AI akan reject: "Saya hanya bisa membantu dengan dashboard movie..."
```

### Test Anti-Hallucination:
```
❌ Jangan berubah jika tidak diminta
✓ Ketik: "halo" (tanpa instruksi perubahan)
✅ AI jawab tanpa mengubah UI
```

### Test Invalid Values Handling:
```
❌ Ketik: "ubah warna jadi xyz" (invalid class)
✅ Frontend ignore, nilai tetap null
```

---

## 🔧 Debugging Tips

### Jika Fitur Tidak Bekerja:

1. **Diagram tidak berpindah?**
   - Check browser console: `F12 → Console`
   - Verify `#chart-container` exists di HTML
   - Check Plotly script loaded: `typeof Plotly !== 'undefined'`

2. **Warna tidak berubah?**
   - Check `document.body.className` di console
   - Verify Tailwind CSS loaded
   - Check `bg_color` value di AI response (harus `bg-xxx` format)

3. **Filter tidak jalan?**
   - Check `window.allMovies.length` di console
   - Verify `window.originalMovies` backed up
   - Check keyword di console log

4. **KPI tidak reorder?**
   - Check element IDs match: `kpi-total-film`, `kpi-avg-price`, `kpi-total-genre`
   - Verify CSS `order` property applied: `el.style.order = 1`

### Network Debug:
```javascript
// Di browser console, liat response dari AI:
fetch('http://127.0.0.1:8000/chat-dashboard', {...})
  .then(r => r.json())
  .then(d => console.log(d)) // Lihat layout object
```

---

## ✅ FINAL VERIFICATION CHECKLIST

Sebelum declare success, pastikan:

- [ ] ✅ **Fitur 1**: Warna berubah ketika diminta (minimal 3 warna berbeda tested)
- [ ] ✅ **Fitur 2**: KPI reorder berhasil (test tukar minimal 2 posisi)
- [ ] ✅ **Fitur 3**: AI jawab pertanyaan diagram dari DB data (bukan halusinasi)
- [ ] ✅ **Fitur 4**: Filter table works (test horror, PG-13, clear filter)
- [ ] ✅ **Fitur 5**: Diagram pindah atas/bawah + AI explain alasannya
- [ ] ✅ **Bonus**: Out-of-context rejection bekerja
- [ ] ✅ **Bonus**: No unwanted UI changes ketika tidak diminta

---

## 📞 Support Info

**Jika ada error:**
1. Cek backend running: `uvicorn backend.app:app --reload`
2. Cek GROQ API key valid
3. Check database connection
4. Clear browser cache (Ctrl+Shift+Del)
5. Restart frontend (refresh page)

**API Endpoint Test:**
```bash
curl -X POST http://127.0.0.1:8000/chat-dashboard \
  -H "Content-Type: application/json" \
  -d '{"prompt": "ubah warna biru", "dashboard_context": "{}"}'
```

---

## 📊 Feature Completion Status

| Fitur | Status | Test Date | Notes |
|-------|--------|-----------|-------|
| Ganti Warna | ✅ Implemented | - | Tailwind classes validated |
| Ubah Posisi KPI | ✅ Implemented | - | CSS order property works |
| Analisis Diagram | ✅ Implemented | - | DB integration done |
| Filter Tabel | ✅ Implemented | - | Genre translation ready |
| Ubah Posisi Diagram | ✅ Implemented | - | Plotly repositioning fixed |

---

## 🎉 READY FOR TESTING!

Semua 5 fitur sudah siap ditest. Good luck! 🚀
