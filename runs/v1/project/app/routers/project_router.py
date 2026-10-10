from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from app.models import Project
from app.schemas import ProjectCreate, ProjectResponse, ProjectListResponse
from app.database import get_db
from app.auth import get_current_user_or_raise

router = APIRouter()

@router.post("/projects", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_or_raise)):
    db_project = Project(name=project.name, owner_id=current_user.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/projects", response_model=ProjectListResponse)
def get_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_raise)
):
    if current_user.role == "member":
        projects = db.query(Project).filter(Project.owner_id == current_user.id).order_by(Project.id).offset((page - 1) * page_size).limit(page_size).all()
    else:
        projects = db.query(Project).order_by(Project.id).offset((page - 1) * page_size).limit(page_size).all()
    total = len(projects)
    return {"items": projects, "total": total, "page": page, "page_size": page_size}

@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_or_raise)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if current_user.role == "member" and project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not owner or admin")
    return project

@router.delete("/projects/{project_id}", response_model=None)
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_or_raise)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if current_user.role == "member" and project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not owner or admin")
    db.delete(project)
    db.commit()
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
