from fastapi import APIRouter

from api.schemas.categories import CategoryModel

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.post("/")
def create_category(category_details: CategoryModel):
    return {"message": f"Category '{category_details.name}' created successfully."}


@router.delete("/{category_id}")
def delete_category(category_id: str):
    return {"message": f"Category with ID {category_id} deleted successfully."}
