// API Configuration
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
    API_VERSION: 'v1',

    // Storage keys
    STORAGE_KEYS: {
        ACCESS_TOKEN: 'access_token',
        REFRESH_TOKEN: 'refresh_token',
        USER_DATA: 'user_data'
    },

    // API endpoints
    ENDPOINTS: {
        AUTH: {
            GOOGLE_LOGIN: '/api/v1/auth/google/login',
            GOOGLE_CALLBACK: '/api/v1/auth/google/callback',
            REFRESH: '/api/v1/auth/refresh',
            LOGOUT: '/api/v1/auth/logout',
            ME: '/api/v1/auth/me'
        },
        COMPANIES: {
            LIST: '/api/v1/companies',
            CREATE: '/api/v1/companies',
            GET: (id) => `/api/v1/companies/${id}`,
            UPDATE: (id) => `/api/v1/companies/${id}`,
            DELETE: (id) => `/api/v1/companies/${id}`,
            STATS: (id) => `/api/v1/companies/${id}/stats`
        },
        USERS: {
            LIST: '/api/v1/users',
            ME: '/api/v1/users/me',
            GET: (id) => `/api/v1/users/${id}`,
            UPDATE: (id) => `/api/v1/users/${id}`,
            PERMISSIONS: (id) => `/api/v1/users/${id}/permissions`,
            DEACTIVATE: (id) => `/api/v1/users/${id}/deactivate`,
            ACTIVATE: (id) => `/api/v1/users/${id}/activate`
        },
        DEVICES: {
            MY_DEVICES: '/api/v1/devices/my-devices',
            LINK: '/api/v1/devices/link',
            DELETE: (id) => `/api/v1/devices/${id}`
        },
        INVITATIONS: {
            LIST: '/api/v1/invitations',
            SEND: '/api/v1/invitations',
            CANCEL: (id) => `/api/v1/invitations/${id}`
        },
        HEALTH: {
            BASIC: '/api/v1/health',
            DETAILED: '/api/v1/health/detailed'
        }
    }
};
