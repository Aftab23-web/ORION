# Terms and Conditions Implementation

## Overview
This update adds Terms and Conditions functionality to the application. Users will now be required to accept the terms and conditions after logging in for the first time.

## Changes Made

### 1. Database Changes
- **Updated Schema**: Added two new columns to the `users` table:
  - `terms_accepted` (BOOLEAN): Tracks whether user has accepted terms
  - `terms_accepted_at` (TIMESTAMP): Records when terms were accepted

- **Migration Script**: Created `database/migration_add_terms_acceptance.sql` to update existing databases

### 2. New Template
- **Created**: `templates/terms_and_conditions.html`
  - Professional terms and conditions page
  - Clear educational disclaimers
  - Risk warnings
  - User responsibilities
  - Accept button to proceed

### 3. Authentication Updates
- **Modified**: `routes/auth_routes.py`
  - Login handler now checks if user has accepted terms
  - Redirects to terms page if not accepted
  - Added two new routes:
    - `GET /auth/terms-and-conditions`: Display terms page
    - `POST /auth/accept-terms`: Handle terms acceptance
  - Tracks terms acceptance in audit log

### 4. Application Updates
- **Modified**: `app.py`
  - Removed old `/disclaimer` route (replaced with terms)
  - Updated authentication middleware to enforce terms acceptance
  - Updated public routes list

### 5. Navigation Updates
- **Modified**: `templates/base.html`
  - Changed "Disclaimer" link to "Terms" in navigation
  - Links to new terms and conditions page

## User Flow

1. **User logs in** → Authentication successful
2. **System checks** → Has user accepted terms?
   - **No** → Redirect to Terms and Conditions page
   - **Yes** → Proceed to dashboard
3. **User reads terms** → Clicks "I Accept"
4. **System records** → Updates database and audit log
5. **User proceeds** → Redirected to dashboard

## Migration Instructions

### For New Installations
Simply run the main schema file:
```sql
mysql -u root -p < database/schema.sql
```

### For Existing Installations
Run the migration script:
```sql
mysql -u root -p < database/migration_add_terms_acceptance.sql
```

**Note**: By default, existing users will need to accept terms on their next login. If you want to auto-accept for existing users, uncomment the UPDATE statement in the migration script.

## Features

### User Benefits
- Clear understanding of platform purpose
- Educational disclaimers
- Risk warnings
- User rights and responsibilities

### System Benefits
- Legal protection
- Audit trail of acceptances
- Session-based enforcement
- Database tracking

### Security Features
- Terms acceptance tracked per user
- Timestamp of acceptance recorded
- Audit log entry created
- Session validation on every request

## Testing

### Test Cases
1. **New User Registration**
   - Register → Login → See Terms → Accept → Dashboard

2. **Existing User (Terms Not Accepted)**
   - Login → Redirected to Terms → Accept → Dashboard

3. **Existing User (Terms Accepted)**
   - Login → Dashboard (no redirect)

4. **Access Protection**
   - Try to access protected pages → Redirected to Terms if not accepted

5. **Navigation**
   - Check "Terms" link in navigation works
   - Verify disclaimer removed from navigation

## Configuration
No additional configuration required. The system uses existing session management and database connections.

## Notes
- Terms page is accessible to logged-in users only
- Users cannot access other pages until terms are accepted
- Users can view terms again from navigation menu
- The old disclaimer.html template is not used anymore but kept for reference
