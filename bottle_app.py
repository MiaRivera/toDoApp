from bottle import default_app, route, template, request, redirect
import sqlite3
from datetime import date

"""connect to database"""
db = sqlite3.connect("./ToDoApp/task.db")
c = db.cursor()

"""variable to store which user is currently logged in"""
currentUser = ""

@route('/')
def login():
    return template("login.html")

@route('/validateLogin', method='POST')
def checkLogin():
    global currentUser

    """get login information from form"""
    user = request.forms.get("name")
    password = request.forms.get("password")

    """sqlite query for table entry with matching name and password"""
    c.execute("SELECT * FROM user WHERE name = ? AND password = ?", (user, password))
    result = c.fetchone()

    """check if query returned a match"""
    if result is not None:
        """save matching userID as the currentUser, and redirect to home page"""
        currentUser = result[0]
        return redirect('/home')
    else:
        """no match found, send to unsuccessful login page"""
        return template('badLogin.html')

"""home page: displays today's date and tasks that are due today"""
@route('/home')
def home():
    today = date.today().strftime('%Y-%m-%d')
    global currentUser
    return template("index.html", today = today, user = currentUser)

"""updates task completion status in database"""
@route('/updateCompletionStatus', method='POST')
def updateTaskStatuses():
    """grab all tasks that have been checked, updates their completion status in db"""
    tasks = request.forms.getlist('task')
    for record in tasks:
        c.execute("UPDATE task SET isComplete = ? WHERE ID = ?", (1, record))
    db.commit()

    return redirect('/home')

"""contains form to create new task"""
@route('/createTask')
def createTask():
    return template("createNewTask.html")

"""creates new task table entry in database from form information"""
@route('/addTask', method='POST')
def addTask():
    global currentUser
    title = request.forms.get("title")
    date = request.forms.get("dueDate")

    c.execute("INSERT INTO task VALUES(null, ?, ?, ?, ?)", (currentUser, date, title, 0))
    db.commit()
    redirect("/createTask")

"""contains form to choose a task to delete"""
@route('/deleteTask')
def deleteForm():
    global currentUser
    return template("deleteTask.html", c = c, user = currentUser)

"""deletes task from database"""
@route('/delete', method='POST')
def deleteTask():
    taskID = request.forms.get("task")

    c.execute("DELETE FROM task WHERE ID = ?", (taskID))
    db.commit()
    redirect("/deleteTask")

"""contains form to choose which task to edit"""
@route('/editTask')
def chooseTask():
    global currentUser
    return template("editTask.html", c = c, user = currentUser)

"""grabs chosen task to edit, gives form to edit task details"""
@route('/edit', method='POST')
def editTask():
    taskID = request.forms.get("task")
    return template("editForm.html", taskID = taskID, c = c)

"""updates task in database from form values"""
@route('/edited', method='POST')
def update():
    id = request.forms.get("id")
    title = request.forms.get("title")
    date = request.forms.get("dueDate")
    status = request.forms.get("status")

    c.execute("UPDATE task SET dueDate = ?, title = ?, isComplete = ? WHERE ID = ?", (date, title, status, id))
    db.commit()
    redirect('/editTask')

"""allows user to look at home page for different dates"""
@route('/calendar')
def viewCalendar():
    return template("calendar.html")

"""gets user selected date from form, creates home page for selected date"""
@route('/changeDate', method='POST')
def changeDate():
    date = request.forms.get("date")
    return template("index.html", today = date)

"""contains form to create a new user table entry in database"""
@route('/newUser')
def newUser():
    return template("newUser.html")

"""creates new user in database"""
@route('/createUser', method='POST')
def createUser():
    name = request.forms.get("name")
    password = request.forms.get("password")

    c.execute("INSERT INTO user VALUES(null, ?, ?)", (name, password))

    global currentUser
    currentUser = c.lastrowid
    return redirect('/home')

"""logs user out, redirects to login page"""
@route('/logout')
def logout():
    global currentUser
    currentUser = ""
    return redirect('/')


application = default_app()

