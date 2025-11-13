from pydantic import BaseModel, constr

class Rolebase(BaseModel):
    name: str

class RoleCreate(Rolebase):
    pass 
 
class UserCreate(BaseModel):
    name : str
    email : constr(strip_whitespace=True, to_lower=True)
    password : constr(min_length=4, max_length=72)
    family_name : str

class UserLogin(BaseModel):
    email : constr(strip_whitespace=True, to_lower=True)
    password : constr(min_length=4, max_length=72)

class Token(BaseModel):
    access_token: str
    token_type: str
    