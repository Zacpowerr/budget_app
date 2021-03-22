from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import (
    StringField,
    TextAreaField,
    DecimalField,
    SubmitField,
    PasswordField,
    BooleanField,
    SelectField,
)
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email
from budget_app.models import User


class RegisterForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=2, max=20)]
    )
    confirm_password = PasswordField(
        "Confirm password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "That username is taken, please choose a different one."
            )

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is taken, please choose a different one.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class UpdateAccountForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Update")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    "That username is taken, please choose a different one."
                )

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    "That email is taken, please choose a different one."
                )


class CategoryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=20)])
    description = TextAreaField("Description", validators=[Length(max=255)])
    submit = SubmitField("Submit")


class BudgetForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=20)])
    inicial_amount = DecimalField("Inicial amount", places=2, rounding=None)
    category_list = TextAreaField("Categories")
    submit = SubmitField("Submit")


class BudgetCategoryForm(FlaskForm):
    category_id = SelectField(u"Category", coerce=int)
    threshold = DecimalField("Threshold", places=2, rounding=None)
    submit = SubmitField("Submit")


class UpdateBudgetCategoryForm(FlaskForm):
    used_amount = DecimalField("Used amount", places=2, rounding=None)
    use_all = SubmitField("Use all")
    submit = SubmitField("Submit")
