from pymongo import MongoClient
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
import json
import uuid
import time

# Connect to our local MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Choose database
db = client['DSMarkets']

# Choose collections
users_db = db['Users']
products_db = db['Products']

# Initialize cart
cart = {"products": [], "total_cost": 0}

# Initiate Flask App
app = Flask(__name__)

# Initialize dictionary for user login sessions
users_sessions = {}

# Create function that generates a unique id for a user's login
# The keys of users_sessions will be the unique user_uuid
# The values will be a tuple with user's email and time of login
def create_session(email):
    user_uuid = str(uuid.uuid1())
    users_sessions[user_uuid] = (email, time.time())
    return user_uuid  

# Create function that validates if a user is logged in
# by checking if user_uuid is in users_sessions
def is_session_valid(user_uuid):
    return user_uuid in users_sessions

# Εγγραφή χρηστών στο σύστημα
@app.route('/register', methods=['POST'])
def register_user():
    # Request JSON data
    data = None
    # Load request data
    try:
        data = json.loads(request.data)
    # In case of an error show error message in console
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    # Check if data is empty
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    # Check if email or name or password are absent
    if not "email" in data or not "name" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    # Έλεγχος δεδομένων email / name / password
    # Αν δεν υπάρχει user με το email που έχει δοθεί. 
    if users_db.find({"email": data['email']}).count() == 0:
        users_db.insert_one({"email": data['email'], "name": data['name'], "password": data['password'], "category": "simple user", "orderHistory": []})
        # Μήνυμα επιτυχίας
        return Response(data['name']+" was successfully added to the database", status=200, mimetype='application/json')
    # Διαφορετικά, αν υπάρχει ήδη κάποιος χρήστης με αυτό το email.
    else:
        # Μήνυμα λάθους (Υπάρχει ήδη κάποιος χρήστης με αυτό το email)
        return Response("A user with the given email already exists in the database", status=400, mimetype='application/json')

# Σύνδεση απλών χρηστών στο σύστημα
@app.route('/login', methods=['POST'])
def login_user():
    # Request JSON data
    data = None
    # Load request data
    try:
        data = json.loads(request.data)
    # In case of an error show error message in console
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    # Check if data is empty
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    # Check if email or password are absent
    if not "email" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    # Έλεγχος δεδομένων username / password
    # Αν η αυθεντικοποίηση είναι επιτυχής. 
    if users_db.find({"$and": [{"email": {"$eq": data['email']}}, {"password": {"$eq": data['password']}}]}).count() == 1:
        users_sessions.clear()
        user_uuid = create_session(data['email'])
        res = {"uuid": user_uuid, "email": data['email']}
        # Μήνυμα επιτυχίας
        return Response("Login was successful\n\n"+json.dumps(res), status=200, mimetype='application/json')
    # Διαφορετικά, αν η αυθεντικοποίηση είναι ανεπιτυχής.
    else:
        # Μήνυμα λάθους (Λάθος username ή password)
        return Response("Wrong username or password.", status=400, mimetype='application/json')
    

# Αναζήτηση ονόματος προϊόντος
@app.route('/search-pname', methods=['GET'])
def search_p_name():
    # Αποθηκεύουμε το id της αυθεντικοποίησης και το argument του χρήστη
    auth_id = request.headers.get('authorization')
    p_name = request.args.get('name')

    # Έλεγχος αν ο χρήστης εισήγαγε κάποιο argument
    if p_name == None:
        return Response("Bad request", status=500, mimetype='application/json')
    # Έλεγχος
    if(is_session_valid(auth_id)):
        user_email = users_sessions[auth_id][0]
        user_cat = users_db.find_one({"email": user_email})

        if(user_cat['category'] == "simple user"):
            res = products_db.find({"name": p_name})
            if res.count() != 0:
                products = []
                for product in res:
                    product['_id'] = None
                    products.append(product)
                
                # Ταξινόμηση πίνακα με βάση το όνομα προϊόντος με αύξουσα σειρά
                products = sorted(products, key=lambda prod: prod["name"])
                # Η παρακάτω εντολή χρησιμοποιείται μόνο στη περίπτωση επιτυχούς
                # αναζήτησης ονόματος προϊόντος (δηλ. υπάρχει προϊόν ή προϊόντα με 
                # αυτό το όνομα).
                return Response(json.dumps(products), status=200, mimetype='application/json')
            else:
                # Μήνυμα λάθους (δεν βρέθηκε προϊόν με αυτό το όνομα)
                return Response("No products found with name: '"+p_name+"'", status=400, mimetype='application/json')
        else:
            return Response("Permission denied", status=401, mimetype='application/json')
    else:
        # Μήνυμα λάθους (λάθος id αυθεντικοποίησης)
        return Response("user is not authenticated", status=401, mimetype='application/json')

# Αναζήτηση κατηγορίας προϊόντος
@app.route('/search-pcat', methods=['GET'])
def search_p_cat():
    # Αποθηκεύουμε το id της αυθεντικοποίησης και το argument του χρήστη
    auth_id = request.headers.get('authorization')
    p_cat = request.args.get('cat')

    # Έλεγχος αν ο χρήστης εισήγαγε κάποιο argument
    if p_cat == None:
        return Response("Bad request", status=500, mimetype='application/json')

    if(is_session_valid(auth_id)):
        user_email = users_sessions[auth_id][0]
        user_cat = users_db.find_one({"email": user_email})

        if(user_cat['category'] == "simple user"):
            res = products_db.find({"category": p_cat})
            if res.count() != 0:
                products = []
                for product in res:
                    product['_id'] = None
                    products.append(product)
                # Ταξινόμηση πίνακα με βάση την τιμή προϊόντος με αύξουσα σειρά
                products = sorted(products, key=lambda prod: prod['price'])
                # Η παρακάτω εντολή χρησιμοποιείται μόνο στη περίπτωση επιτυχούς
                # αναζήτησης κατηγορίας προϊόντος (δηλ. υπάρχει προϊόν ή προϊόντα 
                # στην κατηγορία αυτή).
                return Response(json.dumps(products), status=200, mimetype='application/json')
            else:
                # Μήνυμα λάθους (δεν βρέθηκε προϊόν στην κατηγορία αυτή)
                return Response("No products found in category: '"+p_cat+"'", status=400, mimetype='application/json')
        else:
            return Response("Permission denied", status=401, mimetype='application/json')
    else:
        # Μήνυμα λάθους (λάθος id αυθεντικοποίησης)
        return Response("user is not authenticated", status=401, mimetype='application/json')

# Αναζήτηση κωδικού προϊόντος
@app.route('/search-pcode', methods=['GET'])
def search_p_code():
    # Αποθηκεύουμε το id της αυθεντικοποίησης και το argument του χρήστη
    auth_id = request.headers.get('authorization')
    p_code = request.args.get('code')

    # Έλεγχος αν ο χρήστης εισήγαγε κάποιο argument
    if p_code == None:
        return Response("Bad request", status=500, mimetype='application/json')

    if(is_session_valid(auth_id)):
        user_email = users_sessions[auth_id][0]
        user_cat = users_db.find_one({"email": user_email})

        if(user_cat['category'] == "simple user"):
            res = products_db.find_one({"_id": ObjectId(str(p_code))})
            if res != None:
                product = {"id": p_code, "name": res['name'], "price": res['price'], "description": res['description'], "category": res['category'], "stock": res['stock']}
                # Η παρακάτω εντολή χρησιμοποιείται μόνο στη περίπτωση επιτυχούς
                # αναζήτησης κωδικού προϊόντος (δηλ. υπάρχει προϊόν ή προϊόντα 
                # με τον κωδικό αυτό).
                return Response(json.dumps(product), status=200, mimetype='application/json')
            else:
                # Μήνυμα λάθους (δεν βρέθηκε προϊόν στην κατηγορία αυτή)
                return Response("No products found with code: '"+p_code+"'", status=400, mimetype='application/json')
        else:
            return Response("Permission denied", status=401, mimetype='application/json')
    else:
        # Μήνυμα λάθους (λάθος id αυθεντικοποίησης)
        return Response("user is not authenticated", status=401, mimetype='application/json')

# Προσθήκη προϊόντων στο καλάθι του χρήστη
@app.route('/add-to-cart', methods=['GET'])
def add_to_cart():
    auth_id = request.headers.get('authorization')
    p_code = request.args.get('code')
    p_quan = request.args.get('quantity')

    if p_code == None or p_quan == None:
        return Response("Bad request", status=500, mimetype='application/json')
    
    if(is_session_valid(auth_id)):
        user_email = users_sessions[auth_id][0]
        user_cat = users_db.find_one({"email": user_email})

        if(user_cat['category'] == "simple user"):
            res = products_db.find_one({"_id": ObjectId(str(p_code))})
            if res != None:
                if int(p_quan) <= res['stock']:
                    product = {"id": p_code, "name": res['name'], "price": res['price'], "quantity": int(p_quan)}
                    cart['products'].append(product)
                    cart['total_cost'] += res['price'] * int(p_quan)
                    cart['total_cost'] = round(cart['total_cost'], 2)
                    return Response("Cart:\n\n"+json.dumps(cart), status=200, mimetype='application/json')
                else:
                    return Response("The quantity is more than the available stock.", status=400, mimetype='application/json')
            else:
                return Response("No products found with code: '"+p_code+"'", status=400, mimetype='application/json')
        else:
            return Response("Permission denied", status=401, mimetype='application/json')
    else:
        # Μήνυμα λάθους (λάθος id αυθεντικοποίησης)
        return Response("user is not authenticated", status=401, mimetype='application/json')


# Εμφάνιση του καλαθιού με τα προϊόντα προς αγορά
@app.route('/show-cart', methods=['GET'])
def show_cart():
    auth_id = request.headers.get('authorization')

    if(is_session_valid(auth_id)):
        user_email = users_sessions[auth_id][0]
        user_cat = users_db.find_one({"email": user_email})

        if(user_cat['category'] == "simple user"):
            print(users_sessions)
            return Response("Cart:\n\n"+json.dumps(cart), status=200, mimetype='application/json')
        else:
            return Response("Permission denied", status=401, mimetype='application/json')
    else:
        # Μήνυμα λάθους (λάθος id αυθεντικοποίησης)
        return Response("user is not authenticated", status=401, mimetype='application/json')

    

# Διαγραφή προϊόντος από το καλάθι αγορών
@app.route('/delete-from-cart', methods=['DELETE'])
def delete_from_cart():
    auth_id = request.headers.get('authorization')
    p_code = request.args.get('code')

    if p_code == None:
        return Response("Bad request", status=500, mimetype='application/json')
    
    if(is_session_valid(auth_id)):
        user_email = users_sessions[auth_id][0]
        user_cat = users_db.find_one({"email": user_email})

        if(user_cat['category'] == "simple user"):
            products_in_cart = cart["products"]
            print(products_in_cart)
            found = False
            
            for i,prod in enumerate(products_in_cart):
                if(prod["id"] == p_code):
                    found = True
                    cart["total_cost"] -= prod["quantity"] * prod["price"]
                    cart["total_cost"] = round(cart["total_cost"], 2)
                    del products_in_cart[i]
            
            if(found == True):
                return Response("Cart:\n\n"+json.dumps(cart), status=200, mimetype='application/json')
            else:
                return Response("No product found in cart with code: '"+p_code+"'", status=400, mimetype='application/json')
        else:
            return Response("Permission denied", status=401, mimetype='application/json')
    else:
        # Μήνυμα λάθους (λάθος id αυθεντικοποίησης)
        return Response("user is not authenticated", status=401, mimetype='application/json')

# Αγορά προϊόντων
@app.route('/payment', methods=['PATCH'])
def payment():
    # Request JSON data
    data = None
    # Load request data
    try:
        data = json.loads(request.data)
    # In case of an error show error message in console
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    # Check if data is empty
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    # Check if email or password are absent
    if not "card_number" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")
    
    auth_id = request.headers.get('authorization')

    if(is_session_valid(auth_id)):
        user_email = users_sessions[auth_id][0]
        user_cat = users_db.find_one({"email": user_email})

        if(user_cat['category'] == "simple user"):
            if(len(data['card_number']) == 16):
                receipt = {"products": [], "total_cost": cart["total_cost"]}
                for i,prod in enumerate(cart["products"]):
                    receipt_prod = {"name": prod["name"], "price": prod["price"], "quantity": prod["quantity"]}
                    receipt["products"].append(receipt_prod)
                
                users_db.update_one({"email": user_email}, {"$push": {"orderHistory": receipt}})

                return Response("Receipt:\n\n"+json.dumps(receipt), status=200, mimetype='application/json')
            else:
                return Response("The card number you gave is false. It has to be 16 digits.", status=400, mimetype='application/json')
        else:
            return Response("Permission denied", status=401, mimetype='application/json')
    else:
        # Μήνυμα λάθους (λάθος id αυθεντικοποίησης)
        return Response("user is not authenticated", status=401, mimetype='application/json')

# Εμφάνιση ιστορικού παραγγελίας χρήστη
@app.route('/show-order-history', methods=['GET'])
def show_order_history():
    auth_id = request.headers.get('authorization')

    if(is_session_valid(auth_id)):
        user_email = users_sessions[auth_id][0]
        user_cat = users_db.find_one({"email": user_email})

        if(user_cat['category'] == "simple user"):
            history = users_db.find_one({"email": user_email}, {"orderHistory": 1, "_id": 0})
            return Response("Order History:\n\n"+json.dumps(history), status=200, mimetype='application/json')
        else:
            return Response("Permission denied", status=401, mimetype='application/json')
    else:
        # Μήνυμα λάθους (λάθος id αυθεντικοποίησης)
        return Response("user is not authenticated", status=401, mimetype='application/json')

# Διαγραφή λογαριασμού χρήστη
@app.route('/delete-account', methods=['DELETE'])
def delete_account():
    auth_id = request.headers.get('authorization')

    if(is_session_valid(auth_id)):
        user_email = users_sessions[auth_id][0]
        user_cat = users_db.find_one({"email": user_email})

        if(user_cat['category'] == "simple user"):
            users_db.delete_one({"email": user_email})
            del users_sessions[auth_id]
            return Response("Account was successfully deleted", status=200, mimetype='application/json')
        else:
            return Response("Permission denied", status=401, mimetype='application/json')
    else:
        # Μήνυμα λάθους (λάθος id αυθεντικοποίησης)
        return Response("user is not authenticated", status=401, mimetype='application/json')

# Εισαγωγή νέων προϊόντων
@app.route('/add-new-product', methods=['POST'])
def add_new_product():
    # Request JSON data
    data = None
    # Load request data
    try:
        data = json.loads(request.data)
    # In case of an error show errr message in console
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    # Check if data is empty
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    # Check if email or name or password are absent
    if not "name" in data or not "price" in data or not "description" in data or not "category" in data or not "stock" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    auth_id = request.headers.get('authorization')

    if(is_session_valid(auth_id)):
        user_email = users_sessions[auth_id][0]
        user_cat = users_db.find_one({"email": user_email})

        if(user_cat['category'] == "admin user"):
            products_db.insert_one({"name": data['name'], "price": data['price'], "description": data['description'], "category": data['category'], "stock": data['stock']})
            return Response("Product was successfully inserted to database", status=200, mimetype='application/json')
        else:
            return Response("Permission denied", status=401, mimetype='application/json')
    else:
        # Μήνυμα λάθους (λάθος id αυθεντικοποίησης)
        return Response("user is not authenticated", status=401, mimetype='application/json')

# Διαγραφή προϊόντων
@app.route('/delete-product', methods=['DELETE'])
def delete_product():
    auth_id = request.headers.get('authorization')
    p_code = request.args.get('code')

    if p_code == None:
        return Response("Bad request", status=500, mimetype='application/json')
    
    if(is_session_valid(auth_id)):
        user_email = users_sessions[auth_id][0]
        user_cat = users_db.find_one({"email": user_email})

        if(user_cat['category'] == "admin user"):
            product = products_db.find_one({"_id": ObjectId(str(p_code))})
            
            if product != None:
                products_db.delete_one({"_id": ObjectId(str(p_code))})
                return Response("Product with code: "+p_code+" was successfully deleted", status=200, mimetype='application/json')
            else:
                return Response("No product found in database with code: '"+p_code+"'", status=400, mimetype='application/json')
        else:
            return Response("Permission denied", status=401, mimetype='application/json')
    else:
        # Μήνυμα λάθους (λάθος id αυθεντικοποίησης)
        return Response("user is not authenticated", status=401, mimetype='application/json')

# Ενημέρωση προϊόντος
@app.route('/update-product', methods=['PUT'])
def update_product():
    # Request JSON data
    data = None
    # Load request data
    try:
        data = json.loads(request.data)
    # In case of an error show errr message in console
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    # Check if data is empty
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')

    auth_id = request.headers.get('authorization')
    p_code = request.args.get('code')

    if p_code == None:
        return Response("Bad request", status=500, mimetype='application/json')

    if(is_session_valid(auth_id)):
        user_email = users_sessions[auth_id][0]
        user_cat = users_db.find_one({"email": user_email})

        if(user_cat['category'] == "admin user"):
            print(users_sessions)
            product = products_db.find_one({"_id": ObjectId(str(p_code))})
            if product != None:
                acceptable_keys = ["name", "price", "description", "price"]
                non_acc_keys = False
                
                for key in data:
                    if(key not in acceptable_keys):
                        non_acc_keys = True

                if(non_acc_keys == True):
                    return Response("Invalid product field", status=400, mimetype='application/json')
                else:
                    for key in data:
                        if(key == "name"):
                            products_db.update_one({"_id": ObjectId(str(p_code))}, {"$set": {str(key): data['name']}})
                        elif(key == "price"):
                            products_db.update_one({"_id": ObjectId(str(p_code))}, {"$set": {str(key): data['price']}})
                        elif(key == "description"):
                            products_db.update_one({"_id": ObjectId(str(p_code))}, {"$set": {str(key): data['description']}})
                        elif(key == "stock"):
                            products_db.update_one({"_id": ObjectId(str(p_code))}, {"$set": {str(key): data['stock']}})
                    
                    return Response("Product with code: "+p_code+" was updated successfully", status=200, mimetype='application/json')
            else:
                return Response("Product with code: "+p_code+" not found in database", status=400, mimetype='application/json')
        else:
            return Response("Permission denied", status=401, mimetype='application/json')
    else:
        # Μήνυμα λάθους (λάθος id αυθεντικοποίησης)
        return Response("user is not authenticated", status=401, mimetype='application/json')


# Εκτέλεση flask service σε debug mode, στην port 5000. 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
