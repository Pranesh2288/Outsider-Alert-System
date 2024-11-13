from pymongo import MongoClient

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['AccessTracker']
collection = db['Entries']

def delete_user():
    user_id = input("Enter the ID of the user to delete (or type 'exit' to quit): ")
    if user_id.lower() == 'exit':
        return
    
    # Search for the user by id
    user = collection.find_one({'id': user_id})
    
    if user:
        print(f"User found: {user['name']} (Access level: {user['access']})")
        
        confirm = input(f"Are you sure you want to delete the user {user['name']}? (yes/no): ").lower()
        if confirm == 'yes':
            # Delete the user from the database
            collection.delete_one({'id': user_id})
            print(f"User {user['name']} with ID {user_id} has been deleted.")
        else:
            print("Deletion canceled.")
    else:
        print("No user found with the given ID.")

if __name__ == '__main__':
    while True:
        delete_user()
        cont = input("Do you want to delete another user? (yes/no): ").lower()
        if cont != 'yes':
            break
    print("Deletion process finished.")
