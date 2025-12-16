import tkinter as tk
from tkinter import ttk, messagebox


class ShopView(ttk.Frame):
    def __init__(self, parent, controller):
        # main frame for the shop view
        super().__init__(parent, padding=15)
        self.controller = controller  # Reference to the business logic

        # layout configuration
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # create UI sections
        self.create_header_widgets()
        self.create_add_item_widgets()
        self.create_shop_list_widgets()
        self.create_action_widgets()
        
        # initial UI update
        self.refresh_ui()

    def create_header_widgets(self):
        """Creates the shop title and token display."""
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)
        
        ttk.Label(
            header_frame,
            text="Rewards Shop",
            font=("-size 16 -weight bold")
        ).grid(row=0, column=0, sticky="w")

        # displays the user's current token balance
        self.shop_tokens_label = ttk.Label(
            header_frame,
            text="Your Tokens: 0",
            font=("-size 12")
        )
        self.shop_tokens_label.grid(row=1, column=0, sticky="w")

    def create_add_item_widgets(self):
        """Creates inputs for adding a new reward to the shop."""
        add_item_frame = ttk.LabelFrame(self, text="Add New Reward", padding=10)
        add_item_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        add_item_frame.columnconfigure(1, weight=1)

        ttk.Label(add_item_frame, text="Reward:").grid(row=0, column=0, padx=(0, 5))
        self.reward_entry = ttk.Entry(add_item_frame)
        self.reward_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        ttk.Label(add_item_frame, text="Price:").grid(row=0, column=2, padx=(0, 5))
        self.price_entry = ttk.Entry(add_item_frame, width=10)
        self.price_entry.grid(row=0, column=3, padx=(0, 10))
        
        add_btn = ttk.Button(
            add_item_frame,
            text="Add",
            command=self.add_shop_item,
            style="success.TButton"
        )
        add_btn.grid(row=0, column=4)

    def create_shop_list_widgets(self):
        """Creates the list of available rewards."""
        shop_list_frame = ttk.LabelFrame(self, text="Available Rewards", padding=10)
        shop_list_frame.grid(row=2, column=0, sticky="nsew")
        shop_list_frame.rowconfigure(0, weight=1)
        shop_list_frame.columnconfigure(0, weight=1)
        
        self.shop_listbox = tk.Listbox(shop_list_frame, height=15)
        self.shop_listbox.grid(row=0, column=0, sticky="nsew")

        shop_scrollbar = ttk.Scrollbar(
            shop_list_frame,
            orient="vertical",
            command=self.shop_listbox.yview
        )
        shop_scrollbar.grid(row=0, column=1, sticky="ns")
        self.shop_listbox.config(yscrollcommand=shop_scrollbar.set)

    def create_action_widgets(self):
        """Creates action buttons (buy reward)."""
        shop_action_frame = ttk.Frame(self, padding=(0, 10, 0, 0))
        shop_action_frame.grid(row=3, column=0, sticky="ew")
        
        buy_btn = ttk.Button(
            shop_action_frame,
            text="Buy Reward",
            command=self.buy_item,
            style="primary.TButton"
        )
        buy_btn.pack(side="left")

    def add_shop_item(self):
        """Attempts to add a new reward using the controller."""
        success, message = self.controller.add_shop_item(
            self.reward_entry.get(),
            self.price_entry.get()
        )

        if success:
            # clear inputs and refresh UI on success
            self.reward_entry.delete(0, tk.END)
            self.price_entry.delete(0, tk.END)
            self.refresh_ui()
        else:
            messagebox.showwarning("Invalid Input", message)
            
    def buy_item(self):
        """Attempts to purchase the selected reward."""
        try:
            selected_index = self.shop_listbox.curselection()[0]
            success, message = self.controller.buy_item(selected_index)

            if success:
                messagebox.showinfo("Purchase Successful", message)
                self.refresh_ui()
            else:
                messagebox.showerror("Purchase Failed", message)

        except IndexError:
            # no item selected in the list
            messagebox.showwarning(
                "No Selection",
                "Please select a reward to purchase."
            )

    def refresh_ui(self):
        """Updates token display and reward list."""
        self.shop_tokens_label.config(
            text=f"Your Tokens: {self.controller.tokens}"
        )

        self.shop_listbox.delete(0, tk.END)
        for item in self.controller.shop_items:
            self.shop_listbox.insert(
                tk.END,
                f"{item['name']} - Price: {item['price']} Tokens"
            )