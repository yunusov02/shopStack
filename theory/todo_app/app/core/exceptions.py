class TaskNotFoundError(Exception):
    def __init__(self, task_id: str) -> None:
        super().__init__(f"Task {task_id} not found")
        self.task_id = task_id
