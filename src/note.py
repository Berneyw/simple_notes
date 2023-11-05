import datetime
import threading
import notifications
import csv
import ast
import smart_helper
from os import path
from dateutil import parser as date_parser
from time import sleep
from colorama import Fore

# Used Black for formatting

# list_of_tasks = [
#     {"task": "Test1", "status": "Undone"},
#     {"task": "Test2", "status": "Done"},
#     {"task": "Test3", "status": "Undone"},
# ]

# TODO: Statistics about tasks, history of tasks


# TODO: Better cancel input handling


def cancel_function(user_input):
    try:
        user_input = int(user_input) - 1
    except ValueError:
        if isinstance(user_input, str) and user_input.casefold() == "cancel":
            return 1


class Note:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Note, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        # Initialize the instance (constructor logic)
        self.list_of_tasks = []

    def save_tasks_to_csv(self, filename):
        """
        Save tasks to a CSV file.

        Parameters:
            filename (str): The name of the CSV file to save the tasks to.
        """
        with open(filename, "w", newline="") as file:
            fieldnames = [
                "task",
                "status",
                "deadline",
                "subtasks",
                "description",
            ]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.list_of_tasks)

    @classmethod
    def load_tasks_from_csv(cls, filename):
        """Load tasks from a CSV file

        Args:
            filename (str): The name of the CSV file to load

        Returns:
            list: list of tasks from CSV file
        """
        try:
            with open(filename, "r", newline="") as file:
                reader = csv.DictReader(file)
                tasks = list(reader)
                for task in tasks:
                    if "deadline" in task:
                        task["deadline"] = date_parser.isoparse(task["deadline"])
                    if "subtasks" in task:
                        subtasks_str = task["subtasks"]
                        if subtasks_str:
                            task["subtasks"] = ast.literal_eval(subtasks_str)
                        else:
                            task["subtasks"] = []

                # TODO: BUG FIX

            return tasks
        except FileNotFoundError:
            return []

    def display_list(self):
        """
        Display the list of tasks.

        This function prints the list of tasks along with their details.
        It iterates over the list of tasks and prints each task along with
        its status, deadline, and description (if available). If a task has subtasks,
        it prints them as well.

        Return:
        - None
        """
        print("SimpleNotes")
        print("---------------------------")

        for index, task_info in enumerate(self.list_of_tasks, start=1):
            task, status, deadline, description = (
                task_info.get("task"),
                task_info.get("status"),
                task_info.get("deadline"),
                task_info.get("description"),
            )

            if task is not None and status is not None:
                if isinstance(deadline, datetime.datetime):
                    if deadline.time() == datetime.time(0, 0):
                        # Display only the date if the time is midnight
                        deadline_str = deadline.strftime("%d %B")
                    else:
                        deadline_str = deadline.strftime("%d %B %H:%M")
                else:
                    deadline_str = str(deadline)

                if description:
                    task_string = (
                        f"{index}. {task} | {status} | Deadline: {deadline_str} | *"
                    )
                else:
                    task_string = (
                        f"{index}. {task} | {status} | Deadline: {deadline_str}"
                    )

                print(task_string)

            if "subtasks" in task_info:
                subtask_list = task_info["subtasks"]

                for subtask in subtask_list:
                    print(f"    - {subtask}")

        print("---------------------------")

    def change_status(self):
        """
        Changes the status (Done/Undone) of a task based on the user's input.

        Returns:
            None
        """

        number_of_task = input("Enter a number of task: ")

        if cancel_function(number_of_task) == 1:
            return None
        else:
            number_of_task = int(number_of_task) - 1

        print("What status to change to?\n")
        print("1 = Done")
        print("2 = Undone")
        new_status = input(">> ")

        match new_status:
            case "1":
                self.list_of_tasks[number_of_task]["status"] = "Done"
                print("Successfully changed status to Done")
                ask_to_delete = input("Do you want to delete this task? (Y/N)\n >> ")
                ask_to_delete = ask_to_delete.casefold()

                if ask_to_delete in [
                    "yes",
                    "y",
                    "yeah",
                    "of course",
                    "certainly",
                    "ye",
                ]:
                    self.list_of_tasks.pop(number_of_task)
                    print(
                        "\nSuccessfully deleted task"
                        f" '{self.list_of_tasks[number_of_task]['task']}'\n"
                    )

            case "2":
                self.list_of_tasks[number_of_task]["status"] = "Undone"
            case _:
                print("Incorrect status! Enter 1 or 2")

    def append_task(self):
        """
        Prompts the user to enter a task name and deadline,
        and appends the task to the list of tasks.

        Returns:
            None.
        """
        task_append_name = input("Enter name of a task\n >> ")

        if cancel_function(task_append_name) == 1:
            return None

        if len(task_append_name) == 0 or len(task_append_name) > 70:
            print("Task name must be between 1 and 70 characters")
            return None

        task_deadline = input(
            "Enter task deadline (e.g., '14 October' or '15:00' or 'October 15')\n >> "
        )

        if cancel_function(task_deadline) == 1:
            return None

        # Check if the user has provided a specific time (e.g., '15:00') in the input
        if ":" in task_deadline:
            deadline_date = self.parse_deadline(task_deadline)
        else:
            # If no time is specified, set the time to 23:59 (11:59 PM)
            deadline_date = self.parse_deadline(f"{task_deadline} 23:59")

        if deadline_date is not None:
            self.list_of_tasks.append(
                {
                    "task": task_append_name,
                    "status": "Undone",
                    "deadline": deadline_date,
                }
            )
            print(f"Successfully added task with name: {task_append_name}")

    def delete_task(self):
        """
        Deletes a task from the list of tasks.

        Returns:
            None: If the task number is invalid or the task is not found.
            str: The deleted task.
        """

        task_delete_index = input("Enter number of task to delete\n >> ")

        if cancel_function(task_delete_index) == 1:
            return None

        try:
            task_delete_index = int(task_delete_index)

            if task_delete_index < 1 or task_delete_index > len(self.list_of_tasks):
                print("Invalid task number. Task not found.")
                return None

            # Subtract 1 from task_delete_index to match the list indexing (starting from 0)
            deleted_task = self.list_of_tasks.pop(task_delete_index - 1)
            print(f"\nSuccessfully deleted task: {deleted_task['task']}\n")

        except ValueError:
            print("Invalid input. Please enter a valid task number.")

    @classmethod
    def parse_deadline(cls, deadline_str):
        """
        Parses a string representation of a deadline date and time into a valid datetime object.

        Args:
            deadline_str (str): A string representing the deadline date and time.

        Returns:
            datetime.datetime or None: A datetime object representing
            the parsed deadline date and time.

        Raises:
            ValueError: If the input string cannot be parsed into a datetime object.
        """
        try:
            # Attempt to parse the input using dateutil.parser
            deadline_date = date_parser.parse(
                deadline_str, dayfirst=True, yearfirst=False
            )
            return deadline_date
        except ValueError:
            print(
                "Invalid deadline format. Please use a valid date and time format (e.g., '15 October' or '15:00')."
            )
            return None

    @staticmethod
    def check_deadlines():
        """
        Checks the deadlines of tasks and sends notifications if a task's deadline has passed.

        This function iterates through the list of tasks stored in
        `note.list_of_tasks` and checks if each task's deadline has passed.
        If a task's deadline has passed and its status is "Undone", a notification
        is sent using the `notifications.send_notification_deadline` function.
        The function keeps track of tasks that have already been notified using
        the `notified_tasks` dictionary.

        Returns:
            None
        """
        notified_tasks = {}
        while True:
            current_time = datetime.datetime.now()
            for task_info in note.list_of_tasks:
                if (
                    isinstance(task_info["deadline"], datetime.datetime)
                    and task_info["status"] == "Undone"
                    and current_time >= task_info["deadline"]
                    and task_info["task"] not in notified_tasks
                ):
                    task_name = task_info["task"]
                    notifications.send_notification_deadline(task_name)
                    notified_tasks[task_name] = True
                    # Pause between checks
            sleep(30)

    def create_subtask(self):
        """
        Creates a subtask for a task in the list of tasks.

        Returns:
            None
        """

        task_index = input(
            "Enter the number of the task for which you want to add a subtask\n >> "
        )

        if cancel_function(task_index) == 1:
            return None
        else:
            task_index = int(task_index) - 1

        if task_index < 0 or task_index >= len(self.list_of_tasks):
            print("Invalid task number. Task not found.")
            return None

        subtask_name = input("Enter a name for subtask\n >> ")

        if subtask_name is not None:
            if "subtasks" not in self.list_of_tasks[task_index]:
                self.list_of_tasks[task_index]["subtasks"] = []

            if isinstance(self.list_of_tasks[task_index]["subtasks"], str):
                self.list_of_tasks[task_index]["subtasks"] = list(
                    self.list_of_tasks[task_index]["subtasks"]
                )

            self.list_of_tasks[task_index]["subtasks"].append(subtask_name)

    def change_priority(self):
        """
        Changes the priority (actually color with colorama.FORE)
        of a task based on the user's input.

        Returns:
            None
        """
        task_index = input("Enter task index\n >> ")
        if cancel_function(task_index) == 1:
            return None

        # Current task saved in variable
        current_task = self.list_of_tasks[task_index - 1]["task"]

        current_task = (
            current_task.replace(Fore.RED, "")
            .replace(Fore.MAGENTA, "")
            .replace(Fore.YELLOW, "")
            .replace(Fore.GREEN, "")
            .replace(Fore.WHITE, "")
        )

        priority_value = input(
            "Enter priority of your task\n"
            "1 = Red (Highest)\n"
            "2 = Pink (High)\n"
            "3 = Yellow (Medium)\n"
            "4 = Green (Light)\n"
            "5 = White (Reset priority)\n >> "
        )
        priority_value = int(priority_value)

        # Changes task color
        match priority_value:
            case 1:
                self.list_of_tasks[task_index - 1]["task"] = (
                    Fore.RED + current_task + Fore.RESET
                )
            case 2:
                self.list_of_tasks[task_index - 1]["task"] = (
                    Fore.MAGENTA + current_task + Fore.RESET
                )
            case 3:
                self.list_of_tasks[task_index - 1]["task"] = (
                    Fore.YELLOW + current_task + Fore.RESET
                )
            case 4:
                self.list_of_tasks[task_index - 1]["task"] = (
                    Fore.GREEN + current_task + Fore.RESET
                )
            case 5:
                self.list_of_tasks[task_index - 1]["task"] = current_task + Fore.RESET

    def make_description(self):
        """
        Prompts the user to enter a task index and a task description.
        Updates the 'description' field of the task at the given
        index in the 'list_of_tasks' list.

        Returns:
            None
        """
        task_index = input("Enter task index\n >> ")

        if cancel_function(task_index) == 1:
            return None

        task_description = input("Enter task description\n >> ")

        if cancel_function(task_description) == 1:
            return None
        else:
            task_index = int(task_index) - 1

        self.list_of_tasks[task_index]["description"] = task_description

    def read_description(self):
        """
        Reads the description of a task based on the user's input.

        Returns:
            None
        """
        task_index = input("Enter task index\n >> ")

        if cancel_function(task_index) == 1:
            return None
        else:
            task_index = int(task_index) - 1

        print(f"\nDescription: {self.list_of_tasks[task_index]['description']}\n")

    def statistics_about_tasks(self):
        # TODO: Tasks/week, Tasks/month, Most active days
        # Tasks per week/month patter:
        # Tasks done per week:
        # -taskname1
        # -taskname2
        # ...
        # This should be seen from user command, maybe handle user input if
        # user calls this function and ask him, if he wants to see other statistics
        # like tasks/week/month and etc.

        done_tasks = 0
        done_tasks_names = []
        # tasks_per_week = []

        for task in self.list_of_tasks:
            if task["status"] == "Done":
                done_tasks += 1
                done_tasks_names.append(task["task"])
        print(f"Tasks done: {done_tasks}\n")

        for tasks in done_tasks_names:
            print(f"- {tasks}")


note = Note()

# note.list_of_tasks.append(
#     {"task": "Test1", "status": "Undone", "deadline": "14 October"}
# )
# note.list_of_tasks.append(
#     {"task": "Test2", "status": "Done", "deadline": "14 October"}
# )
# note.list_of_tasks.append(
#     {"task": "Test3", "status": "Undone", "deadline": "14 October"}
# )

help_message = [
    "1: show TODO list",
    "2: change status of task",
    "3: add new task",
    "4: delete task",
    "5: create subtask",
    "6: change priority",
    "7: add description",
    "8: read description",
    "9: statistics about tasks",
]

# path from OS module
base_dir = path.dirname(path.abspath(__file__))
commands_dir = path.join(base_dir, "..", "commands")

list_file = path.join(base_dir, commands_dir, "list.txt")
status_file = path.join(base_dir, commands_dir, "status.txt")
append_file = path.join(base_dir, commands_dir, "append.txt")
delete_file = path.join(base_dir, commands_dir, "delete.txt")
subtask_file = path.join(base_dir, commands_dir, "subtask.txt")
priority_file = path.join(base_dir, commands_dir, "priority.txt")
description_file = path.join(base_dir, commands_dir, "description.txt")
read_description_file = path.join(base_dir, commands_dir, "read_description.txt")
statistics_file = path.join(base_dir, commands_dir, "statistics.txt")


def incorrect_command(user_input):
    """
    Takes a user input and checks if it is a valid command. If the input is not a valid command,
    it prints an error message and a help message. If the input is a valid command,
    it does nothing.

    Args:
        user_input: A string representing the user's input.
    Returns:
        None
    """

    most_similar_command = smart_helper.SmartHelper.find_similar_command(
        smart_helper.SmartHelper, user_input
    )
    if most_similar_command is None:
        print(
            "Incorrect command!\n"
            "Enter 'help' for list of available commands, or 'q' to quit"
        )
    else:
        most_similar_command = most_similar_command[:-1]
        print(
            f"Incorrect command, maybe you meant '{most_similar_command}'?"
            "\nOr enter 'help' for list of available commands"
        )


def main():
    tasks = Note.load_tasks_from_csv("tasks.csv")
    note.list_of_tasks = tasks

    # Start thread to check if task deadline passed with "check_deadlines" function
    deadline_thread = threading.Thread(target=Note.check_deadlines)
    deadline_thread.daemon = True
    deadline_thread.start()

    while True:
        command = input(
            "Enter what you want to do ('help' for all commands or 'q' to quit) \n >> "
        )
        command = command.casefold()

        if len(command.casefold()) < 2 and command.casefold() != "q":
            incorrect_command(command)
            continue

        # TODO: make more efficient way to parse commands, if possible

        if command == "help":
            for i in help_message:
                print(i)
        elif command == "q":
            note.save_tasks_to_csv("tasks.csv")
            break
        elif command == "1" or check_command_in_file(command, list_file):
            note.display_list()
        elif command == "2" or check_command_in_file(command, status_file):
            note.change_status()
        elif command == "3" or check_command_in_file(command, append_file):
            note.append_task()
        elif command == "4" or check_command_in_file(command, delete_file):
            note.delete_task()
        elif command == "5" or check_command_in_file(command, subtask_file):
            note.create_subtask()
        elif command == "6" or check_command_in_file(command, priority_file):
            note.change_priority()
        elif command == "7" or check_command_in_file(command, description_file):
            note.make_description()
        elif command == "8" or check_command_in_file(command, read_description_file):
            note.read_description()
        elif command == "9" or check_command_in_file(command, statistics_file):
            note.statistics_about_tasks()
        else:
            incorrect_command(command)
            continue


def check_command_in_file(command, file_name):
    """
    Check if a given command exists in a specified file.

    Parameters:
        command (str): The command to search for.
        file_name (str): The name of the file to search in.

    Returns:
        bool: True if the command is found in the file, False otherwise.

    """
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            file_contents = file.read()
            return command in file_contents
    except FileNotFoundError:
        return False


if __name__ == "__main__":
    main()
