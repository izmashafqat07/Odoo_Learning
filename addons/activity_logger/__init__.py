from . import models
from . import controllers

# Ensure ORM hooks are patched after registry is ready
def post_load():
    from .models.orm_hook import patch_orm_methods
    patch_orm_methods()


