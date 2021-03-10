import json
from flask import request, render_template, url_for, flash, redirect, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from budget_app import app, db, bcrypt
from budget_app.models import User, Category, Budget, Budget_category
from budget_app.forms import (
    CategoryForm,
    RegisterForm,
    LoginForm,
    UpdateAccountForm,
    BudgetForm,
    BudgetCategoryForm,
    UpdateBudgetCategoryForm,
)

colors = [
    "#F7464A",
    "#46BFBD",
    "#FDB45C",
    "#FEDCBA",
    "#ABCDEF",
    "#DDDDDD",
    "#ABCABC",
    "#4169E1",
    "#C71585",
    "#FF4500",
    "#FEDCBA",
    "#46BFBD",
]

# Web routes
@app.route("/home")
@app.route("/")
def home():
    b = ""
    if current_user.is_authenticated:
        b = (
            Budget.query.filter_by(user_id=current_user.id)
            .order_by(Budget.id.desc())
            .first()
        )
    return render_template("home.html", budget=b)


@app.route("/about")
def about():
    return render_template("about.html")


# Authentication routes
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data, email=form.email.data, password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash(f"Account created! go ahead and login with you new account.", "success")
        return redirect(url_for("login"))
    return render_template("auth/register.html", form=form, title="Register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Login unsuccessful. Please check your email and password", "danger")
    return render_template("auth/login.html", form=form, title="Login")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


# END Authentication routes
@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for("static", filename="profile_pics/avatarDefault.png")
    return render_template(
        "account.html", title="Account", form=form, image_file=image_file
    )


@app.route("/categories")
@login_required
def categories():
    categories = (
        Category.query.filter_by(deleted=False)
        .filter((Category.user_id == current_user.id) | (Category.user_id == None))
        .all()
    )
    return render_template("categories.html", categories=categories, title="Categories")


@app.route("/category/<category_id>", methods=["GET", "POST"])
@login_required
def category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.deleted:
        flash(f"Category does not exist.", "danger")
        return redirect(url_for("categories"))
    return render_template("category.html", category=category, title=category.name)


@app.route("/category/new", methods=["GET", "POST"])
@login_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category.query.filter_by(name=form.name.data).first()
        if category is None:
            category = Category(
                name=form.name.data,
                description=form.description.data,
                user_id=current_user.id,
            )
        else:
            category.deleted = False
        db.session.add(category)
        db.session.commit()
        flash(f"Category {form.name.data} created!", "success")
        return redirect(url_for("categories"))

    return render_template("new_category.html", form=form, title="New Category")


@app.route("/category/<category_id>/update", methods=["GET", "POST"])
@login_required
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm()
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        db.session.commit()
        flash(f"The category has been updated!", "success")
        return redirect(url_for("category", category_id=category.id))
    elif request.method == "GET":
        form.name.data = category.name
        form.description.data = category.description
    return render_template(
        "new_category.html",
        category=category,
        category_id=category_id,
        form=form,
        title="Update Category",
    )


@app.route("/category/<category_id>/delete", methods=["POST"])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.id == 100:
        flash(f"The category can`t deleted!", "warning")
        return redirect(url_for("categories"))
    # Removing category from budgets
    budget_categories = Budget_category.query.filter_by(category_id=category_id).all()
    for budget_category in budget_categories:
        budget = Budget.query.filter_by(id=budget_category.budget_id).first()
        default_category = (
            Budget_category.query.filter_by(budget_id=budget.id)
            .filter_by(category_id=100)
            .first()
        )
        default_category.threshold = (
            default_category.threshold + budget_category.available_amount
        )
        default_category.available_amount = (
            default_category.available_amount + budget_category.available_amount
        )
        default_category.used_amount = (
            default_category.used_amount + budget_category.used_amount
        )
        db.session.add(default_category)
        db.session.add(budget)
        db.session.delete(budget_category)
        db.session.commit()
    # END Removing category from budgets
    if category.deleted:
        flash(f"The category has been deleted!", "success")
        return redirect(url_for("categories"))
    category.deleted = True
    db.session.add(category)
    db.session.commit()
    flash(f"The category has been deleted!", "success")
    return redirect(url_for("categories"))


@app.route("/budgets")
@login_required
def budgets():
    budgets = Budget.query.filter_by(user_id=current_user.id).all()
    return render_template("budgets.html", title="Budgets", budgets=budgets)


@app.route("/budget/<budget_id>", methods=["GET", "POST"])
@login_required
def budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    categories = []
    for c in budget.categories:
        category_db = Category.query.filter_by(id=c.category.id).first()
        category = {
            "id": c.id,
            "name": category_db.name,
            "used_amount": c.used_amount,
            "threshold": c.threshold,
            "available_amount": c.available_amount,
        }
        categories.append(category)

    categories = sorted(categories, key=lambda x: x["name"])
    return render_template(
        "budget.html", budget=budget, title=budget.name, categories=categories
    )


@app.route("/budget/new", methods=["GET", "POST"])
@login_required
def new_budget():
    form = BudgetForm()
    form_bc = BudgetCategoryForm()
    form_bc.category_id.choices = [
        (c.id, c.name)
        for c in Category.query.filter_by(deleted=False)
        .filter_by(user_id=current_user.id)
        .filter(Category.id != 100)
        .order_by("id")
    ]
    if form.validate_on_submit():
        available_amount = form.inicial_amount.data
        budget = Budget(
            name=form.name.data,
            inicial_amount=form.inicial_amount.data,
            user_id=current_user.id,
            available_amount=available_amount,
        )
        db.session.add(budget)
        db.session.commit()
        raw_string = form.category_list.data
        obj_list = raw_string.rsplit(" - ")
        obj_list.remove("")
        new_category_amount = 0
        for obj in obj_list:
            data = json.loads(obj)
            available_amount = data["threshold"]
            # Verifying amount for the default category
            new_category_amount = new_category_amount + float(available_amount)
            # Verifying limit for the budget
            if new_category_amount > budget.inicial_amount:
                form.category_list.data = ""
                flash(
                    f"Error in creating budget, the threshold of categories has to be less then the available amount of the budget",
                    "danger",
                )
                return render_template(
                    "new_budget.html",
                    form=form,
                    form_bc=form_bc,
                    title="Budget creation",
                )
            budget_category = Budget_category(
                threshold=data["threshold"],
                category_id=data["category_id"],
                budget_id=budget.id,
                available_amount=available_amount,
            )
            db.session.add(budget_category)
        db.session.commit()
        # Adding new category with leftovers of the other categories
        threshold = budget.available_amount - new_category_amount
        if threshold > 0:
            # print(budget, file=sys.stderr)
            default_category = Budget_category(
                threshold=threshold,
                category_id=100,
                budget_id=budget.id,
                available_amount=threshold,
            )
            db.session.add(default_category)
            db.session.commit()
        flash(f"Budget created!", "success")
        return redirect(url_for("budgets"))

    return render_template(
        "new_budget.html", form=form, form_bc=form_bc, title="Budget creation"
    )


@app.route("/budget/<budget_id>/update", methods=["GET", "POST"])
@login_required
def update_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    form = BudgetForm()
    form_bc = BudgetCategoryForm()
    form_bc.category_id.choices = [
        (c.id, c.name)
        for c in Category.query.filter_by(deleted=False)
        .filter(Category.id != 100)
        .order_by("id")
    ]
    if form.validate_on_submit():
        budget.name = form.name.data
        previous = budget.inicial_amount
        budget.inicial_amount = form.inicial_amount.data
        amount_dif = float(budget.inicial_amount) - previous
        budget.available_amount = budget.available_amount + amount_dif
        db.session.commit()
        new_category_amount = 0
        if len(form.category_list.data) > 0:
            raw_string = form.category_list.data
            obj_list = raw_string.rsplit(" - ")
            obj_list.remove("")
            for obj in obj_list:
                data = json.loads(obj)
                available_amount = data["threshold"]
                # Verifying amount for the default category
                new_category_amount = new_category_amount + float(available_amount)
                # Verifying limit for the budget
                if new_category_amount > budget.inicial_amount:
                    form.category_list.data = ""
                    flash(
                        f"Error in creating budget, the threshold of categories has to be less then the available amount of the budget",
                        "danger",
                    )
                    return render_template(
                        "new_budget.html",
                        form=form,
                        form_bc=form_bc,
                        title="Budget creation",
                    )
                budget_category = Budget_category(
                    threshold=data["threshold"],
                    category_id=data["category_id"],
                    budget_id=budget.id,
                    available_amount=available_amount,
                )
                db.session.add(budget_category)
            # Adding new category with leftovers of the other categories
            budget_categories = (
                Budget_category.query.filter(Budget_category.category_id != 100)
                .filter_by(budget_id=budget.id)
                .all()
            )
            threshold = 0
            for bc in budget_categories:
                threshold = threshold + float(bc.threshold)
            if threshold > 0:
                default_category = (
                    Budget_category.query.filter_by(budget_id=budget.id)
                    .filter_by(category_id=100)
                    .first()
                )
                default_category.threshold = budget.inicial_amount - threshold
                default_category.available_amount = (
                    default_category.available_amount - float(available_amount)
                )
                db.session.add(default_category)
                db.session.commit()
            flash(f"Budget updated!", "success")
            return redirect(url_for("budget", budget_id=budget.id))
        else:
            default_category = (
                Budget_category.query.filter_by(budget_id=budget.id)
                .filter_by(category_id=100)
                .first()
            )
            default_category.threshold = default_category.threshold + amount_dif
            default_category.available_amount = (
                default_category.available_amount + amount_dif
            )
            db.session.add(default_category)
            db.session.commit()
            flash(f"Budget updated!", "success")
            return redirect(url_for("budget", budget_id=budget.id))
    elif request.method == "GET":
        form.name.data = budget.name
        form.inicial_amount.data = budget.inicial_amount
        budget_id = budget.id
    return render_template(
        "new_budget.html",
        form=form,
        form_bc=form_bc,
        budget_id=budget_id,
        title="Update Budget",
    )


@app.route("/budget/<budget_id>/delete", methods=["POST"])
@login_required
def delete_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    budget_categories = Budget_category.query.filter_by(budget_id=budget.id).all()
    for category in budget_categories:
        db.session.delete(category)
    db.session.delete(budget)
    db.session.commit()
    flash(f"The budget has been deleted!", "success")
    return redirect(url_for("budgets"))


@app.route("/budget/<budget_id>/details", methods=["GET"])
@login_required
def budget_details(budget_id):
    budget = Budget.query.filter_by(id=budget_id).first()
    threshold_labels = []
    threshold_values = []
    available_labels = []
    available_values = []
    for c in budget.categories:
        category_db = Category.query.filter_by(id=c.category.id).first()
        threshold_labels.append(category_db.name)
        threshold_values.append(c.threshold)
        if c.available_amount != 0:
            available_labels.append(category_db.name)
            available_values.append(c.available_amount)

    return render_template(
        "budget_details.html",
        budget=budget,
        title=budget.name,
        max=17000,
        chartT=zip(threshold_values, threshold_labels, colors),
        chartA=zip(available_values, available_labels, colors),
    )


@app.route("/budget/<budget_id>/update/category/<category_id>", methods=["GET", "POST"])
@login_required
def update_budget_category(budget_id, category_id):
    budget_category = Budget_category.query.get_or_404(category_id)
    category = Category.query.filter_by(id=budget_category.category.id).first()
    category_name = category.name
    budget = Budget.query.get_or_404(budget_id)
    form = UpdateBudgetCategoryForm()
    previous = budget_category.used_amount
    if form.validate_on_submit():
        budget_category.used_amount = previous + float(form.used_amount.data)
        budget_category.available_amount = budget_category.available_amount - float(
            form.used_amount.data
        )
        db.session.add(budget_category)
        if form.used_amount.data != 0:
            budget.available_amount = budget.available_amount - float(
                form.used_amount.data
            )
            db.session.add(budget)
            if budget_category.category.id != 100:
                default_category = Budget_category.query.filter_by(
                    category_id=100
                ).first()
                default_category.available_amount = (
                    default_category.available_amount
                    - (budget_category.available_amount * -1)
                )
                default_category.threshold = default_category.threshold - (
                    budget_category.available_amount * -1
                )
                db.session.add(default_category)
        db.session.commit()
        flash(f"The category has been updated!", "success")
        return redirect(url_for("budget", budget_id=budget_id))
    elif request.method == "GET":
        form.used_amount.data = 0.0
    return render_template(
        "budget_category_update.html",
        previous=previous,
        category_name=category_name,
        form=form,
        category_id=category_id,
        budget_id=budget_id,
    )


@app.route("/budget/<budget_id>/update/category/<category_id>/delete", methods=["POST"])
@login_required
def delete_budget_category(budget_id, category_id):
    budget_category = Budget_category.query.get_or_404(category_id)
    budget = Budget.query.get_or_404(budget_id)
    default_category = Budget_category.query.filter_by(category_id=100).first()
    default_category.threshold = (
        default_category.threshold + budget_category.available_amount
    )
    default_category.available_amount = (
        default_category.available_amount + budget_category.available_amount
    )
    default_category.used_amount = (
        default_category.used_amount + budget_category.used_amount
    )
    db.session.add(default_category)
    db.session.add(budget)
    db.session.delete(budget_category)
    db.session.commit()
    flash(f"The category has been deleted!", "success")
    return redirect(url_for("budget", budget_id=budget_id))


# END Web routes

# API routes
@app.route("/api", methods=["GET"])
def hello_world():
    return jsonify({"message": "Hello world"})


@app.route("/user/register", methods=["GET"])
def regiter_user():
    user = User(saving_total=0, total_available_amount=0)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created successfully"})


@app.route("/api/user/", methods=["GET"])
def get_users():
    users = User.query.all()
    list = []
    for u in users:
        user = {
            "id": u.id,
            "saving_total": u.saving_total,
            "total_available_amount": u.total_available_amount,
        }
        list.append(u)
    return jsonify(list)


# END API routes
