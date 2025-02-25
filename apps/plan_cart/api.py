from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from apps.plan_cart.schema import CheckoutInput, CartOutput
from apps.plan_cart.service import PlanCartService

plan_cart_router = APIRouter(prefix="/Plan_cart", tags=["購物車 API"])

#TODO: 1. 檢查使用者JWT的裝飾器, 2. 檢查使用者正確性相關套件 3. 購物車DB應用 
@plan_cart_router.post("/", response_model=CartOutput)
def calculate_cart_total(data: CheckoutInput, service: PlanCartService = Depends()):
    try:
        parsed_data = service.data_precheck(data.data)
        result = service.calculate_cart_total(parsed_data)
        return {"total_price": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))