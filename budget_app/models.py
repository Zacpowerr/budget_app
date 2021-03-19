from budget_app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), unique=True)
    email = db.Column(db.String(45), unique=True)
    password = db.Column(db.String(45))
    saving_total = db.Column(db.Float(precision=2), nullable=True, default=0)
    total_available_amount = db.Column(db.Float(precision=2), nullable=True, default=0)
    budgets = db.relationship("Budget", backref="user", lazy=True)
    categories = db.relationship("Category", backref="user", lazy=True)

    def __repr__(self):
        return f"User('{self.username}','{self.total_available_amount}')"


class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    inicial_amount = db.Column(db.Float(precision=2))
    saving_amount = db.Column(db.Float(precision=2), nullable=True, default=0)
    available_amount = db.Column(db.Float(precision=2), nullable=True, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"Budget('{self.name}',{self.inicial_amount},{self.available_amount})"

    def amount_available(self):
        for categories in self.budget_categories:
            flash("category threshold: {categories.threshold}")

        return value


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False, unique=False)
    description = db.Column(db.String(45), nullable=True)
    deleted = db.Column(db.Boolean(), default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    budgets = db.relationship("Budget_category", backref="category", lazy=True)

    def __repr__(self):
        return f"Category('{self.name}','{self.description}')"


class Budget_category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    threshold = db.Column(db.Float(precision=2), nullable=False)
    used_amount = db.Column(db.Float(precision=2), nullable=True, default=0)
    available_amount = db.Column(db.Float(precision=2), nullable=True, default=0)
    budget_id = db.Column(db.Integer, db.ForeignKey("budget.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    budgets = db.relationship("Budget", backref="categories", lazy=True)

    def __repr__(self):
        return f"Budget_category('{self.budget_id}','{self.category_id}','{self.threshold}')"
