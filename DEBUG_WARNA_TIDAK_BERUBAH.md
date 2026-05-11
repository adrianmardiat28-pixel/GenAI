# 🐛 Debug - Warna Tidak Berubah

Jika warna tidak berubah, ikuti langkah-langkah ini untuk debug:

## 1️⃣ Buka Browser Console

**Di halaman Analysis:**
- Tekan: `F12` (atau Ctrl+Shift+I pada Windows)
- Buka tab: **Console**
- Klik di jendela console untuk fokus

## 2️⃣ Test Warna Melalui Chatbot

Ketik di chatbot:
```
ubah background jadi merah, warnanya tetap putih
```

## 3️⃣ Lihat Debug Logs di Console

Kamu akan lihat output seperti:

```
📩 Server Response: {
  layout: {
    bg_color: "bg-red-600",
    text_color: "text-white",
    chart_order: null,
    swap_stores: null
  },
  message: "Background diubah ke merah dengan text putih..."
}

🎨 Layout data found, applying changes...
🖼️ Applying AI Changes: {
  bg_color: "bg-red-600",
  text_color: "text-white",
  ...
}
Colors: { bgColor: 'bg-red-600', textColor: 'text-white' }
✅ Applying bg_color: bg-red-600
New body className: bg-red-600 text-white
✅ Applying explicit text_color: text-white
New body className: bg-red-600 text-white
```

## 4️⃣ Checklist Debugging

### Jika Console Error:

**Error 1: "Cannot read property 'layout' of undefined"**
- ✅ Cek: Endpoint `/chat-analysis` running?
- ✅ Cek: Backend return valid JSON?
- ✅ Solution: Refresh page, try again

**Error 2: "JSON.parse error"**
- ✅ Backend return JSON dalam markdown code block?
- ✅ AI return plain text bukan JSON?
- ✅ Solution: Cek API response di backend logs

**Error 3: Layout data tidak found**
- Lihat "Server Response" di console
- Cek apakah "layout" key ada di response
- Jika tidak, backend perlu fix

### Jika Background Tidak Berubah (Tapi Tidak Error):

**Check 1: Apakah bg_color correct?**
```javascript
// Di console, ketik:
console.log(document.body.className)
// Lihat apakah ada 'bg-red-600' (atau warna apapun)
```

**Check 2: Apakah Tailwind CSS loaded?**
```javascript
// Di console, ketik:
console.log(typeof Tailwind)
// Seharusnya return "object", bukan "undefined"
```

**Check 3: Apakah CSS actual effect?**
```javascript
// Di console, ketik:
const bgClass = document.body.className.split(" ").find(c => c.startsWith("bg-"));
const computedColor = window.getComputedStyle(document.body).backgroundColor;
console.log('bg class:', bgClass);
console.log('computed BG color:', computedColor);
// Lihat RGB value berubah atau tidak
```

## 5️⃣ Manual Test di Console

Untuk test warna change tanpa chatbot:

```javascript
// Langsung ubah className
document.body.className += " bg-blue-900 text-white";

// Check hasil
console.log(document.body.className);
console.log(window.getComputedStyle(document.body).backgroundColor);
```

Jika ini berhasil, berarti Tailwind bekerja dan masalah ada di AI response parsing.

## 6️⃣ Test API Response Langsung

Gunakan curl di terminal untuk test:

```bash
curl -X POST http://127.0.0.1:8000/chat-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "ubah background merah, text putih",
    "dashboard_context": "{\"halaman_aktif\": \"test\"}"
  }' | python -m json.tool
```

Pastikan response format:
```json
{
  "layout": {
    "bg_color": "bg-red-600",  // HARUS ada
    "text_color": "text-white",  // HARUS ada
    "chart_order": null,
    "swap_stores": null
  },
  "message": "..."
}
```

## 7️⃣ Restart Services

Jika semuanya terlihat benar tapi masih tidak bekerja:

```bash
# Terminal 1: Kill backend
Ctrl+C

# Terminal 1: Restart backend
cd backend
python app.py

# Browser: Refresh page
Ctrl+F5 (hard refresh)

# Try again
```

## 📝 Common Issues & Solutions

| Issue | Debug | Solution |
|-------|-------|----------|
| Warna tidak berubah | Lihat `New body className` di console | Check apakah `bg-` class ada |
| Error di JSON parse | Lihat `Server Response` | Backend return JSON yang benar? |
| Tailwind tidak bekerja | Check `computed BG color` RGB | Include CSS di HTML head? |
| Chat tidak respond | Network error? | Check backend running & CORS |

## 📞 Hubungi Untuk Help

Jika sudah coba semua tapi masih tidak bekerja:

1. **Screenshot console logs** - kirim ke developer
2. **Backend logs** - cek apa error message
3. **Network tab** - lihat response JSON di DevTools Network tab

Good luck debugging! 🚀
