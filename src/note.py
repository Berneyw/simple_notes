import datetime
import threading
import notifications
import csv
from os import path, getcwd
from dateutil import parser as date_parser
from time import sleep
from colorama import Fore

# list_of_tasks = [
#     {"task": "Test1", "status": "Undone"},
#     {"task": "Test2", "status": "Done"},
#     {"task": "Test3", "status": "Undone"},
# ]

# TODO: Statistics about tasks, history of tasks

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
        with open(filename, 'w', newline='') as file:
            fieldnames = ['task', 'status', 'deadline', 'description']  # Замените на свои поля
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.list_of_tasks)
            
    @classmethod
    def load_tasks_from_csv(cls, filename):
        try:
            with open(filename, 'r', newline='') as file:
                reader = csv.DictReader(file)
                tasks = list(reader)
                for task in tasks:
                    if "deadline" in task:
                        task["deadline"] = date_parser.isoparse(task["deadline"])
                return tasks
        except FileNotFoundError:
            return []
        
    def display_list(self):
        print("SimpleNotes")
        print("---------------------------")

        for index, task_info in enumerate(self.list_of_tasks, start=1):
            task, status, deadline, description = task_info.get("task"), task_info.get("status"), task_info.get("deadline"), task_info.get("description")

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
                    task_string = f"{index}. {task} | {status} | Deadline: {deadline_str} | *"
                else:
                    task_string = f"{index}. {task} | {status} | Deadline: {deadline_str}"

                print(task_string)

            if "subtasks" in task_info:
                for subtask in task_info["subtasks"]:
                    subtask_task, subtask_status = subtask.get("task"), subtask.get("status")
                    if subtask_task is not None:
                        print(f"  - {subtask_task}")

        print("---------------------------")

    def change_status(self):
        
        """
        This function changes the status of tasks between Done | Undone
        checks if user input is a valid number of the actual task and then
        changes its status depending on user input
        """
        
        number_of_task = input("Enter a number of task: ")

        try:
            number_of_task = int(number_of_task) - 1

            if number_of_task < 0 or number_of_task >= len(self.list_of_tasks):
                print("Task not found")
                return

        except ValueError:
            print("\nEnter a valid task!\n")
            return
        except TypeError:
            print("\nEnter a valid task!\n")
            return

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
                
                if ask_to_delete in ["yes", "y", "yeah", "of course", "certainly", "ye"]:
                    self.list_of_tasks.pop(number_of_task)
                    print("\nSuccessfully deleted task"
                          f" '{self.list_of_tasks[number_of_task]['task']}'\n")
                
            case "2":
                self.list_of_tasks[number_of_task]["status"] = "Undone"
            case _:
                print("Incorrect status! Enter 1 or 2")
                
    def append_task(self):
        task_append_name = input("Enter name of a task\n >> ")

        if len(task_append_name) == 0 or len(task_append_name) > 70:
            print("Task name must be between 1 and 70 characters")
            return

        task_deadline = input("Enter task deadline (e.g., '14 October' or '15:00' or 'October 15')\n >> ")

        # Check if the user has provided a specific time (e.g., '15:00') in the input
        if ':' in task_deadline:
            deadline_date = self.parse_deadline(task_deadline)
        else:
            # If no time is specified, set the time to 23:59 (11:59 PM)
            deadline_date = self.parse_deadline(f"{task_deadline} 23:59")

        if deadline_date is not None:
            self.list_of_tasks.append({"task": task_append_name, "status": "Undone", "deadline": deadline_date})
            print(f"Successfully added task with name: {task_append_name}")
    
    def delete_task(self):
        task_delete_index = input("Enter number of task to delete\n >> ")
        
        try:
            task_delete_index = int(task_delete_index)
        
            if task_delete_index < 1 or task_delete_index > len(self.list_of_tasks):
                print("Invalid task number. Task not found.")
                return
        
            # Subtract 1 from task_delete_index to match the list indexing (starting from 0)
            deleted_task = self.list_of_tasks.pop(task_delete_index - 1)
            print(f"\nSuccessfully deleted task: {deleted_task['task']}\n")
    
        except ValueError:
            print("Invalid input. Please enter a valid task number.")
    
    @classmethod
    def parse_deadline(cls, deadline_str):
        try:
            # Attempt to parse the input using dateutil.parser
            deadline_date = date_parser.parse(deadline_str, dayfirst=True, yearfirst=False)
            return deadline_date
        except ValueError:
            print("Invalid deadline format. Please use a valid date and time format (e.g., '15 October' or '15:00').")
            return None

    @staticmethod
    def check_deadlines():  
        """  
        This function checks if current datetime equals to task deadline  
        and sends notification that deadline ended if it is.  
        """  
        notified_tasks = {}
        while True:  
            current_time = datetime.datetime.now()  
            for task_info in note.list_of_tasks:  
                if isinstance(task_info["deadline"], datetime.datetime) and task_info["status"] == "Undone":  
                    if current_time >= task_info["deadline"]:  
                        task_name = task_info["task"]  
                        if task_name not in notified_tasks:  
                            # Sends notification
                            notifications.send_notification_deadline(task_name)  
                            # Checks if notification sent
                            notified_tasks[task_name] = True  
            # Pause between checks
            sleep(30)
    
    def create_subtask(self):
        """Subtask should have this pattern:
        1. Task | Undone | Deadline: 17:30
            -Subtask | Undone
            -Subtask2 | Undone
            -Subtask3 | Done
        """
        # self.list_of_tasks.append
        # ({"task": task_append_name, "status": "Undone", "deadline": deadline_date})
        task_index = input("Enter the number of the task for which you want to add a subtask\n >> ")
        task_index = int(task_index)
        
        if task_index < 1 or task_index > len(self.list_of_tasks):
                print("Invalid task number. Task not found.")
                return
            
        subtask_name = input("Enter a name for subtask\n >> ")
        if subtask_name != None:
        # Check if the task already has subtasks, and if not, create an empty list
            if "subtasks" not in self.list_of_tasks[task_index - 1]:
                self.list_of_tasks[task_index - 1]["subtasks"] = []
            # Append the subtask to the list of subtasks within the parent task
            self.list_of_tasks[task_index - 1]["subtasks"].append({"task": subtask_name})
            
            print(f"Succesfully created subtask '{subtask_name}'")
            
    def change_priority(self):
        task_index = input("Enter task index\n >> ")
        task_index = int(task_index)
        # Current task saved in variable
        current_task = self.list_of_tasks[task_index - 1]["task"]
        
        current_task = current_task.replace(Fore.RED, '').replace(Fore.MAGENTA, '').replace(Fore.YELLOW, '').replace(Fore.GREEN, '').replace(Fore.WHITE, '')

        priority_value = input("Enter priority of your task\n"
                            "1 = Red (Highest)\n"
                            "2 = Pink (High)\n"
                            "3 = Yellow (Medium)\n"
                            "4 = Green (Light)\n"
                            "5 = White (Reset priority)\n >> ")
        priority_value = int(priority_value)
        
        # Changes task color 
        match priority_value:
            case 1:
                self.list_of_tasks[task_index - 1]["task"] = Fore.RED + current_task + Fore.RESET
            case 2:
                self.list_of_tasks[task_index - 1]["task"] = Fore.MAGENTA + current_task + Fore.RESET
            case 3:
                self.list_of_tasks[task_index - 1]["task"] = Fore.YELLOW + current_task + Fore.RESET
            case 4:
                self.list_of_tasks[task_index - 1]["task"] = Fore.GREEN + current_task + Fore.RESET
            case 5:
                self.list_of_tasks[task_index - 1]["task"] = current_task + Fore.RESET
                
    def make_description(self):
        task_index = input("Enter task index\n >> ")
        task_index = int(task_index)
        
        task_description = input("Enter task description\n >> ")
        self.list_of_tasks[task_index - 1]["description"] = task_description
        
    def read_description(self):
        task_index = input("Enter task index\n >> ")
        task_index = int(task_index)
        
        print(f"\nDescription: {self.list_of_tasks[task_index - 1]['description']}\n")
        
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
        tasks_per_week = []

        for task in self.list_of_tasks:
            if task["status"] == "Done":
                done_tasks += 1
                done_tasks_names.append(task["task"])
        print(f"Tasks done: {done_tasks}\n")

        for tasks in done_tasks_names:
            print(f"- {tasks}")

note = Note()

note.list_of_tasks.append({"task": "Test1", "status": "Undone", "deadline": "14 October"})
note.list_of_tasks.append({"task": "Test2", "status": "Done", "deadline": "14 October"})
note.list_of_tasks.append({"task": "Test3", "status": "Undone", "deadline": "14 October"})

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


def main():
    
    tasks = Note.load_tasks_from_csv("tasks.csv")
    note.list_of_tasks = tasks
    
    deadline_thread = threading.Thread(target=Note.check_deadlines)
    deadline_thread.daemon = True
    deadline_thread.start()
    
    while True:
        command = input("Enter what you want to do ('help' for all commands or 'q' to quit)\n >> ")
        command = command.casefold()
        
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
            print("Incorrect command, enter \"help\" for a list of available commands\n"
                        "Or enter \"q\" to exit terminal")

def check_command_in_file(command, file_name):
    """
    Check if a given command exists in a specified file.

    Args:
        command (str): The command to search for.
        file_name (str): The name of the file to search in.

    Returns:
        bool: True if the command is found in the file, False otherwise.
        
    """
    
    try:
        with open(file_name, 'r', encoding="utf-8") as file:
            file_contents = file.read()
            return command in file_contents
    except FileNotFoundError:
        return False


if __name__ == "__main__":
    main()