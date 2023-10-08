import datetime
import threading
import notifications
from dateutil import parser as date_parser
from time import sleep


# list_of_tasks = [
#     {"task": "Test1", "status": "Undone"},
#     {"task": "Test2", "status": "Done"},
#     {"task": "Test3", "status": "Undone"},
# ]

class Note:

    _instance = None  # Class-level variable to store the single instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Note, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        # Initialize the instance (constructor logic)
        self.list_of_tasks = []

    def display_list(self):
        
        """
        This function prints all the tasks
        """
        
        print("SimpleNotes")
        print("---------------------------")

        for index, task_info in enumerate(self.list_of_tasks, start=1):
            task, status, deadline = task_info["task"], task_info["status"], task_info["deadline"]

            if isinstance(deadline, datetime.datetime):
                deadline_str = deadline.strftime("%H:%M")
            else:
                deadline_str = str(deadline)

            if task_info["deadline"] == "":
                print(f"{index}. {task} | {status}")
            print(f"{index}. {task} | {status} | Deadline: {deadline_str}")

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
            case "2":
                self.list_of_tasks[number_of_task]["status"] = "Undone"
            case _:
                print("Incorrect status! Enter 1 or 2")
                
    def append_task(self):
        task_append_name = input("Enter name of a task\n >> ")
        task_deadline = input("Enter task deadline (e.g., '14 October' or '15:00' or 'October 15')\n >> ")

        deadline_date = self.parse_deadline(task_deadline)
        
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
    
    @staticmethod
    def parse_deadline(deadline_str):
        
        """
        Supports many user input for deadline, like 15 October, 15:00 and etc.
        """
        
        try:
            deadline_date = date_parser.parse(deadline_str)
            return deadline_date
        except ValueError:
            print("Invalid deadline format. Please use a valid date and time format.")
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



note = Note()

note.list_of_tasks.append({"task": "Test1", "status": "Undone", "deadline": "14 October"})
note.list_of_tasks.append({"task": "Test2", "status": "Done", "deadline": "14 October"})
note.list_of_tasks.append({"task": "Test3", "status": "Undone", "deadline": "14 October"})

help_message = [
    "1: show TODO list",
    "2: change status of task",
    "3: add new task",
    "4: delete task",
]

def main():
    
    deadline_thread = threading.Thread(target=Note.check_deadlines)
    deadline_thread.daemon = True
    deadline_thread.start()
    
    
    while True:
        command = input("Enter what you want to do ('help' for all commands or 'q' to quit)\n >> ")
        
        command = command.lower()
        
        if command == "help":
            for i in help_message:
                print(i)
                
        elif command == "q":
            break
        elif command == "1" or command == "list" or command == "show":
            note.display_list()
        elif command == "2" or command == "change":
            note.change_status()
        elif command == "3" or command == "add":
            note.append_task()
        elif command == "4" or command == "del":
            note.delete_task()


# note.append_task()

if __name__ == "__main__":
    main()

