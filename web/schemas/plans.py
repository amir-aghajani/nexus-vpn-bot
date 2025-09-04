from pydantic import BaseModel, field_validator, ValidationInfo, PydanticUserError

from database import db_client


class PlanModel(BaseModel):
    name: str
    price: int
    duration: int
    bandwidth: int
    categoryId: str

    @field_validator('categoryId', mode='after')
    def validate_category_id(cls, category_id, info: ValidationInfo):
        if not db_client.exists('categories', category_id):
            raise ValueError('INVALID_CATEGORY_ID')

        return category_id
