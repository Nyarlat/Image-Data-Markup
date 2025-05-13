import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from PIL import Image, ImageTk, ImageDraw
import numpy as np


class AnnotationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YOLO Segmentation Annotation Tool")
        self.root.geometry("1200x800")

        # Configuration
        self.image_folder = ""
        self.classes = []
        self.class_colors = {}
        self.current_image_index = -1
        self.images = []
        self.annotations = {}
        self.current_annotation_id = 0
        self.current_class = None
        self.current_polygon = []
        self.dragging_vertex = None
        self.dragging_polygon = None
        self.dragging_offset = (0, 0)
        self.ctrl_pressed = False

        # UI Setup
        self.setup_ui()

        # Bind keyboard shortcuts
        self.bind_shortcuts()

    def setup_ui(self):
        # Main frames
        self.left_frame = tk.Frame(self.root, width=200, bg='#f0f0f0')
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.right_frame = tk.Frame(self.root, bg='white')
        self.right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Left panel controls
        tk.Label(self.left_frame, text="Image Folder:", bg='#f0f0f0').pack(pady=(10, 0), anchor='w')
        self.folder_entry = tk.Entry(self.left_frame, width=25)
        self.folder_entry.pack(fill=tk.X, padx=5)

        self.browse_btn = tk.Button(self.left_frame, text="Browse", command=self.browse_folder)
        self.browse_btn.pack(pady=(0, 10), fill=tk.X)

        # Image navigation controls
        tk.Label(self.left_frame, text="Images:", bg='#f0f0f0').pack(pady=(10, 0), anchor='w')
        nav_frame = tk.Frame(self.left_frame, bg='#f0f0f0')
        nav_frame.pack(fill=tk.X, pady=(10, 0))

        self.prev_btn = tk.Button(nav_frame, text="<<", command=self.prev_image)
        self.prev_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.image_num_entry = tk.Entry(nav_frame, width=5)
        self.image_num_entry.pack(side=tk.LEFT, padx=2)
        self.image_num_entry.bind("<KeyRelease>", self.jump_to_image)

        self.next_btn = tk.Button(nav_frame, text=">>", command=self.next_image)
        self.next_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Image rename button
        self.rename_image_btn = tk.Button(self.left_frame, text="Rename Image", command=self.rename_current_image)
        self.rename_image_btn.pack(fill=tk.X, padx=5, pady=(5, 0))

        # Classes controls
        tk.Label(self.left_frame, text="Classes (1-9):", bg='#f0f0f0').pack(pady=(10, 0), anchor='w')

        classes_btn_frame = tk.Frame(self.left_frame, bg='#f0f0f0')
        classes_btn_frame.pack(fill=tk.X)

        self.add_class_btn = tk.Button(classes_btn_frame, text="Add", command=self.add_class)
        self.add_class_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.rename_class_btn = tk.Button(classes_btn_frame, text="Rename", command=self.rename_class)
        self.rename_class_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.remove_class_btn = tk.Button(classes_btn_frame, text="Remove", command=self.remove_class)
        self.remove_class_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # Import/Export buttons
        classes_io_frame = tk.Frame(self.left_frame, bg='#f0f0f0')
        classes_io_frame.pack(fill=tk.X, pady=(5, 0))

        self.import_classes_btn = tk.Button(classes_io_frame, text="Import", command=self.import_classes)
        self.import_classes_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.export_classes_btn = tk.Button(classes_io_frame, text="Export", command=self.export_classes)
        self.export_classes_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.classes_listbox = tk.Listbox(self.left_frame, height=10, selectmode=tk.SINGLE)
        self.classes_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Change class button
        self.change_class_btn = tk.Button(self.left_frame, text="Change Class to Selected",
                                          command=self.change_selected_polygon_class)
        self.change_class_btn.pack(fill=tk.X, padx=5, pady=(0, 10))

        # Annotation controls
        tk.Label(self.left_frame, text="Annotation Tools:", bg='#f0f0f0').pack(pady=(10, 0), anchor='w')

        tool_frame = tk.Frame(self.left_frame, bg='#f0f0f0')
        tool_frame.pack(fill=tk.X)

        self.delete_poly_btn = tk.Button(tool_frame, text="Delete Selected", command=self.delete_selected_polygon)
        self.delete_poly_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.clear_all_btn = tk.Button(tool_frame, text="Clear All", command=self.clear_all_annotations)
        self.clear_all_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        self.delete_image_btn = tk.Button(self.left_frame, text="Delete Image", command=self.delete_current_image)
        self.delete_image_btn.pack(fill=tk.X, padx=5, pady=(10, 0))

        # Status bar
        self.status_bar = tk.Label(self.left_frame, text="No folder selected", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                   bg='#f0f0f0')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Image canvas
        self.canvas = tk.Canvas(self.right_frame, bg='gray', cursor="cross")
        self.canvas.pack(expand=True, fill=tk.BOTH)

        # Bind canvas events
        self.canvas.bind("<Button-1>", self.canvas_left_click)
        self.canvas.bind("<Button-3>", self.canvas_right_click)
        self.canvas.bind("<Motion>", self.canvas_mouse_move)
        self.canvas.bind("<B1-Motion>", self.canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_release)
        self.canvas.bind("<Double-Button-1>", self.canvas_double_click)

        # Image display variables
        self.image_on_canvas = None
        self.image_ratio = 1.0
        self.image_position = (0, 0)

    def bind_shortcuts(self):
        # Bind number keys 1-9 to select classes
        for i in range(1, 10):
            self.root.bind(str(i), lambda event, idx=i - 1: self.select_class_by_index(idx))

        # Bind Ctrl+Z for undo
        self.root.bind("<Control-z>", self.undo_last_action)

        # Bind Ctrl key events
        self.root.bind("<Control_L>", lambda e: self.set_ctrl_state(True))
        self.root.bind("<Control_R>", lambda e: self.set_ctrl_state(True))
        self.root.bind("<KeyRelease-Control_L>", lambda e: self.set_ctrl_state(False))
        self.root.bind("<KeyRelease-Control_R>", lambda e: self.set_ctrl_state(False))

        # Bind arrow keys for navigation
        self.root.bind("<Left>", lambda e: self.prev_image())
        self.root.bind("<Right>", lambda e: self.next_image())

        # Bind Delete key to delete selected polygon
        self.root.bind("<Delete>", lambda e: self.delete_selected_polygon())

    def set_ctrl_state(self, state):
        self.ctrl_pressed = state
        if state:
            self.canvas.config(cursor="fleur")  # Change cursor when Ctrl is pressed
        else:
            self.canvas.config(cursor="cross")
            self.dragging_vertex = None

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.image_folder = folder
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)
            self.load_images()

    def load_images(self):
        if not self.image_folder:
            return

        self.images = []
        supported_formats = ('.jpg', '.jpeg', '.png', '.bmp')

        for file in os.listdir(self.image_folder):
            if file.lower().endswith(supported_formats):
                self.images.append(file)

        self.images.sort()
        self.current_image_index = -1

        if self.images:
            self.next_image()
            self.status_bar.config(text=f"Folder loaded: {len(self.images)} images")
        else:
            self.status_bar.config(text="No images found in folder")

    def load_annotations(self, image_file):
        annotation_file = os.path.splitext(image_file)[0] + ".txt"
        annotation_path = os.path.join(self.image_folder, annotation_file)

        self.annotations = {}
        self.current_annotation_id = 0

        if os.path.exists(annotation_path):
            with open(annotation_path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) < 6:  # At least class + 3 points (x,y)
                        continue

                    class_id = int(parts[0])
                    if class_id >= len(self.classes):
                        continue

                    points = list(map(float, parts[1:]))
                    normalized_points = [(points[i], points[i + 1]) for i in range(0, len(points), 2)]

                    self.annotations[self.current_annotation_id] = {
                        'class_id': class_id,
                        'points': normalized_points
                    }
                    self.current_annotation_id += 1

    def save_annotations(self):
        if not self.image_folder or self.current_image_index == -1:
            return

        image_file = self.images[self.current_image_index]
        annotation_file = os.path.splitext(image_file)[0] + ".txt"
        annotation_path = os.path.join(self.image_folder, annotation_file)

        with open(annotation_path, 'w') as f:
            for ann_id, ann in self.annotations.items():
                class_id = ann['class_id']
                points = ann['points']

                # Flatten points list
                flat_points = [str(coord) for point in points for coord in point]
                line = f"{class_id} {' '.join(flat_points)}\n"
                f.write(line)

    def display_image(self):
        if not self.images or self.current_image_index == -1:
            return

        image_file = self.images[self.current_image_index]
        image_path = os.path.join(self.image_folder, image_file)

        try:
            self.current_image = Image.open(image_path)
            self.update_image_display()

            # Update image counter
            self.image_num_entry.delete(0, tk.END)
            self.image_num_entry.insert(0, str(self.current_image_index + 1))

            # Update status
            self.status_bar.config(text=f"Image {self.current_image_index + 1}/{len(self.images)}: {image_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

    def update_image_display(self):
        """Update the image display to fit the canvas while maintaining aspect ratio"""
        self.canvas.delete("all")

        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            return

        # Calculate aspect ratio
        img_width, img_height = self.current_image.size
        img_ratio = img_width / img_height
        canvas_ratio = canvas_width / canvas_height

        # Calculate new dimensions
        if canvas_ratio > img_ratio:
            # Canvas is wider than image
            new_height = canvas_height
            new_width = int(new_height * img_ratio)
        else:
            # Canvas is taller than image
            new_width = canvas_width
            new_height = int(new_width / img_ratio)

        # Calculate position to center the image
        x_pos = (canvas_width - new_width) // 2
        y_pos = (canvas_height - new_height) // 2

        # Store scaling factors and position for coordinate conversion
        self.image_ratio = new_width / img_width
        self.image_position = (x_pos, y_pos)

        # Resize image
        resized_img = self.current_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized_img)

        # Display image
        self.image_on_canvas = self.canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=self.photo)

        # Draw annotations
        self.draw_annotations()

    def draw_annotations(self):
        for ann_id, ann in self.annotations.items():
            class_id = ann['class_id']
            points = ann['points']

            if len(points) < 2:
                continue

            # Scale points to image coordinates
            img_width, img_height = self.current_image.size
            scaled_points = [
                (point[0] * img_width * self.image_ratio + self.image_position[0],
                 point[1] * img_height * self.image_ratio + self.image_position[1])
                for point in points
            ]

            # Check if this polygon is selected
            is_selected = False
            for item in self.canvas.find_withtag(f"polygon_{ann_id}"):
                if "selected" in self.canvas.gettags(item):
                    is_selected = True
                    break

            # Create polygon with more transparent fill
            outline_color = "#ffffff" if is_selected else self.get_class_color(class_id)
            outline_width = 3 if is_selected else 2

            polygon_id = self.canvas.create_polygon(
                scaled_points,
                outline=outline_color,
                fill="",  # No solid fill
                width=outline_width,
                tags=("polygon", f"polygon_{ann_id}")
            )

            # Add very transparent fill (using stipple pattern with lighter pattern)
            fill_id = self.canvas.create_polygon(
                scaled_points,
                outline="",
                fill=self.get_class_color(class_id),
                stipple="gray25",
                tags=("fill", f"fill_{ann_id}")
            )

            # Add class label
            if self.classes and class_id < len(self.classes):
                label_text = self.classes[class_id]
                # Place label near the first point
                label_x, label_y = scaled_points[0]
                label_id = self.canvas.create_text(
                    label_x, label_y - 10,
                    text=label_text,
                    fill=self.get_class_color(class_id),
                    font=("Arial", 10, "bold"),
                    tags=("label", f"label_{ann_id}")
                )

            # Draw vertices
            for i, (x, y) in enumerate(scaled_points):
                vertex_id = self.canvas.create_oval(
                    x - 3, y - 3, x + 3, y + 3,
                    fill=self.get_class_color(class_id),
                    outline="white",
                    tags=("vertex", f"vertex_{ann_id}_{i}")
                )

    def get_class_color(self, class_id):
        if class_id not in self.class_colors:
            # Generate a color based on class_id
            hue = (class_id * 30) % 360
            rgb = self.hsv_to_rgb(hue / 360, 0.8, 0.8)
            hex_color = "#{:02x}{:02x}{:02x}".format(*rgb)
            self.class_colors[class_id] = hex_color
        return self.class_colors[class_id]

    def hsv_to_rgb(self, h, s, v):
        if s == 0.0:
            return (int(v * 255), int(v * 255), int(v * 255))
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i = i % 6

        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        elif i == 5:
            r, g, b = v, p, q

        return (int(r * 255), int(g * 255), int(b * 255))

    def add_class(self):
        new_class = simpledialog.askstring("Add Class", "Enter class name:")
        if new_class and new_class not in self.classes:
            self.classes.append(new_class)
            self.update_classes_listbox()
            self.refresh_annotations()

    def rename_class(self):
        selection = self.classes_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        new_name = simpledialog.askstring("Rename Class", "Enter new class name:",
                                          initialvalue=self.classes[index])
        if new_name and new_name not in self.classes:
            self.classes[index] = new_name
            self.update_classes_listbox()
            self.refresh_annotations()

    def remove_class(self):
        selection = self.classes_listbox.curselection()
        if selection:
            index = selection[0]
            self.classes.pop(index)
            self.update_classes_listbox()
            self.refresh_annotations()

    def import_classes(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file_path:
            return

        try:
            with open(file_path, 'r') as f:
                imported_classes = json.load(f)

            if isinstance(imported_classes, list):
                self.classes = imported_classes
                self.update_classes_listbox()
                self.refresh_annotations()
                messagebox.showinfo("Success", "Classes imported successfully")
            else:
                messagebox.showerror("Error", "Invalid format: expected list of classes")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import classes: {e}")

    def export_classes(self):
        if not self.classes:
            messagebox.showwarning("Warning", "No classes to export")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile="classes.json"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'w') as f:
                json.dump(self.classes, f, indent=2)
            messagebox.showinfo("Success", "Classes exported successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export classes: {e}")

    def refresh_annotations(self):
        """Refresh annotations after class changes"""
        if self.current_image_index != -1:
            image_file = self.images[self.current_image_index]
            self.load_annotations(image_file)
            self.display_image()

    def rename_current_image(self):
        if not self.images or self.current_image_index == -1:
            return

        old_name = self.images[self.current_image_index]
        new_name = simpledialog.askstring("Rename Image", "Enter new image name:",
                                          initialvalue=old_name)

        if not new_name or new_name == old_name:
            return

        # Check if new name already exists
        if new_name in self.images:
            messagebox.showerror("Error", "Image with this name already exists")
            return

        try:
            # Rename image file
            old_path = os.path.join(self.image_folder, old_name)
            new_path = os.path.join(self.image_folder, new_name)
            os.rename(old_path, new_path)

            # Rename annotation file if exists
            old_ann = os.path.splitext(old_name)[0] + ".txt"
            new_ann = os.path.splitext(new_name)[0] + ".txt"

            old_ann_path = os.path.join(self.image_folder, old_ann)
            new_ann_path = os.path.join(self.image_folder, new_ann)

            if os.path.exists(old_ann_path):
                os.rename(old_ann_path, new_ann_path)

            # Update images list
            self.images[self.current_image_index] = new_name
            self.display_image()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to rename image: {e}")

    def update_classes_listbox(self):
        self.classes_listbox.delete(0, tk.END)
        for i, cls in enumerate(self.classes):
            self.classes_listbox.insert(tk.END, f"{i + 1}. {cls}")

    def select_class_by_index(self, index):
        if 0 <= index < len(self.classes):
            self.classes_listbox.selection_clear(0, tk.END)
            self.classes_listbox.selection_set(index)
            self.classes_listbox.activate(index)
            self.current_class = index
            self.status_bar.config(text=f"Selected class: {self.classes[index]}")

    def jump_to_image(self, event=None):
        try:
            num = int(self.image_num_entry.get())
            if 1 <= num <= len(self.images):
                self.current_image_index = num - 1
                self.load_annotations(self.images[self.current_image_index])
                self.display_image()
        except ValueError:
            pass

    def next_image(self):
        if not self.images:
            return

        if self.current_image_index < len(self.images) - 1:
            # Save current annotations before switching
            if self.current_polygon:
                self.save_current_polygon()
            self.save_annotations()

            self.current_image_index += 1
            self.load_annotations(self.images[self.current_image_index])
            self.display_image()

    def prev_image(self):
        if not self.images:
            return

        if self.current_image_index > 0:
            # Save current annotations before switching
            if self.current_polygon:
                self.save_current_polygon()
            self.save_annotations()

            self.current_image_index -= 1
            self.load_annotations(self.images[self.current_image_index])
            self.display_image()

    def save_current_polygon(self):
        """Save the current polygon if it has enough points"""
        if len(self.current_polygon) >= 3:
            self.annotations[self.current_annotation_id] = {
                'class_id': self.current_class,
                'points': self.current_polygon
            }
            self.current_annotation_id += 1
            self.current_polygon = []
            self.save_annotations()

    def delete_current_image(self):
        if not self.images or self.current_image_index == -1:
            return

        image_file = self.images[self.current_image_index]
        confirm = messagebox.askyesno("Delete Image", f"Delete {image_file}?")

        if confirm:
            # Delete image file
            image_path = os.path.join(self.image_folder, image_file)
            try:
                os.remove(image_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete image: {e}")
                return

            # Delete annotation file if exists
            annotation_file = os.path.splitext(image_file)[0] + ".txt"
            annotation_path = os.path.join(self.image_folder, annotation_file)
            if os.path.exists(annotation_path):
                try:
                    os.remove(annotation_path)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete annotation: {e}")

            # Update UI
            self.images.pop(self.current_image_index)
            if self.current_image_index >= len(self.images):
                self.current_image_index = len(self.images) - 1

            if self.images:
                self.load_annotations(self.images[self.current_image_index])
                self.display_image()
            else:
                self.current_image_index = -1
                self.canvas.delete("all")
                self.status_bar.config(text="No images in folder")

    def delete_selected_polygon(self):
        if not self.annotations:
            return

        # Find selected polygon (last clicked)
        selected = None
        for item in self.canvas.find_withtag("selected"):
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith("polygon_"):
                    ann_id = int(tag.split("_")[1])
                    selected = ann_id
                    break
            if selected is not None:
                break

        if selected is not None and selected in self.annotations:
            del self.annotations[selected]
            self.save_annotations()
            self.display_image()

    def change_selected_polygon_class(self):
        if not self.annotations or self.current_class is None:
            return

        # Find selected polygon (last clicked)
        selected = None
        for item in self.canvas.find_withtag("selected"):
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith("polygon_"):
                    ann_id = int(tag.split("_")[1])
                    selected = ann_id
                    break
            if selected is not None:
                break

        if selected is not None and selected in self.annotations:
            self.annotations[selected]['class_id'] = self.current_class
            self.save_annotations()
            self.display_image()

    def clear_all_annotations(self):
        if not self.annotations:
            return

        confirm = messagebox.askyesno("Clear All", "Delete all annotations for this image?")
        if confirm:
            self.annotations = {}
            self.save_annotations()
            self.display_image()

    def canvas_left_click(self, event):
        if not self.classes or self.current_class is None:
            messagebox.showwarning("Warning", "Please select a class first")
            return

        # Check if we're dragging a vertex (with Ctrl pressed)
        if self.ctrl_pressed:
            clicked_items = self.canvas.find_overlapping(event.x - 5, event.y - 5, event.x + 5, event.y + 5)
            for item in clicked_items:
                tags = self.canvas.gettags(item)
                if "vertex" in tags:
                    parts = tags[1].split("_")
                    ann_id = int(parts[1])
                    vertex_idx = int(parts[2])
                    self.dragging_vertex = (ann_id, vertex_idx)
                    return
            return

        # Normal annotation mode
        if self.dragging_vertex is not None:
            return

        # Check if we clicked on a vertex
        clicked_items = self.canvas.find_overlapping(event.x - 5, event.y - 5, event.x + 5, event.y + 5)
        vertex_clicked = False

        for item in clicked_items:
            tags = self.canvas.gettags(item)
            if "vertex" in tags:
                vertex_clicked = True
                break

        if vertex_clicked:
            return

        # Check if we clicked on a polygon edge (to select it)
        for item in clicked_items:
            tags = self.canvas.gettags(item)
            if "polygon" in tags:
                # Select this polygon
                self.canvas.itemconfig("polygon", width=2)
                self.canvas.itemconfig(item, width=3, tags=tags + ("selected",))
                return

        # Convert canvas coordinates to image coordinates
        img_x = (event.x - self.image_position[0]) / self.image_ratio
        img_y = (event.y - self.image_position[1]) / self.image_ratio

        # Check if click is within image bounds
        img_width, img_height = self.current_image.size
        if 0 <= img_x <= img_width and 0 <= img_y <= img_height:
            # Normalize coordinates
            normalized_x = img_x / img_width
            normalized_y = img_y / img_height

            self.current_polygon.append((normalized_x, normalized_y))

            # Draw the current polygon
            self.draw_current_polygon(event.x, event.y)

    def canvas_right_click(self, event):
        if len(self.current_polygon) >= 3:
            # Save the polygon
            self.save_current_polygon()
            self.display_image()

    def canvas_mouse_move(self, event):
        if len(self.current_polygon) > 0:
            # Draw preview line from last point to current mouse position
            self.draw_current_polygon(event.x, event.y)

    def canvas_drag(self, event):
        if self.dragging_vertex is not None and self.ctrl_pressed:
            ann_id, vertex_idx = self.dragging_vertex
            if ann_id in self.annotations:
                # Convert canvas coordinates to image coordinates
                img_x = (event.x - self.image_position[0]) / self.image_ratio
                img_y = (event.y - self.image_position[1]) / self.image_ratio

                # Constrain to image bounds
                img_width, img_height = self.current_image.size
                img_x = max(0, min(img_x, img_width))
                img_y = max(0, min(img_y, img_height))

                # Update vertex position
                normalized_x = img_x / img_width
                normalized_y = img_y / img_height
                self.annotations[ann_id]['points'][vertex_idx] = (normalized_x, normalized_y)

                # Redraw
                self.save_annotations()
                self.display_image()

    def canvas_release(self, event):
        self.dragging_vertex = None

    def canvas_double_click(self, event):
        # Check if we double-clicked on a polygon edge to add a vertex
        clicked_items = self.canvas.find_overlapping(event.x - 5, event.y - 5, event.x + 5, event.y + 5)

        for item in clicked_items:
            tags = self.canvas.gettags(item)
            if "polygon" in tags:
                ann_id = int(tags[1].split("_")[1])
                if ann_id in self.annotations:
                    # Convert canvas coordinates to image coordinates for calculations
                    img_width, img_height = self.current_image.size
                    points = [
                        ((p[0] * img_width * self.image_ratio + self.image_position[0],
                          p[1] * img_height * self.image_ratio + self.image_position[1]))
                        for p in self.annotations[ann_id]['points']
                    ]

                    # Find the closest edge
                    closest_edge = None
                    min_dist = float('inf')
                    new_point = None

                    for i in range(len(points)):
                        p1 = points[i]
                        p2 = points[(i + 1) % len(points)]

                        # Calculate distance to line segment
                        dist, closest = self.point_to_line_distance((event.x, event.y), p1, p2)

                        if dist < min_dist:
                            min_dist = dist
                            closest_edge = i
                            new_point = closest

                    if closest_edge is not None and min_dist < 10:  # Only if close enough
                        # Convert back to normalized coordinates
                        img_x = (new_point[0] - self.image_position[0]) / self.image_ratio
                        img_y = (new_point[1] - self.image_position[1]) / self.image_ratio
                        normalized_x = img_x / img_width
                        normalized_y = img_y / img_height

                        # Add new vertex
                        self.annotations[ann_id]['points'].insert(closest_edge + 1, (normalized_x, normalized_y))

                        self.save_annotations()
                        self.display_image()
                        return

    def draw_current_polygon(self, mouse_x=None, mouse_y=None):
        if not self.current_polygon:
            return

        # Delete previous preview
        self.canvas.delete("preview")

        # Convert normalized coordinates to canvas coordinates
        img_width, img_height = self.current_image.size
        scaled_points = [
            (point[0] * img_width * self.image_ratio + self.image_position[0],
             point[1] * img_height * self.image_ratio + self.image_position[1])
            for point in self.current_polygon
        ]

        # Draw polygon
        if len(scaled_points) >= 2:
            self.canvas.create_polygon(
                scaled_points,
                outline=self.get_class_color(self.current_class),
                fill="",
                width=2,
                tags="preview"
            )

        # Draw vertices
        for x, y in scaled_points:
            self.canvas.create_oval(
                x - 3, y - 3, x + 3, y + 3,
                fill=self.get_class_color(self.current_class),
                outline="white",
                tags="preview"
            )

        # Draw line to mouse if provided
        if mouse_x is not None and mouse_y is not None and len(scaled_points) > 0:
            last_x, last_y = scaled_points[-1]
            self.canvas.create_line(
                last_x, last_y, mouse_x, mouse_y,
                fill=self.get_class_color(self.current_class),
                dash=(4, 2),
                tags="preview"
            )

    def point_to_line_distance(self, point, line_start, line_end):
        # Calculate distance from point to line segment and the closest point on the line
        line_vec = np.array([line_end[0] - line_start[0], line_end[1] - line_start[1]])
        point_vec = np.array([point[0] - line_start[0], point[1] - line_start[1]])

        line_len = np.linalg.norm(line_vec)
        if line_len == 0:
            return np.linalg.norm(point_vec), line_start

        line_unit = line_vec / line_len
        projection = np.dot(point_vec, line_unit)

        if projection < 0:
            closest = line_start
        elif projection > line_len:
            closest = line_end
        else:
            closest = line_start + line_unit * projection

        dist = np.linalg.norm(np.array(point) - closest)
        return dist, closest

    def undo_last_action(self, event=None):
        if self.current_polygon:
            self.current_polygon.pop()
            self.draw_current_polygon()
        elif self.annotations:
            last_id = max(self.annotations.keys())
            del self.annotations[last_id]
            self.save_annotations()
            self.display_image()


if __name__ == "__main__":
    root = tk.Tk()
    app = AnnotationApp(root)
    root.mainloop()