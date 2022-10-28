from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select
from db.models import core
from dependencies import get_db
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlalchemy.orm import load_only

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


@router.get(
    "/heatmap/{species}/{z}/{x}/{y}.png",
    response_class=Response
)
def get_species_heatmap(species, z: int, x: int, y: int, db: Session = Depends(get_db)):
    north_west, south_east = get_bounds(x, y, z)

    id = db.exec(select(core.Species.id).where(
        core.Species.species == species)).first()

    if id is None:
        raise HTTPException(status_code=404, detail="Species not found")

    points = db.exec(
        select(
            core.GbifObservation
            # ((core.GbifObservation.latitude or 0) - south_east[0],
            #  (core.GbifObservation.longitude or 0) - north_west[1])
        ).where(
            core.GbifObservation.species_id == id,
            (core.GbifObservation.latitude or 300) < north_west[0],
            (core.GbifObservation.latitude or -300) > south_east[0],
            (core.GbifObservation.longitude or 300) > north_west[1],
            (core.GbifObservation.longitude or -300) < south_east[1],
        ).options(load_only("latitude", "longitude"))
    ).all()

    points = [((p.latitude or 0) - south_east[0],
               (p.longitude or 0) - north_west[1]) for p in points]

    img = generate_heatmap_bytes(points,
                                 north_west[0] - south_east[0],
                                 south_east[1] - north_west[1],
                                 256,
                                 z
                                 )
    return Response(content=img, media_type="image/png")


@router.get(
    "/heatmap/{species}/{z}/img.png",
    response_class=Response
)
def get_species_heatmap_lat_long(species, z: int, lat: float, lng: float, db: Session = Depends(get_db)):
    x, y = deg2num(lat, lng, z)
    # print(f"lat: {lat}, lng: {lng}, z: {z}, x: {x}, y: {y}")
    # print(f"https://tile.openstreetmap.org/{z}/{x}/{y}.png")
    return get_species_heatmap(species, z, x, y, db)
