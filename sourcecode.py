from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time
import json

# Load tasks from the JSON file
def load_tasks():
    try:
        with open('tasks.json', 'r') as file:
            tasks = json.load(file)
    except FileNotFoundError:
        tasks = []
    return tasks

# Save tasks to the JSON file
def save_tasks(tasks):
    with open('tasks.json', 'w') as file:
        json.dump(tasks, file, indent=4)

# Function to calculate task priority score
def calculate_score(deadline):
    currdate = datetime.now()
    date1 = datetime.strptime(deadline, "%Y-%m-%d")
    days_left = (date1 - currdate).days
    return max(0, 100 - days_left)  # Higher score for closer deadlines

# Allot function to calculate days left and print reminder
def allot():
    tasks = load_tasks()
    currdate = datetime.now()
    reminders = []
    for task in tasks:
        date1 = datetime.strptime(task["deadline"], "%Y-%m-%d")
        days_left = (date1 - currdate).days
        if days_left >= 0 and not task["completed"]:  # Only include tasks that are upcoming and not completed
            task_score = calculate_score(task["deadline"])
            reminders.append(f"Hey, don't forget! The task '{task['task']}' is due in {days_left} day(s). (Deadline: {task['deadline']}, Priority Score: {task_score})")
    
    if reminders:
        # Sort reminders based on priority score
        reminders = sorted(reminders, key=lambda x: int(x.split("Priority Score: ")[1][:-2]), reverse=True)
        print("\n".join(reminders))
    else:
        print("I couldn't find any upcoming tasks at the moment. Maybe you can add some? 😊")

# Function to add a task to the JSON file
def add_task(task_name, deadline):
    tasks = load_tasks()
    task = {
        "task": task_name,
        "deadline": deadline,
        "completed": False
    }
    tasks.append(task)
    save_tasks(tasks)

# Function to mark a task as completed
def complete_task(task_name):
    tasks = load_tasks()
    for task in tasks:
        if task["task"].lower() == task_name.lower():
            task["completed"] = True
            print(f"Yay! Task '{task_name}' has been marked as completed! 🎉")
            break
    else:
        print(f"Oops! I couldn't find a task named '{task_name}' 😕.")
    save_tasks(tasks)

def main():
    scheduler = BackgroundScheduler()
    is_scheduler_running = False

    try:
        while True:
            print("\n--- Chatbot Task Manager ---")
            print("1. Add a Task 📅")
            print("2. Mark Task as Completed ✅")
            print("3. Exit 👋")
            choice = input("What would you like to do? Please type the number: ")

            if choice == "1":
                task_name = input("Great! What's the name of the task you want to add? 📝: ")
                deadline = input("When is the deadline for this task? (Please enter the date in YYYY-MM-DD format) 📅: ")
                add_task(task_name, deadline)  # Save new task to JSON
                print(f"Awesome! I've added the task '{task_name}' with the deadline of {deadline} 😊.")
                if not is_scheduler_running:
                    # Start the scheduler only when tasks are added
                    scheduler.add_job(allot, 'interval', seconds=5)
                    scheduler.start()
                    is_scheduler_running = True

            elif choice == "2":
                task_name = input("Which task would you like to mark as completed? ✅: ")
                complete_task(task_name)

            elif choice == "3":
                print("Goodbye! Take care, and don't forget your tasks! 👋")
                # Stop the scheduler when exiting
                scheduler.shutdown()
                break

            else:
                print("Hmm... I didn't quite get that. Please select a valid option! 🤔")
            time.sleep(1)

    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    main()
