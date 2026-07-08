"""
Terminal To-Do App v3
------------------------------------------------------------------
New in v3:
  - Deadline notifications on startup
  - Calendar view
  - Categories (Study / Work / Personal)
  - ASCII pie chart (completed vs pending) - no external libraries
  - Password protection (local only - sha256, no salt, good enough
    for a personal terminal app, not for anything sensitive)
  - Dark / light theme toggle (ANSI colors)

Data files (created automatically in the same folder):
  tasks.json    -> your tasks
  config.json   -> password hash + theme preference
  report.txt    -> written when you export
------------------------------------------------------------------
"""

import json
import os
import math
import hashlib
import calendar as cal_module
from datetime import datetime

try:
    import getpass
    HAS_GETPASS = True
except ImportError:
    HAS_GETPASS = False

DATA_FILE = "tasks.json"
CONFIG_FILE = "config.json"
REPORT_FILE = "report.txt"

PRIORITIES = {"1": "High", "2": "Medium", "3": "Low"}
PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}
CATEGORIES = {"1": "Study", "2": "Work", "3": "Personal"}
DATE_FORMAT = "%Y-%m-%d %H:%M"

# ---------------- ANSI colors ----------------

RESET = "\033[0m"
BOLD = "\033[1m"

THEMES = {
    "dark": {
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "cyan": "\033[96m",
        "gray": "\033[90m",
    },
    "light": {
        "green": "\033[32m",
        "yellow": "\033[33m",
        "red": "\033[31m",
        "cyan": "\033[36m",
        "gray": "\033[37m",
    },
}


def colorize(text, color_key, theme):
    code = THEMES.get(theme, THEMES["dark"]).get(color_key, "")
    return f"{code}{text}{RESET}" if code else text


# ---------------- config (password + theme) ----------------

def load_config():
    default = {"password_hash": None, "password_salt": None, "theme": "dark"}
    if not os.path.exists(CONFIG_FILE):
        return default
    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
        default.update(data)
        return default
    except (json.JSONDecodeError, KeyError):
        return default


def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except IOError as e:
        print(f"Error saving config: {e}")


def hash_password(password, salt=None):
    """PBKDF2-HMAC-SHA256 with a random salt. Good enough for a local
    personal app - for anything real-world (web app, shared service),
    use a dedicated library like bcrypt or argon2 instead."""
    if salt is None:
        salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return salt.hex(), digest.hex()


def read_secret(prompt):
    """Hides input where possible, falls back to plain input if the
    terminal doesn't support it (e.g. some IDE consoles)."""
    if HAS_GETPASS:
        try:
            return getpass.getpass(prompt)
        except Exception:
            pass
    return input(prompt)


def authenticate(config):
    if not config.get("password_hash"):
        print("No password set yet - let's create one for this to-do list.")
        while True:
            pw1 = read_secret("New password: ")
            pw2 = read_secret("Confirm password: ")
            if not pw1:
                print("Password cannot be empty.")
                continue
            if pw1 != pw2:
                print("Passwords didn't match, try again.")
                continue
            salt_hex, hash_hex = hash_password(pw1)
            config["password_salt"] = salt_hex
            config["password_hash"] = hash_hex
            save_config(config)
            print("Password set.\n")
            return True

    attempts = 3
    salt = bytes.fromhex(config["password_salt"])
    while attempts > 0:
        pw = read_secret("Enter password: ")
        _, hash_hex = hash_password(pw, salt=salt)
        if hash_hex == config["password_hash"]:
            return True
        attempts -= 1
        print(f"Incorrect password. {attempts} attempt(s) left.")
    print("Too many failed attempts. Exiting.")
    return False


# ---------------- Task ----------------

class Task:
    def __init__(self, title, deadline, priority, category="Personal",
                 done=False, task_id=None):
        self.id = task_id
        self.title = title
        self.deadline = deadline
        self.priority = priority
        self.category = category
        self.done = done

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "deadline": self.deadline,
            "priority": self.priority,
            "category": self.category,
            "done": self.done,
        }

    @staticmethod
    def from_dict(data):
        return Task(
            title=data["title"],
            deadline=data["deadline"],
            priority=data["priority"],
            category=data.get("category", "Personal"),
            done=data["done"],
            task_id=data.get("id"),
        )

    def deadline_dt(self):
        try:
            return datetime.strptime(self.deadline, DATE_FORMAT)
        except ValueError:
            return datetime.max

    def is_overdue(self):
        return (not self.done) and self.deadline_dt() < datetime.now()

    def hours_left(self):
        return max(0, (self.deadline_dt() - datetime.now()).total_seconds() / 3600)

    def status_icon(self, theme="dark"):
        if self.done:
            return colorize("\u2705 Completed", "gray", theme)

        seconds = (self.deadline_dt() - datetime.now()).total_seconds()
        if seconds < 0:
            return colorize("\U0001F534 OVERDUE", "red", theme)
        if seconds < 86400:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return colorize(f"\U0001F7E1 {hours}h {minutes}m left", "yellow", theme)
        days = (self.deadline_dt() - datetime.now()).days
        return colorize(f"\U0001F7E2 {days}d left", "green", theme)


# ---------------- TaskManager ----------------

class TaskManager:
    def __init__(self, filepath=DATA_FILE):
        self.filepath = filepath
        self.tasks = []
        self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            self.tasks = []
            return
        try:
            with open(self.filepath, "r") as f:
                raw = json.load(f)
        except (json.JSONDecodeError, KeyError):
            print("Warning: tasks.json was unreadable, starting fresh.")
            self.tasks = []
            return
        self.tasks = [Task.from_dict(t) for t in raw]
        self._migrate_ids()

    def save(self):
        try:
            with open(self.filepath, "w") as f:
                json.dump([t.to_dict() for t in self.tasks], f, indent=2)
        except IOError as e:
            print(f"Error saving tasks: {e}")

    def _migrate_ids(self):
        needs_save = False
        for i, t in enumerate(self.tasks, start=1):
            if not (isinstance(t.id, str) and t.id.startswith("TASK-")):
                t.id = f"TASK-{i:03d}"
                needs_save = True
        if needs_save:
            self.save()

    def next_id(self):
        max_num = 0
        for t in self.tasks:
            if isinstance(t.id, str) and t.id.startswith("TASK-"):
                try:
                    max_num = max(max_num, int(t.id.split("-")[1]))
                except ValueError:
                    pass
        return f"TASK-{max_num + 1:03d}"

    def add_task(self, title, deadline, priority, category):
        task = Task(title, deadline, priority, category, task_id=self.next_id())
        self.tasks.append(task)
        self.save()
        return task

    def delete_task(self, task_id):
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self.save()
        return len(self.tasks) < before

    def toggle_done(self, task_id):
        for t in self.tasks:
            if t.id == task_id:
                t.done = not t.done
                self.save()
                return t
        return None

    def edit_task(self, task_id, title=None, deadline=None, priority=None, category=None):
        for t in self.tasks:
            if t.id == task_id:
                if title:
                    t.title = title
                if deadline:
                    t.deadline = deadline
                if priority:
                    t.priority = priority
                if category:
                    t.category = category
                self.save()
                return t
        return None

    def sorted_tasks(self, tasks=None):
        pool = self.tasks if tasks is None else tasks
        pending = [t for t in pool if not t.done]
        done = [t for t in pool if t.done]
        pending.sort(key=lambda t: (PRIORITY_ORDER.get(t.priority, 3), t.deadline_dt()))
        done.sort(key=lambda t: t.deadline_dt())
        return pending + done

    def search(self, keyword):
        keyword = keyword.lower()
        matches = [
            t for t in self.tasks
            if keyword in t.title.lower()
            or keyword in t.category.lower()
            or keyword in t.priority.lower()
        ]
        return self.sorted_tasks(matches)

    def filter_tasks(self, mode, category=None):
        if mode == "pending":
            pool = [t for t in self.tasks if not t.done]
        elif mode == "completed":
            pool = [t for t in self.tasks if t.done]
        elif mode == "high":
            pool = [t for t in self.tasks if t.priority == "High"]
        elif mode == "overdue":
            pool = [t for t in self.tasks if t.is_overdue()]
        elif mode == "category":
            pool = [t for t in self.tasks if t.category == category]
        else:
            pool = self.tasks
        return self.sorted_tasks(pool)

    def stats(self):
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.done)
        pending = total - completed
        overdue = sum(1 for t in self.tasks if t.is_overdue())
        high = sum(1 for t in self.tasks if t.priority == "High")
        medium = sum(1 for t in self.tasks if t.priority == "Medium")
        low = sum(1 for t in self.tasks if t.priority == "Low")
        completion_rate = round((completed / total) * 100) if total else 0
        return {
            "total": total, "completed": completed, "pending": pending,
            "overdue": overdue, "high": high, "medium": medium, "low": low,
            "completion_rate": completion_rate,
        }

    def upcoming_and_overdue(self, hours=24):
        upcoming, overdue = [], []
        for t in self.tasks:
            if t.done:
                continue
            if t.is_overdue():
                overdue.append(t)
            elif t.hours_left() <= hours:
                upcoming.append(t)
        # nearest deadline first within each group
        overdue.sort(key=lambda t: t.deadline_dt())
        upcoming.sort(key=lambda t: t.deadline_dt())
        return upcoming, overdue

    def tasks_by_day(self, year, month):
        """Returns {day_number: [tasks]} for the given month."""
        by_day = {}
        for t in self.tasks:
            dt = t.deadline_dt()
            if dt.year == year and dt.month == month:
                by_day.setdefault(dt.day, []).append(t)
        return by_day


# ---------------- display helpers ----------------

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_header(title="TO-DO LIST - DEADLINES & PRIORITIES", theme="dark"):
    line = "=" * 60
    print(colorize(line, "cyan", theme))
    print(colorize(title.center(60), "cyan", theme))
    print(colorize(line, "cyan", theme))


def print_tasks(tasks, theme="dark"):
    if not tasks:
        print("\nNo tasks to show.\n")
        return

    header = f"{'#':<4}{'ID':<9}{'Title':<22}{'Deadline':<17}{'Pri':<8}{'Category':<10}{'Status'}"
    print(f"\n{header}")
    print("-" * 95)
    for idx, t in enumerate(tasks, start=1):
        title = (t.title[:19] + "...") if len(t.title) > 22 else t.title
        row = f"{idx:<4}{t.id:<9}{title:<22}{t.deadline:<17}{t.priority:<8}{t.category:<10}"
        print(row + t.status_icon(theme))
    print()


def progress_bar(completed, total, length=20):
    if total == 0:
        return "\u2591" * length + " 0%"
    percent = round((completed / total) * 100)
    filled = round((completed / total) * length)
    bar = "\u2588" * filled + "\u2591" * (length - filled)
    return f"{bar} {percent}%"


def render_pie_chart(completed, total, radius=7):
    """A plain-ASCII pie chart, no external libraries needed."""
    if total == 0:
        return "No tasks yet - nothing to chart."

    fraction_done = completed / total
    lines = []
    for y in range(-radius, radius + 1):
        row = []
        for x in range(-radius * 2, radius * 2 + 1):
            # correct for characters being taller than they are wide
            dist = math.sqrt((x / 2) ** 2 + y ** 2)
            if dist > radius:
                row.append(" ")
                continue
            angle = math.degrees(math.atan2(-y, x / 2)) % 360
            # rotate so the slice starts at 12 o'clock, going clockwise
            adjusted = (90 - angle) % 360
            slice_fraction = adjusted / 360
            row.append("\u2588" if slice_fraction < fraction_done else "\u2591")
        lines.append("".join(row))
    return "\n".join(lines)


def calendar_view(manager, theme="dark", year=None, month=None):
    today = datetime.now()
    year = year or today.year
    month = month or today.month
    by_day = manager.tasks_by_day(year, month)

    print(f"\n{cal_module.month_name[month]} {year}".center(41))
    print("  Mo    Tu    We    Th    Fr    Sa    Su")

    for week in cal_module.Calendar(firstweekday=0).monthdayscalendar(year, month):
        row = []
        for day in week:
            if day == 0:
                row.append("     ")
            elif day in by_day:
                marked = f"{day}({len(by_day[day])})"
                has_overdue = any(t.is_overdue() for t in by_day[day])
                color = "red" if has_overdue else "yellow"
                row.append(colorize(f"{marked:>5}", color, theme))
            else:
                row.append(f"{day:>5}")
        print(" ".join(row))

    if by_day:
        print("\nDeadlines this month:")
        for day in sorted(by_day):
            titles = ", ".join(t.title for t in by_day[day])
            print(f"  {day:>2} {cal_module.month_name[month][:3]} - {titles}")
    print()


# ---------------- input helpers ----------------

def get_valid_deadline(current=None):
    prompt = "Deadline (YYYY-MM-DD HH:MM)"
    prompt += f" [Enter to keep: {current}]: " if current else ": "
    while True:
        raw = input(prompt).strip()
        if not raw and current:
            return current
        try:
            datetime.strptime(raw, DATE_FORMAT)
            return raw
        except ValueError:
            print("Invalid format. Example: 2026-07-10 18:00")


def get_valid_priority(current=None):
    while True:
        suffix = f"  [Enter to keep: {current}]" if current else ""
        print(f"Priority: 1) High  2) Medium  3) Low{suffix}")
        choice = input("Choose (1-3): ").strip()
        if not choice and current:
            return current
        if choice in PRIORITIES:
            return PRIORITIES[choice]
        print("Invalid choice, try again.")


def get_valid_category(current=None):
    while True:
        suffix = f"  [Enter to keep: {current}]" if current else ""
        print(f"Category: 1) Study  2) Work  3) Personal{suffix}")
        choice = input("Choose (1-3): ").strip()
        if not choice and current:
            return current
        if choice in CATEGORIES:
            return CATEGORIES[choice]
        print("Invalid choice, try again.")


def pick_task(tasks, theme="dark"):
    print_tasks(tasks, theme)
    if not tasks:
        return None
    raw = input("Enter task # (or blank to cancel): ").strip()
    if not raw:
        return None
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(tasks):
            return tasks[idx]
    except ValueError:
        pass
    print("Invalid selection.")
    return None


def pause():
    input("Press Enter to continue...")


# ---------------- flows ----------------

def show_notifications(manager, theme):
    upcoming, overdue = manager.upcoming_and_overdue(hours=24)
    if not upcoming and not overdue:
        print(colorize("\nNo urgent deadlines - you're on top of things.\n", "green", theme))
        return

    print()
    for t in overdue:
        print(colorize(f"\U0001F534 OVERDUE: {t.title} (was due {t.deadline})", "red", theme))
    for t in upcoming:
        hrs = int(t.hours_left())
        print(colorize(f"\U0001F7E1 Due soon: {t.title} ({hrs}h left)", "yellow", theme))
    print()


def add_task_flow(manager):
    title = input("Task title: ").strip()
    if not title:
        print("Title cannot be empty.")
        return
    deadline = get_valid_deadline()
    priority = get_valid_priority()
    category = get_valid_category()
    task = manager.add_task(title, deadline, priority, category)
    print(f"Task added as {task.id}.\n")


def edit_task_flow(manager, theme):
    task = pick_task(manager.sorted_tasks(), theme)
    if not task:
        return
    print(f"\nEditing {task.id}")
    print(f"Current title:\n{task.title}\n")
    new_title = input("New title (Enter to keep): ").strip()
    new_deadline = get_valid_deadline(current=task.deadline)
    new_priority = get_valid_priority(current=task.priority)
    new_category = get_valid_category(current=task.category)
    manager.edit_task(
        task.id,
        title=new_title if new_title else None,
        deadline=new_deadline,
        priority=new_priority,
        category=new_category,
    )
    print("Task updated.\n")


def toggle_flow(manager, theme):
    task = pick_task(manager.sorted_tasks(), theme)
    if task:
        manager.toggle_done(task.id)
        print("Updated.\n")


def delete_flow(manager, theme):
    task = pick_task(manager.sorted_tasks(), theme)
    if task:
        confirm = input(f"Delete '{task.title}'? (y/n): ").strip().lower()
        if confirm == "y":
            manager.delete_task(task.id)
            print("Deleted.\n")


def search_flow(manager):
    keyword = input("Search: ").strip()
    if not keyword:
        return
    results = manager.search(keyword)
    if not results:
        print("No matching tasks.\n")
        return
    print()
    for idx, t in enumerate(results, start=1):
        print(f"{idx}. {t.title}")
    print()
    pause()


def filter_flow(manager, theme):
    print("""
1. Show All
2. Pending
3. Completed
4. High Priority
5. Overdue
6. By Category
""")
    choice = input("Choose a filter: ").strip()
    mapping = {"1": "all", "2": "pending", "3": "completed", "4": "high", "5": "overdue"}
    if choice == "6":
        category = get_valid_category()
        print_tasks(manager.filter_tasks("category", category), theme)
    else:
        mode = mapping.get(choice, "all")
        print_tasks(manager.filter_tasks(mode), theme)
    pause()


def dashboard_flow(manager, theme):
    s = manager.stats()
    print_header("DASHBOARD", theme)
    print(f"\nTotal Tasks   : {s['total']}")
    print(f"Completed     : {s['completed']}")
    print(f"Pending       : {s['pending']}")
    print(colorize(f"Overdue       : {s['overdue']}", "red" if s["overdue"] else "green", theme))
    print(f"Completion Rate: {s['completion_rate']}%")
    print()
    print(f"High Priority : {s['high']}")
    print(f"Medium        : {s['medium']}")
    print(f"Low           : {s['low']}")
    print()
    print("Tasks Completed")
    print(progress_bar(s["completed"], s["total"]))
    print()
    print("Completed vs Pending")
    print(render_pie_chart(s["completed"], s["total"]))
    print(colorize("\u2588 completed   \u2591 pending", "gray", theme))
    print()
    pause()


def calendar_flow(manager, theme):
    raw = input("Month to view (YYYY-MM, Enter for current): ").strip()
    year = month = None
    if raw:
        try:
            parts = raw.split("-")
            if len(parts) != 2:
                raise ValueError
            year, month = int(parts[0]), int(parts[1])
            if month < 1 or month > 12:
                raise ValueError
        except ValueError:
            print("Invalid format, showing current month instead.")
            year = month = None
    calendar_view(manager, theme, year, month)
    pause()


def export_flow(manager):
    tasks = manager.sorted_tasks()
    with open(REPORT_FILE, "w") as f:
        f.write("========== TO DO REPORT ==========\n\n")
        for t in tasks:
            dt = t.deadline_dt()
            deadline_display = t.deadline if dt == datetime.max else dt.strftime("%d %B")
            status = "Completed" if t.done else ("Overdue" if t.is_overdue() else "Pending")
            f.write(f"{t.title}\n")
            f.write(f"Task ID  : {t.id}\n")
            f.write(f"Category : {t.category}\n")
            f.write(f"Priority : {t.priority}\n")
            f.write(f"Deadline : {deadline_display}\n")
            f.write(f"Status   : {status}\n\n")
    print(f"Report exported to {REPORT_FILE}\n")
    pause()


def theme_flow(config):
    config["theme"] = "light" if config["theme"] == "dark" else "dark"
    save_config(config)
    print(f"Theme switched to {config['theme']}.\n")
    pause()


def exit_flow():
    confirm = input("Exit? (Y/N): ").strip().lower()
    return confirm == "y"


# ---------------- main loop ----------------

def main():
    config = load_config()
    if not authenticate(config):
        return

    manager = TaskManager()
    theme = config["theme"]

    clear_screen()
    print_header(theme=theme)
    show_notifications(manager, theme)
    pause()

    while True:
        theme = config["theme"]
        clear_screen()
        print_header(theme=theme)
        print_tasks(manager.sorted_tasks(), theme)
        print("""
1. Add Task
2. Edit Task
3. Mark Done / Undone
4. Delete Task
5. Search Tasks
6. Filter Tasks
7. Dashboard
8. Calendar View
9. Export Report
10. Toggle Theme (Dark/Light)
11. Exit
""")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_task_flow(manager)
            pause()
        elif choice == "2":
            edit_task_flow(manager, theme)
            pause()
        elif choice == "3":
            toggle_flow(manager, theme)
            pause()
        elif choice == "4":
            delete_flow(manager, theme)
            pause()
        elif choice == "5":
            search_flow(manager)
        elif choice == "6":
            filter_flow(manager, theme)
        elif choice == "7":
            dashboard_flow(manager, theme)
        elif choice == "8":
            calendar_flow(manager, theme)
        elif choice == "9":
            export_flow(manager)
        elif choice == "10":
            theme_flow(config)
        elif choice == "11":
            if exit_flow():
                print("Goodbye!")
                break
        else:
            print("Invalid option.")
            pause()


if __name__ == "__main__":
    main()