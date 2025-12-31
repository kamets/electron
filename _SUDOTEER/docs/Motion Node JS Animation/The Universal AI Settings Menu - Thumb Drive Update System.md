### Part 1: The "Universal AI" Settings Menu

You need a Settings page in Electron that saves keys to a secure config file, and a Python backend that acts as a "Router" to send your prompt to the right place.

#### 1. The React Settings UI

Create a new view in your app called `Settings.js`. This creates a `config.json` file that persists even if you restart the app.

```python
import React, { useState, useEffect } from 'react';

export default function Settings() {
  const [keys, setKeys] = useState({
    selectedProvider: 'gemini', // 'gemini', 'openai', 'local'
    geminiKey: '',
    openaiKey: '',
    localEndpoint: 'http://localhost:11434/v1', // Default for Ollama
  });

  // Load saved settings on startup
  useEffect(() => {
    window.electronAPI.getSettings().then((saved) => {
      if (saved) setKeys(saved);
    });
  }, []);

  const handleSave = () => {
    window.electronAPI.saveSettings(keys);
    alert("Settings Saved & AI Reconnected!");
  };

  return (
    <div style={{ padding: '40px', color: 'white' }}>
      <h2>AI Brain Configuration</h2>
      
      {/* 1. SELECT THE ACTIVE BRAIN */}
      <div style={{ marginBottom: '20px' }}>
        <label>Active Model Provider:</label>
        <select 
          value={keys.selectedProvider}
          onChange={(e) => setKeys({...keys, selectedProvider: e.target.value})}
          style={{ marginLeft: '10px', padding: '5px' }}
        >
          <option value="gemini">Google Gemini</option>
          <option value="openai">OpenAI (GPT-4)</option>
          <option value="local">Local LLM (Ollama/Llama 3)</option>
        </select>
      </div>

      {/* 2. ENTER KEYS */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', maxWidth: '400px' }}>
        <input 
          type="password" 
          placeholder="Gemini API Key"
          value={keys.geminiKey}
          onChange={(e) => setKeys({...keys, geminiKey: e.target.value})}
        />
        <input 
          type="password" 
          placeholder="OpenAI API Key"
          value={keys.openaiKey}
          onChange={(e) => setKeys({...keys, openaiKey: e.target.value})}
        />
        <input 
          type="text" 
          placeholder="Local URL (e.g. http://localhost:11434)"
          value={keys.localEndpoint}
          onChange={(e) => setKeys({...keys, localEndpoint: e.target.value})}
        />
      </div>

      <button onClick={handleSave} style={{ marginTop: '20px', padding: '10px 20px' }}>
        Save Configuration
      </button>
    </div>
  );
}
```

#### 2. The Python "Router"

In your `greenhouse_backend.py`, you need a function that checks which provider is selected and routes the traffic.

```python
import google.generativeai as genai
import openai
import requests

class AIGateway:
    def __init__(self, config):
        self.config = config # Load from that JSON file
        
    def ask_ai(self, prompt):
        provider = self.config.get('selectedProvider')
        
        try:
            if provider == 'gemini':
                genai.configure(api_key=self.config['geminiKey'])
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(prompt)
                return response.text
                
            elif provider == 'openai':
                client = openai.OpenAI(api_key=self.config['openaiKey'])
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
                
            elif provider == 'local':
                # Talking to Ollama or LM Studio locally
                url = f"{self.config['localEndpoint']}/chat/completions"
                payload = {
                    "model": "llama3", 
                    "messages": [{"role": "user", "content": prompt}]
                }
                response = requests.post(url, json=payload)
                return response.json()['choices'][0]['message']['content']
                
        except Exception as e:
            return f"AI Error: {str(e)}"
```

---

## Part 2: The "Thumb Drive" Update System (Seamless)

This is a classic industrial requirement. You want to walk up to the greenhouse, plug in a USB stick, hit "Update," and walk away.

The trick to "not erasing anything" (like your API keys or calibration data) is **Folder Separation**.

### 1. The Folder Structure

You must structure your app on the hard drive (or SD card) like this:

```Plaintext
/GreenhouseSystem
    /App (Code)       <-- THIS gets deleted and replaced every update
    /Data (User)      <-- THIS is NEVER touched by the updater
        settings.json (Your API keys live here)
        logs/
        calibration.db
```

If you put `settings.json` inside the `App` folder, an update will wipe it. Always keep them separate.

#### 2. The Update Logic (The "Swapper")

You don't need complex server code. You can write a simple Node.js script in your Electron main process that looks for a specific file.

**Scenario:** You put a file named `update.zip` on a USB stick.

**The Logic flow:**

1. User clicks "Scan for Update" in Electron Settings.
    
2. Electron scans connected drives for `update.zip`.
    
3. **Validation:** It unzips it to a temporary folder (`/temp_update`).
    
4. **The Swap:**
    
    - It deletes the contents of `/GreenhouseSystem/App`.
        
    - It moves the contents of `/temp_update` to `/GreenhouseSystem/App`.
        
5. **The Restart:** It commands the app to reboot.
    

Because `/GreenhouseSystem/Data` was outside that folder, your API keys and pump calibration settings are still there when it wakes up.

#### 3. Why this is "Air-Gap" Safe

This approach is perfect for security. Since the update comes from a physical stick you control, you don't have to worry about the greenhouse downloading a malicious update from the internet automatically. It only updates when you physically permit it.

---





## Thumb Drive Updater.

This is the most robust way to handle it. We solve the "File Locking" problem (you can't delete a program while it is running) by using a **"Swap Script."**

When you click "Update," the app won't try to update itself directly. Instead, it will:

1. Find the `update.zip` on the USB drive.
    
2. Unzip it to a temporary spot.
    
3. Write a tiny `.bat` (Windows) or `.sh` (Mac/Linux) script.
    
4. Launch that script and **kill itself immediately**.
    
5. The script waits 2 seconds, moves the new files into place, and re-launches the app.
    

### 1. The Dependencies

You need one library to handle the unzipping. Run this in your project folder:

```bash
npm install adm-zip
```

### 2. The Update Logic (Add to `main.js`)

Add this block to your `main.js`. It listens for the command from your UI.

```javascript
const fs = require('fs');
const path = require('path');
const { app, ipcMain } = require('electron');
const AdmZip = require('adm-zip');
const { spawn } = require('child_process');

// Define where your User Data lives (Keep this separate from code!)
// In development: ./data. In production: AppData or adjacent folder.
const DATA_DIR = path.join(__dirname, '../Data'); 
const APP_DIR = __dirname; // The folder containing main.js, renderer, etc.

ipcMain.handle('perform-usb-update', async (event) => {
  try {
    // 1. SCAN FOR USB DRIVE (Simplified logic)
    // On Windows, drives are D:, E:, F:, etc. On Mac/Linux: /Volumes or /media
    // We look for a specific file: 'greenhouse_update.zip'
    let updateFile = null;
    const potentialDrives = ['D:\\', 'E:\\', 'F:\\', 'G:\\', '/Volumes/USB', '/media/usb'];
    
    for (const drive of potentialDrives) {
      const candidate = path.join(drive, 'greenhouse_update.zip');
      if (fs.existsSync(candidate)) {
        updateFile = candidate;
        break;
      }
    }

    if (!updateFile) {
      return { success: false, message: "No 'greenhouse_update.zip' found on USB." };
    }

    // 2. UNZIP TO TEMP FOLDER
    console.log(`Found update at: ${updateFile}`);
    const tempDir = path.join(app.getPath('temp'), 'gh_update_stage');
    
    // Clean old temp if exists
    if (fs.existsSync(tempDir)) fs.rmSync(tempDir, { recursive: true, force: true });
    fs.mkdirSync(tempDir);

    const zip = new AdmZip(updateFile);
    zip.extractAllTo(tempDir, true);

    // 3. CREATE THE SWAP SCRIPT
    // This script runs AFTER the app closes.
    const isWindows = process.platform === 'win32';
    const scriptPath = path.join(tempDir, isWindows ? 'update.bat' : 'update.sh');
    
    const executablePath = process.execPath; // Path to your currently running .exe

    if (isWindows) {
      // Windows Batch Script
      const batContent = `
        @echo off
        timeout /t 3 /nobreak > NUL
        echo Updating Greenhouse System...
        xcopy "${tempDir}\\*" "${APP_DIR}" /E /H /Y
        echo Restarting...
        start "" "${executablePath}"
        exit
      `;
      fs.writeFileSync(scriptPath, batContent);
    } else {
      // Linux/Mac Bash Script
      const shContent = `
        #!/bin/bash
        sleep 3
        cp -R "${tempDir}/" "${APP_DIR}/"
        "${executablePath}" &
        exit 0
      `;
      fs.writeFileSync(scriptPath, shContent);
      fs.chmodSync(scriptPath, '755'); // Make executable
    }

    // 4. LAUNCH SCRIPT AND QUIT
    console.log("Launching swap script and quitting...");
    
    const subprocess = spawn(scriptPath, [], {
      detached: true,
      stdio: 'ignore',
      shell: isWindows // Required for .bat files
    });
    
    subprocess.unref(); // Allow script to run after we die
    app.quit(); // Suicide to release file locks

    return { success: true };

  } catch (error) {
    console.error(error);
    return { success: false, message: error.message };
  }
});
```

### 3. The React Trigger (Settings Page)

In your `Settings.js` (or wherever you put the button):

```javascript
const handleUpdate = async () => {
  if (!confirm("Are you sure you want to update from USB? The system will restart.")) return;

  setIsUpdating(true);
  
  // Call the main process
  const result = await window.electronAPI.invoke('perform-usb-update');
  
  if (!result.success) {
    alert("Update Failed: " + result.message);
    setIsUpdating(false);
  }
  // If success, the app will close itself, so no need to do anything else.
};

return (
  <button onClick={handleUpdate} disabled={isUpdating}>
    {isUpdating ? "Installing..." : "Install Update from USB"}
  </button>
);
```

_(Note: You will need to add `invoke` to your `preload.js` whitelist similar to how we did `send`)_.

### Why this is safe for your Data

Notice the `xcopy` command in step 3. It copies the _extracted code_ into your `APP_DIR`.

As long as your `settings.json` (API Keys) and `calibration.db` are stored in a separate folder (like the `DATA_DIR` variable I defined above, or `%APPDATA%`), the update script **will not touch them**. It only overwrites the application code files.

### Here is the updated `preload.js`.

I have added the **`invoke`** command. The difference between `send` and `invoke` is critical here:

- **`send` (Fire and Forget):** Good for "Set Pump Speed." You don't need to wait.
    
- **`invoke` (Promise/Async):** Good for "Update System" or "Get Settings." The UI pauses and waits for the Main process to reply with "Success" or "Error."
    

### Updated `preload.js`

```javascript
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // 1. ONE-WAY COMMANDS (UI -> Main -> Python)
  // Use this for hardware controls where speed matters
  sendToPython: (channel, data) => {
    const validChannels = ['set_pump_speed', 'update_threshold', 'emergency_stop'];
    if (validChannels.includes(channel)) {
      ipcRenderer.send(channel, data);
    }
  },

  // 2. TWO-WAY COMMANDS (UI <-> Main)
  // Use this when the UI needs an answer (e.g., "Did the update work?")
  invoke: (channel, data) => {
    const validChannels = [
      'perform-usb-update', // The new Update trigger
      'get-settings',       // Loading your API keys
      'save-settings'       // Saving your API keys
    ];
    if (validChannels.includes(channel)) {
      return ipcRenderer.invoke(channel, data);
    }
    return Promise.reject(new Error("Invalid IPC Channel"));
  },

  // 3. LISTENERS (Main -> UI)
  // Use this to hear back from Python (Ghost Jump fix, Status Reports)
  onPythonUpdate: (callback) => {
    ipcRenderer.on('python-data', (event, ...args) => callback(...args));
  }
});
```

### Important: The Folder Check

To make sure your "Thumb Drive Update" doesn't accidentally erase your API keys, confirm your project folder looks like this on your development machine (and the target machine):


```plaintext
/MyGreenhouseProject
   /App           <-- This is where your code lives (main.js, etc.)
   /Data          <-- CREATE THIS FOLDER MANUALLY
      settings.json
```

In your `main.js`, make sure the path to settings points to that neighbor folder, not inside `App`:

```javascript
// In main.js
const DATA_DIR = path.join(__dirname, '../Data'); // Go up one level, then into Data
```

---


Here is the logic to make your settings **persistent** and **update-proof**.

This connects the `Settings.js` frontend to a secure JSON file on your hard drive that sits _outside_ the application folder. This ensures that when you run that USB update, your API keys are not deleted.

### 1. The Backend Handlers (`main.js`)

Add this code to your `main.js` file (near the other `ipcMain` handlers). This code manages the reading and writing of the file.

```javascript
const { ipcMain, app } = require('electron');
const fs = require('fs');
const path = require('path');

// --- THE SAFE ZONE STRATEGY ---
// We go 'up' one level from the app code to find the 'Data' folder.
// Structure:
//   /GreenhouseSystem/App/  (This file lives here)
//   /GreenhouseSystem/Data/ (Your keys live here)
const DATA_DIR = path.join(__dirname, '..', 'Data');
const CONFIG_PATH = path.join(DATA_DIR, 'config.json');

// Ensure Data folder exists on startup
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

// 1. GET SETTINGS (Load on startup)
ipcMain.handle('get-settings', async () => {
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      const raw = fs.readFileSync(CONFIG_PATH, 'utf-8');
      return JSON.parse(raw);
    }
    // Default values if file doesn't exist yet
    return {
      selectedProvider: 'gemini',
      geminiKey: '',
      openaiKey: '',
      localEndpoint: 'http://localhost:11434'
    };
  } catch (err) {
    console.error("Error reading settings:", err);
    return null;
  }
});

// 2. SAVE SETTINGS (Write on click)
ipcMain.handle('save-settings', async (event, newSettings) => {
  try {
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(newSettings, null, 2));
    console.log("Settings saved to:", CONFIG_PATH);
    
    // OPTIONAL: Tell Python to reload config immediately?
    // pythonProcess.stdin.write(JSON.stringify({ action: "reload_config" }) + "\n");
    
    return { success: true };
  } catch (err) {
    console.error("Error saving settings:", err);
    return { success: false, error: err.message };
  }
});
```
### 2. The Frontend Component (`Settings.js`)

This React component automatically loads your keys when you open the page, and saves them when you click the button.

```javascript
import React, { useState, useEffect } from 'react';

export default function Settings() {
  const [loading, setLoading] = useState(true);
  const [isUpdating, setIsUpdating] = useState(false);
  
  // State for your keys
  const [config, setConfig] = useState({
    selectedProvider: 'gemini',
    geminiKey: '',
    openaiKey: '',
    localEndpoint: 'http://localhost:11434'
  });

  // 1. Load Settings on Mount
  useEffect(() => {
    window.electronAPI.invoke('get-settings')
      .then((savedConfig) => {
        if (savedConfig) setConfig(savedConfig);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load settings", err);
        setLoading(false);
      });
  }, []);

  // 2. Save Handler
  const handleSave = async () => {
    const result = await window.electronAPI.invoke('save-settings', config);
    if (result.success) {
      alert("Configuration Saved Securely!");
    } else {
      alert("Error Saving: " + result.error);
    }
  };

  // 3. Update Handler (From previous step)
  const handleUpdate = async () => {
    if (!confirm("Insert USB drive with 'greenhouse_update.zip' and click OK.")) return;
    setIsUpdating(true);
    const result = await window.electronAPI.invoke('perform-usb-update');
    if (!result.success) {
      alert("Update Failed: " + result.message);
      setIsUpdating(false);
    }
  };

  if (loading) return <div style={{color: 'white'}}>Loading Configuration...</div>;

  return (
    <div style={styles.container}>
      <h2 style={{ borderBottom: '1px solid #333', paddingBottom: '10px' }}>Global Settings</h2>

      {/* AI BRAIN SECTION */}
      <section style={styles.section}>
        <h3>AI Brain Connection</h3>
        
        <div style={styles.row}>
          <label style={styles.label}>Provider:</label>
          <select 
            value={config.selectedProvider}
            onChange={(e) => setConfig({...config, selectedProvider: e.target.value})}
            style={styles.input}
          >
            <option value="gemini">Google Gemini</option>
            <option value="openai">OpenAI (GPT-4)</option>
            <option value="local">Local LLM (Ollama)</option>
          </select>
        </div>

        <div style={styles.row}>
          <label style={styles.label}>Gemini Key:</label>
          <input 
            type="password" 
            value={config.geminiKey}
            onChange={(e) => setConfig({...config, geminiKey: e.target.value})}
            style={styles.input}
          />
        </div>

        <div style={styles.row}>
          <label style={styles.label}>OpenAI Key:</label>
          <input 
            type="password" 
            value={config.openaiKey}
            onChange={(e) => setConfig({...config, openaiKey: e.target.value})}
            style={styles.input}
          />
        </div>

        <button onClick={handleSave} style={styles.saveBtn}>Save Keys</button>
      </section>

      {/* SYSTEM UPDATE SECTION */}
      <section style={styles.section}>
        <h3>System Maintenance</h3>
        <p style={{color: '#888', fontSize: '14px'}}>
          To update, place <code>greenhouse_update.zip</code> on a USB drive.
        </p>
        <button 
          onClick={handleUpdate} 
          disabled={isUpdating}
          style={isUpdating ? styles.disabledBtn : styles.updateBtn}
        >
          {isUpdating ? "Installing Update..." : "Install Update from USB"}
        </button>
      </section>
    </div>
  );
}

// Simple Styles
const styles = {
  container: { padding: '40px', color: 'white', maxWidth: '600px' },
  section: { marginBottom: '40px', padding: '20px', backgroundColor: '#1a1a1a', borderRadius: '8px' },
  row: { marginBottom: '15px' },
  label: { display: 'block', marginBottom: '5px', color: '#aaa', fontSize: '14px' },
  input: { width: '100%', padding: '8px', backgroundColor: '#333', border: '1px solid #444', color: 'white', borderRadius: '4px' },
  saveBtn: { padding: '10px 20px', backgroundColor: '#4fd1c5', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' },
  updateBtn: { padding: '10px 20px', backgroundColor: '#f687b3', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', color: 'black' },
  disabledBtn: { padding: '10px 20px', backgroundColor: '#555', border: 'none', borderRadius: '4px', cursor: 'not-allowed' }
};
```

### What happens now?

1. **First Run:** The app looks for `../Data/config.json`. It doesn't exist, so it creates the folder and loads defaults.
    
2. **You Enter Keys:** You paste your Gemini key and hit "Save". The file `../Data/config.json` is created.
    
3. **Update Time:** You insert a USB stick and click update. The app wipes `../App` but leaves `../Data` alone.
    
4. **Restart:** The new version of the app starts up, reads `../Data/config.json`, and **your Gemini key is still there.**


# This is the final piece of the puzzle. We need to make sure your Python script knows where to look for that secure `config.json` file so it can initialize the AI models.

Here is the updated Python architecture.

### 1. The Python Logic (`greenhouse_backend.py`)

We will update the script to:

1. Find the `../Data/config.json` file.
    
2. Load the keys.
    
3. **Hot-Reload:** If you change the key in the UI, Python reloads it instantly without a restart.

```python
import sys
import json
import os
import google.generativeai as genai
from openai import OpenAI
# import requests # For local LLM calls

class AIConfigManager:
    def __init__(self):
        # Locate the Data folder relative to this script
        # Script is in /App, Config is in /Data
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(base_dir, '..', 'Data', 'config.json')
        self.config = {}
        self.reload_config()

    def reload_config(self):
        """Reads the latest keys from disk"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                print(f"[Backend] Config loaded. Provider: {self.config.get('selectedProvider')}")
            else:
                print("[Backend] Warning: config.json not found.")
        except Exception as e:
            print(f"[Backend] Config Error: {e}")

    def get_response(self, prompt):
        provider = self.config.get('selectedProvider', 'gemini')
        
        try:
            # --- GEMINI ---
            if provider == 'gemini':
                key = self.config.get('geminiKey')
                if not key: return "Error: No Gemini API Key found in settings."
                
                genai.configure(api_key=key)
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(prompt)
                return response.text

            # --- OPENAI ---
            elif provider == 'openai':
                key = self.config.get('openaiKey')
                if not key: return "Error: No OpenAI Key found."
                
                client = OpenAI(api_key=key)
                completion = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )
                return completion.choices[0].message.content

            # --- LOCAL (OLLAMA) ---
            elif provider == 'local':
                # Stub for local LLM (requests library needed)
                return "Local LLM response placeholder"
                
        except Exception as e:
            return f"AI Generation Error: {str(e)}"

# --- MAIN LOOP UPDATE ---
def main():
    ai_manager = AIConfigManager()
    
    # ... PLC init code ...

    while True:
        try:
            line = sys.stdin.readline()
            if not line: break
            
            data = json.loads(line.strip())
            
            # 1. HANDLE HARDWARE COMMANDS
            if data.get('action') == 'set_pump':
                pass # ... pump logic ...

            # 2. HANDLE CONFIG RELOAD (Sent from Electron when you click Save)
            elif data.get('action') == 'reload_config':
                ai_manager.reload_config()
                # Confirm back to UI
                print(json.dumps({"type": "status", "msg": "AI Brain Updated"}))

            # 3. HANDLE AI REQUESTS
            elif data.get('action') == 'ask_ai':
                user_prompt = data.get('prompt')
                answer = ai_manager.get_response(user_prompt)
                
                # Send answer back to UI
                print(json.dumps({
                    "type": "ai_response", 
                    "answer": answer
                }))
                
        except Exception as e:
            sys.stderr.write(f"Loop Error: {e}\n")

if __name__ == "__main__":
    main()
```
### 2. The Bridge Update (`main.js`)

Now, we need to make sure that when you click "Save" in React, we poke the Python script and say "Hey, reload your settings!"

Update your `save-settings` handler in `main.js`:

```javascript
ipcMain.handle('save-settings', async (event, newSettings) => {
  try {
    // 1. Write to disk (Persistent)
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(newSettings, null, 2));
    
    // 2. Tell Python to refresh (Live)
    if (pythonProcess) {
      const msg = JSON.stringify({ action: "reload_config" });
      pythonProcess.stdin.write(msg + "\n");
    }
    
    return { success: true };
  } catch (err) {
    return { success: false, error: err.message };
  }
});
```

### Summary of What You Have Built

You now have a complete, professional-grade "Industrial Edge AI" system:

1. **Frontend:** A React Dashboard with "Hardware Safe" sliders (Debouncing).
    
2. **Settings:** A menu to switch brains (Gemini/OpenAI) dynamically without restarting.
    
3. **Update System:** An "Air-Gapped" USB updater that preserves your keys and data.
    
4. **Backend:** A Python script that bridges the gap between high-level AI concepts and low-level PLC serial commands.

**Next Step for you:** I recommend testing the **USB Updater** first with a dummy zip file (just put a text file in a zip called `greenhouse_update.zip`) to watch the script swap the files. It is the most satisfying part of the build!