# 🖼️ Edge Annotation Tool

A lightweight **Tkinter-based polygon annotation tool** for computer vision projects.  
It allows you to label objects with polygons and automatically saves them in **YOLO-Seg format** (`.txt`) and **JSON format**.

---

## ✨ Features

- 📌 **Polygon Annotation** with mouse clicks.  
- 🎨 **Custom Colors** per class (click on legend swatches to change).  
- 📂 **Load Labels** (`labels.txt`) and Image Folders easily.  
- 💾 **Saves annotations** in:
  - `JSON` (polygon coordinates, metadata)
  - `YOLOSeg TXT` (class id, bbox, normalized polygon points)
- ⌨️ **Keyboard Shortcuts**:
  - **A** → Previous Image  
  - **D** → Next Image  
  - **S** → Save Annotation  
  - **U** → Undo last point/polygon  
  - **R** → Reset all polygons  

---

## 🖥️ Installation

1. Clone this repo:
   ```bash
   git clone https://github.com/KUNTALinGITHUB/Edge-Annotation-Tool.git
   cd Edge-Annotation-Tool
