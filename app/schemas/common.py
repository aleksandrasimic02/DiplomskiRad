from pydantic import BaseModel, Field, EmailStr, constr, conint
from datetime import date
PHONE_RE = r'^[0-9+()\- ]{6,20}$'
