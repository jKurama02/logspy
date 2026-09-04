from pydantic import BaseModel, Field , EmailStr, ConfigDict

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=50)

class UserRead(BaseModel):        # ESCE verso il client
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)

