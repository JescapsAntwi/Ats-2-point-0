# MongoDB Setup Instructions

## Important: Replace Database Password

Your MongoDB URI has been added to the `.env` file, but you need to **replace `<db_password>`** with your actual database password.

### Steps:

1. **Open the `.env` file** in the project root directory

2. **Find this line:**
   ```
   MONGODB_URI=mongodb+srv://jescaps_db_user:<db_password>@cluster0.wclxgzz.mongodb.net/?appName=Cluster0
   ```

3. **Replace `<db_password>`** with your actual MongoDB Atlas database password

   For example:
   ```
   MONGODB_URI=mongodb+srv://your_username:your_password@cluster0.xxxxx.mongodb.net/?appName=Cluster0
   ```
   
   ⚠️ **Important**: Never commit your actual credentials to Git. Keep them only in your local `.env` file.

4. **Save the file**

## Verify Your MongoDB Atlas Setup

Make sure you've completed these steps in MongoDB Atlas:

1. ✅ **Database User Created**
   - Username: `jescaps_db_user`
   - Password: (your password)
   - User has read/write permissions

2. ✅ **Network Access Configured**
   - Your IP address is whitelisted, OR
   - `0.0.0.0/0` is allowed (for development only)

3. ✅ **Cluster is Running**
   - Your cluster `Cluster0` is active

## Test the Connection

After updating the password in `.env`, test the connection by starting the backend:

```bash
cd backend
uvicorn backend_api:app --reload --port 8000
```

If the connection is successful, you should see:
```
Successfully connected to MongoDB database: ats_scanner
```

If you see an error, check:
- Password is correct (no `<db_password>` placeholder)
- Network access allows your IP
- Database user has proper permissions
- Cluster is running

## Security Note

⚠️ **Never commit your `.env` file to version control!** It contains sensitive information.

The `.env` file should already be in `.gitignore`, but double-check to ensure your credentials stay secure.

