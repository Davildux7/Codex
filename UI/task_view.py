import tkinter as tk
from tkinter import ttk, messagebox
from logic import PAUSE_COST
from datetime import date


class AddMandatoryTaskDialog(tk.Toplevel):
    """Modal dialog for creating a new mandatory (recurring) task."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.transient(parent)
        self.title("New Mandatory Task")
        self.controller = controller
        self.parent = parent
        self.result = None

        # maps weekday names to Python's weekday integers
        self.days_map = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 5,
            "Sunday": 6
        }

        frame = ttk.Frame(self, padding="10")
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="Task Name:").grid(row=0, column=0, sticky="w", pady=2)
        self.name_entry = ttk.Entry(frame, width=40)
        self.name_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=2)

        ttk.Label(frame, text="Activation Day:").grid(row=2, column=0, sticky="w", pady=2)
        self.day_var = tk.StringVar(value="Monday")
        self.day_menu = ttk.Combobox(
            frame,
            textvariable=self.day_var,
            values=list(self.days_map.keys()),
            state="readonly"
        )
        self.day_menu.grid(row=3, column=0, columnspan=2, sticky="ew", pady=2)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Add",
            command=self.add,
            style="success.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.destroy
        ).pack(side="left", padx=5)

        # make the dialog modal
        self.grab_set()
        self.name_entry.focus_set()
        self.wait_window(self)

    def add(self):
        """Validates input and sends the new mandatory task to the controller."""
        name = self.name_entry.get()
        day_str = self.day_var.get()
        day_int = self.days_map[day_str]

        success, message = self.controller.add_mandatory_task(name, day_int)
        if success:
            self.destroy()
        else:
            messagebox.showerror("Error", message, parent=self)


class TaskView(ttk.Frame):
    """Main task management view."""

    def __init__(self, parent, controller):
        super().__init__(parent, padding=15)
        self.controller = controller

        # unified list maps visible items to their real indices
        self.unified_task_list = []

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.create_status_widgets()
        self.create_input_widgets()
        self.create_list_widgets()
        self.create_action_widgets()
        self.refresh_ui()

    def create_status_widgets(self):
        """Creates the status bar (tokens, level, XP, streak)."""
        stats_frame = ttk.LabelFrame(self, text="Status", padding=10)
        stats_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        stats_frame.columnconfigure(2, weight=1)

        self.tokens_label = ttk.Label(stats_frame, text="Tokens: 0", font=("-weight bold"))
        self.tokens_label.grid(row=0, column=0, padx=(0, 15))

        self.level_label = ttk.Label(stats_frame, text="Level: 1")
        self.level_label.grid(row=0, column=1)

        self.xp_bar = ttk.Progressbar(stats_frame, orient="horizontal", mode="determinate")
        self.xp_bar.grid(row=0, column=2, sticky="ew", padx=10)

        self.xp_label = ttk.Label(stats_frame, text="XP: 0/100")
        self.xp_label.grid(row=0, column=3, padx=(0, 15))

        self.streak_label = ttk.Label(stats_frame, text="Multiplier: x1.0 (0 days)")
        self.streak_label.grid(row=0, column=4)

    def create_input_widgets(self):
        """Creates inputs for adding a regular task."""
        input_frame = ttk.LabelFrame(self, text="New Regular Task", padding=10)
        input_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Task:").grid(row=0, column=0, padx=(0, 5))
        self.task_entry = ttk.Entry(input_frame)
        self.task_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        ttk.Label(input_frame, text="Difficulty:").grid(row=0, column=2, padx=(0, 5))
        self.difficulty_var = tk.StringVar(value="Easy")
        self.difficulty_menu = ttk.Combobox(
            input_frame,
            textvariable=self.difficulty_var,
            values=["Very Easy", "Easy", "Medium", "Hard", "Very Hard"],
            state="readonly",
            width=12
        )
        self.difficulty_menu.grid(row=0, column=3, padx=(0, 10))

        ttk.Label(input_frame, text="Priority:").grid(row=0, column=4, padx=(0, 5))
        self.priority_var = tk.StringVar(value="Low")
        self.priority_menu = ttk.Combobox(
            input_frame,
            textvariable=self.priority_var,
            values=["Irrelevant", "Low", "Medium", "High", "Urgent"],
            state="readonly",
            width=10
        )
        self.priority_menu.grid(row=0, column=5, padx=(0, 10))

        ttk.Button(
            input_frame,
            text="Add",
            command=self.add_task,
            style="success.TButton"
        ).grid(row=0, column=6)

    def create_list_widgets(self):
        """Creates the task listbox."""
        list_frame = ttk.LabelFrame(self, text="Pending Tasks", padding=10)
        list_frame.grid(row=2, column=0, sticky="nsew")
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        self.task_listbox = tk.Listbox(
            list_frame,
            height=15,
            selectbackground="#007bff",
            selectforeground="white"
        )
        self.task_listbox.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.task_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.task_listbox.config(yscrollcommand=scrollbar.set)

    def create_action_widgets(self):
        """Creates action buttons for tasks."""
        action_frame = ttk.Frame(self, padding=(0, 10, 0, 0))
        action_frame.grid(row=3, column=0, sticky="ew")

        ttk.Button(
            action_frame,
            text="Complete Task",
            command=self.complete_task,
            style="primary.TButton"
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            action_frame,
            text="Delete Task",
            command=self.delete_task,
            style="danger.TButton"
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            action_frame,
            text="New Mandatory",
            command=self.add_mandatory_task,
            style="info.TButton"
        ).pack(side="left")

        self.pause_btn = ttk.Button(
            action_frame,
            text=f"Pause Day ({PAUSE_COST} Tokens)",
            command=self.pause_day,
            style="warning.TButton"
        )
        self.pause_btn.pack(side="right")

    def add_task(self):
        """Adds a regular task through the controller."""
        success, message = self.controller.add_task(
            self.task_entry.get(),
            self.difficulty_var.get(),
            self.priority_var.get()
        )

        if success:
            self.task_entry.delete(0, tk.END)
            self.refresh_ui()
        else:
            messagebox.showwarning("Invalid Input", message)

    def add_mandatory_task(self):
        """Opens the mandatory task dialog."""
        AddMandatoryTaskDialog(self, self.controller)
        self.refresh_ui()

    def delete_task(self):
        """Deletes the selected task (regular or mandatory)."""
        try:
            selected_index = self.task_listbox.curselection()[0]
            task_info = self.unified_task_list[selected_index]

            if task_info['type'] == 'regular':
                self.controller.delete_task(task_info['original_index'])
            else:
                self.controller.delete_mandatory_task(task_info['original_index'])

            self.refresh_ui()

        except IndexError:
            messagebox.showwarning("No Selection", "Please select a task to delete.")

    def complete_task(self):
        """Completes the selected task."""
        try:
            selected_index = self.task_listbox.curselection()[0]
            task_info = self.unified_task_list[selected_index]

            if task_info['type'] == 'regular':
                result_message = self.controller.complete_task(task_info['original_index'])
                title = "Task Completed!"
            else:
                result_message = self.controller.complete_mandatory_task(task_info['original_index'])
                title = "Mandatory Task"

            if result_message:
                messagebox.showinfo(title, result_message)
                self.refresh_ui()

        except IndexError:
            messagebox.showwarning("No Selection", "Please select a task to complete.")

    def pause_day(self):
        """Pauses the current day by spending tokens."""
        if messagebox.askyesno(
            "Confirm Pause",
            f"Are you sure you want to spend {PAUSE_COST} Tokens to pause today?"
        ):
            success, message = self.controller.pause_day()

            if success:
                messagebox.showinfo("Day Paused", message)
                self.refresh_ui()
            else:
                messagebox.showerror("Insufficient Tokens", message)

    def refresh_ui(self):
        """Refreshes the task list and all status indicators."""
        self.task_listbox.delete(0, tk.END)
        self.unified_task_list = []

        today_weekday = date.today().weekday()
        days_list = [
            "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday"
        ]

        # 1. mandatory tasks (with color-coded states wow so fancy)
        for i, task in enumerate(self.controller.mandatory_tasks):
            self.unified_task_list.append({"type": "mandatory", "original_index": i})

            day_name = days_list[task['activation_day']]
            display_text = f"◆ {task['name']} (Mandatory - {day_name})"
            self.task_listbox.insert(tk.END, display_text)

            is_active_today = today_weekday == task['activation_day']
            is_completed_today = task.get('completed_today', False)

            if is_completed_today:
                color = "#242446"   # dark blue: completed
            elif is_active_today:
                color = "#DAA520"   # gold: active today
            else:
                color = "grey"      # inactive

            self.task_listbox.itemconfig(tk.END, {'fg': color})

        # 2. regular tasks
        for i, task in enumerate(self.controller.tasks):
            self.unified_task_list.append({"type": "regular", "original_index": i})
            display_text = (
                f"| {task['name']} | Difficulty: {task['difficulty']} "
                f"| Priority: {task['priority']} |"
            )
            self.task_listbox.insert(tk.END, display_text)

        # 3. status updates
        self.tokens_label.config(text=f"Tokens: {self.controller.tokens}")
        self.level_label.config(text=f"Level: {self.controller.level}")
        self.xp_label.config(
            text=f"XP: {self.controller.xp}/{self.controller.xp_to_next_level}"
        )

        self.xp_bar['value'] = (
            (self.controller.xp / self.controller.xp_to_next_level) * 100
            if self.controller.xp_to_next_level > 0 else 0
        )

        self.streak_label.config(
            text=f"Multiplier: x{self.controller.streak_multiplier:.1f} "
                 f"({self.controller.streak_days} days)"
        )

        self.pause_btn.config(text=f"Pause Day ({PAUSE_COST} Tokens)")

# this code fucking sucks
