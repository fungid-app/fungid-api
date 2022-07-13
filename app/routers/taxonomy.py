from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from db import crud
from db.models import core
from dependencies import get_db
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

router = APIRouter(
    tags=["taxonomy"],
    prefix="/taxonomy"
)


@router.get("/species/", response_model=Page[core.Species])
def read_users(db: Session = Depends(get_db)):
    species = crud.get_all_species(db)
    return paginate(species)


@router.get("/species/{name_or_id}", response_model=core.Species)
def read_user(name_or_id: str, db: Session = Depends(get_db)):
    db_species = crud.get_species(db, name=name_or_id)

    if db_species is None:
        db_species = crud.get_species_by_id(db, id=int(name_or_id))

    if db_species is None:
        raise HTTPException(status_code=404, detail="User not found")

    return db_species
