from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks (Завдання)"])

# Тимчасова база даних задач в пам'яті
tasks_db = {}
task_id_counter = 1


class TaskCreate(BaseModel):
    project_id: int = Field(ge=1, description="ID проєкту, до якого належить задача")
    title: str = Field(min_length=3, max_length=150, description="Назва задачі")
    description: str | None = Field(default=None, max_length=1000)
    priority: int = Field(default=1, ge=1, le=5, description="Пріоритет (від 1 до 5)")


class TaskRead(BaseModel):
    id: int
    project_id: int
    title: str
    description: str | None
    priority: int


class TaskUpdate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str | None = None
    priority: int = Field(ge=1, le=5)


# 1. Створення задачі
@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    global task_id_counter
    # На реальному проєкті ми б тут перевіряли, чи існує такий project_id у БД
    new_task = {
        "id": task_id_counter,
        "project_id": task.project_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
    }
    tasks_db[task_id_counter] = new_task
    task_id_counter += 1
    return new_task


# 2. Отримання списку задач із фільтрацією за project_id та пріоритетом
@router.get("/", response_model=list[TaskRead])
async def list_tasks(
    project_id: Annotated[int | None, Query(ge=1)] = None,
    priority: Annotated[int | None, Query(ge=1, le=5)] = None,
    skip: int = 0,
    limit: int = 10,
):
    tasks_list = list(tasks_db.values())

    # Застосовуємо фільтри
    if project_id is not None:
        tasks_list = [t for t in tasks_list if t["project_id"] == project_id]
    if priority is not None:
        tasks_list = [t for t in tasks_list if t["priority"] == priority]

    return tasks_list[skip : skip + limit]


# 3. Отримання однієї задачі за ID
@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: Annotated[int, Path(ge=1)]):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Задачу не знайдено")
    return tasks_db[task_id]


# 4. Оновлення задачі
@router.put("/{task_id}", response_model=TaskRead)
async def update_task(task_id: Annotated[int, Path(ge=1)], task_data: TaskUpdate):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Задачу не знайдено")

    current_task = tasks_db[task_id]
    current_task["title"] = task_data.title
    current_task["description"] = task_data.description
    current_task["priority"] = task_data.priority

    tasks_db[task_id] = current_task
    return current_task


# 5. Видалення задачі
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: Annotated[int, Path(ge=1)]):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Задачу не знайдено")
    del tasks_db[task_id]
    return None
