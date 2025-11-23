# Email Verification Setup Guide

## Overview
The ATS Scanner now includes email verification to ensure users have valid email addresses and prevent bot signups.

## How It Works

1. **User Signs Up** → Account created as "unverified"
2. **Verification Email Sent** → 6-digit code sent to user's email
3. **User Enters Code** → On verification page
4. **Account Activated** → User can now login and use the app

## Gmail SMTP Setup

### Step 1: Enable 2-Step Verification
1. Go to https://myaccount.google.com/security
2. Click on "2-Step Verification"
3. Follow the prompts to enable it

### Step 2: Create App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" for app type
3. Select "Other (Custom name)" for device
4. Enter "ATS Scanner" as the name
5. Click "Generate"
6. **Copy the 16-character password** (looks like: `abcd efgh ijkl mnop`)

### Step 3: Update .env File
Add these lines to your `.env` file:

```env
# Email Configuration (Gmail SMTP)
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
```

Replace:
- `your-email@gmail.com` with your Gmail address
- `abcdefghijklmnop` with the 16-character app password (remove spaces)

## Testing

1. **Start the backend server**:
   ```bash
   uvicorn backend.backend_api:app --reload --port 8000
   ```

2. **Start the frontend server**:
   ```bash
   cd frontend
   python3 -m http.server 8080
   ```

3. **Test the flow**:
   - Go to http://localhost:8080/signup.html
   - Sign up with a real email address
   - Check your email for the verification code
   - Enter the code on the verification page
   - You should be logged in automatically

## Features

### For Users:
- ✅ Secure email verification
- ✅ 6-digit code (easy to type)
- ✅ Code expires in 15 minutes
- ✅ Resend code option
- ✅ Beautiful email templates
- ✅ Welcome email after verification

### For Developers:
- ✅ Prevents fake signups
- ✅ Validates email addresses
- ✅ Bot protection
- ✅ Clean user database

## API Endpoints

### 1. Signup (Modified)
```
POST /api/auth/signup
```
Now creates unverified account and sends verification email.

**Response:**
```json
{
  "message": "Account created successfully. Please check your email for verification code.",
  "email": "user@example.com",
  "user_id": "..."
}
```

### 2. Verify Email (New)
```
POST /api/auth/verify-email
```

**Request:**
```json
{
  "email": "user@example.com",
  "verification_code": "123456"
}
```

**Response:**
```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": { ... }
}
```

### 3. Resend Verification (New)
```
POST /api/auth/resend-verification
```

**Request:**
```json
{
  "email": "user@example.com"
}
```

### 4. Login (Modified)
Now checks if email is verified before allowing login.

## Troubleshooting

### Email not sending?
1. Check your Gmail credentials in `.env`
2. Make sure 2-Step Verification is enabled
3. Verify the App Password is correct (no spaces)
4. Check backend console for error messages

### "Less secure app access" error?
- You need to use an **App Password**, not your regular Gmail password
- Regular passwords don't work anymore for SMTP

### Code expired?
- Codes expire after 15 minutes
- Click "Resend Code" to get a new one

### Already verified error?
- If you see this, your email is already verified
- Go to the login page instead

## Security Notes

- ⚠️ Never commit your `.env` file to Git
- ⚠️ Keep your App Password secret
- ⚠️ Codes expire after 15 minutes
- ⚠️ Each code can only be used once
- ⚠️ Unverified accounts cannot login

## Production Recommendations

For production, consider using:
- **SendGrid** - Professional email service
- **AWS SES** - Amazon's email service
- **Resend** - Modern email API

These services offer:
- Better deliverability
- Email analytics
- Higher sending limits
- Custom domains
- Professional templates

