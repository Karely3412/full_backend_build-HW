import psycopg2
from flask import Flask, jsonify, request


app = Flask(__name__)

conn = psycopg2.connect("dbname='be-cruda' host='localhost'")
cursor = conn.cursor()


def create_tables():
    print("Creating Tables...")

# WE HAVE TO DO ORGS FIRST BEACUSE WE NEED THE TABLE CREATED THAT HAS THE VALUE WE ARE GOING TO NEED WHEN WE REFERENCE A VALUE THAT IS IN THE TABLE WE NEED.  
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Organizations(
            org_id SERIAL PRIMARY KEY,
            name VARCHAR NOT NULL,
            phone VARCHAR,
            email VARCHAR,
            city VARCHAR,
            state VARCHAR,
            active smallint
        );
    
    """)

# REMEMBER WE HAVE TO 1. ADD THE FOREIN KEY & REFERENCE AT THE END 2. WE ALSO ADDED A CONSTRAINT AT THE END.. WHICH IS THE LAST TWO LINES OF SYNTAX AT THE END OF THE QUERY..
# ..THE CONSTRAINTS ARE, FOREIN KEY(ORG_ID) FOR THE COLUMN NAME & IN THAT COLUMN, REFERENCE WILL LOOK FOR THE TABLE AT THE COLUMN OF ORGANIZATIONS BY THE NAME THATS IN THE PARENTHESIS.    

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Students(
            student_id SERIAL PRIMARY KEY,
            first_name VARCHAR NOT NULL,
            last_name VARCHAR,
            email VARCHAR NOT NULL UNIQUE,
            phone VARCHAR,
            city VARCHAR,
            state VARCHAR,
            org_id INT, 
            active smallint,
            FOREIGN KEY(org_id) 
                REFERENCES Organizations (org_id)

        );
    
    """)

    conn.commit()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# CREATE - [C]RUDA

@app.route("/org/add", methods=["POST"])
def org_add():

    req_data = request.json if request.json else request.form

    if not req_data:
        return jsonify({'error': 'not data entered'}), 404

    name = req_data.get("name")
    phone = req_data.get("phone") 
    email = req_data.get("email")
    city = req_data.get("city") 
    state = req_data.get("state")     
    active = req_data.get("active")


    cursor.execute(
        "INSERT INTO Organizations (name, phone, email, city, state, active) VALUES(%s, %s, %s, %s, %s, %s)",
        [name, phone, email, city, state, active]) 
    conn.commit()
    return jsonify({"message":"Organization successfully ADDED"}), 201


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# CREATE - C[R]UDA

@app.route("/org/get", methods=["GET"])
def all_orgs():
    cursor.execute(
        "SELECT org_id, name, phone, city, state, active FROM Organizations WHERE active =1")
    results = cursor.fetchall()
    if not results:
        return jsonify({"message": "invalid input"}), 404
    else:
        orgs_result = []
        for result in results:
            results_dict = {
                'org_id': result[0],
                'name': result[1],
                'phone': result[2],
                'city': result[3],
                'state': result[4],
                'active': result[5]
            }
            orgs_result.append(results_dict)
        return jsonify(orgs_result), 200


@app.route("/org/active", methods=["GET"])
def all_active_orgs():
    cursor.execute(
        "SELECT * FROM Organizations WHERE active =1")
    results = cursor.fetchall()
    if not results:
        return jsonify({"error": "invalid input"}), 404
    else:
        orgs_result = []
        for result in results:
            results_dict = {
                'org_id': result[0],
                'name': result[1],
                'phone': result[2],
                'city': result[3],
                'state': result[4],
                'active': result[5]
            }
            orgs_result.append(results_dict)
        return jsonify(orgs_result), 200


@app.route("/org/get/<org_id>", methods=["GET"])
def get_org_by_id(org_id):
    cursor.execute("SELECT org_id, name, phone, city, state, active FROM Organizations WHERE org_id = %s;",
                   [org_id])
    result = cursor.fetchone()
    if not result:
        return jsonify("organization does NOT exist"), 404
    else:
        results_dict = {
            'org_id': result[0],
            'name': result[1],
            'phone': result[2],
            'city': result[3],
            'state': result[4],
            'active': result[5]
        }
        return jsonify(results_dict), 200



@app.route("/org/activate/<org_id>", methods=["PATCH"])
def get_activate_org(org_id):
    cursor.execute(
        "UPDATE Organizations SET active = 1 WHERE org_id = %s", [org_id])
    conn.commit()
    return jsonify({"message": "organization successfully ACTIVATED"}), 200


@app.route("/org/deactivate/<org_id>", methods=["PATCH"])
def deactivate_org(org_id):
    cursor.execute("UPDATE Organizations SET active =0 WHERE org_id =%s", [org_id])
    conn.commit()
    return jsonify({"message": "organization successfully DEACTIVATED"}), 200


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# CREATE - CRU[D]A

@app.route('/org/update/<org_id>', methods=["PATCH"]) 
def org_status(org_id):  
    cursor.execute("SELECT name, phone, email, city, state, active FROM Organizations WHERE org_id =%s;", [org_id]) 
    result = cursor.fetchone() 

    if not result: 
        return jsonify({"error": "Organization id does not exists"}), 404 

    result_dict = {  
        "name": result[0], 
        "phone": result[1], 
        "email": result[2], 
        "city": result[3], 
        "state": result[4], 
        "active": result[5] } 
    conn.commit() 
    

    req_data = request.json if request.json else request.form

    for key, val in req_data.items():
        if val:
            result_dict[key] = val

    cursor.execute(
        '''UPDATE Organizations SET 
        name = %s, 
        phone = %s, 
        email = %s, 
        city = %s, 
        state = %s, 
        active = %s 
    
        WHERE org_id = %s
    ''',
    [
        result_dict['name'],
        result_dict['phone'],
        result_dict['email'],
        result_dict['city'],
        result_dict['state'],
        result_dict['active'],
        org_id

    ])
    conn.commit()
    return jsonify(result_dict), 201


#___________________________________________________________________
# CREATE - [C]RUDA

@app.route("/student/add", methods=["POST"])
def student_add():

    req_data = request.json if request.json else request.form
    
    if not req_data:
        return jsonify({'error': 'no data entered'}), 404

    first_name = req_data.get("first_name")
    last_name = req_data.get("last_name") 
    email = req_data.get("email")
    phone = req_data.get("phone") 
    city = req_data.get("city") 
    state = req_data.get("state")     
    org_id = req_data.get("org_id") 
    active = req_data.get("active")



    # print(req_data)
    cursor.execute(
        "INSERT INTO Students(first_name, last_name, email, phone, city, state, org_id, active) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",[first_name, last_name, email, phone, city, state, org_id, active]) 
    
    conn.commit()
    return jsonify({"message":"student successfully ADDED"}), 201

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# READ - C[R]UDA

@app.route('/students/get')
def get_all_students():
    cursor.execute("SELECT * FROM Students")
    results = cursor.fetchall()

    if results == "":
        return jsonify({"error": "invalid input"}), 404
    else:
        result_list = []
        for result in results:
            results_dict = {
                "student_id": result[0],
                "first_name": result[1],
                "last_name": result[2],
                "email": result[3],
                "phone": result[4],
                "city": result[5],
                "state": result[6],
                "org_id": result[7],
                "active": result[8]
            }
            result_list.append(results_dict)

    conn.commit()
    return jsonify(result_list)


@app.route('/students/active', methods=["PATCH"])
def get_active_students():
    cursor.execute("SELECT * FROM Students WHERE active=1;")
    results = cursor.fetchall()

    if results == "":
        return jsonify({"error": "invalid input"}), 404
    else:
        result_list = []
        for result in results:
            results_dict = {
                "student_id": result[0],
                "first_name": result[1],
                "last_name": result[2],
                "email": result[3],
                "phone": result[4],
                "city": result[5],
                "state": result[6],
                "org_id": result[7],
                "active": result[8]
            }
            result_list.append(results_dict)


    conn.commit()
    return result_list



@app.route('/student/student_id/<student_id>', methods=["GET"]) 
def get_student_id(student_id): 
    
    cursor.execute("SELECT * FROM Students WHERE student_id=%s;", [student_id]) 
    result = cursor.fetchone() 
    if result is None: 
        return jsonify({"error": "invalid input"}), 404 
        
    result_dict = { 
        "student_id": result[0], 
        "first_name": result[1], 
        "last_name": result[2], 
        "email": result[3], 
        "phone": result[4], 
        "city": result[5], 
        "state": result[6], 
        "org_id": result[7], 
        "active": result[8] } 
    conn.commit() 
    return jsonify(result_dict)


@app.route('/student/email/<email>', methods=["GET"]) 
def get_student_email(email): 
    
    cursor.execute("SELECT * FROM Students WHERE email=%s;", [email]) 
    result = cursor.fetchone() 
    if result is "": 
        return jsonify({"error": "invalid input"}), 404 
        
    result_dict = { 
        "student_id": result[0], 
        "first_name": result[1], 
        "last_name": result[2], 
        "email": result[3], 
        "phone": result[4], 
        "city": result[5], 
        "state": result[6], 
        "org_id": result[7], 
        "active": result[8] } 
    conn.commit() 
    return jsonify(result_dict)

# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# # UPDATE - CR[U]DA


@app.route('/student/update/<student_id>', methods=["PATCH"]) 
def update_stud_status(student_id):  
    cursor.execute("SELECT first_name, last_name, email, phone, city, state, org_id, active FROM Students WHERE student_id =%s;", [student_id]) 
    result = cursor.fetchone() 
    if result is None: 
        return jsonify({"error": "invalid input"}), 404 

    result_dict = {  
        "first_name": result[0], 
        "last_name": result[1], 
        "email": result[2], 
        "phone": result[3], 
        "city": result[4], 
        "state": result[5], 
        "org_id": result[6], 
        "active": result[7] } 
    conn.commit() 
    # return jsonify(result_dict)

    req_data = request.json if request.json else request.form

    for key, val in req_data.items():
        if val:
            result_dict[key] = val

    cursor.execute(
        '''UPDATE Students SET 
        first_name = %s, 
        last_name = %s, 
        email = %s, 
        phone = %s, 
        city = %s, 
        state = %s, 
        org_id = %s, 
        active = %s 
    
        WHERE Student_id = %s
    ''',
    [
        result_dict['first_name'],
        result_dict['last_name'],
        result_dict['email'],
        result_dict['phone'],
        result_dict['city'],
        result_dict['state'],
        result_dict['org_id'],
        result_dict['active'],
        student_id

    ])
    conn.commit()
    return jsonify(result_dict), 201


# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# # ACTIVATE - CRUD[A]


@app.route('/student/activate/<student_id>', methods=["PATCH"])
def student_activation(student_id):
    cursor.execute("UPDATE Students SET active = 1 WHERE student_id = %s", [student_id])
    conn.commit() 
    return jsonify({"message": "Activated"}), 200


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# DEACTIVATE - CRU[D]A


@app.route('/student/deactivate/<student_id>', methods=["PATCH"])
def deactivate_student(student_id):
    cursor.execute("UPDATE Students SET active = 0 WHERE student_id = %s", [student_id])
    conn.commit()
    return jsonify({"message": "Deactivated"}), 200


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# DEACTIVATE - CRU[D]A

@app.route('/student/delete/<student_id>', methods=["DELETE"])
def delete_student(student_id):
    cursor.execute("DELETE FROM Students WHERE student_id = %s", [student_id])
    conn.commit()
    return jsonify({"message": "Student DELETED"}), 200



if __name__ == "__main__":
    create_tables()
    app.run(port="8082", debug=True )




