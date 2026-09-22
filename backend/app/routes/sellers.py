"""Sellers management routes — /sellers"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.models.models import Seller
from app.core.security import require_api_key

router = APIRouter()


class SellerCreate(BaseModel):
    seller_name: str
    marketplace: str = "multi"
    region:      str = "IN"
    email:       Optional[str] = None


@router.post("/", summary="Register a new seller", dependencies=[Depends(require_api_key)])
async def create_seller(payload: SellerCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Check if seller already exists by name or email
        existing_query = select(Seller).where(
            (Seller.seller_name == payload.seller_name) | 
            (Seller.email == payload.email)
        )
        result = await db.execute(existing_query)
        existing_seller = result.scalar_one_or_none()
        
        if existing_seller:
            return {
                "seller_id":   str(existing_seller.seller_id),
                "seller_name": existing_seller.seller_name,
                "marketplace": existing_seller.marketplace,
                "created_at":  str(existing_seller.created_at),
                "message": "Existing seller found"
            }

        seller = Seller(
            seller_name = payload.seller_name,
            marketplace = payload.marketplace,
            region      = payload.region,
            email       = payload.email,
        )
        db.add(seller)
        await db.commit()
        await db.refresh(seller)
        return {
            "seller_id":   str(seller.seller_id),
            "seller_name": seller.seller_name,
            "marketplace": seller.marketplace,
            "created_at":  str(seller.created_at),
        }
    except Exception as e:
        import traceback
        raise HTTPException(status_code=400, detail=str(traceback.format_exc()))


@router.get("/", summary="List all sellers", dependencies=[Depends(require_api_key)])
async def list_sellers(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Seller).where(Seller.is_active == True))
        sellers = result.scalars().all()
        return [
            {"seller_id": str(s.seller_id), "seller_name": s.seller_name, "marketplace": s.marketplace}
            for s in sellers
        ]
    except Exception as e:
        import traceback
        raise HTTPException(status_code=400, detail=str(traceback.format_exc()))


@router.get("/{seller_id}", summary="Get seller by ID")
async def get_seller(seller_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Seller).where(Seller.seller_id == seller_id))
    seller = result.scalar_one_or_none()
    if not seller:
        raise HTTPException(404, "Seller not found")
    return {
        "seller_id":   str(seller.seller_id),
        "seller_name": seller.seller_name,
        "marketplace": seller.marketplace,
        "region":      seller.region,
        "email":       seller.email,
        "created_at":  str(seller.created_at),
    }
