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

  Στον παραπάνω κώδικα, ορίζουμε το endpoint σε ```/search-pname``` καθώς και την μέθοδο που θα χρησιμοποιήσουμε GET για να αναζητήσουμε και επιστρέψουμε τα στοιχεία ενός προϊόντος με βάση το όνομα του από το σύστημα. Έπειτα, φτιάχνουμε μια συνάρτηση ```search_pname()``` και μέσα της αποθηκεύουμε στη μεταβλητή ```auth_id``` τον αναγνωριστικό κωδικό του χρήστη που το έχει εισάγει στα headers του μηνύματος και στη μεταβλητή ```p_name``` αποθηκεύουμε το όνομα του προϊόντος που θέλει ο χρήστης να πραγματοποιήσει αναζήτηση εισάγωντας στο url του endpoint το argument, π.χ. ```/search-pname?name=Calgon```. Σε περίπτωση που το argument name είναι τύπου None, δηλαδή ο χρήστης δεν έχει εισάγει όνομα προϊόντος, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500.
  
  Καλώντας την ```is_session_valid()``` συνάρτηση, αν το αναγνωριστικό του χρήστη υπάρχει στο ευρετήριο ```users_sessions```, δηλαδή αν ο χρήστης είναι συνδεδεμένος, τότε αποθηκεύουμε στη μεταβλητή ```user_email``` το email του χρήστη που το παίρνουμε από το ευρετήριο ```users_sessions``` μέσω του αναγνωριστικού του χρήστη και στη μεταβλητή ```user_cat``` αποθηκεύουμε το αποτέλεσμα της αναζήτησης με το email του χρήστη στο collection Users προκειμένου να μπορούμε να ανακτήσουμε την κατηγορία του. Έπειτα, για να αποφύγουμε την περίπτωση κάποιος συνδεδεμένος διαχειριστής να μπορεί να χρησιμοποιήσει το endpoint του απλού χρήστη, ελέγχουμε μέσω της μεταβλητής ```user_cat``` αν η κατηγορία του συνδεδεμένου χρήστη είναι "simple user", δηλαδή απλός χρήστης.
  
```
            res = products_db.find({"name": p_name})
            if res.count() != 0:
                products = []
                for product in res:
                    product['_id'] = None
                    products.append(product)
                
                # Ταξινόμηση λίστας με βάση το όνομα προϊόντος με αύξουσα σειρά
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
  
  Στη συνέχεια, ταξινομούμε την λίστα ```products``` με βάση το όνομα, ο οποίος περιέχει το προϊόν/τα προϊόντα που επιστρέφονται από την αναζήτηση. Η ταξινόμηση γίνεται με τη χρήση της συνάρτησης ```sorted()```, η οποία δέχεται σαν πρώτο όρισμα μια λίστα και σαν δεύτερο όρισμα την παράμετρο που θα ταξινομηθεί (σε αυτήν την περίπτωση το κλειδί "name"). Έπειτα, επιστρέφουμε αντικείμενο Response με το προϊόν που βρέθηκε και κωδικό επιτυχίας 200.
  
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

  Στον παραπάνω κώδικα, ορίζουμε το endpoint σε ```/search-pcat``` καθώς και την μέθοδο που θα χρησιμοποιήσουμε GET για να αναζητήσουμε και επιστρέψουμε τα στοιχεία ενός προϊόντος με βάση την κατηγορία του από το σύστημα. Έπειτα, φτιάχνουμε μια συνάρτηση ```search_pcat()``` και μέσα της αποθηκεύουμε στη μεταβλητή ```auth_id``` τον αναγνωριστικό κωδικό του χρήστη που το έχει εισάγει στα headers του μηνύματος και στη μεταβλητή ```p_cat``` αποθηκεύουμε την κατηγορία του προϊόντος που θέλει ο χρήστης να πραγματοποιήσει αναζήτηση εισάγωντας στο url του endpoint το argument, π.χ. ```/search-pcat?cat=cleaning```. Σε περίπτωση που το argument cat είναι τύπου None, δηλαδή ο χρήστης δεν έχει εισάγει κατηγορία προϊόντος, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500.
  
  Καλώντας την ```is_session_valid()``` συνάρτηση, αν το αναγνωριστικό του χρήστη υπάρχει στο ευρετήριο ```users_sessions```, δηλαδή αν ο χρήστης είναι συνδεδεμένος, τότε αποθηκεύουμε στη μεταβλητή ```user_email``` το email του χρήστη που το παίρνουμε από το ευρετήριο ```users_sessions``` μέσω του αναγνωριστικού του χρήστη και στη μεταβλητή ```user_cat``` αποθηκεύουμε το αποτέλεσμα της αναζήτησης με το email του χρήστη στο collection Users προκειμένου να μπορούμε να ανακτήσουμε την κατηγορία του. Έπειτα, για να αποφύγουμε την περίπτωση κάποιος συνδεδεμένος διαχειριστής να μπορεί να χρησιμοποιήσει το endpoint του απλού χρήστη, ελέγχουμε μέσω της μεταβλητής ```user_cat``` αν η κατηγορία του συνδεδεμένου χρήστη είναι "simple user", δηλαδή απλός χρήστης.
  
```
            res = products_db.find({"category": p_cat})
            if res.count() != 0:
                products = []
                for product in res:
                    product['_id'] = None
                    products.append(product)
                # Ταξινόμηση λίστας με βάση την τιμή προϊόντος με αύξουσα σειρά
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
  
  Στη συνέχεια, ταξινομούμε την λίστα ```products``` με βάση την τιμή του, ο οποίος περιέχει το προϊόν/τα προϊόντα που επιστρέφονται από την αναζήτηση. Η ταξινόμηση γίνεται με τη χρήση της συνάρτησης ```sorted()```, η οποία δέχεται σαν πρώτο όρισμα μια λίστα και σαν δεύτερο όρισμα την παράμετρο που θα ταξινομηθεί (σε αυτήν την περίπτωση το κλειδί "price"). Έπειτα, επιστρέφουμε αντικείμενο Response με το προϊόν που βρέθηκε και κωδικό επιτυχίας 200.
  
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

  Στον παραπάνω κώδικα, ορίζουμε το endpoint σε ```/search-pcode``` καθώς και την μέθοδο που θα χρησιμοποιήσουμε GET για να αναζητήσουμε και επιστρέψουμε τα στοιχεία ενός προϊόντος με βάση τον κωδικό του από το σύστημα. Έπειτα, φτιάχνουμε μια συνάρτηση ```search_pcode()``` και μέσα της αποθηκεύουμε στη μεταβλητή ```auth_id``` τον αναγνωριστικό κωδικό του χρήστη που το έχει εισάγει στα headers του μηνύματος και στη μεταβλητή ```p_code``` αποθηκεύουμε τον κωδικό του προϊόντος που θέλει ο χρήστης να πραγματοποιήσει αναζήτηση εισάγωντας στο url του endpoint το argument, π.χ. ```/search-pcode?code=4234dfsjdfsdfsd3434```. Σε περίπτωση που το argument code είναι τύπου None, δηλαδή ο χρήστης δεν έχει εισάγει κωδικό προϊόντος, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500.
  
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

  Στον παραπάνω κώδικα, ορίζουμε το endpoint σε ```/add-to-cart``` καθώς και την μέθοδο που θα χρησιμοποιήσουμε GET για να αναζητήσουμε και επιστρέψουμε τα στοιχεία ενός προϊόντος με βάση τον κωδικό του από το σύστημα για να το εισάγουμε στο καλάθι αγορών. Έπειτα, φτιάχνουμε μια συνάρτηση ```add_to_cart()``` και μέσα της αποθηκεύουμε στη μεταβλητή ```auth_id``` τον αναγνωριστικό κωδικό του χρήστη που το έχει εισάγει στα headers του μηνύματος, στη μεταβλητή ```p_code``` αποθηκεύουμε τον κωδικό του προϊόντος που θέλει ο χρήστης να πραγματοποιήσει αναζήτηση και στη μεταβλητή ```p_quan``` την ποσότητα του προϊόντος που θέλει να προσθέσει στο καλάθι, εισάγωντας στο url του endpoint τα arguments, π.χ. ```/add-to-cart?code=4234dfsjdfsdfsd3434&quantity=5```. Σε περίπτωση που το argument code ή quantity είναι τύπου None, δηλαδή ο χρήστης δεν έχει εισάγει κωδικό ή ποσότητα προϊόντος, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500.
  
  Καλώντας την ```is_session_valid()``` συνάρτηση, αν το αναγνωριστικό του χρήστη υπάρχει στο ευρετήριο ```users_sessions```, δηλαδή αν ο χρήστης είναι συνδεδεμένος, τότε αποθηκεύουμε στη μεταβλητή ```user_email``` το email του χρήστη που το παίρνουμε από το ευρετήριο ```users_sessions``` μέσω του αναγνωριστικού του χρήστη και στη μεταβλητή ```user_cat``` αποθηκεύουμε το αποτέλεσμα της αναζήτησης με το email του χρήστη στο collection Users προκειμένου να μπορούμε να ανακτήσουμε την κατηγορία του. Έπειτα, για να αποφύγουμε την περίπτωση κάποιος συνδεδεμένος διαχειριστής να μπορεί να χρησιμοποιήσει το endpoint του απλού χρήστη, ελέγχουμε μέσω της μεταβλητής ```user_cat``` αν η κατηγορία του συνδεδεμένου χρήστη είναι "simple user", δηλαδή απλός χρήστης.
  
```
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
```

  Αν ο χρήστης είναι απλός, τότε αποθηκεύουμε σε μεταβλητή ```res``` το αποτέλεσμα της αναζήτησης προϊόντος με βάση τον κωδικό του χρησιμοποιώντας το argument ```p_code```. Επειδή ο κωδικός προϊόντος αποδίδεται αυτόματα όταν γίνεται εισαγωγή προϊόντος στο collection Products από την mongodb και είναι τύπου αντικειμένου ObjectId, μέσω της εισαγωγής της βιβλιοθήκης ```bson.objectid``` στο προγραμμά μας, μπορούμε να μετατρέψουμε τον κωδικό ```p_code``` που εισήγαγε ο χρήστης ως argument σε τύπο που να αναγνωρίζει η mongodb βάση. 
  
  Αν βρεθεί το προϊόν με τον δωθέν κωδικό, δηλαδή αν η μεταβλητή ```res``` δεν είναι τύπου None/κενή, τότε ελέγχουμε αν η ποσότητα ```p_quan``` που εισήγαγε ο χρήστης είναι μικρότερη ή ίση με το απόθεμα του προϊόντος στη βάση, δηλαδή αν υπάρχει αρκετό απόθεμα για να προστεθεί το προϊόν στο καλάθι και να ικανοποιεί την ζητούμενη ποσότητα του χρήστη. Αν υπάρχει αρκετό απόθεμα, τότε δημιουργούμε ευρετήριο με το προϊόν που ζήτησε ο χρήστης παιρνόντας το id, όνομα, τιμή και ποσότητα ως κλειδιά και προσθέτουμε αυτό το ευρετήριο (προϊόν) στο στοιχείο ```products``` της λίστας του καλαθιού. Έπειτα, υπολογίζουμε το συνολικό κόστος πολλαπλασιάζοντας την τιμή και την ποσότητα του προϊόντος που εισάγαμε στο καλάθι και αποθηκεύουμε το συνολικό κόστος στο στοιχείο ```total_cost``` του καλαθιού. Για να αποφύγουμε πολλά ψηφία μετά την υποδιαστολή, στρογγυλοποιούμε το συνολικό κόστος σε 2 ψηφία μετά την υποδιαστολή. Έπειτα, επιστρέφουμε το καλάθι αγορών στο χρήστη μαζί με κωδικό επιτυχίας 200.
  
  Αν δεν υπάρχει αρκετό απόθεμα, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 400.
  
  Αν δεν βρεθεί το προϊόν με το δωθέν κωδικό στο collection Products, επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 400. 
  
  Αν ο χρήστης είναι τύπου διαχειριστής, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 401. 
  
  Σε περίπτωση που έχει γίνει λάθος αυθεντικοποίηση του χρήστη, δηλαδή το user_uuid δεν αντιστοιχεί σε κάποιον χρήστη του ευρετηρίου ```users_sessions```, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 401.

### 7. Εμφάνιση του καλαθιού αγορών του χρήστη - ```/show-cart``` endpoint

```
# Εμφάνιση του καλαθιού με τα προϊόντα προς αγορά
@app.route('/show-cart', methods=['GET'])
def show_cart():
    auth_id = request.headers.get('authorization')

    if(is_session_valid(auth_id)):
        user_email = users_sessions[auth_id][0]
        user_cat = users_db.find_one({"email": user_email})

        if(user_cat['category'] == "simple user"):
            return Response("Cart:\n\n"+json.dumps(cart), status=200, mimetype='application/json')
        else:
            return Response("Permission denied", status=401, mimetype='application/json')
    else:
        # Μήνυμα λάθους (λάθος id αυθεντικοποίησης)
        return Response("user is not authenticated", status=401, mimetype='application/json')
```

  Στον παραπάνω κώδικα, ορίζουμε το endpoint σε ```/add-to-cart``` καθώς και την μέθοδο που θα χρησιμοποιήσουμε GET για να αναζητήσουμε και επιστρέψουμε τα στοιχεία του χρήστη για να γίνει ο έλεγχος της κατηγορίας του. Έπειτα, φτιάχνουμε μια συνάρτηση ```show_cart()``` και μέσα της αποθηκεύουμε στη μεταβλητή ```auth_id``` τον αναγνωριστικό κωδικό του χρήστη που το έχει εισάγει στα headers του μηνύματος. 
  
  Έπειτα, καλώντας την ```is_session_valid()``` συνάρτηση, αν το αναγνωριστικό του χρήστη υπάρχει στο ευρετήριο ```users_sessions```, δηλαδή αν ο χρήστης είναι συνδεδεμένος, τότε αποθηκεύουμε στη μεταβλητή ```user_email``` το email του χρήστη που το παίρνουμε από το ευρετήριο ```users_sessions``` μέσω του αναγνωριστικού του χρήστη και στη μεταβλητή ```user_cat``` αποθηκεύουμε το αποτέλεσμα της αναζήτησης με το email του χρήστη στο collection Users προκειμένου να μπορούμε να ανακτήσουμε την κατηγορία του. Έπειτα, για να αποφύγουμε την περίπτωση κάποιος συνδεδεμένος διαχειριστής να μπορεί να χρησιμοποιήσει το endpoint του απλού χρήστη, ελέγχουμε μέσω της μεταβλητής ```user_cat``` αν η κατηγορία του συνδεδεμένου χρήστη είναι "simple user", δηλαδή απλός χρήστης.
  
  Αν ο χρήστης είναι απλός, τότε επιστρέφουμε αντικείμενο Response με το καλάθι αγορών του χρήστη μαζί με κωδικό επιτυχίας 200.
  
  Αν ο χρήστης είναι τύπου διαχειριστής, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 401.
  
  Σε περίπτωση που έχει γίνει λάθος αυθεντικοποίηση του χρήστη, δηλαδή το user_uuid δεν αντιστοιχεί σε κάποιον χρήστη του ευρετηρίου ```users_sessions```, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 401.

### 8. Διαγραφή προϊόντος απο το καλάθι αγορών του χρήστη - ```/delete-from-cart``` endpoint

```
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
```

  Στον παραπάνω κώδικα, ορίζουμε το endpoint σε ```/delete-from-cart``` καθώς και την μέθοδο που θα χρησιμοποιήσουμε DELETE για να διαγράψουμε ένα προϊόν από το καλάθι αγορών του χρήστη. Έπειτα, φτιάχνουμε μια συνάρτηση ```delete_from_cart()``` και μέσα της αποθηκεύουμε στη μεταβλητή ```auth_id``` τον αναγνωριστικό κωδικό του χρήστη που το έχει εισάγει στα headers του μηνύματος και στη μεταβλητή ```p_code``` αποθηκεύουμε τον κωδικό του προϊόντος που θέλει ο χρήστης να διαγράψει από το καλάθι αγορών εισάγωντας στο url του endpoint το argument, π.χ. ```/delete-from-cart?code=4234dfsjdfsdfsd3434```. Σε περίπτωση που το argument code είναι τύπου None, δηλαδή ο χρήστης δεν έχει εισάγει κωδικό προϊόντος, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500.
  
  Έπειτα, καλώντας την ```is_session_valid()``` συνάρτηση, αν το αναγνωριστικό του χρήστη υπάρχει στο ευρετήριο ```users_sessions```, δηλαδή αν ο χρήστης είναι συνδεδεμένος, τότε αποθηκεύουμε στη μεταβλητή ```user_email``` το email του χρήστη που το παίρνουμε από το ευρετήριο ```users_sessions``` μέσω του αναγνωριστικού του χρήστη και στη μεταβλητή ```user_cat``` αποθηκεύουμε το αποτέλεσμα της αναζήτησης με το email του χρήστη στο collection Users προκειμένου να μπορούμε να ανακτήσουμε την κατηγορία του. Έπειτα, για να αποφύγουμε την περίπτωση κάποιος συνδεδεμένος διαχειριστής να μπορεί να χρησιμοποιήσει το endpoint του απλού χρήστη, ελέγχουμε μέσω της μεταβλητής ```user_cat``` αν η κατηγορία του συνδεδεμένου χρήστη είναι "simple user", δηλαδή απλός χρήστης.
  
```
            products_in_cart = cart["products"]
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
```

  Αν ο χρήστης είναι απλός, τότε αποθηκεύουμε σε μια λίστα ```products_in_cart``` τα προϊόντα του καλαθιού αντλώντας την πληροφορία αυτή από την λίστα του καλαθιού και δημιμουργοουμε επίσης μεταβλητή found με τιμή False, η οποία θα χρησιμοποιηθεί για να δούμε αν βρέθηκε το προϊόν που θέλει να διαγράψει ο χρήστης στο καλάθι. Έπειτα, πραγματοποιούμε επανάληψη στη λίστα ```products_in_cart``` με τα προϊόντα του καλαθιού και ελέγχουμε αν ο κωδικός του προϊόντος που προσπελαύνουμε είναι ίσος με τον κωδικό ```p_code``` που εισήγαγε ο χρήστης. Σε περίπτωση που είναι, τότε θέτουμε τη μεταβλητή ```found``` σε True, αφαιρούμε το ανάλογο ποσό από το συνολικό κόστος, με βάση την ποσότητα και την τιμή του προϊόντος προς διαγραφή, και διαγράφουμε τελικά το προϊόν από τη λίστα του καλαθιού.
  
  Αν το προϊόν προς διαγραφή υπάρχει στο καλάθι αγορών, τότε επιστρέφουμε αντικείμενο Response με το ανανεωμένο καλάθι αγορών μαζί με κωδικό επιτυχίας 200.
  
  Αν το προϊόν προς διαγραφή δεν υπάρχει στο καλάθι αγορών, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 400.
  
  Αν ο χρήστης είναι τύπου διαχειριστής, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 401.
  
  Σε περίπτωση που έχει γίνει λάθος αυθεντικοποίηση του χρήστη, δηλαδή το user_uuid δεν αντιστοιχεί σε κάποιον χρήστη του ευρετηρίου ```users_sessions```, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 401.
  
### 9. Ολοκλήρωση αγορών - Πληρωμή προϊόντων - ```/payment``` endpoint

```
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
```

  Στον παραπάνω κώδικα, ορίζουμε το endpoint σε ```/payment``` καθώς και την μέθοδο που θα χρησιμοποιήσουμε PATCH για να ενημερώσουμε το ιστορικό παραγγελιών του χρήστη με τη νέα του αγορά. Έπειτα, φτιάχνουμε μια συνάρτηση ```payment()``` και μέσα της αρχικοποιούμε τη μεταβλητή ```data``` δίνοντας της τον τύπο None, δηλαδή ότι είναι κενή, η οποία θα χρησιμοποιηθεί για να προσπελάσουμε τα στοιχεία του χρήστη από το request του μηνύματος και αποθηκεύουμε στη μεταβλητή ```auth_id``` τον αναγνωριστικό κωδικό του χρήστη που το έχει εισάγει στα headers του μηνύματος. Φορτώνουμε τα δεδομένα από το request στη μεταβλητή ```data``` μέσω της μεθόδου ```loads()``` της βιβλιοθήκης json. Σε περίπτωση που υπάρξει error κατά την φόρτωση των δεδομένων του request, τότε επιστρέφουμε ```Response``` αντικείμενο στην κονσόλα με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500.
  
  #### ΣΗΜΕΙΩΣΗ: τα δεδομένα του request από το body του μηνύματος είναι σε μορφή json, δηλαδή ένα ευρετήριο με τα δεδομένα να είναι κλειδιά και τιμές, π.χ. ```{"card_number": "1234567890123456"}```
  
  Σε περίπτωση που δεν υπάρχουν δεδομένα στο request του μηνύματος, δηλαδή η μεταβλητή ```data``` έχει τιμή None, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500. Σε περίπτωση που δεν υπάρχει κάποιο από τα απαιτούμενα στοιχεία του χρήστη στο request του μηνύματος για να είναι έγκυρη η πληρωμή, δηλαδή αν δεν υπάρχει το κλειδί "card_number" στην μεταβλητή ```data```, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500.
  
  Έπειτα, καλώντας την ```is_session_valid()``` συνάρτηση, αν το αναγνωριστικό του χρήστη υπάρχει στο ευρετήριο ```users_sessions```, δηλαδή αν ο χρήστης είναι συνδεδεμένος, τότε αποθηκεύουμε στη μεταβλητή ```user_email``` το email του χρήστη που το παίρνουμε από το ευρετήριο ```users_sessions``` μέσω του αναγνωριστικού του χρήστη και στη μεταβλητή ```user_cat``` αποθηκεύουμε το αποτέλεσμα της αναζήτησης με το email του χρήστη στο collection Users προκειμένου να μπορούμε να ανακτήσουμε την κατηγορία του. Έπειτα, για να αποφύγουμε την περίπτωση κάποιος συνδεδεμένος διαχειριστής να μπορεί να χρησιμοποιήσει το endpoint του απλού χρήστη, ελέγχουμε μέσω της μεταβλητής ```user_cat``` αν η κατηγορία του συνδεδεμένου χρήστη είναι "simple user", δηλαδή απλός χρήστης.
  
```
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
```

  Αν ο χρήστης είναι απλός, τότε ελέγχουμε αν ο αριθμός κάρτας που εισήγαγε ο χρήστης είναι 16ψήφιος. Εαν είναι, δημιουργούμε ένα ευρετήριο ```receipt``` το οποίο θα περιέχει συνοπτικά το όνομα, την τιμή και την ποσότητα των προϊόντων που αγοράστηκαν καθώς και το συνολικό ποσό που πληρώθηκε για την αγορά τους. Tο συνολικό ποσό το αντλούμε κατευθείαν από το ευρετήριο του καλαθιού ```cart["products"]```. Έπειτα, πραγματοποιούμε επανάληψη στη λίστα με τα ```products``` που υπάρχουν στο ευρετήριο του καλαθιού αγορών και για κάθε προϊόν της λίστας δημιουργούμε ευρετήριο με το όνομα, τιμή, αγορασμένη ποσότητα του προϊόντος προς αγορά και το προσθέτουμε στο κλειδί ```products``` του ευρετηρίου της απόδειξης ```receipt```. Μετά το πέρας των επαναλήψεων, το ευρετήριο ```receipt``` θα περιέχει όλα τα προϊόντα που ήταν στο καλάθι αγορών του χρήστη. Έτσι, χρησιμοποιώντας την εντολή ```update_one``` πάμε και προσθέτουμε την απόδειξη στο ιστορικό παραγγελιών του συνδεδεμένου χρήστη. Προσθέτουμε το ευρετήριο ```receipt``` στη λίστα ```orderHistory``` του document του συνδεδεμένου χρήστη με τον τελεστή ```$push```. Τελικά, επιστρέφουμε αντικείμενο Response με την απόδειξη του χρήστη μαζί με τον κωδικό επιτυχίας 200.
  
  Σε περίπτωση που ο χρήστης έχει εισάγει λάθος αριθμό κάρτας, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 400.
  
  Αν ο χρήστης είναι τύπου διαχειριστής, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 401.
  
  Σε περίπτωση που έχει γίνει λάθος αυθεντικοποίηση του χρήστη, δηλαδή το user_uuid δεν αντιστοιχεί σε κάποιον χρήστη του ευρετηρίου ```users_sessions```, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 401.
  
### 10. Εμφάνιση ιστορικού παραγγελιών χρήστη - ```/show-order-history``` endpoint

```
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
```

  Στον παραπάνω κώδικα, ορίζουμε το endpoint σε ```/show-order-history``` καθώς και την μέθοδο που θα χρησιμοποιήσουμε GET για να επιστρέψουμε το ιστορικό παραγγελιών του χρήστη. Έπειτα, φτιάχνουμε μια συνάρτηση ```show_order_history()``` και μέσα της αποθηκεύουμε στη μεταβλητή ```auth_id``` τον αναγνωριστικό κωδικό του χρήστη που το έχει εισάγει στα headers του μηνύματος.
  
  Έπειτα, καλώντας την ```is_session_valid()``` συνάρτηση, αν το αναγνωριστικό του χρήστη υπάρχει στο ευρετήριο ```users_sessions```, δηλαδή αν ο χρήστης είναι συνδεδεμένος, τότε αποθηκεύουμε στη μεταβλητή ```user_email``` το email του χρήστη που το παίρνουμε από το ευρετήριο ```users_sessions``` μέσω του αναγνωριστικού του χρήστη και στη μεταβλητή ```user_cat``` αποθηκεύουμε το αποτέλεσμα της αναζήτησης με το email του χρήστη στο collection Users προκειμένου να μπορούμε να ανακτήσουμε την κατηγορία του. Έπειτα, για να αποφύγουμε την περίπτωση κάποιος συνδεδεμένος διαχειριστής να μπορεί να χρησιμοποιήσει το endpoint του απλού χρήστη, ελέγχουμε μέσω της μεταβλητής ```user_cat``` αν η κατηγορία του συνδεδεμένου χρήστη είναι "simple user", δηλαδή απλός χρήστης.
  
  Αν ο χρήστης είναι απλός, τότε δημιουργούμε μεταβλητή ```history``` στην οποία αποθηκεύουμε το αποτέλεσμα της αναζήτησης του συνδεδεμένου χρήστη με βάση το email του. Μέσα στην μέθοδο ```find_one``` διευκρινίζουμε μέσω της παραμέτρου ```{"orderHistory": 1, "_id": 0}``` ότι θέλουμε η μέθοδος να βρει τα στοιχεία του συνδεδεμένου χρήστη στο collection Users αλλά να επιστρέψει πίσω μόνο το πεδίο ```orderHistory``` χωρίς το πεδίο ```_id```. Το ποιο πεδίο θα επιστραφεί το ορίζουμε τον αριθμό 1 αν θέλουμε να επιστραφεί και με τον αριθμό 0 αν δεν θέλουμε. Στη συνέχεια, επιστρέφουμε αντικείμενο Response με το αποτέλεσμα της αναζήτησης του χρήστη, δηλαδή το ιστορικό παραγγελιών του, μαζί με κωδικό επιτυχίας 200.
  
  Αν ο χρήστης είναι τύπου διαχειριστής, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 401.
  
  Σε περίπτωση που έχει γίνει λάθος αυθεντικοποίηση του χρήστη, δηλαδή το user_uuid δεν αντιστοιχεί σε κάποιον χρήστη του ευρετηρίου ```users_sessions```, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 401.
  
### 11. Διαγραφή χρήστη από το σύστημα - ```/delete-account``` endpoint

```
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
```

  Στον παραπάνω κώδικα, ορίζουμε το endpoint σε ```/delete-account``` καθώς και την μέθοδο που θα χρησιμοποιήσουμε DELETE για να διαγράψουμε τον χρήστη από τη βάση δεδομένων. Έπειτα, φτιάχνουμε μια συνάρτηση ```delete_account()``` και μέσα της αποθηκεύουμε στη μεταβλητή ```auth_id``` τον αναγνωριστικό κωδικό του χρήστη που το έχει εισάγει στα headers του μηνύματος.
  
  Έπειτα, καλώντας την ```is_session_valid()``` συνάρτηση, αν το αναγνωριστικό του χρήστη υπάρχει στο ευρετήριο ```users_sessions```, δηλαδή αν ο χρήστης είναι συνδεδεμένος, τότε αποθηκεύουμε στη μεταβλητή ```user_email``` το email του χρήστη που το παίρνουμε από το ευρετήριο ```users_sessions``` μέσω του αναγνωριστικού του χρήστη και στη μεταβλητή ```user_cat``` αποθηκεύουμε το αποτέλεσμα της αναζήτησης με το email του χρήστη στο collection Users προκειμένου να μπορούμε να ανακτήσουμε την κατηγορία του. Έπειτα, για να αποφύγουμε την περίπτωση κάποιος συνδεδεμένος διαχειριστής να μπορεί να χρησιμοποιήσει το endpoint του απλού χρήστη, ελέγχουμε μέσω της μεταβλητής ```user_cat``` αν η κατηγορία του συνδεδεμένου χρήστη είναι "simple user", δηλαδή απλός χρήστης.
  
  Αν ο χρήστης είναι απλός, τότε με τη μέθοδο ```delete_one``` διαγράφουμε τον χρήστη από το collection Users χρησιμοποιώντας το email του και αφαιρούμε επίσης την εγγραφή του χρήστη μέσα στο ευρετήριο ```users_sessions``` με τους συνδεδεμένους χρήστες. Η διαγραφή από το ευρετήριο πραγματοποιείται με την εντολή ```del```. Έπειτα, επιστρέφουμε αντικείμενο Response με κατάλληλο μήνυμα επιτυχίας και με κωδικό επιτυχίας 200.
  
  Αν ο χρήστης είναι τύπου διαχειριστής, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 401.
  
  Σε περίπτωση που έχει γίνει λάθος αυθεντικοποίηση του χρήστη, δηλαδή το user_uuid δεν αντιστοιχεί σε κάποιον χρήστη του ευρετηρίου ```users_sessions```, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 401.
  
### 12. Εισαγωγή νέου προϊόντος στο σύστημα - ```/add-new-product``` endpoint

```
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
```

  Στον παραπάνω κώδικα, ορίζουμε το endpoint σε ```/add-new-product``` καθώς και την μέθοδο που θα χρησιμοποιήσουμε POST για να στείλουμε τα στοιχεία του προϊόντος στο σύστημα. Έπειτα, φτιάχνουμε μια συνάρτηση ```add_new_product()``` και μέσα της αρχικοποιούμε τη μεταβλητή ```data``` δίνοντας της τον τύπο None, δηλαδή ότι είναι κενή, η οποία θα χρησιμοποιηθεί για να προσπελάσουμε τα στοιχεία του προϊόντος από το request του μηνύματος και αποθηκεύουμε στη μεταβλητή ```auth_id``` τον αναγνωριστικό κωδικό του χρήστη που το έχει εισάγει στα headers του μηνύματος. Φορτώνουμε τα δεδομένα από το request στη μεταβλητή ```data``` μέσω της μεθόδου ```loads()``` της βιβλιοθήκης json. Σε περίπτωση που υπάρξει error κατά την φόρτωση των δεδομένων του request, τότε επιστρέφουμε ```Response``` αντικείμενο στην κονσόλα με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500.
  
  #### ΣΗΜΕΙΩΣΗ: τα δεδομένα του request από το body του μηνύματος είναι σε μορφή json, δηλαδή ένα ευρετήριο με τα δεδομένα να είναι κλειδιά και τιμές, π.χ. ```{"name": "Ariel", "price": 8.80, "description": "Best Ariel", "category": "cleaning", "stock": 30}```
  
  Σε περίπτωση που δεν υπάρχουν δεδομένα στο request του μηνύματος, δηλαδή η μεταβλητή ```data``` έχει τιμή None, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500. Σε περίπτωση που δεν υπάρχει κάποιο από τα απαιτούμενα στοιχεία του προϊόντος στο request του μηνύματος για να είναι έγκυρη η εισαγωγή του, δηλαδή αν δεν υπάρχει ένα από τα κλειδιά "name", "price", "description", "category", "stock" στην μεταβλητή ```data```, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500.
  
```
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
```

  Έπειτα, καλώντας την ```is_session_valid()``` συνάρτηση, αν το αναγνωριστικό του χρήστη υπάρχει στο ευρετήριο ```users_sessions```, δηλαδή αν ο χρήστης είναι συνδεδεμένος, τότε αποθηκεύουμε στη μεταβλητή ```user_email``` το email του χρήστη που το παίρνουμε από το ευρετήριο ```users_sessions``` μέσω του αναγνωριστικού του χρήστη και στη μεταβλητή ```user_cat``` αποθηκεύουμε το αποτέλεσμα της αναζήτησης με το email του χρήστη στο collection Users προκειμένου να μπορούμε να ανακτήσουμε την κατηγορία του. Έπειτα, για να αποφύγουμε την περίπτωση κάποιος συνδεδεμένος απλός χρήστης να μπορεί να χρησιμοποιήσει το endpoint του διαχειριστή, ελέγχουμε μέσω της μεταβλητής ```user_cat``` αν η κατηγορία του συνδεδεμένου χρήστη είναι "admin user", δηλαδή διαχειριστής.
  
  Αν ο χρήστης είναι διαχειριστής, τότε μέσω της μεθόδου ```insert_one``` εισάγουμε ένα νέο document προϊόντος στο collection Products αντλώντας στοιχεία από τη μεταβλητή ```data``` που περιέχει τα δεδομένα από το request body του μηνύματος. Έπειτα, επιστρέφουμε αντικείμενο Response με κατάλληλο μήνυμα επιτυχίας και κωδικό επιτυχίας 200.
  
  Αν ο χρήστης είναι απλός χρήστης, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 401.
  
  Σε περίπτωση που έχει γίνει λάθος αυθεντικοποίηση του χρήστη, δηλαδή το user_uuid δεν αντιστοιχεί σε κάποιον χρήστη του ευρετηρίου ```users_sessions```, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 401.
  
### 13. Διαγραφή προϊόντος από το σύστημα - ```/delete-product``` endpoint

```
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
```

  Στον παραπάνω κώδικα, ορίζουμε το endpoint σε ```/delete-product``` καθώς και την μέθοδο που θα χρησιμοποιήσουμε DELETE για να διαγράψουμε ένα προϊόν από το σύστημα. Έπειτα, φτιάχνουμε μια συνάρτηση ```delete_product()``` και μέσα της αποθηκεύουμε στη μεταβλητή ```auth_id``` τον αναγνωριστικό κωδικό του χρήστη που το έχει εισάγει στα headers του μηνύματος και στη μεταβλητή ```p_code``` αποθηκεύουμε τον κωδικό του προϊόντος που θέλει ο διαχειριστής να διαγράψει εισάγωντας στο url του endpoint το argument, π.χ. ```/delete-product?code=4234dfsjdfsdfsd3434```. Σε περίπτωση που το argument code είναι τύπου None, δηλαδή ο διαχειριστής δεν έχει εισάγει κωδικό προϊόντος, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500.
  
  Καλώντας την ```is_session_valid()``` συνάρτηση, αν το αναγνωριστικό του χρήστη υπάρχει στο ευρετήριο ```users_sessions```, δηλαδή αν ο χρήστης είναι συνδεδεμένος, τότε αποθηκεύουμε στη μεταβλητή ```user_email``` το email του χρήστη που το παίρνουμε από το ευρετήριο ```users_sessions``` μέσω του αναγνωριστικού του χρήστη και στη μεταβλητή ```user_cat``` αποθηκεύουμε το αποτέλεσμα της αναζήτησης με το email του χρήστη στο collection Users προκειμένου να μπορούμε να ανακτήσουμε την κατηγορία του. Έπειτα, για να αποφύγουμε την περίπτωση κάποιος συνδεδεμένος απλός χρήστης να μπορεί να χρησιμοποιήσει το endpoint του διαχειριστή, ελέγχουμε μέσω της μεταβλητής ```user_cat``` αν η κατηγορία του συνδεδεμένου χρήστη είναι "admin user", δηλαδή διαχειριστής.
  
```
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
```

  Αν ο χρήστης είναι διαχειριστής, τότε αποθηκεύουμε σε μεταβλητή ```product``` το αποτέλεσμα της αναζήτησης προϊόντος με βάση τον κωδικό του χρησιμοποιώντας το argument ```p_code```. Επειδή ο κωδικός προϊόντος αποδίδεται αυτόματα όταν γίνεται εισαγωγή προϊόντος στο collection Products από την mongodb και είναι τύπου αντικειμένου ObjectId, μέσω της εισαγωγής της βιβλιοθήκης ```bson.objectid``` στο προγραμμά μας, μπορούμε να μετατρέψουμε τον κωδικό ```p_code``` που εισήγαγε ο χρήστης ως argument σε τύπο που να αναγνωρίζει η mongodb βάση. Αν βρεθεί το προϊόν με τον δωθέν κωδικό, δηλαδή αν η μεταβλητή ```product``` δεν είναι τύπου None/κενή, τότε μέσω της μεθόδου ```delete_one``` διαγράφουμε από το collection Products το προϊόν με τον δωθέν κωδικό. Έπειτα, επιστρέφουμε κατάλληλο μήνυμα επιτυχίας και κωδικό επιτυχίας 200.
  
  Σε περίπτωση που δεν βρεθεί κάποιο προϊόν με τον δωθέν κωδικό, δηλαδή αν η μεταβλητή ```product``` είναι κενή κι επιστρέψει 0 καλώντας την μέθοδο ```count()``` πάνω της, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 400. 
  
  Σε περίπτωση που ο συνδεδεμένος χρήστης είναι απλός χρήστης, δηλαδή το πεδίο category του document του συνδεδεμένου χρήστη είναι "simple user", τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 401.
  
  Σε περίπτωση που έχει γίνει λάθος αυθεντικοποίηση του χρήστη, δηλαδή το user_uuid δεν αντιστοιχεί σε κάποιον χρήστη του ευρετηρίου ```users_sessions```, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 401.
  
### 14. Ενημέρωση στοιχείων προϊόντος του συστήματος - ```/update-product``` endpoint

```
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
```

  Στον παραπάνω κώδικα, ορίζουμε το endpoint σε ```/update-product``` καθώς και την μέθοδο που θα χρησιμοποιήσουμε PUT για να στείλουμε τα στοιχεία του προϊόντος που θέλουμε να ενημερώσουμε και να ενημερώσουμε τα πεδία του προϊόντος στο collection Products. Έπειτα, φτιάχνουμε μια συνάρτηση ```update_product()``` και μέσα της αρχικοποιούμε τη μεταβλητή ```data``` δίνοντας της τον τύπο None, δηλαδή ότι είναι κενή, η οποία θα χρησιμοποιηθεί για να προσπελάσουμε τα στοιχεία του προϊόντος που θέλουμε να ενημερώσουμε από το request του μηνύματος και αποθηκεύουμε στη μεταβλητή ```auth_id``` τον αναγνωριστικό κωδικό του χρήστη που το έχει εισάγει στα headers του μηνύματος. Φορτώνουμε τα δεδομένα από το request στη μεταβλητή ```data``` μέσω της μεθόδου ```loads()``` της βιβλιοθήκης json. Σε περίπτωση που υπάρξει error κατά την φόρτωση των δεδομένων του request, τότε επιστρέφουμε ```Response``` αντικείμενο στην κονσόλα με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500.
  
  #### ΣΗΜΕΙΩΣΗ: τα δεδομένα του request από το body του μηνύματος είναι σε μορφή json, δηλαδή ένα ευρετήριο με τα δεδομένα να είναι κλειδιά και τιμές, π.χ. ```{"name": "Ariel", "price": 8.80, "description": "Best Ariel", "stock": 30}```
  
  Σε περίπτωση που δεν υπάρχουν δεδομένα στο request του μηνύματος, δηλαδή η μεταβλητή ```data``` έχει τιμή None, τότε επιστρέφουμε αντικείμενο Response με κατάλληλο error μήνυμα και κωδικό αποτυχίας 500.
  
  Καλώντας την ```is_session_valid()``` συνάρτηση, αν το αναγνωριστικό του χρήστη υπάρχει στο ευρετήριο ```users_sessions```, δηλαδή αν ο χρήστης είναι συνδεδεμένος, τότε αποθηκεύουμε στη μεταβλητή ```user_email``` το email του χρήστη που το παίρνουμε από το ευρετήριο ```users_sessions``` μέσω του αναγνωριστικού του χρήστη και στη μεταβλητή ```user_cat``` αποθηκεύουμε το αποτέλεσμα της αναζήτησης με το email του χρήστη στο collection Users προκειμένου να μπορούμε να ανακτήσουμε την κατηγορία του. Έπειτα, για να αποφύγουμε την περίπτωση κάποιος συνδεδεμένος απλός χρήστης να μπορεί να χρησιμοποιήσει το endpoint του διαχειριστή, ελέγχουμε μέσω της μεταβλητής ```user_cat``` αν η κατηγορία του συνδεδεμένου χρήστη είναι "admin user", δηλαδή διαχειριστής.
  
```
            product = products_db.find_one({"_id": ObjectId(str(p_code))})
            if product != None:
                acceptable_keys = ["name", "price", "description", "stock"]
                non_acc_keys = False
                
                for key in data:
                    if(key not in acceptable_keys):
                        non_acc_keys = True
```

  
