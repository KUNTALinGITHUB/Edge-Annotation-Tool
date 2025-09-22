import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
from PIL import Image, ImageTk
import os
import json
import math

class EdgeAnnotator:
    def __init__(self, root):
        self.root = root
        self.root.title("Edge Annotation Tool")
        self.root.geometry("1350x820")
        self.root.resizable(False, False)

        # Keyboard shortcuts
        self.root.bind("<a>", lambda e: self.prev_image())
        self.root.bind("<d>", lambda e: self.next_image())
        self.root.bind("<s>", lambda e: self.save_annotation())
        self.root.bind("<u>", lambda e: self.undo_point())
        self.root.bind("<r>", lambda e: self.reset_points())
        # self.root.bind("<l>", lambda e: self.load_labels())
        # self.root.bind("<f>", lambda e: self.load_folder())

        # Show startup instructions
        self.show_shortcuts()

        # State
        self.class_list = []
        self.class_colors = {}
        self.class_var = tk.StringVar()

        # Build UI
        self.build_ui()

        # Annotation state
        self.image_paths = []
        self.current_index = 0
        self.image = None
        self.tk_image = None
        self.current_polygon = []
        self.all_polygons = []
        self.annotations_dir = None

        # Save on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def show_shortcuts(self):
        shortcuts = (
            "📌 Keyboard Shortcuts:\n\n"
            "A → Previous Image\n"
            "D → Next Image\n"
            "S → Save Annotation\n"
            "U → Undo Last Point/Polygon\n"
            "R → Reset Annotations\n"
            # "L → Load Labels File\n"
            # "F → Load Image Folder\n"
        )
        messagebox.showinfo("Shortcut Keys", shortcuts)

    def build_ui(self):
        # --- Left: Classes (scrollable) ---
        tk.Label(self.root, text="Classes", font=("Arial", 10, "bold")).place(x=10, y=20)

        self.class_list_frame = tk.Frame(self.root)
        self.class_list_frame.place(x=10, y=50, width=160, height=300)

        self.class_listbox = tk.Listbox(self.class_list_frame, exportselection=False)
        self.class_scroll = tk.Scrollbar(self.class_list_frame, orient="vertical", command=self.class_listbox.yview)
        self.class_listbox.config(yscrollcommand=self.class_scroll.set)
        self.class_listbox.pack(side="left", fill="both", expand=True)
        self.class_scroll.pack(side="right", fill="y")

        self.class_listbox.bind("<<ListboxSelect>>", self.select_class)

        # Buttons
        self.load_labels_btn = ttk.Button(self.root, text="Load Labels", command=self.load_labels)
        self.load_labels_btn.place(x=10, y=370)

        self.load_folder_btn = ttk.Button(self.root, text="Load Folder", command=self.load_folder)
        self.load_folder_btn.place(x=10, y=410)

        self.undo_btn = ttk.Button(self.root, text="Undo (U)", command=self.undo_point)
        self.undo_btn.place(x=10, y=450)

        self.reset_btn = ttk.Button(self.root, text="Reset (R)", command=self.reset_points)
        self.reset_btn.place(x=10, y=490)

        self.save_btn = ttk.Button(self.root, text="Save (S)", command=self.save_annotation)
        self.save_btn.place(x=10, y=530)

        self.help_btn = ttk.Button(self.root, text="Help", command=self.show_shortcuts)
        self.help_btn.place(x=10, y=570)

        # --- Canvas in Center ---
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.place(x=200, y=10, width=900, height=700)

        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.h_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.config(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        # --- Right: Legend (scrollable) ---
        legend_label = tk.Label(self.root, text="Legend", font=("Arial", 10, "bold"))
        legend_label.place(x=1120, y=20)

        self.legend_container = tk.Frame(self.root, relief="groove", bd=1)
        self.legend_container.place(x=1120, y=50, width=200, height=500)

        # Create canvas + scrollbar
        self.legend_canvas = tk.Canvas(self.legend_container, width=180, height=480)
        self.legend_scroll = tk.Scrollbar(self.legend_container, orient="vertical", command=self.legend_canvas.yview)

        # Frame inside canvas
        self.legend_frame = tk.Frame(self.legend_canvas)

        # Bind resizing of inner frame to update scroll region
        self.legend_frame.bind(
            "<Configure>",
            lambda e: self.legend_canvas.configure(scrollregion=self.legend_canvas.bbox("all"))
        )

        # Place frame inside canvas
        self.legend_canvas.create_window((0, 0), window=self.legend_frame, anchor="nw")

        # Configure scrolling
        self.legend_canvas.configure(yscrollcommand=self.legend_scroll.set)

        # Pack canvas + scrollbar
        self.legend_canvas.pack(side="left", fill="both", expand=True)
        self.legend_scroll.pack(side="right", fill="y")

        # Optional: Mousewheel scroll
        def _on_mousewheel(event):
            self.legend_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.legend_canvas.bind_all("<MouseWheel>", _on_mousewheel)   # Windows/Mac
        self.legend_canvas.bind_all("<Button-4>", lambda e: self.legend_canvas.yview_scroll(-1, "units"))  # Linux
        self.legend_canvas.bind_all("<Button-5>", lambda e: self.legend_canvas.yview_scroll(1, "units"))   # Linux


        # --- Navigation Buttons ---
        self.prev_btn = ttk.Button(self.root, text="Previous (A)", command=self.prev_image)
        self.prev_btn.place(x=200, y=750)

        self.next_btn = ttk.Button(self.root, text="Next (D)", command=self.next_image)
        self.next_btn.place(x=1000, y=750)

    def load_labels(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not file_path:
            return

        with open(file_path, "r") as f:
            self.class_list = [line.strip() for line in f if line.strip()]

        if not self.class_list:
            messagebox.showerror("Error", "Labels file is empty.")
            return

        # 30-color palette
        color_palette = [
            "#FFCCCC", "#CCFFCC", "#CCCCFF", "#FFFFCC", "#FFCCFF", "#CCE5FF", "#E6FFCC", "#FFDACC",
            "#D9CCFF", "#FFB3BA", "#B3FFBA", "#BAE1FF", "#FFDFBA", "#EAD1DC", "#D5E8D4", "#FFF2CC",
            "#F8CECC", "#D4E1F5", "#F5E1D4", "#CCE8F4", "#FFD6E7", "#D6FFD6", "#D6D6FF", "#FFF0D6",
            "#FFD6F0", "#E6D6FF", "#D6FFF6", "#F0FFD6", "#FFD6CC", "#CCE6FF"
        ]

        self.class_colors = {label: color_palette[i % len(color_palette)] for i, label in enumerate(self.class_list)}

        self.class_listbox.delete(0, tk.END)
        for label in self.class_list:
            self.class_listbox.insert(tk.END, label)
        self.class_listbox.select_set(0)
        self.class_var.set(self.class_list[0])

        self.update_legend()
        messagebox.showinfo("Step 2", "Now load your image folder.")

    def update_legend(self):
        for widget in self.legend_frame.winfo_children():
            widget.destroy()

        for label in self.class_list:
            color = self.class_colors[label]
            row = tk.Frame(self.legend_frame)
            row.pack(anchor="w", pady=2, padx=2)

            swatch = tk.Label(row, bg=color, width=3, height=1, relief="ridge", cursor="hand2")
            swatch.pack(side=tk.LEFT, padx=5)
            swatch.bind("<Button-1>", lambda e, lbl=label: self.change_class_color(lbl))

            name = tk.Label(row, text=label, font=("Arial", 9))
            name.pack(side=tk.LEFT)

    def change_class_color(self, label):
        color = colorchooser.askcolor(title=f"Choose color for {label}")
        if color and color[1]:
            self.class_colors[label] = color[1]
            self.update_legend()
            self.redraw_canvas()

    def select_class(self, event):
        selection = self.class_listbox.curselection()
        if selection:
            self.class_var.set(self.class_list[selection[0]])

    def load_folder(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            messagebox.showerror("Error", "You must select an image folder.")
            return

        # collect images
        files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
        files.sort()
        self.image_paths = [os.path.join(folder_path, f) for f in files]
        if not self.image_paths:
            messagebox.showerror("Error", "No images found in the selected folder.")
            return

        self.current_index = 0
        self.annotations_dir = os.path.join(folder_path, "annotations")
        os.makedirs(self.annotations_dir, exist_ok=True)

        self.load_image()

    def load_image(self):
        if not self.image_paths:
            return

        # Clear current polygons
        self.current_polygon = []
        self.all_polygons = []
        self.canvas.delete("all")

        image_path = self.image_paths[self.current_index]
        try:
            self.image = Image.open(image_path).convert("RGBA")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image {image_path}: {e}")
            return

        self.tk_image = ImageTk.PhotoImage(self.image)

        # Update canvas scrollregion and show image
        self.canvas.config(scrollregion=(0, 0, self.image.width, self.image.height),
                           width=min(self.image.width, 800),
                           height=min(self.image.height, 700))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        # Keep a reference so image isn't garbage collected
        self.canvas.image = self.tk_image

        # bind mouse
        self.canvas.bind("<Button-1>", self.add_point)

        # Load existing annotations if present
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        json_path = os.path.join(self.annotations_dir, base_name + ".json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r") as f:
                    data = json.load(f)
                    for shape in data.get("shapes", []):
                        if shape.get("shape_type") == "polygon":
                            points = shape.get("points", [])
                            label = shape.get("label", self.class_list[0] if self.class_list else "0")
                            # ensure points are tuples of floats
                            normalized_points = []
                            for p in points:
                                if isinstance(p, (list, tuple)) and len(p) >= 2:
                                    normalized_points.append((float(p[0]), float(p[1])))
                            if normalized_points:
                                self.all_polygons.append((label, normalized_points))
                # draw loaded annotations
                self.redraw_canvas()
            except Exception as e:
                print(f"Failed to load annotation for {base_name}: {e}")

        # update window title to show which image is loaded
        self.root.title(f"Edge Annotation Tool - {os.path.basename(image_path)} ({self.current_index + 1}/{len(self.image_paths)})")

    def add_point(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        # if clicking close to starting point and polygon has >=3 points, close polygon
        if self.current_polygon:
            start_x, start_y = self.current_polygon[0]
            dist = math.hypot(x - start_x, y - start_y)
            if dist < 10 and len(self.current_polygon) >= 3:
                # commit polygon
                label = self.class_var.get() if self.class_list else "0"
                self.all_polygons.append((label, self.current_polygon.copy()))
                self.current_polygon = []
                self.redraw_canvas()
                return

        # otherwise add point
        self.current_polygon.append((x, y))
        self.redraw_canvas()

    def undo_point(self):
        if self.current_polygon:
            self.current_polygon.pop()
            self.redraw_canvas()
        else:
            # If no current polygon but there exist saved polygons, remove last polygon
            if self.all_polygons:
                self.all_polygons.pop()
                self.redraw_canvas()

    def reset_points(self):
        # Reset both in-progress polygon and all saved polygons for this image
        if messagebox.askyesno("Confirm", "Clear all annotations for this image?"):
            self.current_polygon = []
            self.all_polygons = []
            self.redraw_canvas()

    def redraw_canvas(self):
        # Clear and redraw image + polygons
        self.canvas.delete("all")
        if self.tk_image:
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        # Draw saved polygons
        for label, polygon in self.all_polygons:
            color = self.class_colors.get(label, "#DDDDDD")
            coords = [coord for point in polygon for coord in point]
            # create_polygon expects a flat sequence - supply it
            if len(coords) >= 6:  # at least 3 points
                self.canvas.create_polygon(coords, fill=color, outline="green", width=2)

        # Draw current polygon points and lines
        for i, (x, y) in enumerate(self.current_polygon):
            r = 3
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="red", outline="")
            if i > 0:
                x_prev, y_prev = self.current_polygon[i - 1]
                self.canvas.create_line(x_prev, y_prev, x, y, fill="blue", width=2)

    def save_annotation(self):
        # Save only when image loaded and there is something to save
        if not self.image_paths or not self.image:
            return

        # combine any in-progress polygon (if user closed it by mistake) - we won't auto-commit; require explicit commit
        if not self.all_polygons and not self.current_polygon:
            # nothing to save: remove any existing annotation files for cleanliness
            base_name = os.path.splitext(os.path.basename(self.image_paths[self.current_index]))[0]
            json_path = os.path.join(self.annotations_dir, base_name + ".json")
            txt_path = os.path.join(self.annotations_dir, base_name + ".txt")
            # do not remove without user consent
            return

        img_w, img_h = self.image.size
        base_name = os.path.splitext(os.path.basename(self.image_paths[self.current_index]))[0]
        json_data = {
            "version": "1.0",
            "imagePath": os.path.basename(self.image_paths[self.current_index]),
            "imageWidth": img_w,
            "imageHeight": img_h,
            "shapes": []
        }

        txt_lines = []

        for label, polygon in self.all_polygons:
            # save polygon points as rounded ints for JSON
            json_data["shapes"].append({
                "label": label,
                "points": [[round(float(x)), round(float(y))] for x, y in polygon],
                "shape_type": "polygon"
            })

            x_coords = [x for x, y in polygon]
            y_coords = [y for x, y in polygon]
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)

            x_center = ((x_min + x_max) / 2) / img_w
            y_center = ((y_min + y_max) / 2) / img_h
            width = (x_max - x_min) / img_w
            height = (y_max - y_min) / img_h

            polygon_norm = []
            for x, y in polygon:
                polygon_norm.append(x / img_w)
                polygon_norm.append(y / img_h)

            # class_id fallback if label missing in class_list
            try:
                class_id = self.class_list.index(label)
            except ValueError:
                class_id = 0

            yolo_line = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f} " + \
                        " ".join([f"{coord:.6f}" for coord in polygon_norm])
            txt_lines.append(yolo_line)

        # Save JSON
        try:
            with open(os.path.join(self.annotations_dir, base_name + ".json"), "w") as f:
                json.dump(json_data, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save JSON annotation: {e}")
            return

        # Save YOLOSeg TXT
        try:
            with open(os.path.join(self.annotations_dir, base_name + ".txt"), "w") as f:
                f.write("\n".join(txt_lines))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save TXT annotation: {e}")
            return

        print(f"Saved annotations for {base_name}")

    def _save_current_and_proceed(self, new_index):
        # internal helper: save current, then go to new index
        # Save only if there are polygons to save
        try:
            # if annotations dir exists and we have polygons, save
            if self.annotations_dir:
                self.save_annotation()
        except Exception as e:
            print(f"Warning: failed to save before navigation: {e}")

        self.current_index = new_index
        # clamp index
        self.current_index = max(0, min(self.current_index, len(self.image_paths) - 1))
        self.load_image()

    def next_image(self):
        if not self.image_paths:
            return
        if self.current_index < len(self.image_paths) - 1:
            self._save_current_and_proceed(self.current_index + 1)
        else:
            messagebox.showinfo("Info", "This is the last image.")

    def prev_image(self):
        if not self.image_paths:
            return
        if self.current_index > 0:
            self._save_current_and_proceed(self.current_index - 1)
        else:
            messagebox.showinfo("Info", "This is the first image.")

    def on_close(self):
        # Ask user whether to save before exit if there are annotations
        try:
            if self.all_polygons:
                if messagebox.askyesno("Save", "Save annotations before exiting?"):
                    self.save_annotation()
        except Exception:
            pass
        self.root.destroy()

# --- Run the App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = EdgeAnnotator(root)
    root.mainloop()


#pip install pillow==11.3.0