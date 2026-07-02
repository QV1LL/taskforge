from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/projects", tags=["Projects (Проєкти)"])

# Тимчасова база даних в оперативній пам'яті
projects_db = {}
project_id_counter = 1


# Pydantic-моделі для валідації контракту
class ProjectCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100, description="Назва проєкту")
    description: str | None = Field(
        default=None, max_length=500, description="Опис проєкту"
    )


class ProjectRead(BaseModel):
    id: int
    name: str
    description: str | None


# 1. Створення проєкту
@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate):
    global project_id_counter
    new_project = {
        "id": project_id_counter,
        "name": project.name,
        "description": project.description,
    }
    projects_db[project_id_counter] = new_project
    project_id_counter += 1
    return new_project


# 2. Отримання списку проєктів з пагінацією
@router.get("/", response_model=list[ProjectRead])
async def list_projects(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    projects_list = list(projects_db.values())
    return projects_list[skip : skip + limit]


# 3. Отримання проєкту за ID
@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: Annotated[int, Path(ge=1)]):
    if project_id not in projects_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Проєкт не знайдено"
        )
    return projects_db[project_id]


# 4. Видалення проєкту
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: Annotated[int, Path(ge=1)]):
    if project_id not in projects_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Проєкт не знайдено"
        )
    del projects_db[project_id]
    return None
