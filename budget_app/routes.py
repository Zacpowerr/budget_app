from flask import request, render_template, url_for, flash, redirect, jsonify
from budget_app import app, db, bcrypt
from budget_app.models import User, Category, Budget, Budget_category
from budget_app.forms import CategoryForm, RegisterForm, LoginForm, UpdateAccountForm, BudgetForm, BudgetCategoryForm
from flask_login import login_user, current_user, logout_user, login_required
import json


# Web routes
@app.route('/home')
@app.route('/')
def home():
     return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')
# Authentication routes
@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegisterForm()
    if form.validate_on_submit():
         hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
         user = User(username=form.username.data,email=form.email.data,password=hashed_password)
         db.session.add(user)
         db.session.commit()
         flash(f'Account created! go ahead and login with you new account.','success')
         return redirect(url_for('login'))
    return render_template('auth/register.html',form=form,title='Register')

@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form =LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check your email and password','danger')
    return render_template('auth/login.html',form=form,title='Login')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

#END Authentication routes
@app.route('/account',methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!','success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static',filename='profile_pics/avatarDefault.png')
    return render_template('account.html',title='Account',form=form,image_file=image_file)


@app.route('/categories')
@login_required
def categories():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories, title="Categories")


@app.route('/category/<category_id>',methods=['GET','POST'])
@login_required
def category(category_id):
    category = Category.query.get_or_404(category_id)
    return render_template('category.html',category=category, title=category.name)

@app.route('/category/new',methods=['GET','POST'])
@login_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name = form.name.data,description = form.description.data)
        db.session.add(category)
        db.session.commit()
        flash(f'Category {form.name.data} created!','success')
        return redirect(url_for('categories'))

    return render_template('new_category.html', form=form, title="New Category", legend='New Category')

@app.route('/category/<category_id>/update',methods=['GET','POST'])
@login_required
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm()
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        db.session.commit()
        flash(f'The category has been updated!','success')
        return redirect(url_for('category',category_id=category.id))
    elif request.method == 'GET':
        form.name.data = category.name
        form.description.data = category.description
    return render_template('new_category.html',category=category, form=form, title='Update Category', legend='Update category')

@app.route('/category/<category_id>/delete',methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash(f'The category has been deleted!','success')
    return redirect(url_for('categories'))

@app.route('/users')
def users():
    return render_template('underconstruction.html',title='Under Construction')

@app.route('/budgets')
@login_required
def budgets():
    budgets = Budget.query.all()
    for budget in budgets:
        budget.amount_available()
    return render_template('budgets.html',title='Budgets',budgets=budgets)

@app.route('/budget/new',methods=['GET','POST'])
@login_required
def new_budget():
    form = BudgetForm()
    form_bc = BudgetCategoryForm()
    form_bc.category_id.choices = [(c.id, c.name) for c in Category.query.order_by('name')]
    if form.validate_on_submit():
        budget = Budget(name=form.name.data,inicial_amount=form.inicial_amount.data,user_id=current_user.id)
        db.session.add(budget)
        db.session.commit()
        raw_string = form.category_list.data 
        obj_list = raw_string.rsplit(" - ")
        obj_list.remove("")
        for obj in obj_list:
            data = json.loads(obj)
            budget_category = Budget_category(threshold=data['threshold'],used_amount=data['used_amount'],category_id=data['category_id'],budget_id=budget.id)
            db.session.add(budget_category)
        db.session.commit()
        flash(f'Budget created!','success')
        return redirect(url_for('budgets'))

    return render_template('new_budget.html',form=form, form_bc=form_bc, title='Budget creation')

# END Web routes

# API routes
@app.route('/api',methods = ['GET'])
def hello_world():
    return jsonify({'message':'Hello world'})


@app.route('/user/register',methods=['GET'])
def regiter_user():
    user = User(saving_total=0,total_available_amount=0)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'})

@app.route('/api/user/',methods=['GET'])
def get_users():
    users = User.query.all()
    list = []
    for user in users:
        u = {
            'id':user.id,
            'saving_total': user.saving_total,
            'total_available_amount':user.total_available_amount
            }
        list.append(u)
    return jsonify(list)

# END API routes