import threading
import time
from typing import Optional, Union, Dict, Any
from pynput.keyboard import Key, Controller, Listener
import customtkinter as ctk
import tkinter as tk

class LegendaryAutoPresser:
    """ -- / Main application class for the Legendary Auto Presser. \-- """
    
    def __init__(self):
        # Initialize keyboard controller
        self.keyboard = Controller()
        
        # Application state
        self.is_pressing = False
        self.is_infinity = True
        self.hotkey_is_pressed = False
        self.timer_ms = 100
        self.key_to_press: Union[str, Key] = 'a'
        self.hotkey = 'F6'
        self.system_hotkey = Key.f6
        self.press_thread: Optional[threading.Thread] = None
        
        # Special keys mapping 
        self.special_keys: Dict[str, Key] = {
            "Enter": Key.enter,
            "Space": Key.space,
            "Tab": Key.tab,
            "Backspace": Key.backspace,
            "Esc": Key.esc,
            "Delete": Key.delete,
            "Up": Key.up,
            "Down": Key.down,
            "Left": Key.left,
            "Right": Key.right,
            "Home": Key.home,
            "End": Key.end,
            "Page Up": Key.page_up,
            "Page Down": Key.page_down,
            "Shift": Key.shift,
            "Ctrl": Key.ctrl,
            "Alt": Key.alt,
            "F1": Key.f1,
            "F2": Key.f2,
            "F3": Key.f3,
            "F4": Key.f4,
            "F5": Key.f5,
            "F6": Key.f6,
            "F7": Key.f7,
            "F8": Key.f8,
            "F9": Key.f9,
            "F10": Key.f10,
            "F11": Key.f11,
            "F12": Key.f12,
        }
        
        # Setup keys
        self.available_keys = []
        self.available_keys = list(self.special_keys.keys())
        # Add regular character keys
        self.available_keys.extend("abcdefghijklmnopqrstuvwxyz")
        self.available_keys.extend("0123456789")
        self.available_keys.extend("!@#$%^&*()_+-=[]{};':\"\,./<>?")
        
        # Setup App Design "UI"
        self.setup_ui()
        
        # Start keyboard listener
        self.listener = Listener(on_press=self.on_global_key_press)
        self.listener.start()
    
    def setup_ui(self):
        """ -- / Initialize the user interface. \-- """
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.window = ctk.CTk()
        self.window.geometry("550x400+400+200")
        self.window.title("Legendary Auto Presser v1.5")
        try:
            self.window.iconbitmap("logo.ico")
        except:
            # Handle case where icon file is missing
            pass
        self.window.resizable(False, False)
        
        # Initialize string variables
        self.hour_var = ctk.StringVar(value="0")
        self.min_var = ctk.StringVar(value="0")
        self.sec_var = ctk.StringVar(value="0")
        self.ms_var = ctk.StringVar(value="100")
        self.repeat_var = ctk.StringVar(value="1")
        self.word_var = ctk.StringVar(value="a")
        self.hotkey_var = ctk.StringVar(value=self.hotkey)
        
        # Add trace to time variables for auto-conversion
        self.hour_var.trace_add("write", self.on_time_changed)
        self.min_var.trace_add("write", self.on_time_changed)
        self.sec_var.trace_add("write", self.on_time_changed)
        self.ms_var.trace_add("write", self.on_time_changed)
        
        self.create_title()
        self.create_timer_frame()
        self.create_key_frame()
        self.create_control_buttons()
        self.create_theme_toggle()
        self.create_status_bar()
    
    def create_title(self):
        """ -- / Create the title bar. \-- """
        title = ctk.CTkLabel(
            self.window, 
            text='Legendary Presser',
            font=('bold', 20),
            text_color="#fff",
            fg_color="#2682cb",
            height=50
        )
        title.pack(fill="both")
    
    def create_timer_frame(self):
        """ -- / Create the timer configuration frame. \-- """
        timer_frame = ctk.CTkFrame(
            self.window,
            height=180,
            width=210,
            border_width=2,
            border_color="#000"
        )
        timer_frame.place(x=30, y=80)
        
        # Hours
        hour_lbl = ctk.CTkLabel(timer_frame, text='Hours:', font=('Arial', 14))
        hour_lbl.place(x=35, y=16)
        self.hours_entry = ctk.CTkEntry(timer_frame, width=70, textvariable=self.hour_var)
        self.hours_entry.place(x=110, y=16)
        self.hours_entry.bind("<FocusOut>", self.normalize_time_units)
        
        # Minutes
        min_lbl = ctk.CTkLabel(timer_frame, text='Mins:', font=('Arial', 14))
        min_lbl.place(x=35, y=56)
        self.mins_entry = ctk.CTkEntry(timer_frame, width=70, textvariable=self.min_var)
        self.mins_entry.place(x=110, y=56)
        self.mins_entry.bind("<FocusOut>", self.normalize_time_units)
        
        # Seconds
        sec_lbl = ctk.CTkLabel(timer_frame, text='Secs:', font=('Arial', 14))
        sec_lbl.place(x=35, y=96)
        self.secs_entry = ctk.CTkEntry(timer_frame, width=70, textvariable=self.sec_var)
        self.secs_entry.place(x=110, y=96)
        self.secs_entry.bind("<FocusOut>", self.normalize_time_units)
        
        # Milliseconds
        mili_lbl = ctk.CTkLabel(timer_frame, text='Milisecs:', font=('Arial', 14))
        mili_lbl.place(x=35, y=136)
        self.mili_entry = ctk.CTkEntry(timer_frame, width=70, textvariable=self.ms_var)
        self.mili_entry.place(x=110, y=136)
        self.mili_entry.bind("<FocusOut>", self.normalize_time_units)
    
    def create_key_frame(self):
        """ -- / Create the key selection and repeat options frame. \-- """
        word_frame = ctk.CTkFrame(
            self.window,
            height=180,
            width=230,
            border_width=2,
            border_color="#000"
        )
        word_frame.place(x=280, y=80)
        
        # Key selection
        word_lbl = ctk.CTkLabel(word_frame, text='Key:', font=('Arial', 14))
        word_lbl.place(x=30, y=30)
        self.word_combo = ctk.CTkComboBox(
            word_frame,
            values=self.available_keys,
            width=120,
            font=("Arial", 16),
            variable=self.word_var,
            command=self.on_key_selected
        )
        self.word_combo.place(x=80, y=30)
        
        # Repeat options
        self.radio_var = ctk.IntVar(value=2)
        
        # Repeat X times option
        self.rd1 = ctk.CTkRadioButton(
            word_frame,
            text='Repeat',
            value=1,
            variable=self.radio_var,
            radiobutton_width=15,
            radiobutton_height=15,
            border_width_checked=3,
            border_width_unchecked=2,
            hover_color="#ddd",
            fg_color="#48a4ff",
            command=self.enable_repeat_count
        )
        self.rd1.place(x=30, y=82)
        
        # Repeat count spinbox
        self.rep_spinbox = tk.Spinbox(
            word_frame,
            width=5,
            state="readonly",
            from_=1,
            to=147116,
            textvariable=self.repeat_var
        )
        self.rep_spinbox.place(x=110, y=82)
        
        time_txt = ctk.CTkLabel(word_frame, text="times", font=("Arial", 14))
        time_txt.place(x=170, y=78)
        
        # Repeat until stopped option
        self.rd2 = ctk.CTkRadioButton(
            word_frame,
            text='Repeat until stopped',
            value=2,
            variable=self.radio_var,
            radiobutton_width=15,
            radiobutton_height=15,
            border_width_checked=3,
            border_width_unchecked=2,
            hover_color="#ddd",
            fg_color="#48a4ff",
            command=self.enable_infinity
        )
        self.rd2.place(x=30, y=130)
    
    def create_status_bar(self):
        """ -- / Create a status bar for showing conversion messages. \-- """
        self.status_var = ctk.StringVar(value="")
        self.status_label = ctk.CTkLabel(
            self.window,
            textvariable=self.status_var,
            font=("Arial", 12),
            text_color="#48a4ff"
        )
        self.status_label.place(x=30, y=340)
        
        # Clear status after 3 seconds
        def clear_status():
            self.status_var.set("")
        
        self.clear_status = clear_status
    
    def on_key_selected(self, selection):
        """ -- / Handle key selection from dropdown. \-- """
        # Update the key to press based on selection
        if selection in self.special_keys:
            self.key_to_press = self.special_keys[selection]
        else:
            self.key_to_press = selection[0] if selection else 'a'
    
    def create_control_buttons(self):
        """ -- / Create the control buttons. \-- """
        btn_width = 160
        
        # Start button
        self.start_btn = ctk.CTkButton(
            self.window,
            text=f"({self.hotkey}) Start",
            width=btn_width,
            height=50,
            font=("Arial", 20),
            command=self.toggle_pressing
        )
        self.start_btn.place(x=20, y=280)
        
        # Stop button
        self.stop_btn = ctk.CTkButton(
            self.window,
            text=f"({self.hotkey}) Stop",
            width=btn_width,
            height=50,
            font=("Arial", 20),
            state="disabled",
            command=self.toggle_pressing
        )
        self.stop_btn.place(x=195, y=280)
        
        # Hotkey button
        self.hotkeys_btn = ctk.CTkButton(
            self.window,
            text="Hotkey",
            width=btn_width,
            height=50,
            font=("Arial", 20),
            command=self.open_hotkeys
        )
        self.hotkeys_btn.place(x=370, y=280)
    
    def create_theme_toggle(self):
        """ -- / Create the theme toggle switch. \-- """
        self.theme_switch = ctk.CTkSwitch(
            self.window,
            text="Dark Mode",
            command=self.set_theme
        )
        self.theme_switch.place(x=30, y=360)
    
    def on_time_changed(self, *args):
        """ -- / Handle time input changes for auto-conversion. \-- """
        pass
    
    def normalize_time_units(self, event=None):
        """ -- / Convert time units when appropriate (e.g., 1000ms -> 1s, 60s -> 1m). \-- """
        # Get current values
        try:
            hours = int(''.join(char for char in self.hour_var.get() if char.isdigit()) or "0")
            mins = int(''.join(char for char in self.min_var.get() if char.isdigit()) or "0")
            secs = int(''.join(char for char in self.sec_var.get() if char.isdigit()) or "0")
            ms = int(''.join(char for char in self.ms_var.get() if char.isdigit()) or "0")
            
            # Store original values for change detection
            orig_hours, orig_mins, orig_secs, orig_ms = hours, mins, secs, ms
            
            # Convert milliseconds to seconds if >= 1000
            if ms >= 1000:
                additional_secs = ms // 1000
                ms = ms % 1000
                secs += additional_secs
                self.status_var.set(f"Converted {additional_secs*1000}ms to {additional_secs}s")
                self.window.after(3000, self.clear_status)
            
            # Convert seconds to minutes if >= 60
            if secs >= 60:
                additional_mins = secs // 60
                secs = secs % 60
                mins += additional_mins
                self.status_var.set(f"Converted {additional_mins*60}s to {additional_mins}m")
                self.window.after(3000, self.clear_status)
            
            # Convert minutes to hours if >= 60
            if mins >= 60:
                additional_hours = mins // 60
                mins = mins % 60
                hours += additional_hours
                self.status_var.set(f"Converted {additional_hours*60}m to {additional_hours}h")
                self.window.after(3000, self.clear_status)
            
            # Cap hours at 100
            if hours > 100:
                hours = 100
                mins = 59
                secs = 59
                ms = 999
                self.status_var.set("Maximum time is 100h 59m 59s 999ms")
                self.window.after(3000, self.clear_status)
            
            # Update variables only if values changed
            if hours != orig_hours:
                self.hour_var.set(str(hours))
            if mins != orig_mins:
                self.min_var.set(str(mins))
            if secs != orig_secs:
                self.sec_var.set(str(secs))
            if ms != orig_ms:
                self.ms_var.set(str(ms))
            
            # Calculate total milliseconds
            self.timer_ms = ((hours * 3600) + (mins * 60) + secs) * 1000 + ms
            
        except ValueError:
            # Handle invalid input
            pass
    
    def enable_repeat_count(self):
        """ -- / Enable the repeat count option. \-- """
        self.rep_spinbox.configure(state="normal")
        self.is_infinity = False
    
    def enable_infinity(self):
        """ -- / Enable the repeat until stopped option. \-- """
        self.rep_spinbox.configure(state="readonly")
        self.is_infinity = True
    
    def set_theme(self):
        """ -- / Toggle between light and dark themes. \-- """
        val = self.theme_switch.get()
        if val:
            ctk.set_appearance_mode("light")
            self.theme_switch.configure(text="Light Mode")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_switch.configure(text="Dark Mode")
    
    def validate_time_inputs(self):
        """ -- / Validate and normalize time inputs. \-- """
        # First normalize the units
        self.normalize_time_units()
        
        # Extract digits only from inputs
        hours = ''.join(char for char in self.hour_var.get() if char.isdigit()) or "0"
        mins = ''.join(char for char in self.min_var.get() if char.isdigit()) or "0"
        secs = ''.join(char for char in self.sec_var.get() if char.isdigit()) or "0"
        ms = ''.join(char for char in self.ms_var.get() if char.isdigit()) or "0"
        
        # Convert to integers
        hours_int = min(int(hours), 100)  # Cap at 100 hours
        mins_int = min(int(mins), 59)
        secs_int = min(int(secs), 59)
        ms_int = min(int(ms), 999)
        
        # Update variables with normalized values
        self.hour_var.set(str(hours_int))
        self.min_var.set(str(mins_int))
        self.sec_var.set(str(secs_int))
        self.ms_var.set(str(ms_int))
        
        # Calculate total milliseconds
        self.timer_ms = ((hours_int * 3600) + (mins_int * 60) + secs_int) * 1000 + ms_int
        
        # Ensure minimum delay
        if self.timer_ms < 10:
            self.timer_ms = 10
            self.ms_var.set("10")
    
    def start_pressing(self):
        """ -- / Start the key pressing operation. \-- """
        # Validate inputs
        self.validate_time_inputs()
        
        # Get the key to press from the dropdown
        selection = self.word_var.get()
        if selection in self.special_keys:
            self.key_to_press = self.special_keys[selection]
        elif selection:
            self.key_to_press = selection[0]
        
        # Disable inputs
        self.disable_inputs()
        
        # Start pressing
        self.is_pressing = True
        
        if self.is_infinity:
            # Start continuous pressing in a separate thread
            self.press_thread = threading.Thread(target=self.continuous_pressing)
            self.press_thread.daemon = True
            self.press_thread.start()
        else:
            # Start pressing for a specific number of times
            repeat_count = self.get_repeat_count()
            self.press_thread = threading.Thread(
                target=self.press_n_times, 
                args=(repeat_count,)
            )
            self.press_thread.daemon = True
            self.press_thread.start()
    
    def continuous_pressing(self):
        """ -- / Press the key continuously until stopped. \-- """
        while self.is_pressing:
            try:
                self.keyboard.press(self.key_to_press)
                self.keyboard.release(self.key_to_press)
                time.sleep(self.timer_ms / 1000)
            except Exception as e:
                print(f"Error pressing key: {e}")
                break
    
    def press_n_times(self, count: int):
        """ -- / Press the key a specific number of times. \-- """
        for _ in range(count):
            if not self.is_pressing:
                break
            try:
                self.keyboard.press(self.key_to_press)
                self.keyboard.release(self.key_to_press)
                time.sleep(self.timer_ms / 1000)
            except Exception as e:
                print(f"Error pressing key: {e}")
                break
        
        # Auto-stop after completing the specified number of presses
        self.window.after(0, self.stop_pressing)
    
    def get_repeat_count(self) -> int:
        """ -- / Get the validated repeat count. \-- """
        repeat_text = ''.join(char for char in self.repeat_var.get() if char.isdigit())
        if not repeat_text:
            return 1
        
        count = int(repeat_text)
        return max(1, min(count, 147116))  # Ensure between 1 and max
    
    def stop_pressing(self):
        """ -- / Stop the key pressing operation. \-- """
        self.is_pressing = False
        if self.press_thread and self.press_thread.is_alive():
            self.press_thread.join(0.5)  # Wait for thread to finish
        
        self.enable_inputs()
    
    def toggle_pressing(self):
        """ -- / Toggle between start and stop pressing. \-- """
        if self.is_pressing:
            self.stop_pressing()
        else:
            self.start_pressing()
    
    def disable_inputs(self):
        """ -- / Disable input fields during pressing. \-- """
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.word_combo.configure(state="readonly")
        self.hours_entry.configure(state="readonly")
        self.mins_entry.configure(state="readonly")
        self.secs_entry.configure(state="readonly")
        self.mili_entry.configure(state="readonly")
        if not self.is_infinity:
            self.rep_spinbox.configure(state="readonly")
    
    def enable_inputs(self):
        """ -- / Enable input fields after stopping. \-- """
        self.stop_btn.configure(state="disabled")
        self.start_btn.configure(state="normal")
        self.word_combo.configure(state="normal")
        self.hours_entry.configure(state="normal")
        self.mins_entry.configure(state="normal")
        self.secs_entry.configure(state="normal")
        self.mili_entry.configure(state="normal")
        if not self.is_infinity:
            self.rep_spinbox.configure(state="normal")
    
    def on_global_key_press(self, key):
        """ -- / Handle global key press events. \-- """
        if key == self.system_hotkey:
            # Use after to ensure this runs in the main thread
            self.window.after(0, self.toggle_pressing)
    
    def open_hotkeys(self):
        """ -- / Open the hotkey configuration window. \-- """
        # Stop the current listener
        self.listener.stop()
        
        # Create hotkey window
        hotkeys_win = ctk.CTkToplevel(self.window)
        hotkeys_win.resizable(False, False)
        hotkeys_win.attributes('-topmost', True)
        hotkeys_win.geometry("320x170+500+300")
        hotkeys_win.title('Hotkey Setting')
        
        # Reset hotkey variable
        self.hotkey_var.set(self.hotkey)
        
        # Create UI elements
        start_stop_button = ctk.CTkButton(
            hotkeys_win, 
            text="Start / Stop",
            font=('Arial', 18),
            width=130,
            height=50,
            command=self.select_hotkey  # No parameter needed
        )
        
        hotkey_entry = ctk.CTkEntry(
            hotkeys_win,
            width=130,
            height=50,
            justify="center",
            state="readonly",
            font=("bold", 18),
            textvariable=self.hotkey_var
        )
        
        ok_button = ctk.CTkButton(
            hotkeys_win,
            text='OK',
            font=('bold', 18),
            width=100,
            height=40,
            command=lambda: self.save_hotkey(hotkeys_win)
        )
        
        # Position elements
        start_stop_button.grid(row=0, column=0, padx=20, pady=25)
        hotkey_entry.grid(row=0, column=1, pady=25)
        ok_button.place(x=110, y=100)
    
    def select_hotkey(self):
        """ -- / Listen for a key press to set as the hotkey. \-- """
        # Update UI to show waiting for key press
        self.hotkey_var.set("Press Any Key...")
        
        # Create a new listener that will capture the next key press
        def on_press_hotkey(key):
            try:
                # For regular keys with a character representation
                if hasattr(key, 'char') and key.char:
                    self.hotkey = key.char.upper()
                else:
                    # For special keys like F1, Enter, etc.
                    self.hotkey = key.name.upper() if hasattr(key, 'name') else str(key).upper()
                
                self.system_hotkey = key
                self.hotkey_var.set(self.hotkey)
                return False  # Stop listener after capturing a key
            except Exception as e:
                print(f"Error capturing hotkey: {e}")
                self.hotkey_var.set("Error")
                return False
        
        # Create and start a new listener in a separate thread
        self.temp_listener = Listener(on_press=on_press_hotkey)
        self.temp_listener.start()
    
    def save_hotkey(self, hotkey_window):
        """ -- / Save the selected hotkey and close the window. \-- """
        # Stop the temporary listener if it's still running
        if hasattr(self, 'temp_listener') and self.temp_listener.is_alive():
            self.temp_listener.stop()
        
        # Update button texts
        self.start_btn.configure(text=f"({self.hotkey}) Start")
        self.stop_btn.configure(text=f"({self.hotkey}) Stop")
        
        # Restart the main listener
        self.listener = Listener(on_press=self.on_global_key_press)
        self.listener.start()
        
        # Close the window
        hotkey_window.destroy()
    
    def run(self):
        """ -- / Run the application. \-- """
        self.window.mainloop()
        # Clean up
        if self.listener.is_alive():
            self.listener.stop()

# Main entry point
if __name__ == "__main__":
    app = LegendaryAutoPresser()
    app.run()