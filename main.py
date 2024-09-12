import threading
from PIL import Image as PILImage, ImageGrab, ImageTk, ImageFilter, ImageDraw
import tkinter as tk
from tkinter import *
from tkinter import ttk
from screeninfo import get_monitors

from translate_loop import *
from processing import *

# "defines"
CAPTURE_PREVIEW_HEIGHT = 300
BUTTON_SIZE_PX = 20
MIN_IMAGE_COLORVAL = 0
MAX_IMAGE_COLORVAL = 255
PREVIEW_RECT_WIDTH = 2

class Monitor:
    def __init__(self, root):
        self.root = root
        i_p = PILImage.open(r"img/icon.png")
        i_o = ImageTk.PhotoImage(i_p)
        self.root.wm_iconphoto(True, i_o)
        self.root.title("screen-translator")

        self.main_frame = tk.Frame(root, bg="white")
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Get monitor info
        self.monitors = get_monitors()
        self.selected_monitor = None

        self.preview_label = tk.Label(self.main_frame, text="Capture area preview", font=("Arial", "12", "bold"))
        self.preview_label.pack()

        # threading
        self.main_thread = threading.Thread(target=translate_loop_func, daemon=True)
        
        # dropdown to select the monitor
        self.monitor_var = tk.StringVar()
        self.monitor_dropdown = ttk.Combobox(self.main_frame, textvariable=self.monitor_var, state="readonly")
        self.monitor_dropdown['values'] = [f"Monitor {i + 1}: {m.width}x{m.height}" for i, m in enumerate(self.monitors)]
        self.monitor_dropdown.current(0)
        self.monitor_dropdown.pack(pady=10)
        self.monitor_dropdown.bind("<<ComboboxSelected>>", self.load_monitor_preview)
        
        # canvas to display the monitor preview and the red box
        self.canvas = tk.Canvas(self.main_frame, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # default red box
        self.box = None
        self.red_box_id = None
        self.dragging = False
        self.resizing = False
        self.resize_direction = None
        self.edge_size = 10  # size of edge for resizing sensitivity

        self.load_monitor_preview()
        
        # bind mouse events for resizing and dragging the box
        self.canvas.bind("<ButtonPress-1>", self.start_move_or_resize)
        self.canvas.bind("<B1-Motion>", self.on_move_or_resize)
        self.canvas.bind("<ButtonRelease-1>", self.stop_move_or_resize)
        self.canvas.bind("<Motion>", self.change_cursor)

        # chat frame
        self.chat_frame = tk.Frame(root, width=300, bg="#e0e0e0")
        self.chat_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.sample_message_button = tk.Button(self.chat_frame, text="Send Sample Message", command=self.send_sample_message)
        self.sample_message_button.pack(pady=5)

        # scrollable chat log area
        self.chat_log_frame = tk.Frame(self.chat_frame)
        self.chat_log_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        self.chat_canvas = tk.Canvas(self.chat_log_frame, bg="#f0f0f0", highlightthickness=0)
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # scrollbar for chat log
        self.scrollbar = ttk.Scrollbar(self.chat_log_frame, orient="vertical", command=self.chat_canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.chat_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.chat_canvas.bind('<Configure>', self.update_scroll_region)

        # message frame
        self.chat_log_inner = tk.Frame(self.chat_canvas, bg="#f0f0f0")
        self.chat_canvas.create_window((5, 0), window=self.chat_log_inner, anchor="nw", width=self.chat_canvas.winfo_width())
        self.chat_canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        self.message_entry = tk.Entry(self.chat_frame, width=25)
        self.message_entry.pack(pady=5)
        self.message_entry.bind("<Return>", self.send_message)

        self.messages = []
        self.max_messages = 50
        self.last_message_frame = None

        self.update_scroll_region()  # Ensure scroll region is updated initially

    def load_monitor_preview(self, event=None):
        monitor_idx = self.monitor_dropdown.current()
        self.selected_monitor = self.monitors[monitor_idx]
        monitor_img = ImageGrab.grab(bbox=(self.selected_monitor.x, self.selected_monitor.y, 
                                           self.selected_monitor.width + self.selected_monitor.x, 
                                           self.selected_monitor.height + self.selected_monitor.y), all_screens=True)
        monitor_img.thumbnail((800, 480))  # Scale down preview for GUI
        self.monitor_preview = ImageTk.PhotoImage(monitor_img)

        # clear the canvas and draw the new preview
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.monitor_preview)

        # default red box
        self.red_box_x0 = 50
        self.red_box_y0 = 50
        self.red_box_x1 = 400
        self.red_box_y1 = 300
        
        self.red_box_id = self.canvas.create_rectangle(self.red_box_x0, self.red_box_y0, 
                                                       self.red_box_x1, self.red_box_y1, outline="red", width=2)

    def start_move_or_resize(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

        if self.is_on_edge(event.x, event.y):
            self.resizing = True
            self.resize_direction = self.get_resize_direction(event.x, event.y)
        else:
            self.dragging = True

    def on_move_or_resize(self, event):
        dx = event.x - self.offset_x
        dy = event.y - self.offset_y

        if self.resizing:
            self.resize_box(dx, dy)
        elif self.dragging:
            self.red_box_x0 += dx
            self.red_box_y0 += dy
            self.red_box_x1 += dx
            self.red_box_y1 += dy

            self.canvas.coords(self.red_box_id, self.red_box_x0, self.red_box_y0, 
                               self.red_box_x1, self.red_box_y1)
        
        self.offset_x = event.x
        self.offset_y = event.y

    def stop_move_or_resize(self, event):
        self.dragging = False
        self.resizing = False
        self.resize_direction = None
        
        set_crop(self.get_red_box_dimensions())

    def change_cursor(self, event):
        if self.is_on_edge(event.x, event.y):
            direction = self.get_resize_direction(event.x, event.y)
            if direction in ['left', 'right']:
                self.canvas.config(cursor="sb_h_double_arrow")
            elif direction in ['top', 'bottom']:
                self.canvas.config(cursor="sb_v_double_arrow")
            elif direction in ['top_left', 'bottom_right']:
                self.canvas.config(cursor="size_nw_se")
            elif direction in ['top_right', 'bottom_left']:
                self.canvas.config(cursor="size_ne_sw")
        else:
            self.canvas.config(cursor="")

    def is_on_edge(self, x, y):
        on_left = abs(x - self.red_box_x0) <= self.edge_size
        on_right = abs(x - self.red_box_x1) <= self.edge_size
        on_top = abs(y - self.red_box_y0) <= self.edge_size
        on_bottom = abs(y - self.red_box_y1) <= self.edge_size
        return on_left or on_right or on_top or on_bottom

    def get_resize_direction(self, x, y):
        on_left = abs(x - self.red_box_x0) <= self.edge_size
        on_right = abs(x - self.red_box_x1) <= self.edge_size
        on_top = abs(y - self.red_box_y0) <= self.edge_size
        on_bottom = abs(y - self.red_box_y1) <= self.edge_size
        
        if on_left and on_top:
            return "top_left"
        elif on_right and on_top:
            return "top_right"
        elif on_left and on_bottom:
            return "bottom_left"
        elif on_right and on_bottom:
            return "bottom_right"
        elif on_left:
            return "left"
        elif on_right:
            return "right"
        elif on_top:
            return "top"
        elif on_bottom:
            return "bottom"

    def resize_box(self, dx, dy):
        if self.resize_direction == "left":
            self.red_box_x0 += dx
        elif self.resize_direction == "right":
            self.red_box_x1 += dx
        elif self.resize_direction == "top":
            self.red_box_y0 += dy
        elif self.resize_direction == "bottom":
            self.red_box_y1 += dy
        elif self.resize_direction == "top_left":
            self.red_box_x0 += dx
            self.red_box_y0 += dy
        elif self.resize_direction == "top_right":
            self.red_box_x1 += dx
            self.red_box_y0 += dy
        elif self.resize_direction == "bottom_left":
            self.red_box_x0 += dx
            self.red_box_y1 += dy
        elif self.resize_direction == "bottom_right":
            self.red_box_x1 += dx
            self.red_box_y1 += dy

        # Redraw the red box
        self.canvas.coords(self.red_box_id, self.red_box_x0, self.red_box_y0, 
                           self.red_box_x1, self.red_box_y1)

    def get_red_box_dimensions(self):
        m = self.selected_monitor
        
        o = [self.red_box_x0, self.red_box_y0, self.red_box_x1, self.red_box_y1]
        m1 = [m.x, m.y]
        m2 = [m.width, m.height]
        m3 = [self.monitor_preview.width(), self.monitor_preview.height()]

        for i,e in enumerate(o):
            o[i] = int(float(e)/m3[i%2] * m2[i%2]) + m1[i%2]

        return o
    
    def update_scroll_region(self, event=None):
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        self.chat_canvas.itemconfig(self.chat_canvas.create_window((5, 0), window=self.chat_log_inner), width=self.chat_canvas.winfo_width())

    def send_sample_message(self):
        self.add_message("Sample message")

    def send_message(self, event=None):
        message = self.message_entry.get().strip()
        if message:
            self.add_message(message)
            self.message_entry.delete(0, tk.END)

    def add_message(self, message):
        if len(self.messages) >= self.max_messages:
            oldest_message_frame = self.messages.pop(0)
            oldest_message_frame.pack_forget()

        message_frame = tk.Frame(self.chat_log_inner, bg="#ffffff", bd=1, relief="solid")
        message_frame.pack(fill=tk.X, pady=5)

        message_label = tk.Label(message_frame, text=message, anchor="w", justify="left", bg="#ffffff", padx=5, pady=10, wraplength=self.chat_canvas.winfo_width()-10)
        message_label.pack(fill=tk.X)

        self.messages.append(message_frame)
        self.highlight_recent_message(message_frame)
        self.chat_log_inner.update_idletasks()

        self.update_scroll_region()
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1)

    def highlight_recent_message(self, message_frame):
        if self.last_message_frame:
            self.last_message_frame.winfo_children()[0].config(bg="#ffffff")
        message_frame.winfo_children()[0].config(bg="#d8d8d8")
        self.last_message_frame = message_frame

    def on_mouse_wheel(self, event):
        self.chat_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

if __name__ == "__main__":
    root = tk.Tk()
    app = Monitor(root)
    root.geometry("1218x520")

    root.mainloop()
