import json
from datetime import datetime, date, timedelta

# did you know that you can make constants in python by declaring them in all caps?
# i took 2 years programming to realize that lol
XP_LOSS_PER_DAY = 20
PAUSE_COST = 75
TASKS_FOR_STREAK = 3
STREAK_MULTIPLIER_INCREASE = 0.2
XP_PENALTY_PER_URGENT_TASK = 30
MANDATORY_TASKS_TO_SKIP_DAY = 2


class ToDoLogic:
    """Main application logic: tasks, rewards, streaks, and persistence."""

    def __init__(self):
        self.load_data()

    # sorting logic
    def _sort_tasks(self):
        """Sorts regular tasks by priority (highest first)."""
        priority_map = {
            "Urgent": 4,
            "High": 3,
            "Medium": 2,
            "Low": 1,
            "Irrelevant": 0
        }
        self.tasks.sort(
            key=lambda task: priority_map.get(task.get('priority'), 0),
            reverse=True
        )

    def _sort_shop_items(self):
        """Sorts shop items by ascending price."""
        self.shop_items.sort(key=lambda item: item.get('price', 0))

    def _sort_mandatory_tasks(self):
        """Sorts mandatory tasks by activation weekday."""
        self.mandatory_tasks.sort(key=lambda task: task.get('activation_day', 0))

    # task logic
    def add_task(self, name, difficulty, priority):
        """Adds a new regular task."""
        if not name:
            return False, "Task name cannot be empty."

        task = {
            "name": name,
            "difficulty": difficulty,
            "priority": priority
        }
        self.tasks.append(task)
        self._sort_tasks()
        return True, "Task added successfully."

    def add_mandatory_task(self, name, activation_day):
        """Adds a new mandatory (recurring) task."""
        if not name:
            return False, "Task name cannot be empty."

        task = {
            "name": name,
            "activation_day": activation_day,
            "completed_today": False  # tracks daily completion
        }
        self.mandatory_tasks.append(task)
        self._sort_mandatory_tasks()
        return True, "Mandatory task added successfully."

    def delete_task(self, selected_index):
        """Deletes a regular task by index."""
        if 0 <= selected_index < len(self.tasks):
            del self.tasks[selected_index]
            return True, "Task deleted."
        return False, "Invalid index."

    def delete_mandatory_task(self, selected_index):
        """Deletes a mandatory task by index."""
        if 0 <= selected_index < len(self.mandatory_tasks):
            del self.mandatory_tasks[selected_index]
            return True, "Mandatory task deleted."
        return False, "Invalid index."

    def complete_task(self, selected_index):
        """Completes a regular task and grants rewards."""
        if not (0 <= selected_index < len(self.tasks)):
            return None, "Invalid index."

        task = self.tasks.pop(selected_index)

        difficulty_map = {
            "Very Easy": 1,
            "Easy": 2,
            "Medium": 3,
            "Hard": 5,
            "Very Hard": 7
        }
        priority_map = {
            "Irrelevant": 1,
            "Low": 1,
            "Medium": 1.25,
            "High": 1.5,
            "Urgent": 2
        }

        base_tokens = 10 * difficulty_map[task['difficulty']]
        base_xp = 15 * difficulty_map[task['difficulty']]

        tokens_earned = int(base_tokens * priority_map[task['priority']] * self.streak_multiplier)
        xp_earned = int(base_xp * priority_map[task['priority']] * self.streak_multiplier)

        self.tokens += tokens_earned
        self.xp += xp_earned

        self.update_streak()
        level_up_info = self.check_level_up()

        message = f"You earned {tokens_earned} Tokens and {xp_earned} XP!"
        if level_up_info:
            message += "\n" + level_up_info

        return message

    def complete_mandatory_task(self, selected_index):
        """Completes a mandatory task if it is active today."""
        if not (0 <= selected_index < len(self.mandatory_tasks)):
            return None, "Invalid index."

        task = self.mandatory_tasks[selected_index]
        today = date.today()

        if today.weekday() != task['activation_day']:
            return "This task is not active today."

        if task.get('completed_today', False):
            return "This task has already been completed today."

        task['completed_today'] = True
        self.mandatory_tasks_completed_today += 1

        message = "Mandatory task completed!"

        if self.mandatory_tasks_completed_today >= MANDATORY_TASKS_TO_SKIP_DAY:
            self.last_login_date = today + timedelta(days=1)
            self.mandatory_tasks_completed_today = 0
            message += (
                f"\n\nCongratulations! You completed {MANDATORY_TASKS_TO_SKIP_DAY} "
                "mandatory tasks and skipped the day!"
            )

        return message

    # shop logic
    def add_shop_item(self, name, price_str):
        if not name or not price_str:
            return False, "Please fill in both reward name and price."
        try:
            price = int(price_str)
            if price <= 0:
                raise ValueError
            self.shop_items.append({"name": name, "price": price})
            self._sort_shop_items()
            return True, "Reward added successfully."
        except ValueError:
            return False, "Price must be a positive number."

    def buy_item(self, selected_index):
        if not (0 <= selected_index < len(self.shop_items)):
            return False, "Select a reward to purchase."

        item = self.shop_items[selected_index]
        if self.tokens >= item['price']:
            self.tokens -= item['price']
            del self.shop_items[selected_index]
            return True, f"You purchased '{item['name']}'!"
        return False, "You do not have enough Tokens."

    # gamification wow so cool
    def check_level_up(self):
        """Handles level-ups based on XP."""
        messages = []
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1
            self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
            messages.append(f"Congratulations! You reached Level {self.level}!")
        return "\n".join(messages)

    def update_streak(self):
        """Updates the streak multiplier based on daily task completion."""
        today = date.today()
        self.tasks_completed_today += 1

        if self.tasks_completed_today >= TASKS_FOR_STREAK:
            if self.last_streak_date == today - timedelta(days=1):
                self.streak_days += 1
            elif self.last_streak_date != today:
                self.streak_days = 1

            self.streak_multiplier = 1.0 + (self.streak_days * STREAK_MULTIPLIER_INCREASE)
            self.last_streak_date = today

    # daily and weekly status logic
    def check_daily_status(self):
        """Applies daily penalties, resets, and mandatory task states."""
        today = date.today()
        messages = []

        if today > self.last_login_date:
            days_since_last_login = (today - self.last_login_date).days

            yesterday = today - timedelta(days=1)
            yesterday_was_paused = self.paused_until and self.paused_until == yesterday

            if not yesterday_was_paused and self.last_streak_date < yesterday:
                if self.streak_days > 0:
                    messages.append(("info", "Streak Broken", "Your streak has been reset."))
                self.streak_days = 0
                self.streak_multiplier = 1.0

            for i in range(days_since_last_login):
                check_date = self.last_login_date + timedelta(days=i + 1)

                if self.paused_until and check_date == self.paused_until:
                    messages.append(("info", "Day Paused", f"The day {check_date:%d/%m} was paused."))
                    continue

                if check_date.weekday() < 6:
                    self.xp = max(0, self.xp - XP_LOSS_PER_DAY)
                    messages.append(("warning", "Penalty", f"You lost {XP_LOSS_PER_DAY} XP due to inactivity."))

            self.tasks_completed_today = 0
            self.mandatory_tasks_completed_today = 0

            for task in self.mandatory_tasks:
                task['completed_today'] = False

        self.last_login_date = today
        return messages

    def _increase_task_priorities(self):
        """Escalates task priorities weekly."""
        priority_map = {
            "Low": "Medium",
            "Medium": "High",
            "High": "Urgent"
        }
        for task in self.tasks:
            if task['priority'] in priority_map:
                task['priority'] = priority_map[task['priority']]
        self._sort_tasks()

    def _apply_urgent_task_penalty(self):
        urgent_count = sum(1 for task in self.tasks if task['priority'] == 'Urgent')
        if urgent_count > 0:
            total_loss = urgent_count * XP_PENALTY_PER_URGENT_TASK
            self.xp = max(0, self.xp - total_loss)
            self.pending_weekly_message = (
                f"Weekly Report:\n\nYou lost {total_loss} XP for not completing "
                f"{urgent_count} urgent task(s)."
            )

    def check_weekly_updates(self):
        """Runs weekly maintenance tasks."""
        today = date.today()

        if self.last_weekly_check_date is None:
            self.last_weekly_check_date = today
            return

        last_offset = (self.last_weekly_check_date.weekday() + 1) % 7
        last_sunday = self.last_weekly_check_date - timedelta(days=last_offset)

        today_offset = (today.weekday() + 1) % 7
        current_sunday = today - timedelta(days=today_offset)

        if current_sunday > last_sunday:
            self._apply_urgent_task_penalty()
            self._increase_task_priorities()
            self.last_weekly_check_date = today

    def get_and_clear_pending_message(self):
        message = self.pending_weekly_message
        self.pending_weekly_message = None
        return message

    def pause_day(self):
        """Pauses the current day by spending tokens."""
        if self.tokens >= PAUSE_COST:
            self.tokens -= PAUSE_COST
            self.paused_until = date.today()
            return True, "You successfully paused today."
        return False, f"You need {PAUSE_COST} Tokens to pause the day."

    def reset_progress(self, confirm=False):
        """Fully resets all progress."""
        if not confirm:
            return False, "Confirmation required to reset."

        self.tokens, self.xp, self.level = 0, 0, 1
        self.xp_to_next_level = 100
        self.streak_multiplier = 1.0
        self.streak_days = 0
        self.tasks_completed_today = 0
        self.last_login_date = date.today()
        self.last_streak_date = date.today() - timedelta(days=1)
        self.paused_until = None
        self.tasks = []
        self.shop_items = []
        self.last_weekly_check_date = date.today()
        self.pending_weekly_message = None
        self.mandatory_tasks = []
        self.mandatory_tasks_completed_today = 0

        self.save_data()
        return True, "Progress reset successfully!"

    # --- Data Persistence ---
    def save_data(self):
        """Saves all data to disk."""
        data = {
            "tokens": self.tokens,
            "xp": self.xp,
            "level": self.level,
            "xp_to_next_level": self.xp_to_next_level,
            "streak_multiplier": self.streak_multiplier,
            "streak_days": self.streak_days,
            "tasks_completed_today": self.tasks_completed_today,
            "last_login_date": self.last_login_date.isoformat(),
            "last_streak_date": self.last_streak_date.isoformat(),
            "paused_until": self.paused_until.isoformat() if self.paused_until else None,
            "tasks": self.tasks,
            "shop_items": self.shop_items,
            "last_weekly_check_date": self.last_weekly_check_date.isoformat() if self.last_weekly_check_date else None,
            "pending_weekly_message": self.pending_weekly_message,
            "mandatory_tasks": self.mandatory_tasks,
            "mandatory_tasks_completed_today": self.mandatory_tasks_completed_today
        }

        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        """Loads data from disk or initializes defaults."""
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            self.tokens = data.get("tokens", 0)
            self.xp = data.get("xp", 0)
            self.level = data.get("level", 1)
            self.xp_to_next_level = data.get("xp_to_next_level", 100)
            self.streak_multiplier = data.get("streak_multiplier", 1.0)
            self.streak_days = data.get("streak_days", 0)
            self.tasks_completed_today = data.get("tasks_completed_today", 0)
            self.last_login_date = date.fromisoformat(data.get("last_login_date", date.today().isoformat()))
            self.last_streak_date = date.fromisoformat(
                data.get("last_streak_date", (date.today() - timedelta(days=1)).isoformat())
            )
            self.paused_until = (
                date.fromisoformat(data.get("paused_until"))
                if data.get("paused_until") else None
            )
            self.tasks = data.get("tasks", [])
            self.shop_items = data.get("shop_items", [])
            self.last_weekly_check_date = (
                date.fromisoformat(data.get("last_weekly_check_date"))
                if data.get("last_weekly_check_date") else None
            )
            self.pending_weekly_message = data.get("pending_weekly_message", None)
            self.mandatory_tasks = data.get("mandatory_tasks", [])
            self.mandatory_tasks_completed_today = data.get("mandatory_tasks_completed_today", 0)

        except (FileNotFoundError, json.JSONDecodeError):
            self.tokens, self.xp, self.level = 0, 0, 1
            self.xp_to_next_level = 100
            self.streak_multiplier = 1.0
            self.streak_days = 0
            self.tasks_completed_today = 0
            self.last_login_date = date.today()
            self.last_streak_date = date.today() - timedelta(days=1)
            self.paused_until = None
            self.tasks = []
            self.shop_items = []
            self.last_weekly_check_date = date.today()
            self.pending_weekly_message = None
            self.mandatory_tasks = []
            self.mandatory_tasks_completed_today = 0

        self._sort_tasks()
        self._sort_shop_items()
        self._sort_mandatory_tasks()