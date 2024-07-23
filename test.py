from pymongo import MongoClient

mongodb_uri = "mongodb+srv://adel:ajjC7WOzmGdIBkXy@cluster0.ityqagd.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true"

try:
    client = MongoClient(mongodb_uri)
    client.admin.command('ping')
    print("Connected to MongoDB Atlas successfully!")
except Exception as e:
    print(f"An error occurred: {e}")
