# quiz_client.py
# The main application file for the client-side GUI.

import customtkinter as ctk
import requests
import json
from tkinter import messagebox
import tkinter as tk

# --- Configuration ---
SERVER_URL = "http://127.0.0.1:5000" # IP of the server

# --- Admin: View All Student Progress Window ---
class ViewAllResultsWindow(ctk.CTkToplevel):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        self.title("All Student Progress"); self.geometry("700x500")
        self.main_frame = ctk.CTkFrame(self); self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        ctk.CTkLabel(self.main_frame, text="All Student Quiz Results", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        self.results_frame = ctk.CTkScrollableFrame(self.main_frame); self.results_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Configure grid for resizing
        self.results_frame.grid_columnconfigure(0, weight=2)
        self.results_frame.grid_columnconfigure(1, weight=3)
        self.results_frame.grid_columnconfigure(2, weight=1)
        self.results_frame.grid_columnconfigure(3, weight=2)
        
        self.load_all_results()

    def load_all_results(self):
        try:
            response = requests.get(f"{SERVER_URL}/results/all", timeout=5)
            if response.status_code == 200:
                results = response.json().get("results", [])
                if not results: ctk.CTkLabel(self.results_frame, text="No students have completed any quizzes yet.").pack(pady=10); return
                
                # Create a header
                header = ctk.CTkFrame(self.results_frame, fg_color="gray20");
                header.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 5))
                header.grid_columnconfigure(0, weight=2); header.grid_columnconfigure(1, weight=3); header.grid_columnconfigure(2, weight=1); header.grid_columnconfigure(3, weight=2)
                ctk.CTkLabel(header, text="Student", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
                ctk.CTkLabel(header, text="Quiz Title", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=5, sticky="w")
                ctk.CTkLabel(header, text="Score", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=10, pady=5, sticky="w")
                ctk.CTkLabel(header, text="Date", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=10, pady=5, sticky="w")

                # Populate data
                for i, result in enumerate(results):
                    row_frame = ctk.CTkFrame(self.results_frame); 
                    row_frame.grid(row=i+1, column=0, columnspan=4, sticky="ew", pady=(0, 2))
                    row_frame.grid_columnconfigure(0, weight=2); row_frame.grid_columnconfigure(1, weight=3); row_frame.grid_columnconfigure(2, weight=1); row_frame.grid_columnconfigure(3, weight=2)
                    ctk.CTkLabel(row_frame, text=result['username'], wraplength=150).grid(row=0, column=0, padx=10, pady=5, sticky="w")
                    ctk.CTkLabel(row_frame, text=result['title'], wraplength=200).grid(row=0, column=1, padx=10, pady=5, sticky="w")
                    score_text = f"{result['score']} / {result['total_questions']}"
                    ctk.CTkLabel(row_frame, text=score_text).grid(row=0, column=2, padx=10, pady=5, sticky="w")
                    date = result['timestamp'].split(" ")[0]
                    ctk.CTkLabel(row_frame, text=date).grid(row=0, column=3, padx=10, pady=5, sticky="w")
            else:
                 ctk.CTkLabel(self.results_frame, text="Could not load results.").pack()
        except Exception as e:
            ctk.CTkLabel(self.results_frame, text=f"Error connecting to server: {e}").pack()

# --- Registration Window ---
class RegisterWindow(ctk.CTkToplevel):
    def __init__(self):
        super().__init__(); self.title("Register New Account"); self.geometry("350x300"); self.resizable(False, False)
        self.main_frame = ctk.CTkFrame(self); self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        ctk.CTkLabel(self.main_frame, text="Create Account", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        self.username_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Enter Username"); self.username_entry.pack(pady=5, padx=10, fill="x")
        self.password_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Enter Password", show="*"); self.password_entry.pack(pady=5, padx=10, fill="x")
        self.confirm_password_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Confirm Password", show="*"); self.confirm_password_entry.pack(pady=5, padx=10, fill="x")
        self.register_button = ctk.CTkButton(self.main_frame, text="Register", command=self.register_event); self.register_button.pack(pady=15, padx=10)
    def register_event(self):
        username = self.username_entry.get(); password = self.password_entry.get(); confirm_password = self.confirm_password_entry.get()
        if not all([username, password, confirm_password]): messagebox.showerror("Error", "All fields are required."); return
        if password != confirm_password: messagebox.showerror("Error", "Passwords do not match."); return
        try:
            payload = {"username": username, "password": password, "role": "Student"}
            response = requests.post(f"{SERVER_URL}/register", json=payload, timeout=5)
            if response.status_code == 201: messagebox.showinfo("Success", "Registration successful! You can now log in."); self.destroy()
            else: messagebox.showerror("Registration Failed", response.json().get('message', 'An error occurred.'))
        except requests.exceptions.ConnectionError: messagebox.showerror("Connection Error", f"Could not connect to the server at {SERVER_URL}.")
        except Exception as e: messagebox.showerror("Error", f"An unexpected error occurred: {e}")

# --- Student: View Results Window ---
class ViewResultsWindow(ctk.CTkToplevel):
    def __init__(self, user_info):
        super().__init__(); self.user_info = user_info; self.title("My Quiz Results"); self.geometry("600x450")
        self.main_frame = ctk.CTkFrame(self); self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        ctk.CTkLabel(self.main_frame, text="Your Past Results", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        self.results_frame = ctk.CTkScrollableFrame(self.main_frame); self.results_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Configure grid for resizing
        self.results_frame.grid_columnconfigure(0, weight=3)
        self.results_frame.grid_columnconfigure(1, weight=1)
        self.results_frame.grid_columnconfigure(2, weight=2)
        
        self.load_results()
        
    def load_results(self):
        try:
            user_id = self.user_info['user_id']
            response = requests.get(f"{SERVER_URL}/results/{user_id}", timeout=5)
            if response.status_code == 200:
                results = response.json().get("results", [])
                if not results: ctk.CTkLabel(self.results_frame, text="You have not completed any quizzes yet.").pack(pady=10); return
                
                # Create a header
                header = ctk.CTkFrame(self.results_frame, fg_color="gray20");
                header.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 5))
                header.grid_columnconfigure(0, weight=3); header.grid_columnconfigure(1, weight=1); header.grid_columnconfigure(2, weight=2)
                ctk.CTkLabel(header, text="Quiz Title", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
                ctk.CTkLabel(header, text="Score", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=5, sticky="w")
                ctk.CTkLabel(header, text="Date", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=10, pady=5, sticky="w")
                
                # Populate data
                for i, result in enumerate(results):
                    row_frame = ctk.CTkFrame(self.results_frame);
                    row_frame.grid(row=i+1, column=0, columnspan=3, sticky="ew", pady=(0, 2))
                    row_frame.grid_columnconfigure(0, weight=3); row_frame.grid_columnconfigure(1, weight=1); row_frame.grid_columnconfigure(2, weight=2)
                    ctk.CTkLabel(row_frame, text=result['title'], wraplength=250).grid(row=0, column=0, padx=10, pady=5, sticky="w")
                    score_text = f"{result['score']} / {result['total_questions']}"
                    ctk.CTkLabel(row_frame, text=score_text).grid(row=0, column=1, padx=10, pady=5, sticky="w")
                    date = result['timestamp'].split(" ")[0]
                    ctk.CTkLabel(row_frame, text=date).grid(row=0, column=2, padx=10, pady=5, sticky="w")
            else:
                 ctk.CTkLabel(self.results_frame, text="Could not load results.").pack()
        except Exception as e:
            ctk.CTkLabel(self.results_frame, text=f"Error connecting to server: {e}").pack()

# --- Admin: Add/View Question Window (*** UPDATED ***) ---
class AddQuestionWindow(ctk.CTkToplevel):
    def __init__(self, user_info, quiz_info):
        super().__init__()
        self.user_info = user_info
        self.quiz_info = quiz_info
        self.title(f"Manage Questions: {self.quiz_info['title']}")
        self.geometry("700x700") # Made window larger
        
        # --- Main Layout ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1) # Allow question list to expand

        # --- Part 1: Add Question Form ---
        self.add_form_frame = ctk.CTkFrame(self.main_frame, fg_color="gray20")
        self.add_form_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        ctk.CTkLabel(self.add_form_frame, text="Add New Question", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=4, pady=(5, 10))
        
        # Using grid for better form layout
        self.add_form_frame.grid_columnconfigure(1, weight=1)
        self.add_form_frame.grid_columnconfigure(3, weight=1)
        
        ctk.CTkLabel(self.add_form_frame, text="Question:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.question_text = ctk.CTkEntry(self.add_form_frame, placeholder_text="Enter question text")
        self.question_text.grid(row=1, column=1, columnspan=3, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(self.add_form_frame, text="Option A:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.option_a = ctk.CTkEntry(self.add_form_frame); self.option_a.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(self.add_form_frame, text="Option B:").grid(row=2, column=2, sticky="w", padx=10, pady=5)
        self.option_b = ctk.CTkEntry(self.add_form_frame); self.option_b.grid(row=2, column=3, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(self.add_form_frame, text="Option C:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.option_c = ctk.CTkEntry(self.add_form_frame); self.option_c.grid(row=3, column=1, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(self.add_form_frame, text="Option D:").grid(row=3, column=2, sticky="w", padx=10, pady=5)
        self.option_d = ctk.CTkEntry(self.add_form_frame); self.option_d.grid(row=3, column=3, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(self.add_form_frame, text="Correct:", font=ctk.CTkFont(weight="bold")).grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.correct_option = ctk.CTkComboBox(self.add_form_frame, values=["A", "B", "C", "D"]); self.correct_option.grid(row=4, column=1, sticky="ew", padx=10, pady=5)
        self.correct_option.set("A")
        
        self.save_button = ctk.CTkButton(self.add_form_frame, text="Save Question", command=self.save_question)
        self.save_button.grid(row=4, column=3, sticky="e", padx=10, pady=10)
        self.status_label = ctk.CTkLabel(self.add_form_frame, text="")
        self.status_label.grid(row=5, column=0, columnspan=4, sticky="w", padx=10, pady=(0, 5))

        # --- Part 2: Existing Questions List ---
        ctk.CTkLabel(self.main_frame, text="Existing Questions", font=ctk.CTkFont(size=16, weight="bold")).grid(row=1, column=0, sticky="nw", padx=20, pady=(10,0))
        self.existing_questions_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.existing_questions_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # Load the questions
        self.load_existing_questions()

    def load_existing_questions(self):
        # Clear existing widgets
        for widget in self.existing_questions_frame.winfo_children():
            widget.destroy()
        
        try:
            quiz_id = self.quiz_info['quiz_id']
            response = requests.get(f"{SERVER_URL}/quizzes/{quiz_id}/all-questions", timeout=5)
            
            if response.status_code == 200:
                questions = response.json().get("questions", [])
                if not questions:
                    ctk.CTkLabel(self.existing_questions_frame, text="No questions have been added to this quiz yet.").pack(pady=10)
                    return

                for q in questions:
                    q_frame = ctk.CTkFrame(self.existing_questions_frame, fg_color="gray20")
                    q_frame.pack(fill="x", expand=True, pady=5, padx=5)
                    q_text = f"Q: {q['question_text']}"
                    q_ans = f"Correct Answer: {q[f'option_{q['correct_option'].lower()}']} ({q['correct_option']})"
                    ctk.CTkLabel(q_frame, text=q_text, wraplength=600, justify="left").pack(anchor="w", padx=10, pady=(5,0))
                    ctk.CTkLabel(q_frame, text=q_ans, font=ctk.CTkFont(weight="bold"), text_color="green").pack(anchor="w", padx=10, pady=(0,5))
            else:
                ctk.CTkLabel(self.existing_questions_frame, text="Error loading questions.").pack(pady=10)
        except Exception as e:
            ctk.CTkLabel(self.existing_questions_frame, text=f"Error connecting to server: {e}").pack(pady=10)

    def save_question(self):
        data = {
            "question_text": self.question_text.get(),
            "option_a": self.option_a.get(),
            "option_b": self.option_b.get(),
            "option_c": self.option_c.get(),
            "option_d": self.option_d.get(),
            "correct_option": self.correct_option.get()
        }
        if not all(data.values()):
            messagebox.showerror("Error", "All fields must be filled out.")
            return
        try:
            quiz_id = self.quiz_info['quiz_id']
            response = requests.post(f"{SERVER_URL}/quizzes/{quiz_id}/questions", json=data, timeout=5)
            if response.status_code == 201:
                self.status_label.configure(text="Question saved successfully!", text_color="green")
                # Clear form
                self.question_text.delete(0, "end"); self.option_a.delete(0, "end"); self.option_b.delete(0, "end"); self.option_c.delete(0, "end"); self.option_d.delete(0, "end")
                # Refresh the list of questions
                self.load_existing_questions()
            else:
                self.status_label.configure(text=f"Error: {response.json().get('message')}", text_color="red")
        except Exception as e:
            messagebox.showerror("Connection Error", f"An error occurred: {e}")

# --- Admin: Create Quiz Window ---
class CreateQuizWindow(ctk.CTkToplevel):
    def __init__(self, user_info):
        super().__init__(); self.user_info = user_info; self.title("Create New Quiz"); self.geometry("400x250"); self.resizable(False, False)
        self.main_frame = ctk.CTkFrame(self); self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        ctk.CTkLabel(self.main_frame, text="Quiz Title:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10)
        self.title_entry = ctk.CTkEntry(self.main_frame, placeholder_text="e.g., History 101"); self.title_entry.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(self.main_frame, text="Time Limit (minutes):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10)
        self.time_limit_entry = ctk.CTkEntry(self.main_frame, placeholder_text="e.g., 15"); self.time_limit_entry.pack(pady=5, padx=10, fill="x")
        self.save_button = ctk.CTkButton(self.main_frame, text="Save Quiz", command=self.save_quiz); self.save_button.pack(pady=20)
    def save_quiz(self):
        title = self.title_entry.get(); time_limit = self.time_limit_entry.get()
        if not title or not time_limit: messagebox.showerror("Error", "Both fields are required."); return
        try:
            payload = { "title": title, "time_limit_minutes": int(time_limit), "creator_id": self.user_info['user_id'] }
            response = requests.post(f"{SERVER_URL}/quizzes", json=payload, timeout=5)
            if response.status_code == 201: messagebox.showinfo("Success", "Quiz created successfully!"); self.destroy()
            else: messagebox.showerror("Error", f"Failed to create quiz: {response.json().get('message')}")
        except ValueError: messagebox.showerror("Error", "Time limit must be a number.")
        except Exception as e: messagebox.showerror("Connection Error", f"An error occurred: {e}")

# --- Admin: Manage Quizzes Window ---
class ManageQuizWindow(ctk.CTkToplevel):
    def __init__(self, user_info):
        super().__init__(); self.user_info = user_info; self.title("Manage Quizzes"); self.geometry("500x400")
        self.label = ctk.CTkLabel(self, text="Select a Quiz to Manage", font=ctk.CTkFont(size=20, weight="bold")); self.label.pack(pady=20)
        self.quiz_list_frame = ctk.CTkScrollableFrame(self); self.quiz_list_frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.load_quizzes()
    def load_quizzes(self):
        try:
            response = requests.get(f"{SERVER_URL}/quizzes", timeout=5)
            if response.status_code == 200:
                quizzes = response.json().get("quizzes", [])
                for quiz in quizzes:
                    q_frame = ctk.CTkFrame(self.quiz_list_frame); q_frame.pack(fill="x", pady=5)
                    ctk.CTkLabel(q_frame, text=quiz['title']).pack(side="left", padx=10)
                    ctk.CTkButton(q_frame, text="Add/View Questions", command=lambda q=quiz: self.open_add_question_window(q)).pack(side="right", padx=10)
            else: ctk.CTkLabel(self.quiz_list_frame, text="Could not load quizzes.").pack()
        except Exception: ctk.CTkLabel(self.quiz_list_frame, text="Error connecting to server.").pack()
    def open_add_question_window(self, quiz_info): add_win = AddQuestionWindow(self.user_info, quiz_info); add_win.grab_set()

# --- Quiz Taking Window ---
class QuizWindow(ctk.CTkToplevel):
    def __init__(self, user_info, quiz_info):
        super().__init__(); self.user_info = user_info; self.quiz_info = quiz_info; self.questions = []; self.current_question_index = 0; self.user_answers = {}; self.time_left = self.quiz_info.get("time_limit_minutes", 10) * 60; self.timer_job = None
        self.title(f"Quiz: {self.quiz_info['title']}"); self.geometry("600x500"); self.resizable(False, False)
        self.timer_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=18, weight="bold")); self.timer_label.pack(pady=10)
        self.question_label = ctk.CTkLabel(self, text="Loading question...", font=ctk.CTkFont(size=18), wraplength=550); self.question_label.pack(pady=10, padx=20)
        self.options_frame = ctk.CTkFrame(self); self.options_frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.selected_option = tk.StringVar(value=None)
        self.radio_a = ctk.CTkRadioButton(self.options_frame, text="A", variable=self.selected_option, value="A")
        self.radio_b = ctk.CTkRadioButton(self.options_frame, text="B", variable=self.selected_option, value="B")
        self.radio_c = ctk.CTkRadioButton(self.options_frame, text="C", variable=self.selected_option, value="C")
        self.radio_d = ctk.CTkRadioButton(self.options_frame, text="D", variable=self.selected_option, value="D")
        self.next_button = ctk.CTkButton(self, text="Next Question", command=self.next_question); self.next_button.pack(pady=20)
        self.protocol("WM_DELETE_WINDOW", self.on_closing); self.load_quiz_questions()
    def update_timer(self):
        minutes, seconds = self.time_left // 60, self.time_left % 60
        self.timer_label.configure(text=f"Time Left: {minutes:02d}:{seconds:02d}")
        if self.time_left > 0: self.time_left -= 1; self.timer_job = self.after(1000, self.update_timer)
        else: messagebox.showinfo("Time's up!", "Quiz will be submitted automatically."); self.submit_quiz(auto_submit=True)
    def load_quiz_questions(self):
        try:
            quiz_id = self.quiz_info['quiz_id']; response = requests.get(f"{SERVER_URL}/quizzes/{quiz_id}", timeout=5)
            if response.status_code == 200:
                self.questions = response.json().get("quiz", {}).get("questions", [])
                if not self.questions: messagebox.showerror("Error", "This quiz has no questions."); self.destroy(); return
                self.display_question(); self.update_timer()
            else: messagebox.showerror("Error", "Could not load quiz questions."); self.destroy()
        except Exception as e: messagebox.showerror("Connection Error", f"An error occurred: {e}"); self.destroy()
    def display_question(self):
        if self.current_question_index < len(self.questions):
            q = self.questions[self.current_question_index]
            self.question_label.configure(text=f"Q{self.current_question_index + 1}: {q['question_text']}")
            self.radio_a.configure(text=f"A) {q['option_a']}"); self.radio_b.configure(text=f"B) {q['option_b']}"); self.radio_c.configure(text=f"C) {q['option_c']}"); self.radio_d.configure(text=f"D) {q['option_d']}")
            self.radio_a.pack(anchor="w", pady=5, padx=20); self.radio_b.pack(anchor="w", pady=5, padx=20); self.radio_c.pack(anchor="w", pady=5, padx=20); self.radio_d.pack(anchor="w", pady=5, padx=20)
            self.selected_option.set(None)
            if self.current_question_index == len(self.questions) - 1: self.next_button.configure(text="Submit Quiz")
    def next_question(self):
        selected = self.selected_option.get()
        if not selected: messagebox.showwarning("No Selection", "Please select an answer."); return
        self.user_answers[self.questions[self.current_question_index]['question_id']] = selected
        self.current_question_index += 1
        if self.current_question_index < len(self.questions): self.display_question()
        else: self.submit_quiz()
    def submit_quiz(self, auto_submit=False):
        if self.timer_job: self.after_cancel(self.timer_job); self.timer_job = None
        if not auto_submit and self.selected_option.get(): self.user_answers[self.questions[self.current_question_index-1]['question_id']] = self.selected_option.get()
        payload = { "user_id": self.user_info['user_id'], "answers": [{"question_id": q_id, "answer": ans} for q_id, ans in self.user_answers.items()] }
        try:
            quiz_id = self.quiz_info['quiz_id']
            response = requests.post(f"{SERVER_URL}/quizzes/{quiz_id}/submit", json=payload, timeout=10)
            if response.status_code == 200: result = response.json(); messagebox.showinfo("Quiz Finished!", f"Score: {result['score']} / {result['total_questions']} ({result['percentage']}%)")
            else: messagebox.showerror("Submission Failed", "Problem submitting your quiz.")
        except Exception as e: messagebox.showerror("Error", f"An error occurred: {e}")
        self.destroy()
    def on_closing(self):
        if self.timer_job: self.after_cancel(self.timer_job)
        self.destroy()

# --- Admin Dashboard Window ---
class AdminDashboard(ctk.CTkToplevel):
    def __init__(self, user_info):
        super().__init__(); self.user_info = user_info; self.title(f"Admin Dashboard - Welcome, {self.user_info.get('username')}"); self.geometry("500x400"); self.resizable(False, False)
        self.label = ctk.CTkLabel(self, text="Admin Controls", font=ctk.CTkFont(size=20, weight="bold")); self.label.pack(pady=20)
        self.create_quiz_button = ctk.CTkButton(self, text="Create New Quiz", command=self.create_quiz_action); self.create_quiz_button.pack(pady=10)
        self.manage_questions_button = ctk.CTkButton(self, text="Manage Quizzes", command=self.manage_quizzes_action); self.manage_questions_button.pack(pady=10)
        self.view_progress_button = ctk.CTkButton(self, text="View Student Progress", command=self.view_progress_action); self.view_progress_button.pack(pady=10)
    def create_quiz_action(self): create_win = CreateQuizWindow(self.user_info); create_win.grab_set()
    def manage_quizzes_action(self): manage_win = ManageQuizWindow(self.user_info); manage_win.grab_set()
    def view_progress_action(self): progress_win = ViewAllResultsWindow(self.user_info); progress_win.grab_set()

# --- Student Dashboard Window ---
class StudentDashboard(ctk.CTkToplevel):
    def __init__(self, user_info):
        super().__init__(); self.user_info = user_info; self.title(f"Student Dashboard - Welcome, {self.user_info.get('username')}"); self.geometry("500x400")
        self.label = ctk.CTkLabel(self, text="Available Quizzes", font=ctk.CTkFont(size=20, weight="bold")); self.label.pack(pady=20)
        self.quiz_list_frame = ctk.CTkScrollableFrame(self); self.quiz_list_frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.view_results_button = ctk.CTkButton(self, text="View My Results", command=self.view_results_action); self.view_results_button.pack(pady=20)
        self.load_quizzes()
    def load_quizzes(self):
        try:
            for widget in self.quiz_list_frame.winfo_children(): widget.destroy()
            response = requests.get(f"{SERVER_URL}/quizzes", timeout=5)
            if response.status_code == 200:
                quizzes = response.json().get("quizzes", [])
                if not quizzes: ctk.CTkLabel(self.quiz_list_frame, text="No quizzes available.").pack(pady=10); return
                for quiz in quizzes:
                    quiz_frame = ctk.CTkFrame(self.quiz_list_frame); quiz_frame.pack(fill="x", pady=5, padx=5)
                    ctk.CTkLabel(quiz_frame, text=f"{quiz['title']} ({quiz['time_limit_minutes']} mins)").pack(side="left", padx=10, pady=5)
                    ctk.CTkButton(quiz_frame, text="Start Quiz", command=lambda q=quiz: self.start_quiz_action(q)).pack(side="right", padx=10, pady=5)
            else: messagebox.showerror("Error", "Failed to load quizzes.")
        except requests.exceptions.ConnectionError: messagebox.showerror("Connection Error", f"Could not connect to {SERVER_URL}.")
        except Exception as e: messagebox.showerror("Error", f"An unexpected error occurred: {e}")
    def start_quiz_action(self, quiz_info): quiz_window = QuizWindow(self.user_info, quiz_info); quiz_window.grab_set()
    def view_results_action(self): results_win = ViewResultsWindow(self.user_info); results_win.grab_set()

# --- Login Window ---
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__(); self.title("Quiz System Login"); self.geometry("350x300"); self.resizable(False, False)
        ctk.set_appearance_mode("System"); ctk.set_default_color_theme("blue")
        self.main_frame = ctk.CTkFrame(self); self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.title_label = ctk.CTkLabel(self.main_frame, text="User Login", font=ctk.CTkFont(size=20, weight="bold")); self.title_label.pack(pady=10)
        self.username_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Username"); self.username_entry.pack(pady=5, padx=10, fill="x")
        self.password_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Password", show="*"); self.password_entry.pack(pady=5, padx=10, fill="x")
        self.button_frame = ctk.CTkFrame(self.main_frame); self.button_frame.pack(pady=15, padx=10)
        self.login_button = ctk.CTkButton(self.button_frame, text="Login", command=self.login_event); self.login_button.pack(side="left", padx=5)
        self.register_button = ctk.CTkButton(self.button_frame, text="Register", command=self.register_window_event, fg_color="gray"); self.register_button.pack(side="left", padx=5)
    def login_event(self):
        username, password = self.username_entry.get(), self.password_entry.get()
        if not username or not password: messagebox.showwarning("Login Failed", "Please enter both username and password."); return
        try:
            payload = {"username": username, "password": password}
            response = requests.post(f"{SERVER_URL}/login", json=payload, timeout=5)
            if response.status_code == 200:
                user_data = response.json().get("user")
                self.destroy()
                if user_data.get('role') == 'Admin': dashboard = AdminDashboard(user_data)
                else: dashboard = StudentDashboard(user_data)
                dashboard.mainloop()
            else: messagebox.showerror("Login Failed", response.json().get("message", "An unknown error occurred."))
        except requests.exceptions.ConnectionError: messagebox.showerror("Connection Error", f"Could not connect to {SERVER_URL}.")
        except Exception as e: messagebox.showerror("Error", f"An unexpected error occurred: {e}")
    def register_window_event(self): reg_win = RegisterWindow(); reg_win.grab_set()

if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()

