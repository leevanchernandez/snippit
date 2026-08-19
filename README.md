
# Snippit ✂️

A lightweight, cross-platform snipping tool with built-in offline AI background removal.

<img width="1280" height="720" alt="snippit" src="https://github.com/user-attachments/assets/17b96e32-222a-4709-9acf-7f4ce825be87" />

---

## ✨ Features (Phase 1)

- 📸 **Global Hotkey Trigger**: Instant screen freeze with `Win+Alt+S`.
- 🖥️ **Multi-Monitor Support**: Spans all connected displays seamlessly.
- 🎯 **Rubber-Band Selector**: Drag-and-drop crop with real-time dimension badge (`W × H px`) and dimmed backdrop.
- 📋 **Immediate Clipboard Copy**: Raw snapshot is instantly available in the clipboard in both standard bitmap and alpha-preserved PNG MIME formats.
- 🪄 **Floating Action Toolbar**: Post-capture pill widget with **Save** and **Close**, plus auto-dismiss on inactivity.
- 🗔 **System Tray Residency**: Unobtrusive tray icon with quick capture and settings access.
- 🧪 **Offline First**: Zero cloud dependencies or telemetry.

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository and navigate into directory
cd Snippit

# Create virtual environment & activate
python -m venv .venv
.venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the App

```bash
python -m snippit
```

### Running Tests

```bash
pytest -v
```

---

## ⌨️ Controls & Shortcuts

| Action | Shortcut |
|---|---|
| **Trigger Screen Capture** | `Win+Alt+S` (or tray icon click) |
| **Select Region** | Left Click + Drag |
| **Cancel Selection** | `Escape` or Right Click |
| **Dismiss Toolbar** | `Escape` or `✕` button |
| **Save Snippet** | Click `💾 Save` on floating toolbar |

---

## 🗺️ Roadmap

- [x] **Phase 1**: Core Snipping Tool (Tray, Hotkey, Freeze Overlay, Rubber-Band, Clipboard, Floating Toolbar).
- [ ] **Phase 2**: Offline AI Background Removal with `rembg` session cache & background worker.
- [ ] **Phase 3**: UX polish, HiDPI refinement, custom hotkey settings dialog.
- [ ] **Phase 4**: Standalone PyInstaller & Nuitka binary packaging.
