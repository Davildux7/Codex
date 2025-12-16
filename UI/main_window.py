import ttkbootstrap as ttk
from tkinter import messagebox
from logic import ToDoLogic
from UI.task_view import TaskView
from UI.shop_view import ShopView


class MainWindow(ttk.Window):
    def __init__(self):
        # initialize the main window with a predefined theme
        super().__init__(themename="superhero")
        
        # window title and size
        self.title("Codex")
        self.geometry("800x600")

        # main application controller (handles all business stuff)
        self.controller = ToDoLogic()

        # notebook (tab container)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # application views
        self.task_view = TaskView(self.notebook, self.controller)
        self.shop_view = ShopView(self.notebook, self.controller)

        # add tabs to the notebook
        self.notebook.add(self.task_view, text="Tasks")
        self.notebook.add(self.shop_view, text="Shop")
        
        # refresh UI whenever the user changes tabs
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # initialization logic
        self.check_status_on_startup()

        # ensure data is saved when the window is closed
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def check_status_on_startup(self):
        """
        Runs all startup checks in the correct order:
        - Weekly updates (penalties, promotions, reports)
        - Daily status checks
        - UI refresh
        """

        # 1. run weekly logic FIRST to apply penalties and promotions
        self.controller.check_weekly_updates()
        
        # 2. retrieve and display the weekly report message, if any
        weekly_message = self.controller.get_and_clear_pending_message()
        if weekly_message:
            messagebox.showwarning("Weekly Report", weekly_message)

        # 3. run daily logic and display returned messages
        daily_messages = self.controller.check_daily_status()
        for msg_type, title, message in daily_messages:
            if msg_type == "info":
                messagebox.showinfo(title, message)
            elif msg_type == "warning":
                messagebox.showwarning(title, message)

        # 4. update all UI views with the latest data
        self.refresh_all_views()

    def on_tab_changed(self, event):
        """Called whenever the user switches tabs."""
        self.refresh_all_views()

    def refresh_all_views(self):
        """Refreshes all views to keep the UI in sync with the data."""
        self.task_view.refresh_ui()
        self.shop_view.refresh_ui()

    def on_closing(self):
        """Save data and close the application safely."""
        self.controller.save_data()
        self.destroy()
