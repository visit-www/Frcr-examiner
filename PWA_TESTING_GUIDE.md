# PWA Testing Guide for FRCR Examiner

## ✅ Quick Verification Checklist

### 1. **Check Service Worker (Chrome DevTools)**
1. Open your Vercel app URL in Chrome
2. Press `F12` or `Cmd+Option+I` (Mac)
3. Go to **Application** tab
4. Left sidebar → **Service Workers**
5. Should see: ✅ `service-worker.js` - Status: **Activated and running**

### 2. **Check Manifest (Chrome DevTools)**
1. Same DevTools window
2. Left sidebar → **Manifest**
3. Should see:
   - ✅ App name: "FRCR Examiner"
   - ✅ Icons displayed (192x192, 512x512)
   - ✅ Theme color: #007bff
   - ✅ Start URL: /

### 3. **Check Console Logs**
1. Go to **Console** tab in DevTools
2. Refresh page
3. Should see:
   - ✅ `Service Worker registered successfully`
   - ✅ `PWA installation available` (if not already installed)
   - ✅ No errors in red

---

## 📱 Testing on Mobile (iOS)

### **iPhone/iPad (Safari):**
1. Open Safari
2. Navigate to your Vercel URL
3. Tap **Share button** (box with arrow)
4. Scroll down → Tap **"Add to Home Screen"**
5. Tap **"Add"**
6. ✅ App icon appears on home screen
7. Tap icon to open - should open in full screen (no Safari bars)

### **Android (Chrome):**
1. Open Chrome
2. Navigate to your Vercel URL
3. Look for **"Install app"** banner at bottom
4. Tap **"Install"**
5. Or: Menu (⋮) → **"Install app"** or **"Add to Home screen"**
6. ✅ App icon appears on home screen
7. Tap icon - opens as standalone app

---

## 🖥️ Testing on Desktop

### **Chrome (Mac/Windows/Linux):**
1. Open Chrome
2. Navigate to your Vercel URL
3. Look in address bar for **install icon** (⊕) on the right
4. Click the icon
5. Click **"Install"**
6. ✅ App opens in new window
7. ✅ Check Applications folder (Mac) or Start Menu (Windows)

### **Edge (Mac/Windows):**
1. Open Edge
2. Navigate to your Vercel URL
3. Look for **install icon** in address bar OR
4. Menu (•••) → Apps → **"Install this site as an app"**
5. ✅ App installed

### **Verify Desktop Installation:**
- Check app appears in:
  - **Mac**: Applications folder, can open with Cmd+Space → "FRCR Examiner"
  - **Windows**: Start Menu, can pin to taskbar
  - **Linux**: Application launcher

---

## 🧪 Feature Testing

### **Test 1: Offline Capabilities**
1. Open installed app
2. Open DevTools (if desktop) or use Chrome remote debugging (if mobile)
3. Go to **Network** tab
4. Toggle **"Offline"** mode
5. Refresh the page
6. ✅ Should see: "You're Offline" message
7. Toggle back online
8. ✅ App should work normally

### **Test 2: Database Safety (Critical!)**
1. Toggle **"Offline"** mode
2. Try to login
3. ✅ Should fail with error message
4. Try to create/edit anything
5. ✅ Should fail - no database operations allowed offline

### **Test 3: Caching**
1. Online: Open the app (loads from server)
2. Check Network tab - files downloaded
3. Refresh page
4. Check Network tab → many files from **Service Worker** (cached)
5. ✅ Page loads faster (using cache)

### **Test 4: Icons & Shortcuts**
**Mobile:**
1. Long-press app icon on home screen
2. ✅ Should see shortcuts: "Start Exam", "Prepare"
3. Tap shortcut → should open directly to that page

**Desktop (Chrome):**
1. Right-click app icon in dock/taskbar
2. ✅ Should see shortcuts

---

## 🔍 Troubleshooting

### **"Service Worker registration failed"**
- Check browser console for errors
- Ensure HTTPS is used (Vercel provides this automatically)
- Clear cache and hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)

### **"Install prompt doesn't appear"**
- Already installed? Check home screen/applications
- Some browsers require HTTPS and manifest to be valid
- iOS Safari: Use "Add to Home Screen" manually (no automatic prompt)

### **"App doesn't work offline"**
- Expected! Database operations require internet
- Static pages (cached) should load
- Should show "You're Offline" message

### **"Icons don't show"**
- Check DevTools → Application → Manifest
- Verify icon files exist: `/static/images/icon-192x192.png`
- Clear browser cache and reinstall

---

## 📊 Testing Checklist

Copy this and check off as you test:

```
Desktop Testing:
[ ] Chrome - Install icon visible
[ ] Chrome - App installs successfully
[ ] Chrome - App opens in standalone window
[ ] Edge - Install works
[ ] App appears in Applications/Start Menu
[ ] Service Worker registered (check DevTools)
[ ] Manifest loads correctly
[ ] No console errors

Mobile Testing:
[ ] iOS Safari - Add to Home Screen works
[ ] iOS - App icon appears on home screen
[ ] iOS - Opens in full screen (no browser bars)
[ ] Android Chrome - Install prompt appears
[ ] Android - App installs successfully
[ ] Android - Shortcuts work (long-press icon)

Feature Testing:
[ ] Offline: Shows "You're Offline" message
[ ] Offline: Cannot login (expected)
[ ] Offline: Cannot modify data (expected)
[ ] Online: Everything works normally
[ ] Caching: Pages load faster on reload
[ ] Icons: Correct icon on home screen/app menu

Security Testing:
[ ] Cannot save data while offline
[ ] Database operations require internet
[ ] No console errors about mixed content
[ ] HTTPS working (check address bar for 🔒)
```

---

## 🎉 Success Criteria

Your PWA is working correctly if:

1. ✅ **Installable** - Install prompt appears on all platforms
2. ✅ **Standalone** - Opens without browser UI
3. ✅ **Offline-aware** - Shows appropriate message when offline
4. ✅ **Database-safe** - No data operations possible offline
5. ✅ **Fast** - Loads quickly due to caching
6. ✅ **Professional** - Icon and app name appear correctly

---

## 📱 Share Testing Link

**Your App URL:** https://your-app.vercel.app

**To test on phone:**
1. Send this link to your phone (iMessage, WhatsApp, etc.)
2. Open in mobile browser
3. Follow installation steps above

**To test on different desktop:**
1. Open link in Chrome/Edge
2. Look for install icon
3. Install and test

---

## 🐛 Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Install icon not showing | Wait 5 seconds, refresh page, check manifest in DevTools |
| iOS Safari no prompt | Manual only - use Share → Add to Home Screen |
| Service Worker error | Check console, verify HTTPS, clear cache |
| Icons wrong size | Check manifest.json paths, verify files exist |
| App won't go offline | Not a bug! Database requires internet by design |
| Can't uninstall | Chrome: chrome://apps, iOS: long-press → Remove App |

---

## 🎓 Developer Notes

### Files Created:
- `/static/manifest.json` - App metadata
- `/static/service-worker.js` - Caching & offline logic
- `/static/pwa-register.js` - Service worker registration
- `/static/images/icon-*.png` - App icons
- `/templates/base.html` - Updated with PWA meta tags

### How It Works:
1. Browser loads page
2. Detects manifest.json
3. Shows install prompt (if criteria met)
4. User installs
5. Service worker caches static files
6. App works offline (limited) and loads fast

### Safety Features:
- All `/api/*` routes bypass cache
- POST/PUT/DELETE always hit server
- Offline shows clear error messages
- No local database modifications

---

**Ready to market your app? Your FRCR Examiner is now installable on all major platforms! 🚀**
