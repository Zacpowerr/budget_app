from budget_app.models import Category
from budget_app import db, app
from budget_app import default_category_id


# create default category
with app.app_context():
    default_category = Category.query.filter_by(id=default_category_id).first()
    if default_category == None:
        default_category = Category(
        id=default_category_id,
        name="Leftovers",
        description="Money that is leftover from other categories",
        user_id=None,
    )
    db.session.add(default_category)
    db.session.commit()