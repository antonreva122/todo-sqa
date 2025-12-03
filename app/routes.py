from app import db
from flask import render_template, request, redirect, url_for, flash, abort
from app.forms import LoginForm, RegistrationForm
from app.models import User, Todo
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from urllib.parse import urlsplit


def get_user_task_or_404(task_id):
    """
    Retrieve a task by ID and verify it belongs to the current user.
    Returns the task if authorized, otherwise aborts with 404.
    
    Args:
        task_id: The ID of the task to retrieve
        
    Returns:
        Todo: The task object if authorized
        
    Raises:
        404 error: If task doesn't exist or doesn't belong to current user
    """
    task = db.session.get(Todo, task_id)
    if task is None or task.user_id != current_user.id:
        abort(404)
    return task


def init_routes(app):
    @app.route("/")
    @login_required
    def index():
        todo_count = Todo.query.count()
        return render_template("index.html", todo_count=todo_count)

    @app.route("/tasks")
    @login_required
    def all_tasks():
        todos = Todo.query.filter_by(user_id=current_user.id).all()
        return render_template("tasks.html", todos=todos)

    @app.route("/task/<int:task_id>")
    @login_required
    def task(task_id):
        task = get_user_task_or_404(task_id)
        return render_template("task.html", task=task)

    @app.route("/edit-task/<int:task_id>", methods=["GET", "POST"])
    @login_required
    def edit_task(task_id):
        task = get_user_task_or_404(task_id)
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            if not title:
                flash("Title is required")
                return redirect(url_for("edit_task", task_id=task_id))
            if len(title) > 255:
                flash("Title must be less than 255 characters")
                return redirect(url_for("edit_task", task_id=task_id))
            if len(description) > 2000:
                flash("Description must be less than 2000 characters")
                return redirect(url_for("edit_task", task_id=task_id))
            task.title = title
            task.description = description
            db.session.commit()
            flash(f"Task '{task.title}' updated successfully")
            return redirect(url_for("task", task_id=task_id))
        return render_template("task_form.html", task=task)

    @app.route("/new-task", methods=["GET", "POST"])
    @login_required
    def create_task():
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            if not title:
                flash("Title is required")
                return redirect(url_for("create_task"))
            if len(title) > 255:
                flash("Title must be less than 255 characters")
                return redirect(url_for("create_task"))
            if len(description) > 2000:
                flash("Description must be less than 2000 characters")
                return redirect(url_for("create_task"))
            task = Todo(
                title=title,
                description=description,
                user=current_user,
            )
            db.session.add(task)
            db.session.commit()
            flash(f"Task '{task.title}' created successfully")
            return redirect(url_for("task", task_id=task.id))
        return render_template("task_form.html", task=None)

    @app.route("/delete-task/<int:task_id>", methods=["POST"])
    @login_required
    def delete_task(task_id):
        task = get_user_task_or_404(task_id)
        task_title = task.title
        db.session.delete(task)
        db.session.commit()
        flash(f"Task '{task_title}' deleted successfully")
        return redirect(url_for("all_tasks"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        form = LoginForm()
        if form.validate_on_submit():
            user = db.session.scalar(
                sa.select(User).where(User.username == form.username.data)
            )
            if user is None or not user.get_password(form.password.data):
                flash("Invalid username or password")
                return redirect(url_for("login"))
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get("next")
            if not next_page or urlsplit(next_page).netloc != "":
                next_page = url_for("index")
            return redirect(next_page)
        return render_template("login.html", form=form)

    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for("index"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Congratulations, your registration was successful")
            return redirect(url_for("login"))
        return render_template("register.html", form=form)

    @app.route("/task/<int:task_id>/toggle", methods=["POST"])
    @login_required
    def toggle_task_completion(task_id):
        task = get_user_task_or_404(task_id)
        task.completed = not task.completed
        db.session.commit()

        if task.completed:
            flash(f"Task '{task.title}' marked as completed.")
        else:
            flash(f"Task '{task.title}' reopened.")
        return redirect(url_for("all_tasks"))
