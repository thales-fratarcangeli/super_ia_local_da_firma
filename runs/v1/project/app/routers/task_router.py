from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from app.models import Task, Project
from app.schemas import TaskCreate, TaskResponse, TaskListResponse
from app.database import get_db
from app.auth import get_current_user_or_raise

router = APIRouter()

@router.post("/projects/{project_id}/tasks", response_model=TaskResponse)
def create_task(
    project_id: int,
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_raise)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if current_user.role == "member" and project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not owner or admin")
    db_task = Task(**task.model_dump())
    db_task.project_id = project_id
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/projects/{project_id}/tasks", response_model=TaskListResponse)
def get_tasks(
    project_id: int,
    status: Optional[Literal["todo", "doing", "done"]] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_raise)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if current_user.role == "member" and project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not owner or admin")
    filters = []
    if status:
        filters.append(Task.status == status)
    tasks = db.query(Task).filter(*filters).order_by(Task.id).offset((page - 1) * page_size).limit(page_size).all()
    total = len(tasks)
    return {"items": tasks, "total": total, "page": page, "page_size": page_size}

@router.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_raise)
):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if current_user.role == "member" and db_task.project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not owner or admin")
    for key, value in task.items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/tasks/{task_id}", response_model=None)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_or_raise)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if current_user.role == "member" and db_task.project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not owner or admin")
    db.delete(db_task)
    db.commit()
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
