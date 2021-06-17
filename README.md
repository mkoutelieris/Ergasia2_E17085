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
  
  #### ΣΗΜΕΙΩΣΗ: τα δεδομένα του request του μηνύματος είναι σε μορφή json, δηλαδή ένα ευρετήριο με τα δεδομένα να είναι κλειδιά και τιμές, π.χ. {"email": "john@example.com", "name": "John", ...}
  
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
