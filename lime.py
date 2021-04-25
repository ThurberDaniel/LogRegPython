from flask import Flask, render_template, redirect, request, session, flash
from connect5000 import connectToMySQL
import re
from flask_bcrypt import Bcrypt

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "lemonlimeapplesweets"

########## SHOWS MAIN PAGE #########################
@app.route("/")
def index():
    mysql = connectToMySQL('dojo_sch')
    # friends = mysql.query_db('SELECT * FROM dojo_table;')
    return render_template("main.html")
################## END OF SHOW PAGE ################################

############## ADD USER _ INPUT VALIDATION ##########################################
@app.route("/add", methods=["POST", "GET"])
def input():
    is_valid = True
    if len(request.form['reg_fname']) < 2:
        flash("First Name should be at least 2 characters")
    if len(request.form['reg_lname']) < 2:
        flash("Last Name should be at least 2 characters")
    if len(request.form['reg_email']) < 5:
        flash("Please enter a valid email")
    if len(request.form['reg_pass']) < 5:
        flash("Password should be at least 5 characters")
    if request.form['reg_pass'] != request.form['con_pass']:
        flash("Password do not match- Please try again")

    if not EMAIL_REGEX.match(request.form['reg_email']):    # test whether a field matches the pattern
        flash("Invalid email address!")
        #$$$$$$$$$$$$$$$ CONNECTS AND CHECKS FOR EMAIL VALIDATION#$$$$$$$$$$$$$$$$$$
    database = connectToMySQL('dojo_sch')
    query = "SELECT * FROM dojo_table WHERE email= %(ema)s;"
    data = {
            'ema' : request.form['reg_email'],
        }
    result = database.query_db(query, data)
    if len(result)>0:  #IF A USER THAT ALREADY EXIST THEN FLASH MSG **** DO NOT ENTER ******
        flash("Email already in use - Please try again")
    if not '_flashes' in session.keys(): #IF THERE ARE NO FLASH MSG THEN PROCESS TO PUT INFO INTO DB
        flash("Successfully Added",)
        database = connectToMySQL('dojo_sch')
        pw_hash = bcrypt.generate_password_hash(request.form['reg_pass'])
        print(pw_hash)
        query = "INSERT INTO dojo_table(first_name, last_name, email, password)VALUES(%(fn)s,%(ln)s,%(em)s,%(pass)s);"
        qwerty = {
                'fn' : request.form['reg_fname'],
                'ln' : request.form['reg_lname'],
                'em' : request.form['reg_email'],
                'pass': pw_hash,
        }
        info=database.query_db(query,qwerty)
        print(info)
        queryDB = "SELECT * FROM dojo_table WHERE email = %(eml)s;" #ROADMAP INTO THE EMAIL IN THE DB

        dataDB = {
            "eml" : request.form['reg_email'],
        }
        db = connectToMySQL('dojo_sch') # linking db 
        show = db.query_db(queryDB,dataDB)
        session['userid'] = show[0]['id_track']
        session['fn'] = show[0]['first_name']


        return redirect("/winner")
    else:
        return redirect("/")
################# END OF ADD USER W/ VALIDATION #######################################


######### HTML SHOW PAGE WITH DB INFORMATION #####################
@app.route("/winner", methods=["GET"] )
def so1o():
    if  not "userid" in session:
        return redirect("/logout")
    return render_template('show.html')
###################### END OF SHOW PAGE#######################



#LOG IN ###############################################
@app.route('/WelcomeBack', methods=['POST'])
def login():   # see if the username provided exists in the database
    mysql = connectToMySQL("dojo_sch")
    query = "SELECT * FROM dojo_table WHERE email = %(ema)s;"
    data = {
        "ema" : request.form["log_email"],
        }
    result = mysql.query_db(query, data)
    print("*********************^%$#$%^&^%$#$%^&*^%$#")
    if len(result) > 0:
        if not request.form["log_pass"] =="":
            pw_hash = bcrypt.generate_password_hash(request.form['log_pass'])
            print (pw_hash)
            if bcrypt.check_password_hash(result[0]['password'], request.form['log_pass']):
                # if we get True after checking the password, we may put the user id in session
                session['userid'] = result[0]['id_track']
                # never render on a post, always redirect!
                return redirect('/winner')

    flash("You could not be logged in - Try Again!")
    return redirect("/")


# LOGOUT USER /// CLEAR SESSION
@app.route('/logout',methods=['GET'])
def logout(): 
    session.clear()
    flash("You have been logged out - Please return soon!")
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)





