# Simple Digital Signage - Database Schema

## Database Design Overview
This document describes the PostgreSQL database schema for the Simple Digital Signage application.

## Tables

### 1. users
Stores all user information (Super Admin, Admin, and Users)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    google_id VARCHAR(255) UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    profile_picture_url TEXT,
    role VARCHAR(50) NOT NULL CHECK (role IN ('super_admin', 'admin', 'user')),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    can_add_devices BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_company_id ON users(company_id);
CREATE INDEX idx_users_role ON users(role);
```

**Fields:**
- `id`: Unique identifier for each user
- `email`: User's email address (unique)
- `google_id`: Google account ID for SSO authentication
- `full_name`: User's full name
- `profile_picture_url`: URL to user's profile picture from Google
- `role`: User role (super_admin, admin, or user)
- `company_id`: Reference to company (NULL for super_admin)
- `can_add_devices`: Permission flag set by admin for users
- `is_active`: Account status
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp
- `last_login`: Last login timestamp

---

### 2. companies
Stores company/organization information

```sql
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(100) UNIQUE,
    logo_url TEXT,
    is_active BOOLEAN DEFAULT true,
    max_users INTEGER DEFAULT 10,
    max_devices INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_companies_subdomain ON companies(subdomain);
```

**Fields:**
- `id`: Unique identifier for each company
- `name`: Company name
- `subdomain`: Unique subdomain for the company (optional)
- `logo_url`: Company logo URL
- `is_active`: Company status
- `max_users`: Maximum number of users allowed
- `max_devices`: Maximum number of devices allowed
- `created_at`: Company creation timestamp
- `updated_at`: Last update timestamp

---

### 3. invitations
Tracks invitations sent by super admin to companies/admins

```sql
CREATE TABLE invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'user')),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    invited_by UUID REFERENCES users(id) ON DELETE SET NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'expired', 'cancelled')),
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accepted_at TIMESTAMP
);

CREATE INDEX idx_invitations_email ON invitations(email);
CREATE INDEX idx_invitations_token ON invitations(token);
CREATE INDEX idx_invitations_status ON invitations(status);
```

**Fields:**
- `id`: Unique identifier for each invitation
- `email`: Email address of the invitee
- `role`: Role to be assigned (admin or user)
- `company_id`: Company the user will belong to
- `invited_by`: User who sent the invitation
- `token`: Unique token for invitation link
- `status`: Invitation status
- `expires_at`: Expiration timestamp
- `created_at`: Invitation creation timestamp
- `accepted_at`: When invitation was accepted

---

### 4. google_credentials
Stores Google Cloud credentials for each company (managed by admins)

```sql
CREATE TABLE google_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID UNIQUE REFERENCES companies(id) ON DELETE CASCADE,
    client_id VARCHAR(500) NOT NULL,
    client_secret VARCHAR(500) NOT NULL,
    project_id VARCHAR(255),
    service_account_email VARCHAR(255),
    credentials_json TEXT NOT NULL,
    is_valid BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_validated TIMESTAMP
);

CREATE INDEX idx_google_credentials_company_id ON google_credentials(company_id);
```

**Fields:**
- `id`: Unique identifier
- `company_id`: Company these credentials belong to (one per company)
- `client_id`: Google OAuth client ID
- `client_secret`: Google OAuth client secret (encrypted)
- `project_id`: Google Cloud project ID
- `service_account_email`: Service account email
- `credentials_json`: Full credentials JSON (encrypted)
- `is_valid`: Whether credentials are currently valid
- `created_by`: Admin who added the credentials
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `last_validated`: Last time credentials were validated

---

### 5. devices
Stores TV/device information linked to users

```sql
CREATE TABLE devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    device_name VARCHAR(255) NOT NULL,
    device_code VARCHAR(4) UNIQUE,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    is_online BOOLEAN DEFAULT false,
    is_linked BOOLEAN DEFAULT false,
    current_playlist_id UUID,
    last_seen TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    linked_at TIMESTAMP
);

CREATE INDEX idx_devices_user_id ON devices(user_id);
CREATE INDEX idx_devices_company_id ON devices(company_id);
CREATE INDEX idx_devices_device_code ON devices(device_code);
```

**Fields:**
- `id`: Unique identifier
- `user_id`: User who owns this device
- `company_id`: Company this device belongs to
- `device_name`: Name given to the device
- `device_code`: 4-digit pairing code
- `device_id`: Unique device identifier
- `is_online`: Current online status
- `is_linked`: Whether device is linked to a user
- `current_playlist_id`: Currently playing playlist
- `last_seen`: Last activity timestamp
- `created_at`: Device registration timestamp
- `updated_at`: Last update timestamp
- `linked_at`: When device was linked to user

---

### 6. google_drive_tokens
Stores user's Google Drive access tokens

```sql
CREATE TABLE google_drive_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    token_expiry TIMESTAMP NOT NULL,
    scope TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_google_drive_tokens_user_id ON google_drive_tokens(user_id);
```

**Fields:**
- `id`: Unique identifier
- `user_id`: User who owns this token
- `access_token`: Google Drive access token (encrypted)
- `refresh_token`: Google Drive refresh token (encrypted)
- `token_expiry`: When the access token expires
- `scope`: OAuth scopes granted
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

---

### 7. content (For future use)
Stores media content information

```sql
CREATE TABLE content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content_type VARCHAR(50) CHECK (content_type IN ('image', 'video')),
    file_format VARCHAR(10),
    google_drive_file_id VARCHAR(255),
    local_storage_path TEXT,
    file_size BIGINT,
    duration INTEGER,
    thumbnail_url TEXT,
    is_cached BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_content_user_id ON content(user_id);
CREATE INDEX idx_content_company_id ON content(company_id);
```

---

### 8. playlists (For future use)
Stores playlist information

```sql
CREATE TABLE playlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_playlists_user_id ON playlists(user_id);
```

---

### 9. playlist_content (For future use)
Links content to playlists with ordering

```sql
CREATE TABLE playlist_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    playlist_id UUID REFERENCES playlists(id) ON DELETE CASCADE,
    content_id UUID REFERENCES content(id) ON DELETE CASCADE,
    display_order INTEGER NOT NULL,
    display_duration INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(playlist_id, content_id)
);

CREATE INDEX idx_playlist_content_playlist_id ON playlist_content(playlist_id);
```

---

### 10. audit_logs
Tracks all important actions in the system

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

---

## User Hierarchy and Permissions

### Super Admin
- Can create and manage companies
- Can invite admins to companies
- Can view all users, devices, and content across all companies
- Can deactivate companies or users
- Has full system access

### Admin (Company Level)
- Can invite and manage users within their company
- Can set `can_add_devices` permission for users
- Can add/edit Google Cloud credentials for their company
- Can view all users and devices within their company
- Cannot access other companies' data

### User
- Can link Google Drive account
- Can add devices (if `can_add_devices` = true)
- Can manage their own content and playlists
- Can only see their own data
- Cannot invite other users

## Relationships

```
Super Admin (1) ──> (*) Companies
Companies (1) ──> (*) Admins
Companies (1) ──> (*) Users
Companies (1) ──> (1) Google Credentials
Admin (1) ──> (*) Users (within company)
Users (1) ──> (*) Devices
Users (1) ──> (*) Content
Users (1) ──> (*) Playlists
Playlists (*) ──> (*) Content (through playlist_content)
```

## Security Considerations

1. **Encryption**: All sensitive fields (passwords, tokens, credentials) must be encrypted at rest
2. **Row Level Security**: Implement PostgreSQL RLS policies to ensure data isolation between companies
3. **API Authentication**: All API endpoints require valid JWT tokens with appropriate role checks
4. **Audit Logging**: All critical actions are logged in audit_logs table
5. **Token Expiry**: Invitation tokens and access tokens have expiry timestamps

## Indexes

Indexes are created on:
- Foreign keys for join performance
- Frequently queried fields (email, role, status)
- Unique constraints for data integrity
