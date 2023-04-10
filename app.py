from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)
conn = mysql.connector.connect(
    host="localhost",
    user= "root",
    password= "mysql2023",
    database = "my_database"
)

@app.route('/userpage/<int:user_id>/<string:username>', methods=['POST'])
def add_book(user_id, username):
    title = request.form['title']
    current_page=request.form['current_page']
    cursor = conn.cursor()
    query = "INSERT INTO books(title, current_page) VALUES (%s, %s)"
    values = (title, current_page)
    print("Query:", query)
    print("Values:", values)
    cursor.execute(query, values)
    conn.commit()
    book_id = cursor.lastrowid

    #Insert into other table using the last inserted book_id
    query2 = "INSERT INTO book_user(user_id, book_id) VALUES (%s, %s)"
    values2 = (user_id, book_id)
    cursor.execute(query2, values2)
    conn.commit()

    return redirect(url_for('userpage', user_id=user_id, username = username))

@app.route("/home")
def home():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    return render_template("home.html", data=data)

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == "POST":
        username= request.form['username']
        password = request.form['password']

        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        # Check if the user exists and the password is correct
        if user is None or password != user[2]:
            return render_template("login.html", error = "Invalid !")
        else:
            user_id = user[0]
            return redirect(url_for('userpage', user_id=user_id, username = user[1]))
    else:
        return render_template("login.html")
    
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        cursor = conn.cursor()
        query = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
        values = (username,password,email)
        try:
            cursor.execute(query, values)
            conn.commit()
            print(conn)
        except:
            return render_template('signup.html', error = "Error while inserting to table(duplication can be reason)")

        return render_template('home.html')
    else:
        return render_template('signup.html')
    
@app.route('/userpage/<int:user_id>/<string:username>', methods=['GET', 'POST'])
def userpage(user_id,username):
    cursor = conn.cursor()
    cursor.execute("Select * From books JOIN book_user ON books.id = book_user.book_id WHERE book_user.user_id = %s", (user_id,)) 
    books = cursor.fetchall()
    return render_template('userpage.html', user_id=user_id, username = username, books= books)


if __name__ == "__main__":
    app.run(debug=True)