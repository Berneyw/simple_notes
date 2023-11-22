import datetime
import csv

# DO CSV FILE APPENDER
task_history = set()


def load_history_from_csv():
    task_history.clear()

    with open("history/task_history.csv", "r") as file:
        reader = csv.DictReader(file)
        for index, row in enumerate(reader, start=1):
            task = row.get("task", "")
            status = row.get("status", "")
            deadline_str = row.get("deadline", "")
            subtask = row.get("subtask", "")
            description = row.get("description", "")

            try:
                if deadline_str:
                    deadline = datetime.datetime.strptime(
                        deadline_str, "%Y-%m-%d %H:%M:%S"
                    )
                else:
                    deadline = None
            except ValueError:
                print(f"Invalid datetime format in row {index}: {deadline_str}")
                continue

            task_tuple = (task, status, deadline, subtask, description)
            task_history.add(task_tuple)


def append_task_to_history(task_info):
    # Convert lists to tuples in task_info.values()
    task_history.add(
        tuple(
            tuple(value) if isinstance(value, list) else value
            for value in task_info.values()
        )
    )


def show_task_history():
    for index, task_info in enumerate(task_history, start=1):
        # task_info_length = len(task_info)
        task, status, deadline = task_info[:3]
        deadline_str = deadline.strftime("%d %B %H:%M") if deadline else "None"
        task_string = f"{index}. {task} | {status} | Deadline: {deadline_str}"
        # if task_info_length > 3:
        #     subtask = task_info[3]
        #     task_string += f" | Subtask: {subtask}"
        # if task_info_length > 4:
        #     description = task_info[4]
        #     task_string += f" | Description: {description}"
        print(task_string)


def save_task_to_history():
    with open("history/task_history.csv", "w", newline="") as file:
        fieldnames = [
            "task",
            "status",
            "deadline",
            "subtasks",
            "description",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for task_info in task_history:
            task_dict = {
                "task": task_info[0],
                "status": task_info[1],
                "deadline": task_info[2],
                "subtasks": task_info[3],
                "description": task_info[4],
            }
            writer.writerow(task_dict)


if __name__ == "__main__":
    show_task_history()
