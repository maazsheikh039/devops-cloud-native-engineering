"""TaskBoard - a tiny web app used as the system under test."""
import os
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from jinja2 import DictLoader

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "lab-only-secret-key")

USERS = {"admin": "s3cret"}
DEFAULT_TASKS = [
    {"title": "Patch web servers", "priority": "high"},
    {"title": "Rotate log files", "priority": "low"},
]

TEMPLATES = {
    "base.html": """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>TaskBoard - {% block title %}{% endblock %}</title></head>
<body>
<nav id="nav">
  <a id="home-link" href="/">Home</a>
  {% if session.get("user") %}
    <a id="tasks-link" href="/tasks">Tasks</a>
    <a id="logout" href="/logout">Logout</a>
    <span id="current-user">{{ session["user"] }}</span>
  {% else %}
    <a id="login-link" href="/login">Login</a>
  {% endif %}
</nav>
<main>{% block content %}{% endblock %}</main>
</body>
</html>""",
    "home.html": """{% extends "base.html" %}
{% block title %}Home{% endblock %}
{% block content %}
<h1>Welcome to TaskBoard</h1>
<p class="lead">A tiny task tracker used as the system under test.</p>
{% endblock %}""",
    "login.html": """{% extends "base.html" %}
{% block title %}Login{% endblock %}
{% block content %}
<h1>Sign in</h1>
{% if error %}<div class="error" role="alert">{{ error }}</div>{% endif %}
<form id="login-form" method="post" action="/login">
  <label for="username">Username</label>
  <input id="username" name="username" type="text">
  <label for="password">Password</label>
  <input id="password" name="password" type="password">
  <button id="login-btn" class="btn btn-primary" type="submit">Sign in</button>
</form>
{% endblock %}""",
    "tasks.html": """{% extends "base.html" %}
{% block title %}Tasks{% endblock %}
{% block content %}
<h1>My Tasks</h1>
{% if error %}<div class="error" role="alert">{{ error }}</div>{% endif %}
<form id="add-form" method="post" action="/tasks">
  <input id="task-title" name="title" type="text" placeholder="Task title">
  <select id="priority" name="priority">
    <option value="low">Low</option>
    <option value="medium" selected>Medium</option>
    <option value="high">High</option>
  </select>
  <button id="add-task" type="submit">Add task</button>
</form>
<table id="task-table">
  <thead><tr><th>Title</th><th>Priority</th></tr></thead>
  <tbody>
  {% for t in tasks %}
    <tr class="task-row"><td class="task-title">{{ t.title }}</td><td class="task-priority">{{ t.priority }}</td></tr>
  {% else %}
    <tr id="empty-row"><td colspan="2">No tasks</td></tr>
  {% endfor %}
  </tbody>
</table>
<button id="load-stats" type="button">Load statistics</button>
<div id="stats"></div>
<form id="clear-form" method="post" action="/tasks/clear">
  <button id="clear-all" type="button">Delete all tasks</button>
</form>
<script>
document.getElementById("load-stats").addEventListener("click", function () {
  var box = document.getElementById("stats");
  box.textContent = "Loading...";
  setTimeout(function () {
    fetch("/api/stats").then(function (r) { return r.json(); }).then(function (d) {
      box.innerHTML = 'Total tasks: <span id="stats-total">' + d.total +
        '</span>, high priority: <span id="stats-high">' + d.high + '</span>';
    });
  }, 2500);
});
document.getElementById("clear-all").addEventListener("click", function () {
  if (confirm("Delete all tasks?")) {
    document.getElementById("clear-form").submit();
  }
});
</script>
{% endblock %}""",
}

app.jinja_loader = DictLoader(TEMPLATES)


@app.route("/healthz")
def healthz():
  return "ok"


@app.route("/")
def home():
  return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
  error = None
  if request.method == "POST":
    user = request.form.get("username", "")
    pw = request.form.get("password", "")
    if pw and USERS.get(user) == pw:
      session.clear()
      session["user"] = user
      session["tasks"] = [dict(t) for t in DEFAULT_TASKS]
      return redirect(url_for("tasks"))
    error = "Invalid username or password"
  return render_template("login.html", error=error)


@app.route("/logout")
def logout():
  session.clear()
  return redirect(url_for("home"))


@app.route("/tasks", methods=["GET", "POST"])
def tasks():
  if "user" not in session:
    return redirect(url_for("login"))
  error = None
  items = session.get("tasks", [])
  if request.method == "POST":
    title = request.form.get("title", "").strip()
    priority = request.form.get("priority", "medium")
    if not title:
      error = "Title is required"
    else:
      items.append({"title": title, "priority": priority})
      session["tasks"] = items
      return redirect(url_for("tasks"))
  return render_template("tasks.html", tasks=items, error=error)


@app.route("/tasks/clear", methods=["POST"])
def clear_tasks():
  if "user" not in session:
    return redirect(url_for("login"))
  session["tasks"] = []
  return redirect(url_for("tasks"))


@app.route("/api/stats")
def stats():
  if "user" not in session:
    return jsonify(error="unauthorised"), 401
  items = session.get("tasks", [])
  return jsonify(total=len(items), high=sum(1 for t in items if t["priority"] == "high"))
