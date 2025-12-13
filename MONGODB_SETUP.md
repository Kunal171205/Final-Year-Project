# MongoDB Setup Guide

## Installation

1. Install Python packages:
```bash
pip install -r requirements.txt
```

2. Install MongoDB (if using local MongoDB):
   - Download from: https://www.mongodb.com/try/download/community
   - Or use MongoDB Atlas (cloud): https://www.mongodb.com/cloud/atlas

## Configuration

### Option 1: Local MongoDB
- Default connection: `mongodb://localhost:27017/`
- No changes needed if MongoDB is running locally

### Option 2: MongoDB Atlas (Cloud)
1. Create account at https://www.mongodb.com/cloud/atlas
2. Create a cluster
3. Get your connection string (format: `mongodb+srv://username:password@cluster.mongodb.net/`)
4. Set environment variable:
   ```bash
   # Windows PowerShell
   $env:MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/"
   
   # Windows CMD
   set MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
   
   # Or update app.py directly
   ```

## Usage Examples

### Insert Data
```python
collection = db['users']
user = {
    "name": "John Doe",
    "email": "john@example.com",
    "location": {"lat": 18.5204, "lng": 73.8567}
}
collection.insert_one(user)
```

### Find Data
```python
collection = db['users']
users = collection.find({"name": "John Doe"})
for user in users:
    print(user)
```

### Update Data
```python
collection = db['users']
collection.update_one(
    {"email": "john@example.com"},
    {"$set": {"name": "Jane Doe"}}
)
```

### Delete Data
```python
collection = db['users']
collection.delete_one({"email": "john@example.com"})
```

## API Endpoints

- `GET /api/data` - Get data from MongoDB
- `POST /api/data` - Insert data into MongoDB

## Testing Connection

Run your Flask app and check the console for:
- ✅ "Successfully connected to MongoDB!" - Connection successful
- ❌ "Error connecting to MongoDB" - Check your connection string



