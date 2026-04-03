from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import Task

tasks_bp= Blueprint('task', __name__)

@tasks_bp.route("/")
def view_tasts():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    tasks= Task.query.all()
    return render_template('tasks.html', tasks=tasks)

@tasks_bp.route("/add", methods=["POST"])
def tasks_add():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    title= request.form.get('title')
    if title:
        new_task= Task(title=title, status='Panding')
        db.session.add(new_task)
        db.session.commit()
        flash('task added succesfully', 'success')

    return redirect(url_for('tasks.view_tasks'))    

@tasks_bp("/toggle/<int:task_id>", methods=['POST'])
def toggle_status(task_id):
    task= Task.query.get(task_id)
    if task:
        if task.status=='Panding':
            task.status='working'
        elif task.status=='working':
            task.status='Done'
        else:
            task.status='Panding'
        db.session.commit()

    return redirect(url_for('task.view_tasks'))
        

@tasks_bp("/clear")
def clear_task():
    Task.query.delete()
    db.session.commit()
    flash('All tasks cleared', 'info')
    return redirect(url_for('task.view_tasks'))
    




