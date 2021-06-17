# Ergasia2_E17085
**ΠΑΝΕΠΙΣΤΗΜΙΟ ΠΕΙΡΑΙΩΣ** <br>
**ΤΜΗΜΑ ΨΗΦΙΑΚΩΝ ΣΥΣΤΗΜΑΤΩΝ** <br>
**_ΜΑΘΗΜΑ_**: Πληροφοριακά Συστήματα <br>
**_ΟΝ/ΝΥΜΟ_**: Κουτελιέρης Μιχάλης <br>
**_ΑΜ_**: Ε17085 <br>

## Επεξήγηση Υλοποίησης Ερωτημάτων Εργασίας

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
db = client['InfoSys']

# Choose collections
users_db = db['Users']
products_db = db['Products']

# Initialize cart
cart = {"products": [], "total_cost": 0}

# Initiate Flask App
app = Flask(__name__)
```

Στον παραπάνω κώδικα, εισάγουμε όλες τις βιβλιοθήκες που θα βοηθήσουν στην υλοποίηση των endpoints για το super market. Επιπρόσθετα από τις βιβλιοθήκες που υπήρχαν και στην 1η εργασία, έχει προστεθεί και η ObjectId βιβλιοθήκη για να μπορέσω να προσπελάσω και να επιστρέψω documents της mongodb με βάση το ```id``` που δίνει η βάση στα documents αυτόματα.

Έπειτα, πραγματοποιώ σύνδεση στη βάση mongodb μέσω του Mongodb URI και αποθηκεύω αυτή τη σύνδεση στη μεταβλητή client. Αποθηκεύω τη σύνδεση με το collection 
