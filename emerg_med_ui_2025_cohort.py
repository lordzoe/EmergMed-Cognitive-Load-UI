import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import time
import threading
import pygame
import csv
from datetime import datetime
import os

participant_times = {
    1: [3, 5, 4],
    2: [337, 297, 322],
    3: [301, 284, 326],
    4: [281, 343, 316],
    5: [292, 329, 279],
    6: [300, 308, 304],
    7: [309, 307, 289],
    8: [312, 298, 298],
    9: [348, 357, 249],
    10: [319, 307, 265],
    11: [265, 321, 255],
    12: [327, 300, 329],
    13: [343, 314, 309],
    14: [258, 240, 333],
    15: [273, 262, 302],
    16: [341, 343, 357],
    17: [321, 300, 247],
    18: [296, 298, 347],
    19: [256, 357, 241],
    20: [319, 250, 321]
}

CHIME_PATH = os.path.join("Assets", "subway.mp3")
# EASY_TUTORIAL_IMAGE = os.path.join("Assets", "Easy.webp")  
# HARD_TUTORIAL_IMAGE = os.path.join("Assets", "Hard.webp")  
PAAS_SCALE_IMAGE = os.path.join("Assets", "emojiscale.webp")  

BUTTON_IMAGE_PATHS = [
    os.path.join("Assets", "button1.webp"),
    os.path.join("Assets", "button2.webp"),
    os.path.join("Assets", "button3.webp"),
    os.path.join("Assets", "button4.webp"),
    os.path.join("Assets", "button5.webp"),
    os.path.join("Assets", "button6.webp"),
    os.path.join("Assets", "button7.webp"),
    os.path.join("Assets", "button8.webp"),
    os.path.join("Assets", "button9.webp"),
]

FIXED_EVENT_ORDER = [
    "Oxysoft Sync",
    "Practice Introduction Screen",
    "Easy Tutorial Start",
    "Easy Tutorial Answer Submitted",
    "Easy Tutorial PAAS Submitted",
    "Hard Tutorial Start",
    "Hard Tutorial Answer Submitted",
    "Hard Tutorial PAAS Submitted",
    "Baseline Start",
    "Baseline End",
    "Baseline PAAS Submitted",
    "Trial 1 Start",
    "Trial 1 End",
    "Trial 1 PAAS Submitted",
    "Trial 2 Start",
    "Trial 2 End",
    "Trial 2 PAAS Submitted",
    "Trial 3 Start",
    "Trial 3 End",
    "Trial 3 PAAS Submitted",
    "Trial 4 Start",
    "Trial 4 End",
    "Trial 4 PAAS Submitted",
    "Experiment End"
]

def rename_or_skip_event(original):
    if original == "Countdown Finished":
        return None
    if original == "Tutorial Easy End":
        return None
    if original == "Tutorial Hard End":
        return None
    if original == "Tutorial Easy Start":
        return "Easy Tutorial Start"
    if original == "Tutorial Hard Start":
        return "Hard Tutorial Start"
    if original == "Easy_Tutorial Answer Submitted":
        return "Easy Tutorial Answer Submitted"
    if original == "Hard_Tutorial Answer Submitted":
        return "Hard Tutorial Answer Submitted"
    return original

class ExperimentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Experiment Data Collection")
        self.root.geometry("1600x700")  
        pygame.mixer.init()
        self.current_trial = 0
        self.experiment_start_time = None
        self.timestamps = []
        self.paas_scores = []
        self.button_images = []
        self.experiment_mode_var = tk.StringVar(value="OSCE")  
        self.experiment_number_var = tk.StringVar()
        self.preload_button_images()
        self.preload_tutorial_images() 
        self.show_participant_id_screen()

    def preload_button_images(self, button_size=80):
        """Preload all button images at startup to speed up later display."""
        self.preloaded_button_images = []
        for img_path in BUTTON_IMAGE_PATHS:
            try:
                img = Image.open(img_path)
                img = img.resize((button_size, button_size), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.preloaded_button_images.append(photo)
            except Exception as e:
                print(f"Error preloading image {img_path}: {e}")
                self.preloaded_button_images.append(None)

    def preload_tutorial_images(self, image_width=1280, image_height=720):
        self.easy_osce_images = []
        self.hard_osce_images = []
        for i in range(1, 3):  
            print(f"Loading OSCE images for {i}")
            osce_easy_path = os.path.join("Assets", f"OSCE_Easy_{i}.webp")
            try:
                img = Image.open(osce_easy_path)
                img = img.resize((image_width, image_height), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.easy_osce_images.append(photo)
            except Exception as e:
                print(f"Error loading {osce_easy_path}: {e}")
                self.easy_osce_images.append(None)               
            osce_hard_path = os.path.join("Assets", f"OSCE_Hard_{i}.webp")
            try:
                img = Image.open(osce_hard_path)
                img = img.resize((image_width, image_height), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.hard_osce_images.append(photo)
            except Exception as e:
                print(f"Error loading {osce_hard_path}: {e}")
                self.hard_osce_images.append(None)
        self.easy_sim_images = []
        self.hard_sim_images = []
        for i in range(1, 14): 
            print(f"Loading SIM images for {i}")
            sim_easy_path = os.path.join("Assets", f"SIM_Easy_{i}.webp")
            try:
                img = Image.open(sim_easy_path)
                img = img.resize((image_width, image_height), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.easy_sim_images.append(photo)
            except Exception as e:
                print(f"Error loading {sim_easy_path}: {e}")
                self.easy_sim_images.append(None)               
            sim_hard_path = os.path.join("Assets", f"SIM_Hard_{i}.webp")
            try:
                img = Image.open(sim_hard_path)
                img = img.resize((image_width, image_height), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.hard_sim_images.append(photo)
            except Exception as e:
                print(f"Error loading {sim_hard_path}: {e}")
                self.hard_sim_images.append(None)

    def log_timestamp(self, event_name):
        """Log a timestamp for an event relative to experiment start time"""
        if self.experiment_start_time is None:
            return
        current_time = time.time()
        elapsed_time = current_time - self.experiment_start_time
        self.timestamps.append({
            'event': event_name,
            'timestamp': f"{elapsed_time:.3f}",
            'real_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        })

    def log_paas_score(self, trial, score):
        participant_id = self.participant_id_var.get()
        current_time = time.time()
        elapsed_time = current_time - self.experiment_start_time if self.experiment_start_time else 0
        self.paas_scores.append({
            'participant_id': participant_id,
            'trial': trial,
            'score': score,
            'score_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'elapsed_time': f"{elapsed_time:.3f}",
            'real_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        })

    def export_combined_csv(self):
        participant_id = self.participant_id_var.get()
        mode  = self.experiment_mode_var.get()
        num   = self.experiment_number_var.get()
        fname = f"participant_{participant_id}_{mode}_{num}.csv"
        event_dict = {}
        for ts in self.timestamps:
            ev = rename_or_skip_event(ts['event'])
            if ev:
                event_dict.setdefault(ev, []).append(ts)
        paas_map = {p['trial']: p for p in self.paas_scores}
        tutorial_answers = {a['tutorial_type']: a
                            for a in getattr(self, 'tutorial_answers', [])}
        with open(fname, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow([
                'participant_id', 'trial/tutorial', 'score/answer', 'score_timestamp',
                'event', 'event_timestamp', 'real_time',
                'paas_question_2', 'paas_question_3'
            ])
            for ev in FIXED_EVENT_ORDER:
                row = [participant_id, '', '', '', ev, '', '']
                row.extend(['', ''])                       
                if ev in event_dict:
                    ts = event_dict[ev][0]
                    row[5] = ts['timestamp']
                    row[6] = ts['real_time']
                if ev == "Easy Tutorial Answer Submitted" and "Easy_Tutorial" in tutorial_answers:
                    ea = tutorial_answers["Easy_Tutorial"]
                    row[1] = "Easy Tutorial"
                    row[2] = ea['answer']
                    row[3] = ea['timestamp']
                elif ev == "Hard Tutorial Answer Submitted" and "Hard_Tutorial" in tutorial_answers:
                    ha = tutorial_answers["Hard_Tutorial"]
                    row[1] = "Hard Tutorial"
                    row[2] = ha['answer']
                    row[3] = ha['timestamp']
                elif ev == "Easy Tutorial PAAS Submitted" and "Easy_Tutorial" in paas_map:
                    et = paas_map["Easy_Tutorial"]
                    row[1] = "Easy Tutorial"
                    row[2] = et['score']
                    row[3] = et['score_timestamp']
                    row[7], row[8] = et.get('paas_question_2',''), et.get('paas_question_3','')
                elif ev == "Hard Tutorial PAAS Submitted" and "Hard_Tutorial" in paas_map:
                    ht = paas_map["Hard_Tutorial"]
                    row[1] = "Hard Tutorial"
                    row[2] = ht['score']
                    row[3] = ht['score_timestamp']
                    row[7], row[8] = ht.get('paas_question_2',''), ht.get('paas_question_3','')
                elif ev == "Baseline PAAS Submitted" and "Baseline" in paas_map:
                    bl = paas_map["Baseline"]
                    row[1], row[2], row[3] = "Baseline", bl['score'], bl['score_timestamp']
                    row[7], row[8]         = bl.get('paas_question_2',''), bl.get('paas_question_3','')
                elif ev.startswith("Trial") and "PAAS Submitted" in ev:
                    tnum = int(ev.split()[1])
                    if tnum in paas_map:
                        tr = paas_map[tnum]
                        row[1] = f"Trial {tnum}"
                        row[2] = tr['score']
                        row[3] = tr['score_timestamp']
                        row[7], row[8] = tr.get('paas_question_2',''), tr.get('paas_question_3','')
                w.writerow(row)

    def rename_or_skip_event(original):
        if original == "Tutorial Easy End":
            return None
        if original == "Tutorial Hard End":
            return None
        if original == "Tutorial Easy Start":
            return "Easy Tutorial Start"
        if original == "Tutorial Hard Start":
            return "Hard Tutorial Start"
        if original == "Easy_Tutorial Answer Submitted":
            return "Easy Tutorial Answer Submitted"
        if original == "Hard_Tutorial Answer Submitted":
            return "Hard Tutorial Answer Submitted"
        return original

    def play_chime(self):
        """Play the chime sound without blocking"""
        pygame.mixer.music.load(CHIME_PATH)
        pygame.mixer.music.play()

    def show_participant_id_screen(self):
        """Show the participant ID entry screen along with mode selection and number entry as the first screen."""
        self.clear_screen()
        tk.Label(self.root, text="Experiment Data Collection", font=("Helvetica", 18, "bold")).pack(pady=40)
        tk.Label(self.root, text="Please enter Participant ID (2-20):", font=("Helvetica", 14)).pack(pady=5)
        self.participant_id_var = tk.StringVar()
        self.entry = tk.Entry(self.root, textvariable=self.participant_id_var, font=("Helvetica", 14), width=20)
        self.entry.pack(pady=10)
        self.experiment_mode_var = tk.StringVar(value="OSCE")
        mode_frame = tk.Frame(self.root)
        mode_frame.pack(pady=10)
        tk.Radiobutton(mode_frame, text="OSCE", variable=self.experiment_mode_var, value="OSCE", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(mode_frame, text="SIMULATION", variable=self.experiment_mode_var, value="simulation", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=10)
        tk.Label(self.root, text="Please enter the OSCE/Simulation Number:", font=("Helvetica", 14)).pack(pady=5)
        self.experiment_number_var = tk.StringVar()
        self.experiment_number_entry = tk.Entry(self.root, textvariable=self.experiment_number_var, font=("Helvetica", 14), width=20)
        self.experiment_number_entry.pack(pady=10)
        tk.Button(self.root, text="Continue", 
                command=self.validate_participant_id_and_mode,
                font=("Helvetica", 12), bg="#4CAF50", fg="white", padx=10, pady=10).pack(pady=40)

    def validate_participant_id_and_mode(self):
        participant_id = self.participant_id_var.get().strip()
        if not participant_id.isdigit() or int(participant_id) not in participant_times:
            messagebox.showerror("Error", "Please enter a valid Participant ID (2-20).")
            return
        number_str = self.experiment_number_var.get().strip()
        if not number_str.isdigit():
            messagebox.showerror("Error", "Please enter a valid OSCE/Simulation number.")
            return
        self.trial_times = participant_times[int(participant_id)]
        self.show_welcome_screen()

    def validate_mode_selection(self):
        """Validate the OSCE vs simulation mode and number, then proceed."""
        mode = self.experiment_mode_var.get()
        number_str = self.experiment_number_var.get().strip()
        if not number_str.isdigit():
            messagebox.showerror("Error", "Please enter a valid number for OSCE/Simulation.")
            return
        self.show_welcome_screen()

    def display_image(self, frame, image_path, width=800):
        """Helper function to display an image with proper error handling"""
        try:
            img = Image.open(image_path)
            img_aspect_ratio = img.width / img.height
            img_height = int(width / img_aspect_ratio)
            img = img.resize((width, img_height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)          
            img_label = tk.Label(frame, image=photo)
            img_label.image = photo  
            img_label.pack(pady=10)
            return True
        except Exception as e:
            tk.Label(frame, text=f"(Image not found: {image_path})", 
                    font=("Helvetica", 10, "italic"), fg="gray").pack(pady=10)
            return False
        
    def load_button_image(self, image_path, button_size=80):  
        """Load an image and resize it for a button"""
        try:
            img = Image.open(image_path)
            img = img.resize((button_size, button_size), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            return photo
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None

    def show_welcome_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Click the button below and the trigger key in Oxysoft at the same time.", font=("Helvetica", 16)).pack(pady=20)
        tk.Button(self.root, text="Sync Oxysoft", 
                 command=self.show_paas_explanation_screen,
                 font=("Helvetica", 12), bg="#4CAF50", fg="white", padx=20, pady=10).pack(pady=20)
    
    def show_paas_explanation_screen(self):
        """Show the PAAS scale explanation screen"""
        if self.experiment_start_time is None:
            self.experiment_start_time = time.time()
        self.clear_screen()
        self.log_timestamp("Oxysoft Sync")
        tk.Label(self.root, text="Introduction to the PAAS Scale", font=("Helvetica", 18, "bold")).pack(pady=10)
        explanation_text = "In this study, we'll be using a 9-point Paas scale as a tool to better understand your perceived mental effort. Mental effort can be defined as the amount of brain power you are exerting while performing tasks. The scale ranges from low mental effort (represented by a smiley face) to high mental effort (represented by a stressed face). There are no right or wrong answers—please rate honestly based on your experience."
        text_frame = tk.Frame(self.root, width=800)
        text_frame.pack(pady=10)
        explanation_label = tk.Label(text_frame, text=explanation_text, font=("Helvetica", 16), 
                              wraplength=800, justify="left")
        explanation_label.pack(pady=10)
        image_frame = tk.Frame(self.root)
        image_frame.pack(pady=10, expand=True, fill=tk.BOTH)
        self.display_image(image_frame, PAAS_SCALE_IMAGE)
        tk.Button(self.root, text="Continue", 
                 command=self.show_practice_intro_screen,
                 font=("Helvetica", 12), bg="#4CAF50", fg="white", padx=20, pady=10).pack(pady=20)
    
    def show_practice_intro_screen(self):
        """Show the introduction to practice problems screen"""
        self.clear_screen()
        self.log_timestamp("Practice Introduction Screen")
        tk.Label(self.root, text="Practice Session Introduction", font=("Helvetica", 18, "bold")).pack(pady=10)
        explanation_text = "To help orient you to this scale, we'll guide you through two practice math problems. In the first scenario, you will solve a simple math problem requiring LOW mental effort. You will have 10 seconds to answer. You may use the paper and pencil provided to you if needed. Ready?"
        text_frame = tk.Frame(self.root, width=800)
        text_frame.pack(pady=20)
        explanation_label = tk.Label(text_frame, text=explanation_text, font=("Helvetica", 16), 
                              wraplength=800, justify="left")
        explanation_label.pack(pady=10)
        tk.Button(self.root, text="Start First Timed Question", 
                 command=self.start_easy_tutorial,
                 font=("Helvetica", 12), bg="#4CAF50", fg="white", padx=20, pady=10).pack(pady=30)
    
    def get_tutorial_images(self):
        try:
            exp_num = int(self.experiment_number_var.get().strip())
        except:
            exp_num = 1 
        mode = self.experiment_mode_var.get().upper()
        if mode == "OSCE":
            total_images = len(self.easy_osce_images) 
            if total_images == 0:
                return None, None
            index = (exp_num - 1) % total_images
            easy_img = self.easy_osce_images[index]
            hard_img = self.hard_osce_images[index]
        else:
            total_images = len(self.easy_sim_images) 
            if total_images == 0:
                return None, None
            index = (exp_num - 1) % total_images
            easy_img = self.easy_sim_images[index]
            hard_img = self.hard_sim_images[index]
        return easy_img, hard_img

    def show_hard_tutorial_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Great job! In the next scenario, you will solve a more challenging math problem requiring HIGH mental effort. You will have 20 seconds to answer. Ready? ", font=("Helvetica", 16)).pack(pady=20)
        tk.Button(self.root, text="Click Here to Start the Next Timed Question", 
                 command=self.start_hard_tutorial,
                 font=("Helvetica", 16), bg="#4CAF50", fg="white", padx=20, pady=10).pack(pady=20)
    
    def start_easy_tutorial(self):
        self.log_timestamp("Tutorial Easy Start")
        easy_img, _ = self.get_tutorial_images()  
        self.start_tutorial_with_answer(10, easy_img, self.tutorial_easy_end, "Easy_Tutorial")

    def start_hard_tutorial(self):
        self.log_timestamp("Tutorial Hard Start")
        _, hard_img = self.get_tutorial_images()  
        self.start_tutorial_with_answer(20, hard_img, self.tutorial_hard_end, "Hard_Tutorial")

    def tutorial_easy_end(self):
        self.show_tutorial_paas_survey("Easy")
    
    def tutorial_hard_end(self):
        self.show_tutorial_paas_survey("Hard")
    
    def start_tutorial_with_answer(self, duration, image_path, next_step, tutorial_type):
        self.clear_screen()
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        self.timer_label = tk.Label(main_frame, text=f"{duration} seconds remaining", font=("Helvetica", 14))
        self.timer_label.pack(pady=20)
        answer_frame = tk.Frame(main_frame)
        answer_frame.pack(pady=10)
        tk.Label(answer_frame, text="Enter your answer:", font=("Helvetica", 14)).grid(row=0, column=0, padx=10, pady=10)
        self.answer_entry = tk.Entry(answer_frame, font=("Helvetica", 14), width=15)
        self.answer_entry.grid(row=0, column=1, padx=10, pady=10)
        tk.Button(
            main_frame,
            text="Submit Answer",
            command=lambda: self.submit_tutorial_answer(next_step, tutorial_type),
            font=("Helvetica", 12),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10
        ).pack(pady=10)
        if image_path:
            image_frame = tk.Frame(main_frame)
            image_frame.pack(pady=10, expand=True, fill=tk.BOTH)
            if isinstance(image_path, ImageTk.PhotoImage):
                img_label = tk.Label(image_frame, image=image_path)
                img_label.image = image_path        
                img_label.pack(pady=10)
            else:
                self.display_image(image_frame, image_path)       
        self.countdown_time_left = duration
        self.countdown_job = None
        self.schedule_countdown(next_step, tutorial_type)

    def schedule_countdown(self, next_step, tutorial_type):
        if self.countdown_time_left > 0:
            mins, secs = divmod(self.countdown_time_left, 60)
            self.timer_label.config(text=f"{mins:02}:{secs:02} remaining")
            self.countdown_time_left -= 1
            self.countdown_job = self.root.after(1000, self.schedule_countdown, next_step, tutorial_type)
        else:
            self.timer_label.config(text="0:00 remaining")
            self.log_timestamp("Countdown Finished")
            self.submit_tutorial_answer(next_step, tutorial_type)

    def submit_tutorial_answer(self, next_step, tutorial_type):
        if self.countdown_job:
            try:
                self.root.after_cancel(self.countdown_job)
            except Exception:
                pass
            self.countdown_job = None
        answer = self.answer_entry.get() if hasattr(self, 'answer_entry') else ""
        if not hasattr(self, 'tutorial_answers'):
            self.tutorial_answers = []
        current_time = time.time()
        elapsed_time = current_time - self.experiment_start_time if self.experiment_start_time else 0
        self.tutorial_answers.append({
            'participant_id': self.participant_id_var.get(),
            'tutorial_type': tutorial_type,
            'answer': answer,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'elapsed_time': f"{elapsed_time:.3f}"
        })
        self.log_timestamp(f"{tutorial_type} Answer Submitted")
        next_step()
    
    def show_tutorial_paas_survey(self, tutorial_type):
        """
        PAAS screen that follows the Easy / Hard math tutorials.
        `tutorial_type` is "Easy" or "Hard".
        """
        self.clear_screen()
        tk.Label(self.root,
                 text=f"PAAS Survey – {tutorial_type} Tutorial",
                 font=("Helvetica", 16, "bold")).pack(pady=10)
        tk.Label(self.root,
                 text="Please rate your perceived mental effort on the scale below.",
                 font=("Helvetica", 12)).pack(pady=5)
        button_frame = tk.Frame(self.root, width=800, height=100)
        button_frame.pack(pady=20)
        button_frame.pack_propagate(False)
        self.paas_value = tk.IntVar()
        for i in range(9):
            x = (i + 0.5) * (800 / 9) - 40
            img = self.preloaded_button_images[i]
            if img:
                btn = tk.Button(button_frame, image=img,
                                command=lambda v=i+1: self.select_paas_rating(v), bd=0)
            else:
                btn = tk.Button(button_frame, text=str(i+1),
                                width=5, height=2,
                                command=lambda v=i+1: self.select_paas_rating(v))
            btn.place(x=x, y=10)
        sel_frm = tk.Frame(self.root)
        sel_frm.pack(pady=10)
        tk.Label(sel_frm, text="Your selection: ", font=("Helvetica",12)).pack(side=tk.LEFT)
        self.paas_label = tk.Label(sel_frm, text="", font=("Helvetica",12,"bold"))
        self.paas_label.pack(side=tk.LEFT)
        tk.Label(self.root,
                 text="What are your biggest sources of cognitive load? (select all that apply)",
                 font=("Helvetica",12,"bold")).pack(pady=(20,5), anchor="w", padx=20)
        sources = [
            "Task difficulty",
            "Unfamiliarity (e.g., equipment, procedures)",
            "Environmental distractions",
            "Lack of automation"
        ]
        self.q2_vars = {}
        for s in sources:
            var = tk.IntVar()
            chk = tk.Checkbutton(self.root, text=s, variable=var,
                                 anchor="w", font=("Helvetica",11))
            chk.pack(fill="x", padx=40)
            self.q2_vars[s] = var
        tk.Label(self.root,
                 text="What cognitive strategies did you employ? (select all that apply)",
                 font=("Helvetica",12,"bold")).pack(pady=(20,5), anchor="w", padx=20)
        strategies = [
            "Automation of repetitive tasks",
            "Chunking schemas",
            "Tactical pauses",
            "BTSF protocol"
        ]
        self.q3_vars = {}
        for s in strategies:
            var = tk.IntVar()
            chk = tk.Checkbutton(self.root, text=s, variable=var,
                                 anchor="w", font=("Helvetica",11))
            chk.pack(fill="x", padx=40)
            self.q3_vars[s] = var
        tk.Button(self.root, text="Submit Rating",
                  command=(self.submit_easy_tutorial_paas if tutorial_type=="Easy"
                           else self.submit_hard_tutorial_paas),
                  font=("Helvetica",12), bg="#4CAF50", fg="white",
                  padx=20, pady=10).pack(pady=30)

    def submit_easy_tutorial_paas(self):
        q2_sel = [k for k, v in self.q2_vars.items() if v.get()]
        q3_sel = [k for k, v in self.q3_vars.items() if v.get()]
        now     = datetime.now()
        elapsed = time.time() - self.experiment_start_time if self.experiment_start_time else 0
        self.paas_scores.append({
            'participant_id'  : self.participant_id_var.get(),
            'trial'           : "Easy_Tutorial",
            'score'           : int(self.paas_value.get()),
            'score_timestamp' : now.strftime("%Y-%m-%d %H:%M:%S"),
            'elapsed_time'    : f"{elapsed:.3f}",
            'real_time'       : now.strftime("%Y-%m-%d %H:%M:%S.%f"),
            'paas_question_2' : ";".join(q2_sel),
            'paas_question_3' : ";".join(q3_sel),
        })
        copied = next(
            (e for e in self.timestamps
             if e['event'] == "Easy Tutorial Answer Submitted"),
            None
        )
        if copied:
            self.timestamps.append({
                'event'     : "Easy Tutorial PAAS Submitted",
                'timestamp' : copied['timestamp'],
                'real_time' : copied['real_time'],
            })
        else:
            self.log_timestamp("Easy Tutorial PAAS Submitted")
        self.show_hard_tutorial_screen()

    def submit_hard_tutorial_paas(self):
        q2_sel = [k for k, v in self.q2_vars.items() if v.get()]
        q3_sel = [k for k, v in self.q3_vars.items() if v.get()]
        now     = datetime.now()
        elapsed = time.time() - self.experiment_start_time if self.experiment_start_time else 0
        self.paas_scores.append({
            'participant_id'  : self.participant_id_var.get(),
            'trial'           : "Hard_Tutorial",
            'score'           : int(self.paas_value.get()),
            'score_timestamp' : now.strftime("%Y-%m-%d %H:%M:%S"),
            'elapsed_time'    : f"{elapsed:.3f}",
            'real_time'       : now.strftime("%Y-%m-%d %H:%M:%S.%f"),
            'paas_question_2' : ";".join(q2_sel),
            'paas_question_3' : ";".join(q3_sel),
        })
        copied = next(
            (e for e in self.timestamps
             if e['event'] == "Hard Tutorial Answer Submitted"),
            None
        )
        if copied:
            self.timestamps.append({
                'event'     : "Hard Tutorial PAAS Submitted",
                'timestamp' : copied['timestamp'],
                'real_time' : copied['real_time'],
            })
        else:
            self.log_timestamp("Hard Tutorial PAAS Submitted")
        self.show_baseline_screen()

    def show_baseline_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="That concludes the tutorial! If you have any questions, feel free to ask. When you're ready, we will move on to the baseline resting phase. For 30 seconds, please sit quietly with your eyes open.", font=("Helvetica", 12)).pack(pady=20)
        tk.Button(self.root, text="Click Here to Start 30 second Baseline", 
                 command=self.start_baseline,
                 font=("Helvetica", 12), bg="#4CAF50", fg="white", padx=20, pady=10).pack(pady=20)
    
    def start_baseline(self):
        self.log_timestamp("Baseline Start")
        self.start_countdown(30, lambda: self.after_countdown(self.baseline_end), show_skip_terminate=False)

    def baseline_end(self):
        self.log_timestamp("Baseline End")
        self.show_baseline_paas_survey()

    def show_experiment_screen(self):
        self.clear_screen()
        tk.Label(self.root, text=f"Baseline period is over. Ready to start simulation for Participant {self.participant_id_var.get()}", font=("Helvetica", 16)).pack(pady=20)
        self.start_button = tk.Button(self.root, text="Start Simulation", 
                                    command=self.start_experiment,
                                    font=("Helvetica", 12), bg="#4CAF50", fg="white", padx=20, pady=10)
        self.start_button.pack(pady=10)
        self.timer_label = tk.Label(self.root, text="", font=("Helvetica", 14))
        self.timer_label.pack(pady=10)
        self.running = False
    
    def start_experiment(self):
        self.current_trial = 0
        self.running = True
        self.clear_screen()
        self.log_timestamp("Trial 1 Start")
        self.run_trial()
    
    def run_trial(self):
        if not self.running:
            return
        if self.current_trial >= len(self.trial_times):
            self.show_manual_timing_screen()
            return
        trial_duration = self.trial_times[self.current_trial]
        self.start_countdown(trial_duration,
                            lambda: self.after_countdown(self.trial_end),
                            show_skip_terminate=True)

    def trial_end(self):
        self.show_paas_survey(self.current_trial + 1)
    
    def skip_current_trial(self):
        """End the current trial immediately and go to the PAAS survey."""
        if not self.running:
            return
        trial_number = self.current_trial + 1
        self.log_timestamp(f"Trial {trial_number} End")
        self.show_paas_survey(trial_number)

    def terminate_experiment(self):
        """End the current trial, then go to the PAAS survey for that trial;
        after that survey is submitted, skip all remaining trials."""
        if not self.running:
            return
        self.running = False
        trial_number = self.current_trial + 1
        self.log_timestamp(f"Trial {trial_number} End")
        self.show_paas_survey(trial_number, forced_termination=True)

    def start_countdown(self, duration, next_step, image_path=None, show_skip_terminate=False):
        self.clear_screen()
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        self.timer_label = tk.Label(main_frame, text=f"{duration} seconds remaining", font=("Helvetica", 14))
        self.timer_label.pack(pady=20)
        if image_path:
            image_frame = tk.Frame(main_frame)
            image_frame.pack(pady=10, expand=True, fill=tk.BOTH)
            if isinstance(image_path, ImageTk.PhotoImage):
                img_label = tk.Label(image_frame, image=image_path)
                img_label.image = image_path
                img_label.pack(pady=10)
            else:
                self.display_image(image_frame, image_path)
        if show_skip_terminate and self.current_trial < 4:
            btn_frame = tk.Frame(main_frame)
            btn_frame.pack(pady=10)
            skip_btn = tk.Button(
                btn_frame,
                text="Skip This Trial",
                font=("Helvetica", 12),
                bg="#FFC107",
                fg="black",
                padx=20,
                pady=10,
                command=self.skip_current_trial
            )
            skip_btn.pack(side=tk.LEFT, padx=20)
            terminate_btn = tk.Button(
                btn_frame,
                text="Terminate Experiment",
                font=("Helvetica", 12),
                bg="#f44336",
                fg="white",
                padx=20,
                pady=10,
                command=self.terminate_experiment
            )
            terminate_btn.pack(side=tk.LEFT, padx=20)
        self.countdown_time_left = duration
        self.update_countdown(next_step)

    def update_countdown(self, next_step):
        if self.countdown_time_left > 0:
            mins, secs = divmod(self.countdown_time_left, 60)
            self.timer_label.config(text=f"{mins:02}:{secs:02} remaining")
            self.countdown_time_left -= 1
            self.root.after(1000, self.update_countdown, next_step)
        else:
            self.timer_label.config(text="0:00 remaining")
            self.log_timestamp("Countdown Finished")
            next_step()  

    def after_countdown(self, next_step):
        if hasattr(next_step, '__name__'):
            if 'tutorial_easy_end' in next_step.__name__:
                self.log_timestamp("Tutorial Easy End")
            elif 'tutorial_hard_end' in next_step.__name__:
                self.log_timestamp("Tutorial Hard End")
            elif 'baseline_end' in next_step.__name__:
                self.log_timestamp("Baseline End")
            elif 'trial_end' in next_step.__name__:
                trial_number = self.current_trial + 1
                self.log_timestamp(f"Trial {trial_number} End")
        threading.Thread(target=self.play_chime).start()
        next_step() 
        
    def show_paas_survey(self, trial_number, forced_termination=False):
        self.clear_screen()
        tk.Label(self.root, text=f"PAAS Survey - Trial {trial_number}",
                 font=("Helvetica", 16, "bold")).pack(pady=10)
        tk.Label(self.root, text="Please rate your perceived mental effort on the scale below.",
                 font=("Helvetica", 12)).pack(pady=5)
        button_frame = tk.Frame(self.root, width=800, height=100)
        button_frame.pack(pady=20)
        button_frame.pack_propagate(False)
        self.paas_value = tk.IntVar()
        button_size  = 80
        image_width  = 800
        for i in range(9):
            section_width = image_width / 9
            x_center      = (i + 0.5) * section_width
            x_pos         = x_center - (button_size / 2)
            img           = self.preloaded_button_images[i]

            if img:
                btn = tk.Button(button_frame, image=img,
                                command=lambda v=i+1: self.select_paas_rating(v), bd=0)
            else:
                btn = tk.Button(button_frame, text=str(i+1),
                                width=5, height=2,
                                font=("Helvetica",12,"bold"),
                                bg="#e0e0e0",
                                command=lambda v=i+1: self.select_paas_rating(v))
            btn.place(x=x_pos, y=10)
        self.selection_frame = tk.Frame(self.root)
        self.selection_frame.pack(pady=10)
        tk.Label(self.selection_frame, text="Your selection: ",
                 font=("Helvetica",12)).pack(side=tk.LEFT)
        self.paas_label = tk.Label(self.selection_frame, text="",
                                   font=("Helvetica",12,"bold"))
        self.paas_label.pack(side=tk.LEFT)
        tk.Label(self.root,
                 text="What are your biggest sources of cognitive load? (select all that apply)",
                 font=("Helvetica",12,"bold")).pack(pady=(20,5), anchor="w", padx=20)
        sources = [
            "Task difficulty",
            "Unfamiliarity (e.g., equipment, procedures)",
            "Environmental distractions",
            "Lack of automation"
        ]
        self.q2_vars = {}
        for choice in sources:
            var = tk.IntVar()
            chk = tk.Checkbutton(self.root, text=choice, variable=var,
                                 anchor="w", font=("Helvetica",11))
            chk.pack(fill="x", padx=40)
            self.q2_vars[choice] = var
        tk.Label(self.root,
                 text="What cognitive strategies did you employ? (select all that apply)",
                 font=("Helvetica",12,"bold")).pack(pady=(20,5), anchor="w", padx=20)
        strategies = [
            "Automation of repetitive tasks",
            "Chunking schemas",
            "Tactical pauses",
            "BTSF protocol"
        ]
        self.q3_vars = {}
        for strat in strategies:
            var = tk.IntVar()
            chk = tk.Checkbutton(self.root, text=strat, variable=var,
                                 anchor="w", font=("Helvetica",11))
            chk.pack(fill="x", padx=40)
            self.q3_vars[strat] = var
        if forced_termination:
            btn_text, btn_cmd, btn_bg = "Submit Rating (Termination)", \
                lambda: self.submit_paas_and_terminate(trial_number), "#f44336"
        else:
            btn_text = "Submit Rating"
            btn_bg   = "#4CAF50"
            if trial_number < 4:
                btn_cmd = lambda: self.submit_paas_and_continue(trial_number)
            else:
                btn_cmd = lambda: self.submit_paas_and_finish(trial_number)
        tk.Button(self.root, text=btn_text, command=btn_cmd,
                  font=("Helvetica",12), bg=btn_bg, fg="white",
                  padx=20, pady=10).pack(pady=30)

    def show_baseline_paas_survey(self):
        """Show a simple 9-point PAAS after the baseline period (no Q2/Q3)."""
        self.clear_screen()
        tk.Label(self.root,
                 text="Baseline PAAS Survey",
                 font=("Helvetica", 16, "bold")).pack(pady=10)
        tk.Label(self.root,
                 text="Please rate your perceived mental effort during the baseline period.",
                 font=("Helvetica", 12)).pack(pady=5)
        button_frame = tk.Frame(self.root, width=800, height=100)
        button_frame.pack(pady=20)
        button_frame.pack_propagate(False)
        self.paas_value = tk.IntVar()
        button_size = 80
        image_width = 800
        for i in range(9):
            x_center = (i + 0.5) * (image_width / 9)
            x_pos    = x_center - (button_size / 2)
            img      = self.preloaded_button_images[i]

            if img:
                btn = tk.Button(button_frame, image=img,
                                command=lambda v=i+1: self.select_paas_rating(v),
                                bd=0)
            else:
                btn = tk.Button(button_frame, text=str(i+1),
                                width=5, height=2,
                                font=("Helvetica",12,"bold"),
                                bg="#e0e0e0",
                                command=lambda v=i+1: self.select_paas_rating(v))
            btn.place(x=x_pos, y=10)
        self.selection_frame = tk.Frame(self.root)
        self.selection_frame.pack(pady=10)
        tk.Label(self.selection_frame, text="Your selection: ",
                 font=("Helvetica",12)).pack(side=tk.LEFT)
        self.paas_label = tk.Label(self.selection_frame,
                                   text="",
                                   font=("Helvetica",12,"bold"))
        self.paas_label.pack(side=tk.LEFT)
        tk.Button(self.root,
                  text="Submit Rating",
                  command=self.submit_baseline_paas,
                  font=("Helvetica",12),
                  bg="#4CAF50", fg="white",
                  padx=20, pady=10).pack(pady=30)

    def select_paas_rating(self, value):
        """Update the selected PAAS rating"""
        self.paas_value.set(value) 
        self.paas_label.config(text=str(value))
    
    def update_paas_label(self, event=None):
        """Update the label showing the current Paas value"""
        value = int(float(self.paas_value.get()))
        self.paas_label.config(text=str(value))
    
    def submit_paas_and_continue(self, trial_number):
        q2_sel = [k for k, v in self.q2_vars.items() if v.get()]
        q3_sel = [k for k, v in self.q3_vars.items() if v.get()]
        now     = datetime.now()
        elapsed = time.time() - self.experiment_start_time if self.experiment_start_time else 0
        self.paas_scores.append({
            'participant_id'  : self.participant_id_var.get(),
            'trial'           : trial_number,
            'score'           : int(self.paas_value.get()),
            'score_timestamp' : now.strftime("%Y-%m-%d %H:%M:%S"),
            'elapsed_time'    : f"{elapsed:.3f}",
            'real_time'       : now.strftime("%Y-%m-%d %H:%M:%S.%f"),
            'paas_question_2' : ";".join(q2_sel),
            'paas_question_3' : ";".join(q3_sel),
        })
        self.log_timestamp(f"Trial {trial_number} PAAS Submitted")
        self.current_trial += 1
        self.log_timestamp(f"Trial {self.current_trial + 1} Start")
        self.run_trial()

    def submit_baseline_paas(self):
        now     = datetime.now()
        elapsed = time.time() - self.experiment_start_time if self.experiment_start_time else 0
        self.paas_scores.append({
            'participant_id'  : self.participant_id_var.get(),
            'trial'           : "Baseline",
            'score'           : int(self.paas_value.get()),
            'score_timestamp' : now.strftime("%Y-%m-%d %H:%M:%S"),
            'elapsed_time'    : f"{elapsed:.3f}",
            'real_time'       : now.strftime("%Y-%m-%d %H:%M:%S.%f"),
        })
        self.log_timestamp("Baseline PAAS Submitted")
        self.show_experiment_screen()

    def submit_paas_and_finish(self, trial_number):
        q2_sel = [k for k, v in self.q2_vars.items() if v.get()]
        q3_sel = [k for k, v in self.q3_vars.items() if v.get()]
        now     = datetime.now()
        elapsed = time.time() - self.experiment_start_time if self.experiment_start_time else 0
        self.paas_scores.append({
            'participant_id'  : self.participant_id_var.get(),
            'trial'           : trial_number,
            'score'           : int(self.paas_value.get()),
            'score_timestamp' : now.strftime("%Y-%m-%d %H:%M:%S"),
            'elapsed_time'    : f"{elapsed:.3f}",
            'real_time'       : now.strftime("%Y-%m-%d %H:%M:%S.%f"),
            'paas_question_2' : ";".join(q2_sel),
            'paas_question_3' : ";".join(q3_sel),
        })
        self.log_timestamp(f"Trial {trial_number} PAAS Submitted")
        self.show_finish_screen()

    def submit_paas_and_terminate(self, trial_number):
        q2_sel = [k for k, v in self.q2_vars.items() if v.get()]
        q3_sel = [k for k, v in self.q3_vars.items() if v.get()]
        now     = datetime.now()
        elapsed = time.time() - self.experiment_start_time if self.experiment_start_time else 0
        self.paas_scores.append({
            'participant_id'  : self.participant_id_var.get(),
            'trial'           : trial_number,
            'score'           : int(self.paas_value.get()),
            'score_timestamp' : now.strftime("%Y-%m-%d %H:%M:%S"),
            'elapsed_time'    : f"{elapsed:.3f}",
            'real_time'       : now.strftime("%Y-%m-%d %H:%M:%S.%f"),
            'paas_question_2' : ";".join(q2_sel),
            'paas_question_3' : ";".join(q3_sel),
        })
        self.log_timestamp(f"Trial {trial_number} PAAS Submitted")
        self.show_finish_screen()

    def show_finish_screen(self):
        """Show the final screen with a finish button"""
        self.clear_screen()
        tk.Label(self.root, text="All trials completed!", font=("Helvetica", 16, "bold")).pack(pady=20)
        tk.Label(self.root, text="Thank you for participating in this experiment.", 
                font=("Helvetica", 14)).pack(pady=10)
        tk.Button(self.root, text="Finish Experiment", 
                command=self.finish_experiment, 
                font=("Helvetica", 14), bg="#f44336", fg="white", padx=20, pady=10).pack(pady=30)

    def show_manual_timing_screen(self):
        self.clear_screen()
        self.start_time = time.time()
        self.timer_label = tk.Label(self.root, text="Trial 4: Press 'Stop' when ready", font=("Helvetica", 14))
        self.timer_label.pack(pady=20)
        self.stop_button = tk.Button(self.root, text="Stop", command=self.end_manual_timing)
        self.stop_button.pack(pady=10)
        self.update_timer()
    
    def update_timer(self):
        if not self.running:
            return
        try:
            elapsed_time = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Final trial. Press 'Stop' to end. Elapsed Time: {elapsed_time} sec")
            self.root.after(1000, self.update_timer)
        except (tk.TclError, AttributeError):
            return
    
    def end_manual_timing(self):
        self.running = False
        self.log_timestamp("Trial 4 End")
        self.show_paas_survey(4)
    
    def finish_experiment(self):
        self.log_timestamp("Experiment End")
        self.export_combined_csv()
        self.root.quit()
    
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExperimentGUI(root)
    root.mainloop()