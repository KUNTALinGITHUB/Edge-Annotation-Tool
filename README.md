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
   <img width="1355" height="768" alt="Capture" src="https://github.com/user-attachments/assets/3facc7ab-822a-4d72-95c6-d6f1992a02e1" />

2. Install dependencies:

pip install -r requirements.txt


requirements.txt

pillow

🛠️ Usage

Load Labels (e.g., labels.txt with one class per line).

Load Folder (select the folder with images).

Annotate polygons by clicking on points. Close polygon by clicking near the first point.

Save (S) → annotations saved in annotations/ folder.

📷 Screenshot

📊 Annotation Formats

YOLO-Seg TXT →

class_id x_center y_center width height x1 y1 x2 y2 x3 y3 ...


JSON →

{
  "version": "1.0",
  "imagePath": "image1.jpg",
  "imageWidth": 1280,
  "imageHeight": 720,
  "shapes": [
    {
      "label": "car",
      "points": [[100, 150], [200, 160], [210, 300]],
      "shape_type": "polygon"
    }
  ]
}

🤝 Contributing

Pull requests and feature requests are welcome!
For major changes, please open an issue first.


