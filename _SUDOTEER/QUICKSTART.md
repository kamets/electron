# 🚀 _SUDOTEER Web UI - Quick Start Guide

**Version**: 1.0 (Web Server)
**Status**: Development Mode

---

## ✅ **Step 1: Start the Server**

Open PowerShell and run:

```powershell
cd c:\Users\NAMAN\electron\_SUDOTEER
.\.venv\Scripts\python.exe webserver.py
```

**You should see**:
```
============================================================
  _SUDOTEER Web Server
============================================================

[SERVER] Starting at: http://localhost:8888
[FILES] Serving frontend from: C:\Users\NAMAN\electron\_SUDOTEER\frontend\views

[OPEN] Open in browser: http://localhost:8888

Press Ctrl+C to stop
```

**Server is running when you see**: `Uvicorn running on http://0.0.0.0:8888`

---

## 🌐 **Step 2: Open in Browser**

**Best browsers** (in order):
1. **Chrome** - Best WebSocket support
2. **Edge** - Good compatibility
3. Firefox - Works, but slower WebSockets

**URL**: http://localhost:8888

---

## 🎨 **Step 3: What You Should See**

### **Top Bar**:
- `_SUDOTEER | Industrial Agency` (title)
- System health LED (green dot, pulsing)

### **Center**:
- Large blue pulsing orb (Architect agent)
- "Ready to coordinate protocols" text

### **Workflow Chain** (bottom):
- 5 boxes: Coder → Tester → Doc → Validator → Seeker

### **Stats Cards** (right side):
- CPU usage
- Memory
- Temperature

### **Greenhouse Panel** (bottom-left):
- Temperature gauge
- Humidity %
- pH level with color bar
- Pump control button

---

## 🔧 **Step 4: What Works Right Now**

### ✅ **Working**:
- Static UI loads
- Glassmorphism styling
- Animations (pulse, glow)
- Layout responsive

### ⚠️ **Needs Fixing** (we'll do this next):
- WebSocket connection (real-time data)
- Pump button functionality
- Live telemetry updates

---

## 🐛 **Troubleshooting**

### **"Server won't start" / Port in use**:
```powershell
# Kill existing server
Get-Process -Name python | Where-Object {$_.Path -like "*venv*"} | Stop-Process -Force

# Then restart
.\.venv\Scripts\python.exe webserver.py
```

### **"Page not found"**:
- Check server is running (see console output)
- Use exactly: `http://localhost:8888` (not 127.0.0.1)

### **"UI looks broken"**:
- Hard refresh: `Ctrl + F5`
- Clear cache: `Ctrl + Shift + Delete`

---

## 📝 **Next Steps (After Opening)**

1. **Take a screenshot** - Show me what you see
2. **Open browser console** - Press F12, check for errors
3. **Tell me what doesn't work** - I'll fix it

---

## 🛑 **To Stop Server**

In the PowerShell window where it's running:
- Press `Ctrl + C`
- Wait for "Application shutdown complete"

---

## 💡 **Development Mode Features**

**Auto-reload** (when you edit files):
- HTML/CSS/JS changes = Just refresh browser (F5)
- Python changes = Restart server (Ctrl+C, then run again)

**Debug mode**:
- Check server logs in PowerShell window
- Check browser console (F12) for frontend errors

---

**Ready to test?** Open http://localhost:8000 and tell me what you see!
