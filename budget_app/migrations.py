from budget_app.models import Category
from budget_app import db

# create database
db.create_all()

# create default category
default_category = Category.query.filter_by(id=100).first()
if default_category == None:
    default_category = Category(
        id=100,
        name="Leftovers",
        description="Money that is leftover from other categories",
        user_id=None,
    )
    db.session.add(default_category)
    db.session.commit()