import datetime
import time
from typing import List, Tuple
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select, col
from db.models import core
from dependencies import get_db
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlalchemy.orm import load_only
from sqlalchemy import or_, and_

from mapping.tiles import deg2num, generate_heatmap_bytes, get_bounds

router = APIRouter(
    tags=["observations"],
    prefix="/observations"
)


@router.get("/", response_model=Page[core.GbifObservation])
def get_all_observations(db: Session = Depends(get_db)):
    return paginate(db, select(core.GbifObservation))


@router.get("/{id}", response_model=core.GbifObservation)
def get_observations_by_id(id: int, db: Session = Depends(get_db)):
    return db.exec(select(core.GbifObservation).filter(
        core.GbifObservation.gbifid == id)).first()


@router.get("/by_species/{species}", response_model=Page[core.GbifObservation])
def get_observations_by_species(species: str, db: Session = Depends(get_db)):
    return paginate(
        db,
        select(core.GbifObservation).join(core.Species).where(
            core.Species.species == species)
    )


@router.get("/{observation_id}/images", response_model=Page[core.GbifObservationImage])
def get_observation_images_by_observation_id(observation_id: int, db: Session = Depends(get_db)):
    return paginate(db,
                    select(core.GbifObservationImage).where(
                        core.GbifObservationImage.observation_id == observation_id)
                    )


@router.get("/images", response_model=Page[core.GbifObservationImage])
def get_observation_images(db: Session = Depends(get_db)):
    return paginate(db, select(core.GbifObservationImage))


@router.get("/images/{image_id}", response_model=core.GbifObservationImage)
def get_image_by_id(image_id: int, db: Session = Depends(get_db)):
    return db.exec(
        select(core.GbifObservationImage).where(
            core.GbifObservationImage.id == image_id)
    ).first()


def get_points(zoom, x, y, db: Session, where_clauses: Tuple):
    north_west, south_east = get_bounds(zoom, x, y)

    timer = time.process_time()
    points = db.exec(
        select(
            core.GbifObservation
        ).where(
            *where_clauses,
            (core.GbifObservation.latitude or 300) < north_west[0],
            (core.GbifObservation.latitude or -300) > south_east[0],
            (core.GbifObservation.longitude or 300) > north_west[1],
            (core.GbifObservation.longitude or -300) < south_east[1],
            core.GbifObservation.include_in_map == True,
        ).options(load_only("latitude", "longitude"))

    ).all()
    print(f"Query time: {time.process_time() - timer}")
    return [(p.latitude, p.longitude) for p in points]


# @router.get(
#     "/heatmap/all/{zoom}/{x}/{y}.png",
#     response_class=Response
# )
# def get_all_heatmap(zoom: int, x: int, y: int, db: Session = Depends(get_db)):
#     timer = time.process_time()
#     points = get_points(zoom, x, y, db,
#                         (1 == 1,)
#                         )
#     all_scale = 100
#     heatmap = get_heatmap(points, zoom, x, y, all_scale)
#     print(f"Total time: {time.process_time() - timer}")
#     return heatmap


@router.get(
    "/heatmap/seasonal/{month}/{day}/{zoom}/{x}/{y}.png",
    response_class=Response
)
def get_seasonal_heatmap(month: int, day: int, zoom: int, x: int, y: int, db: Session = Depends(get_db)):
    d = datetime.date(2020, month, day)
    upper = d + datetime.timedelta(weeks=1)
    lower = d - datetime.timedelta(weeks=1)
    timer = time.process_time()
    points = get_points(zoom, x, y, db,
                        (or_(
                            and_(
                                col(core.GbifObservation.month) >= lower.month,
                                col(core.GbifObservation.day) >= lower.day
                            ).self_group(),
                            and_(
                                col(core.GbifObservation.month) <= upper.month,
                                col(core.GbifObservation.day) <= upper.day
                            ).self_group()
                        ),)
                        )
    seasonal_scale = int(2000 / (zoom * 1.5))
    heatmap = get_heatmap(points, zoom, x, y, seasonal_scale)
    print(f"Total time: {time.process_time() - timer}")
    return heatmap


@ router.get(
    "/heatmap/{species}/{zoom}/{x}/{y}.png",
    response_class=Response
)
def get_species_heatmap(species: str, zoom: int, x: int, y: int, db: Session = Depends(get_db)):
    points = get_species_heatmap_observations(species, zoom, x, y, db)
    species_scale = 14
    heatmap = get_heatmap(points, zoom, x, y, species_scale)
    return heatmap


@ router.get(
    "/heatmap/{species}/{zoom}/{x}/{y}",
    response_model=List[Tuple[float, float]]
)
def get_species_heatmap_observations(species: str, zoom: int, x: int, y: int, db: Session = Depends(get_db)):
    id = db.exec(select(core.Species.id).where(
        core.Species.species == species)).first()

    if id is None:
        raise HTTPException(status_code=404, detail="Species not found")

    return get_points(zoom, x, y, db,
                      (core.GbifObservation.species_id == id,)
                      )


def get_heatmap(points, zoom: int, x: int, y: int, scale: int):
    north_west, south_east = get_bounds(zoom, x, y)

    points = [((lat or 0) - south_east[0],
               (lng or 0) - north_west[1]) for (lat, lng) in points]

    img = generate_heatmap_bytes(points,
                                 north_west[0] - south_east[0],
                                 south_east[1] - north_west[1],
                                 256,
                                 scale
                                 )
    return Response(content=img, media_type="image/png")


@ router.get(
    "/heatmap/{species}/{zoom}/img.png",
    response_class=Response
)
def get_species_heatmap_lat_long(species, zoom: int, lat: float, lng: float, db: Session = Depends(get_db)):
    x, y = deg2num(zoom, lat, lng)
    print(f"http://localhost:8080/observations/heatmap/{zoom}/{x}/{y}.png")
    heatmap = get_species_heatmap(species, zoom, x, y, db)
    return heatmap
