import tkinter as tk
from tkinter import filedialog
import os
import cv2
from PIL import Image, ImageTk
from ultralytics import YOLO

try:
    model = YOLO("best (1).pt")
except Exception as e:
    print(f"Model error: {e}. Placeholder model logic will be used if missing.")
    model = None

video_loop_id = None
cap = None

def resize_background(event=None):
    """Safely resizes the background image to match the current window size."""
    global tk_bg, resize_timer
    
    win_width = root.winfo_width()
    win_height = root.winfo_height()
    
    if win_width < 10 or win_height < 10:
        return

    try:
        resized_bg = original_bg_image.resize((win_width, win_height), Image.Resampling.LANCZOS)
        tk_bg = ImageTk.PhotoImage(resized_bg)
        bg_label.config(image=tk_bg)
    except Exception as e:
        print(f"Error resizing background: {e}")

def on_window_resize(event):
    global resize_timer
    if event.widget == root:
        if resize_timer is not None:
            root.after_cancel(resize_timer)
        resize_timer = root.after(50, resize_background)

def stop_video_stream():
    global video_loop_id, cap
    if video_loop_id:
        root.after_cancel(video_loop_id)
        video_loop_id = None
    if cap:
        cap.release()
        cap = None

def update_status_ui(fire_detected, smoke_detected):
    if fire_detected and smoke_detected:
        status_label.config(text="Alert! Fire and Smoke detected", fg="red", bg="white", padx=10, pady=5)
    elif fire_detected:
        status_label.config(text="Alert! Fire Detected", fg="orange", bg="white", padx=10, pady=5)
    elif smoke_detected:
        status_label.config(text="Alert! Smoke Detected", fg="orange", bg="white", padx=10, pady=5)
    else:
        status_label.config(text="Safe, No Detections!", fg="green", bg="white", padx=10, pady=5)

def select_image():
    stop_video_stream()
    
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
    )
    
    if file_path and model:
        results = model.predict(source=file_path, conf=0.25, save=False, line_width=1)
        
        fire_detected = False
        smoke_detected = False
        annotated_frame = None
        
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls)      
                class_name = model.names[class_id].lower()
                
                if class_name == "fire":
                    fire_detected = True
                elif class_name == "smoke":
                    smoke_detected = True
            
            annotated_frame = result.plot(font_size=9, line_width=1)
            
        if annotated_frame is not None:
            rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame).resize((500, 500), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            image_label.config(image=tk_img, bd=2, relief="solid") 
            image_label.image = tk_img  

        update_status_ui(fire_detected, smoke_detected)

def process_video_frame():
    global video_loop_id, cap
    
    if cap is None or not cap.isOpened():
        return

    ret, frame = cap.read()
    if not ret:
        stop_video_stream()
        return

    if model:
        results = model.predict(source=frame, conf=0.25, save=False, verbose=False, line_width=1)
        
        fire_detected = False
        smoke_detected = False
        annotated_frame = frame
        
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls)
                class_name = model.names[class_id].lower()
                if class_name == "fire":
                    fire_detected = True
                elif class_name == "smoke":
                    smoke_detected = True
            
            annotated_frame = result.plot(font_size=9, line_width=1)

        rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame).resize((500, 500), Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(img)
        image_label.config(image=tk_img, bd=2, relief="solid")
        image_label.image = tk_img
        
        update_status_ui(fire_detected, smoke_detected)

    video_loop_id = root.after(30, process_video_frame)

def select_video():
    global cap
    stop_video_stream()
    
    file_path = filedialog.askopenfilename(
        filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov *.wmv")]
    )
    
    if file_path:
        cap = cv2.VideoCapture(file_path)
        process_video_frame()

root = tk.Tk()
root.title("Fire and Smoke Detection Model")

resize_timer = None
tk_bg = None
root.state('zoomed') 

bg_filename = "fire_smoke.png"
if not os.path.exists(bg_filename):
    print(f"Warning: '{bg_filename}' not found! Creating a temporary placeholder background.")
    original_bg_image = Image.new("RGB", (800, 600), color="#2c3e50")
else:
    original_bg_image = Image.open(bg_filename)  

bg_label = tk.Label(root, bg="#2c3e50")
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

root.bind('<Configure>', on_window_resize)

button_frame = tk.Frame(root, bg="")
button_frame.pack(pady=20)

select_img_btn = tk.Button(button_frame, text="Select Image", font=("Helvetica", 16, "bold"), bd=3, command=select_image)
select_img_btn.pack(side=tk.LEFT, padx=15)

select_vid_btn = tk.Button(button_frame, text="Open Video", font=("Helvetica", 16, "bold"), bd=3, command=select_video)
select_vid_btn.pack(side=tk.LEFT, padx=15)

image_label = tk.Label(root, bd=0)
image_label.pack(pady=10)

status_label = tk.Label(root, text="", font=("Helvetica", 16, "bold"), bd=0)
status_label.pack(pady=5)

root.after(100, resize_background)

root.protocol("WM_DELETE_WINDOW", lambda: (stop_video_stream(), root.destroy()))
root.mainloop()
