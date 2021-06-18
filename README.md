# Ergasia2_E17085
**ΠΑΝΕΠΙΣΤΗΜΙΟ ΠΕΙΡΑΙΩΣ** <br>
**ΤΜΗΜΑ ΨΗΦΙΑΚΩΝ ΣΥΣΤΗΜΑΤΩΝ** <br>
**_ΜΑΘΗΜΑ_**: Πληροφοριακά Συστήματα <br>
**_ΟΝ/ΝΥΜΟ_**: Κουτελιέρης Μιχάλης <br>
**_ΑΜ_**: Ε17085 <br>

## Επεξήγηση Υλοποίησης Ερωτημάτων Εργασίας

### Απαραίτητος κώδικας πριν την υλοποίηση των endpoints

```
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
```

  Στον παραπάνω κώδικα, εισάγουμε όλες τις βιβλιοθήκες που θα βοηθήσουν στην υλοποίηση των endpoints για το super market. Επιπρόσθετα από τις βιβλιοθήκες που υπήρχαν και στην 1η εργασία, έχει προστεθεί και η ObjectId βιβλιοθήκη για να μπορέσω να προσπελάσω και να επιστρέψω documents της mongodb με βάση το ```id``` που δίνει η βάση στα documents αυτόματα.

  Έπειτα, πραγματοποιώ σύνδεση στη βάση mongodb μέσω του Mongodb URI και αποθηκεύω αυτή τη σύνδεση στη μεταβλητή ```client```. Αποθηκεύω τη σύνδεση με την βάση δεδομένων DSMarkets στην μεταβλητή ```db``` και μετά μέσω αυτής αποθηκεύω την σύνδεση με τα collections Users και Products στις μεταβλητές ```users_db``` και ```products_db``` αντίστοιχα. Μετά, αρχικοποιώ την μεταβλητή ```cart``` για το καλάθι αγορών του χρήστη η οποία θα περιέχει τα κλειδία ```products``` και ```total_cost``` όπου το products θα περιέχει λίστα με τα προϊόντα προς αγορά και το total_cost θα περιέχει το συνολικό ποσό πληρωμής. Τέλος, κάνουμε εκκίνηση της Flask εφαμοργής μας.

```
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
```

  Στον παραπάνω κώδικα, αρχικοποιούμε το ευρετήριο ```users_sessions``` όπου θα δημιουργούνται και αποθηκεύονται το μοναδικό αναγνωριστικό του χρήστη που είναι συνδεδεμένος καθώς και το email του και η ώρα σύνδεσης. Παρακάτω, με της χρήσης της συνάρτησης ```create_session``` δημιουργούμε το μοναδικό ```user_uuid``` του χρήστη και το παιρνάμε ως κλειδί στο ευρετήριο ```users_sessions``` και ως τιμή του κλειδιού ορίζουμε ένα tuple που περιέχει το email του χρήστη και την ώρα πραγματοποίησης της σύνδεσης του στο σύστημα. Επιστρέφουμε το ```user_uuid```. Έπειτα, μέσω της χρήσης της συνάρτησης ```is_session_valid``` επιστρέφει True ή False ελέγχοντας αν το user_uuid του χρήστη υπάρχει στο users_sessions ευρετήριο, δηλαδή ελέγχει εαν ο χρήστης είναι συνδεδεμένος.

### 1. Εγγραφή απλών χρηστών στο σύστημα - ```/register``` endpoint

```
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
```

  Στον παραπάνω κώδικα, ορίζουμε το endpoint σε ```/register``` καθώς και την μέθοδο που θα χρησιμοποιήσουμε POST για να στείλουμε τα στοιχεία του χρήστη στο σύστημα. Έπειτα, φτιάχνουμε μια συνάρτηση ```register_user()``` και μέσα της αρχικοποιούμε τη μεταβλητή ```data``` δίνοντας της τον τύπο None, δηλαδή ότι είναι κενή, η οποία θα χρησιμοποιηθεί για να προσπελάσουμε τα στοιχεία του χρήστη από το request του μηνύματος. Φορτώνουμε τα δεδομένα από το request στη μεταβλητή ```data``` μέσω της μεθόδου ```loads()``` της βιβλιοθήκης json. Σε περίπτωση που υπάρξει error κατά την φόρτωση των δεδομένων του request, τότε επιστρέφουμε ```Response``` αντικείμενο στην κονσόλα με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500.
  
  #### ΣΗΜΕΙΩΣΗ: τα δεδομένα του request από το body του μηνύματος είναι σε μορφή json, δηλαδή ένα ευρετήριο με τα δεδομένα να είναι κλειδιά και τιμές, π.χ. ```{"email": "john@example.com", "name": "John", "password": "3242"}```
  
  Σε περίπτωση που δεν υπάρχουν δεδομένα στο request του μηνύματος, δηλαδή η μεταβλητή ```data``` έχει τιμή None, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500. Σε περίπτωση που δεν υπάρχει κάποιο από τα απαιτούμενα στοιχεία του χρήστη στο request του μηνύματος για να είναι έγκυρη η εγγραφή του, δηλαδή αν δεν υπάρχει ένα από τα κλειδιά "email", "name", "password" στην μεταβλητή ```data```, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500.

```
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
```

  Στον παραπάνω κώδικα, με την εντολή ```users_db.find({"email": data['email']})``` πραγματοποιούμε αναζήτηση στο collection Users με query το email του χρήστη και στην ουσία πραγματοποιούμε αναζήτηση να δούμε αν υπάρχει ήδη χρήστης με αυτό το email στο collection. Η εντολή ```find``` επιστρέφει ένα αντικείμενο με το document του χρήστη, αν υπάρχει, με το συγκεκριμένο email. Καλώντας την μέθοδο ```count()``` στην εντολή αναζήτησης στην ουσία μετράμε τα documents που επεστράφησαν. 
  
  Αν τα documents που επεστράφησαν είναι 0, δηλαδή ο χρήστης δεν υπάρχει στη βάση ήδη, τότε μέσω της εντολής ```insert_one``` εισάγουμε τα δεδομένα από το request του μηνύματος στο collection Users εισάγοντας επίσης και το πεδίο "category" και "orderHistory" με τιμές "simple user" και κενή λίστα για το ιστορικό. Τελικά, επιστρέφουμε αντικείμενο Response με κατάλληλο μήνυμα επιτυχίας και κωδικό επιτυχίας 200. Στην περίπτωση που υπάρχει ήδη εγγεγραμμένος χρήστη στο collection Users, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 400.

### 2. Σύνδεση χρηστών στο σύστημα - ```/login``` endpoint

```
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
```

  Στον παραπάνω κώδικα, ορίζουμε το endpoint σε ```/login``` καθώς και την μέθοδο που θα χρησιμοποιήσουμε POST για να στείλουμε τα στοιχεία του χρήστη στο σύστημα. Έπειτα, φτιάχνουμε μια συνάρτηση ```login_user()``` και μέσα της αρχικοποιούμε τη μεταβλητή ```data``` δίνοντας της τον τύπο None, δηλαδή ότι είναι κενή, η οποία θα χρησιμοποιηθεί για να προσπελάσουμε τα στοιχεία του χρήστη από το request του μηνύματος. Φορτώνουμε τα δεδομένα από το request στη μεταβλητή ```data``` μέσω της μεθόδου ```loads()``` της βιβλιοθήκης json. Σε περίπτωση που υπάρξει error κατά την φόρτωση των δεδομένων του request, τότε επιστρέφουμε ```Response``` αντικείμενο στην κονσόλα με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500.
  
   #### ΣΗΜΕΙΩΣΗ: τα δεδομένα του request από το body του μηνύματος είναι σε μορφή json, δηλαδή ένα ευρετήριο με τα δεδομένα να είναι κλειδιά και τιμές, π.χ. ```{"email": "john@example.com", "password": "3242"}```
   
   Σε περίπτωση που δεν υπάρχουν δεδομένα στο request του μηνύματος, δηλαδή η μεταβλητή ```data``` έχει τιμή None, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500. Σε περίπτωση που δεν υπάρχει κάποιο από τα απαιτούμενα στοιχεία του χρήστη στο request του μηνύματος για να είναι έγκυρη η σύνδεση του, δηλαδή αν δεν υπάρχει ένα από τα κλειδιά "email", "password" στην μεταβλητή ```data```, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500.
   
```
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
```

  Στον παραπάνω κώδικα, με την εντολή ```users_db.find({"$and": [{"email": {"$eq": data['email']}}, {"password": {"$eq": data['password']}}]})``` πραγματοποιούμε αναζήτηση στο collection Users με query το email του χρήστη και τον κωδικό του και στην ουσία πραγματοποιούμε αναζήτηση να δούμε αν υπάρχει ο χρήστης με αυτό το email και τον κωδικό στο collection. Η εντολή ```find``` επιστρέφει ένα αντικείμενο με το document του χρήστη, αν υπάρχει, με το συγκεκριμένο email και κωδικό. Καλώντας την μέθοδο ```count()``` στην εντολή αναζήτησης στην ουσία μετράμε τα documents που επεστράφησαν.
  
  Αν τα documents που επεστράφησαν είναι 1, δηλαδή ο χρήστης υπάρχει στη βάση, τότε σε περίπτωση που το ευρετήριο ```users_sessions``` περιέχει κάποιον άλλον χρήστη συνδεδεμένο, πρέπει να εξασφαλίσουμε ότι δεν μπορεί να υπάρχει κάποιος χρήστης παραπάνω από μια φορές στο ευρετήριο γι αυτό αφαιρούμε όλα τα στοιχεία του ευρετηρίου κάθε φορά που κάποιος χρήστης κάνει login. Έπειτα, δημιουργούμε μοναδικό αναγνωριστικό κωδικό για τον χρήστη με τη χρήση της συνάρτησης ```create_session``` παιρνόντας επίσης και στο ευρετήριο ```users_sessions``` τον αναγνωριστικό κωδικό και το email του με την ώρα σύνδεσης. Μετά, δημιουργούμε dictionary ```res``` όπου αποθηκεύουμε τον αναγνωριστικό κωδικό και το email του χρήστη προκειμένου ο χρήστης να γνωρίζει τον κωδικό για να μπορεί να αυθεντικοποιηθεί αργότερα. Τελικά, επιστρέφουμε αντικείμενο Response με κατάλληλο μήνυμα επιτυχίας καθώς και το ευρετήριο με τον μοναδικό κωδικό του χρήστη και κωδικό επιτυχίας 200. 
  
  Στην περίπτωση που δεν υπάρχει χρήστης με το δωθέν email και κωδικό στο collection Users, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 400.
  
### 3. Αναζήτηση προϊόντων με βάση το όνομα τους - ```/search-pname``` endpoint
  
```
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
```

  Στον παραπάνω κώδικα, ορίζουμε το endpoint σε ```/search-pname``` καθώς και την μέθοδο που θα χρησιμοποιήσουμε GET για να αναζητήσουμε και επιστρέψουμε τα στοιχεία ενός προϊόντος με βάση το όνομα του από το σύστημα. Έπειτα, φτιάχνουμε μια συνάρτηση ```search_pname``` και μέσα της αποθηκεύουμε στη μεταβλητή ```auth_id``` τον αναγνωριστικό κωδικό του χρήστη που το έχει εισάγει στα headers του μηνύματος και στη μεταβλητή ```p_name``` αποθηκεύουμε το όνομα του προϊόντος που θέλει ο χρήστης να πραγματοποιήσει αναζήτηση εισάγωντας στο url του endpoint το argument, π.χ. ```/search-pname?name=Calgon```. Σε περίπτωση που το argument name είναι τύπου None, δηλαδή ο χρήστης δεν έχει εισάγει όνομα προϊόντος, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500.
  
  Καλώντας την ```is_session_valid()``` συνάρτηση, αν το αναγνωριστικό του χρήστη υπάρχει στο ευρετήριο ```users_sessions```, δηλαδή αν ο χρήστης είναι συνδεδεμένος, τότε αποθηκεύουμε στη μεταβλητή ```user_email``` το email του χρήστη που το παίρνουμε από το ευρετήριο ```users_sessions``` μέσω του αναγνωριστικού του χρήστη και στη μεταβλητή ```user_cat``` αποθηκεύουμε το αποτέλεσμα της αναζήτησης με το email του χρήστη στο collection Users προκειμένου να μπορούμε να ανακτήσουμε την κατηγορία του. Έπειτα, για να αποφύγουμε την περίπτωση κάποιος συνδεδεμένος διαχειριστής να μπορεί να χρησιμοποιήσει το endpoint του απλού χρήστη, ελέγχουμε μέσω της μεταβλητής ```user_cat``` αν η κατηγορία του συνδεδεμένου χρήστη είναι "simple user", δηλαδή απλός χρήστης.
  
```
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
```

  Αν ο χρήστης είναι απλός, τότε αποθηκεύουμε σε μεταβλητή ```res``` το αποτέλεσμα της αναζήτησης προϊόντος με βάση το όνομα χρησιμοποιώντας το argument ```p_name```. Αν βρεθεί το προϊόν με το δωθέν όνομα στο collection Products, δηλαδή αν ο αριθμός των documents που επιστρέφονται δεν είναι 0, τότε αρχικοποιούμε την μεταβλητή ```products``` η οποία θα χρησιμοποιηθεί για να αποθηκευθούν τα στοιχεία του προϊόντος που αναζητάται. Μετά, μέσω μιας επανάληψης στα αποτελέσματα ```res``` της αναζήτησης του προϊόντος, προσθέτουμε κάθε πεδίο του αποτελέσματος στην μεταβλητή ```products``` φροντίζοντας να θέτουμε το πεδίο ```_id``` σε None για να μην παρουσιάζεται error καθώς η τιμή του πεδίου id δεν είναι σειριοποιήσιμη από τη βιβλιοθήκη JSON.
  
  Στη συνέχεια, ταξινομούμε τον πίνακα ```products``` με βάση το όνομα, ο οποίος περιέχει το προϊόν/τα προϊόντα που επιστρέφονται από την αναζήτηση. Η ταξινόμηση γίνεται με τη χρήση της συνάρτησης ```sorted()```, η οποία δέχεται σαν πρώτο όρισμα έναν πίνακα και σαν δεύτερο όρισμα την παράμετρο που θα ταξινομηθεί (σε αυτήν την περίπτωση το κλειδί "name"). Έπειτα, επιστρέφουμε αντικείμενο Response με το προϊόν που βρέθηκε και κωδικό επιτυχίας 200.
  
  Σε περίπτωση που δεν βρεθεί κάποιο προϊόν με το δωθέν όνομα, δηλαδή αν η μεταβλητή ```res``` είναι κενή κι επιστρέψει 0 καλώντας την μέθοδο ```count()``` πάνω της, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 400. 
  
  Σε περίπτωση που ο συνδεδεμένος χρήστης είναι διαχειριστής, δηλαδή το πεδίο category του document του συνδεδεμένου χρήστη είναι admin user, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 401.
  
  Σε περίπτωση που έχει γίνει λάθος αυθεντικοποίηση του χρήστη, δηλαδή το user_uuid δεν αντιστοιχεί σε κάποιον χρήστη του ευρετηρίου ```users_sessions```, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 401.
  
### 4. Αναζήτηση προϊόντων με βάση την κατηγορία τους - ```/search-pcat``` endpoint

```
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
```

  Στον παραπάνω κώδικα, ορίζουμε το endpoint σε ```/search-pcat``` καθώς και την μέθοδο που θα χρησιμοποιήσουμε GET για να αναζητήσουμε και επιστρέψουμε τα στοιχεία ενός προϊόντος με βάση την κατηγορία του από το σύστημα. Έπειτα, φτιάχνουμε μια συνάρτηση ```search_pcat``` και μέσα της αποθηκεύουμε στη μεταβλητή ```auth_id``` τον αναγνωριστικό κωδικό του χρήστη που το έχει εισάγει στα headers του μηνύματος και στη μεταβλητή ```p_cat``` αποθηκεύουμε την κατηγορία του προϊόντος που θέλει ο χρήστης να πραγματοποιήσει αναζήτηση εισάγωντας στο url του endpoint το argument, π.χ. ```/search-pcat?cat=cleaning```. Σε περίπτωση που το argument cat είναι τύπου None, δηλαδή ο χρήστης δεν έχει εισάγει κατηγορία προϊόντος, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500.
  
  Καλώντας την ```is_session_valid()``` συνάρτηση, αν το αναγνωριστικό του χρήστη υπάρχει στο ευρετήριο ```users_sessions```, δηλαδή αν ο χρήστης είναι συνδεδεμένος, τότε αποθηκεύουμε στη μεταβλητή ```user_email``` το email του χρήστη που το παίρνουμε από το ευρετήριο ```users_sessions``` μέσω του αναγνωριστικού του χρήστη και στη μεταβλητή ```user_cat``` αποθηκεύουμε το αποτέλεσμα της αναζήτησης με το email του χρήστη στο collection Users προκειμένου να μπορούμε να ανακτήσουμε την κατηγορία του. Έπειτα, για να αποφύγουμε την περίπτωση κάποιος συνδεδεμένος διαχειριστής να μπορεί να χρησιμοποιήσει το endpoint του απλού χρήστη, ελέγχουμε μέσω της μεταβλητής ```user_cat``` αν η κατηγορία του συνδεδεμένου χρήστη είναι "simple user", δηλαδή απλός χρήστης.
  
```
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
```

  Αν ο χρήστης είναι απλός, τότε αποθηκεύουμε σε μεταβλητή ```res``` το αποτέλεσμα της αναζήτησης προϊόντος με βάση την κατηγορία του χρησιμοποιώντας το argument ```p_cat```. Αν βρεθεί το προϊόν με τη δωθέν κατηγορία στο collection Products, δηλαδή αν ο αριθμός των documents που επιστρέφονται δεν είναι 0, τότε αρχικοποιούμε την μεταβλητή ```products``` η οποία θα χρησιμοποιηθεί για να αποθηκευθούν τα στοιχεία του προϊόντος που αναζητάται. Μετά, μέσω μιας επανάληψης στα αποτελέσματα ```res``` της αναζήτησης του προϊόντος, προσθέτουμε κάθε πεδίο του αποτελέσματος στην μεταβλητή ```products``` φροντίζοντας να θέτουμε το πεδίο ```_id``` σε None για να μην παρουσιάζεται error καθώς η τιμή του πεδίου id δεν είναι σειριοποιήσιμη από τη βιβλιοθήκη JSON.
  
  Στη συνέχεια, ταξινομούμε τον πίνακα ```products``` με βάση την τιμή του, ο οποίος περιέχει το προϊόν/τα προϊόντα που επιστρέφονται από την αναζήτηση. Η ταξινόμηση γίνεται με τη χρήση της συνάρτησης ```sorted()```, η οποία δέχεται σαν πρώτο όρισμα έναν πίνακα και σαν δεύτερο όρισμα την παράμετρο που θα ταξινομηθεί (σε αυτήν την περίπτωση το κλειδί "price"). Έπειτα, επιστρέφουμε αντικείμενο Response με το προϊόν που βρέθηκε και κωδικό επιτυχίας 200.
  
  Σε περίπτωση που δεν βρεθεί κάποιο προϊόν με τη δωθέν κατηγορία, δηλαδή αν η μεταβλητή ```res``` είναι κενή κι επιστρέψει 0 καλώντας την μέθοδο ```count()``` πάνω της, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 400. 
  
  Σε περίπτωση που ο συνδεδεμένος χρήστης είναι διαχειριστής, δηλαδή το πεδίο category του document του συνδεδεμένου χρήστη είναι admin user, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 401.
  
  Σε περίπτωση που έχει γίνει λάθος αυθεντικοποίηση του χρήστη, δηλαδή το user_uuid δεν αντιστοιχεί σε κάποιον χρήστη του ευρετηρίου ```users_sessions```, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 401.
  
### 5. Αναζήτηση προϊόντων με βάση τον κωδικό τους - ```/search-pcode``` endpoint

```
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
```

  Στον παραπάνω κώδικα, ορίζουμε το endpoint σε ```/search-pcode``` καθώς και την μέθοδο που θα χρησιμοποιήσουμε GET για να αναζητήσουμε και επιστρέψουμε τα στοιχεία ενός προϊόντος με βάση τον κωδικό τους από το σύστημα. Έπειτα, φτιάχνουμε μια συνάρτηση ```search_pcode``` και μέσα της αποθηκεύουμε στη μεταβλητή ```auth_id``` τον αναγνωριστικό κωδικό του χρήστη που το έχει εισάγει στα headers του μηνύματος και στη μεταβλητή ```p_code``` αποθηκεύουμε τον κωδικό του προϊόντος που θέλει ο χρήστης να πραγματοποιήσει αναζήτηση εισάγωντας στο url του endpoint το argument, π.χ. ```/search-pcode?code=4234dfsjdfsdfsd3434```. Σε περίπτωση που το argument code είναι τύπου None, δηλαδή ο χρήστης δεν έχει εισάγει kvdik;o προϊόντος, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500.
  
  Καλώντας την ```is_session_valid()``` συνάρτηση, αν το αναγνωριστικό του χρήστη υπάρχει στο ευρετήριο ```users_sessions```, δηλαδή αν ο χρήστης είναι συνδεδεμένος, τότε αποθηκεύουμε στη μεταβλητή ```user_email``` το email του χρήστη που το παίρνουμε από το ευρετήριο ```users_sessions``` μέσω του αναγνωριστικού του χρήστη και στη μεταβλητή ```user_cat``` αποθηκεύουμε το αποτέλεσμα της αναζήτησης με το email του χρήστη στο collection Users προκειμένου να μπορούμε να ανακτήσουμε την κατηγορία του. Έπειτα, για να αποφύγουμε την περίπτωση κάποιος συνδεδεμένος διαχειριστής να μπορεί να χρησιμοποιήσει το endpoint του απλού χρήστη, ελέγχουμε μέσω της μεταβλητής ```user_cat``` αν η κατηγορία του συνδεδεμένου χρήστη είναι "simple user", δηλαδή απλός χρήστης.
  
```
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
```

  Αν ο χρήστης είναι απλός, τότε αποθηκεύουμε σε μεταβλητή ```res``` το αποτέλεσμα της αναζήτησης προϊόντος με βάση τον κωδικό του χρησιμοποιώντας το argument ```p_code```. Επειδή ο κωδικός προϊόντος αποδίδεται αυτόματα όταν γίνεται εισαγωγή προϊόντος στο collection Products από την mongodb και είναι τύπου αντικειμένου ObjectId, μέσω της εισαγωγής της βιβλιοθήκης ```bson.objectid``` στο προγραμμά μας, μπορούμε να μετατρέψουμε τον κωδικό ```p_code``` που εισήγαγε ο χρήστης ως argument σε τύπο που να αναγνωρίζει η mongodb βάση. Αν βρεθεί το προϊόν με τον δωθέν κωδικό, δηλαδή αν η μεταβλητή ```res``` δεν είναι τύπου None/κενή, τότε δημιουργούμε ένα ευρετήριο ```product``` με τα κλειδιά παρμένα από τη μεταβλητή ```res``` με τα αποτελέσματα της αναζήτησης. Έπειτα, επιστρέφουμε το ευρετήριο με το προϊόν που βρέθηκε και κωδικό επιτυχίας 200.
  
  Σε περίπτωση που δεν βρεθεί κάποιο προϊόν με τον δωθέν κωδικό, δηλαδή αν η μεταβλητή ```res``` είναι κενή κι επιστρέψει 0 καλώντας την μέθοδο ```count()``` πάνω της, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 400. 
  
  Σε περίπτωση που ο συνδεδεμένος χρήστης είναι διαχειριστής, δηλαδή το πεδίο category του document του συνδεδεμένου χρήστη είναι admin user, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 401.
  
  Σε περίπτωση που έχει γίνει λάθος αυθεντικοποίηση του χρήστη, δηλαδή το user_uuid δεν αντιστοιχεί σε κάποιον χρήστη του ευρετηρίου ```users_sessions```, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 401.
  
### 6. Προσθήκη προϊόντων στο καλάθι αγορών του χρήστη - ```/add-to-cart``` endpoint

```
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
```
