from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from core.auth.dependencies import get_current_user
from core.auth.models import User
from core.schemas.room_schema import LocationRequest, MessageResponse
from core.db.database import get_db
from api.room.emergency.service.haversine import haversine

router = APIRouter(
    prefix="/emergency",
    tags=["Emergency"]
)

@router.post(
    "/location",
    summary="농인의 현재 위치 등록 및 근처 응급기관 선택",
    description="농인의 현재 위치(위도, 경도)를 전송받아 가장 가까운 응급기관의 코드를 반환합니다.",
    response_model=MessageResponse,
    responses={
        200: {
            "description": "가장 가까운 응급기관 코드 반환",
            "content": {
                "application/json": {
                    "example": {"message": "a1b2c3d"}
                }
            }
        },
        400: {
            "description": "농인이 아닐 경우",
            "content": {
                "application/json": {
                    "example": {"detail": "농인만 위치를 등록할 수 있습니다."}
                }
            }
        },
        404: {
            "description": "DB 내 해당 유형의 응급기관이 없거나 위치 정보가 누락된 경우",
            "content": {
                "application/json": {
                    "example": {"detail": "병원 유형의 응급기관이 없습니다."}
                }
            }
        },
        500: {
            "description": "DB 내 응급기관 방코드 누락",
            "content": {
                "application/json": {
                    "example": {"detail": "응급기관에 emergency_code가 설정되지 않았습니다."}
                }
            }
        }
    }
)
async def submit_location(
    location: LocationRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "농인":
        raise HTTPException(status_code=400, detail="농인만 위치를 등록할 수 있습니다.")

    request.app.state.emergency_locations[current_user.id] = (location.latitude, location.longitude)

    agencies = db.query(User).filter(
        User.user_type == "응급기관",
        User.emergency_type == location.emergency_type
    ).all()

    if not agencies:
        raise HTTPException(status_code=404, detail=f"{location.emergency_type} 유형의 응급기관이 없습니다.")

    closest_agency = None
    min_distance = float("inf")

    for agency in agencies:
        if agency.latitude is None or agency.longitude is None:
            continue
        dist = haversine(location.latitude, location.longitude, agency.latitude, agency.longitude)
        if dist < min_distance:
            min_distance = dist
            closest_agency = agency

    if not closest_agency:
        raise HTTPException(status_code=404, detail="해당 유형의 응급기관 중 위치 정보가 등록된 곳이 없습니다.")

    emergency_code = closest_agency.emergency_code
    if not emergency_code:
        raise HTTPException(status_code=500, detail="응급기관에 emergency_code가 설정되지 않았습니다.")

    return {"message": emergency_code}