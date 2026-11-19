from fastapi import APIRouter

from shopstack.modules.catalog.routes import catalog_router
from shopstack.modules.sales.routes import sales_router

router = APIRouter()

router.include_router(catalog_router)
router.include_router(sales_router)

