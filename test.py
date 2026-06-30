# import tkinter as tk
# from tkinter import filedialog
# import os
# import cv2
# from PIL import Image, ImageTk
# from ultralytics import YOLO

# # Load the model once at startup
# try:
#     model = YOLO("best.pt")
# except Exception as e:
#     print(f"Model error: {e}. Placeholder model logic will be used if missing.")
#     model = None

# def resize_background(event=None):
#     """Safely resizes the background image to match the current window size."""
#     global tk_bg, resize_timer
    
#     # Get current window dimensions
#     win_width = root.winfo_width()
#     win_height = root.winfo_height()
    
#     # Avoid resizing if the window is too small or minimized
#     if win_width < 10 or win_height < 10:
#         return

#     try:
#         # Resize the original background image to fit the current window size
#         resized_bg = original_bg_image.resize((win_width, win_height), Image.Resampling.LANCZOS)
#         tk_bg = ImageTk.PhotoImage(resized_bg)
        
#         # Apply to the label
#         bg_label.config(image=tk_bg)
#     except Exception as e:
#         print(f"Error resizing background: {e}")

# def on_window_resize(event):
#     """Debounces the resize event to prevent infinite execution loops."""
#     global resize_timer
#     if event.widget == root:
#         if resize_timer is not None:
#             root.after_cancel(resize_timer)
#         # Delay the resize calculation slightly for stability
#         resize_timer = root.after(50, resize_background)

# def select_image():
#     file_path = filedialog.askopenfilename(
#         filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
#     )
    
#     if file_path and model:
#         results = model.predict(source=file_path, conf=0.25, save=False, line_width=1)
#         crack_found = False
        
#         for result in results:
#             for box in result.boxes:
#                 class_id = int(box.cls)      
#                 class_name = model.names[class_id]  
                
#                 if "crack" in class_name.lower():
#                     crack_found = True
            
#             annotated_frame = result.plot(font_size=9, line_width=1)
#             rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
#             img = Image.fromarray(rgb_frame)
            
#             # Resized to 500x500 to sit neatly over the background
#             img = img.resize((500, 500), Image.Resampling.LANCZOS)
            
#             tk_img = ImageTk.PhotoImage(img)
#             image_label.config(image=tk_img, bd=2, relief="solid") 
#             image_label.image = tk_img  
            
#         if crack_found:
#             status_label.config(text="Crack Detected!", fg="red")
#         else:
#             status_label.config(text="No Crack Detected", fg="green")

# # Set up main Tkinter window
# root = tk.Tk()
# root.title("Crack detection Model")

# # Global timer configuration variables
# resize_timer = None
# tk_bg = None

# # Open window in full screen / maximized state
# root.state('zoomed') 

# # Verify if image exists before loading to prevent crashes
# bg_filename = "mining_bg.png"
# if not os.path.exists(bg_filename):
#     print(f"Warning: '{bg_filename}' not found! Creating a temporary placeholder background.")
#     original_bg_image = Image.new("RGB", (800, 600), color="#2c3e50")
# else:
#     original_bg_image = Image.open(bg_filename)  

# # Create a Label widget to hold the background image
# bg_label = tk.Label(root, bg="#2c3e50")
# bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# # Bind the background resizing function to the window adjustments safely
# root.bind('<Configure>', on_window_resize)

# # UI Layout elements
# select_btn = tk.Button(root, text="Select Image", font=("Helvetica", 16, "bold"), bd=3)
# select_btn.config(command=select_image)
# select_btn.pack(pady=20)

# # FIXED: Removed bg="" entirely. With no text, no image, and bd=0, 
# # this label remains completely flat and hidden until you pick an image.
# image_label = tk.Label(root, bd=0)
# image_label.pack(pady=10)

# status_label = tk.Label(root, text="Waiting for image...", font=("Helvetica", 16, "bold"), bg="white", padx=10, pady=5)
# status_label.pack(pady=15)

# # Trigger an initial background display calculation pass once layout completes
# root.after(100, resize_background)

# root.mainloop()

#------------------------------------------------------------------------------------

import tkinter as tk
from tkinter import filedialog
import os
import cv2
from PIL import Image, ImageTk
from ultralytics import YOLO

# Global variable to manage the video playback loop
video_loop_id = None

# Load the model once at startup
try:
    model = YOLO("best.pt")
except Exception as e:
    print(f"Model error: {e}. Placeholder model logic will be used if missing.")
    model = None

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
    """Debounces the resize event to prevent infinite execution loops."""
    global resize_timer
    if event.widget == root:
        if resize_timer is not None:
            root.after_cancel(resize_timer)
        resize_timer = root.after(50, resize_background)

def stop_existing_video():
    """Stops any ongoing video stream loop before starting a new file process."""
    global video_loop_id
    if video_loop_id is not None:
        root.after_cancel(video_loop_id)
        video_loop_id = None

def check_for_crack(results):
    """Helper logic to detect if a crack class is present in YOLO outputs."""
    if not results:
        return False
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls)      
            class_name = model.names[class_id]  
            if "crack" in class_name.lower():
                return True
    return False

def update_ui_with_frame(annotated_frame, has_crack):
    """Helper logic to render the CV2 image frame into the Tkinter window layout."""
    rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb_frame)
    img = img.resize((500, 500), Image.Resampling.LANCZOS)
    
    tk_img = ImageTk.PhotoImage(img)
    image_label.config(image=tk_img, bd=2, relief="solid") 
    image_label.image = tk_img  
    
    if has_crack:
        status_label.config(text="Crack Detected!", fg="red")
    else:
        status_label.config(text="No Crack Detected", fg="green")

def select_image():
    stop_existing_video()  # Stop video if it was running
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
    )
    
    if file_path and model:
        results = model.predict(source=file_path, conf=0.25, save=False, line_width=1)
        crack_found = check_for_crack(results)
        
        if results:
            annotated_frame = results[0].plot(font_size=9, line_width=1)
            update_ui_with_frame(annotated_frame, crack_found)

def select_video():
    stop_existing_video()  # Stop any previous video loops
    file_path = filedialog.askopenfilename(
        filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov")]
    )
    
    if file_path and model:
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            print("Error opening video file")
            return
        
        status_label.config(text="Processing Video...", fg="black")
        stream_video(cap)

def stream_video(cap):
    """Reads video frames sequentially, processes via YOLO, and schedules UI refresh."""
    global video_loop_id
    
    ret, frame = cap.read()
    if ret:
        # Run YOLO on a single frame array stream directly
        results = model.predict(source=frame, conf=0.25, save=False, line_width=1, verbose=False)
        crack_found = check_for_crack(results)
        
        if results:
            annotated_frame = results[0].plot(font_size=9, line_width=1)
            update_ui_with_frame(annotated_frame, crack_found)
        
        # Loop every 30 milliseconds (~33 FPS) targeting live GUI tracking updates
        video_loop_id = root.after(30, stream_video, cap)
    else:
        cap.release()
        status_label.config(text="Video Finished", fg="blue")
        video_loop_id = None

# Set up main Tkinter window
root = tk.Tk()
root.title("Crack detection Model")

# Global timer configuration variables
resize_timer = None
tk_bg = None

# Open window in full screen / maximized state
root.state('zoomed') 

# Verify if image exists before loading to prevent crashes
bg_filename = "mining_bg.png"
if not os.path.exists(bg_filename):
    print(f"Warning: '{bg_filename}' not found! Creating a temporary placeholder background.")
    original_bg_image = Image.new("RGB", (800, 600), color="#2c3e50")
else:
    original_bg_image = Image.open(bg_filename)  

# Create a Label widget to hold the background image
bg_label = tk.Label(root, bg="#2c3e50")
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Bind the background resizing function to the window adjustments safely
root.bind('<Configure>', on_window_resize)

# Container frame for buttons to keep them neatly aligned horizontally
button_frame = tk.Frame(root, bg="#2c3e50")
button_frame.pack(pady=20)

select_img_btn = tk.Button(button_frame, text="Select Image", font=("Helvetica", 16, "bold"), bd=3, command=select_image)
select_img_btn.pack(side="left", padx=10)

select_vid_btn = tk.Button(button_frame, text="Select Video", font=("Helvetica", 16, "bold"), bd=3, command=select_video)
select_vid_btn.pack(side="left", padx=10)

# Main frame space elements
image_label = tk.Label(root, bd=0)
image_label.pack(pady=10)

status_label = tk.Label(root, text="Waiting for input...", font=("Helvetica", 16, "bold"), bg="white", padx=10, pady=5)
status_label.pack(pady=15)

# Trigger an initial background display calculation pass once layout completes
root.after(100, resize_background)

root.mainloop()


