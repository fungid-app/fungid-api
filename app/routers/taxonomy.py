from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db.models import core
from dependencies import get_db
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate

router = APIRouter(
    tags=["taxonomy"],
    prefix="/taxonomy"
)


@router.get("/species/", response_model=Page[core.Species])
def get_all_species(db: Session = Depends(get_db)):
    return paginate(db, select(core.Species))


@router.get("/species/{name_or_id}", response_model=core.Species)
def get_species(name_or_id: str, db: Session = Depends(get_db)):
    db_species = db.exec(
        select(core.Species).where(core.Species.species == name_or_id)).first()

    if db_species is None:
        db_species = db.exec(
            select(core.Species)
            .where(core.Species.id == int(name_or_id))
        ).first()

    if db_species is None:
        raise HTTPException(status_code=404, detail="Species not found")

    return db_species
