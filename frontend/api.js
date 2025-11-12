// API Client
class ApiClient {
    constructor() {
        this.baseURL = CONFIG.API_BASE_URL;
    }

    // Get stored access token
    getAccessToken() {
        return localStorage.getItem(CONFIG.STORAGE_KEYS.ACCESS_TOKEN);
    }

    // Set access token
    setAccessToken(token) {
        localStorage.setItem(CONFIG.STORAGE_KEYS.ACCESS_TOKEN, token);
    }

    // Get refresh token
    getRefreshToken() {
        return localStorage.getItem(CONFIG.STORAGE_KEYS.REFRESH_TOKEN);
    }

    // Set refresh token
    setRefreshToken(token) {
        localStorage.setItem(CONFIG.STORAGE_KEYS.REFRESH_TOKEN, token);
    }

    // Clear tokens
    clearTokens() {
        localStorage.removeItem(CONFIG.STORAGE_KEYS.ACCESS_TOKEN);
        localStorage.removeItem(CONFIG.STORAGE_KEYS.REFRESH_TOKEN);
        localStorage.removeItem(CONFIG.STORAGE_KEYS.USER_DATA);
    }

    // Make API request
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const token = this.getAccessToken();

        const config = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };

        // Add authorization header if token exists
        if (token && !options.skipAuth) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, config);

            // Handle 401 Unauthorized - try to refresh token
            if (response.status === 401 && !options.skipRefresh) {
                const refreshed = await this.refreshAccessToken();
                if (refreshed) {
                    // Retry the request with new token
                    return this.request(endpoint, { ...options, skipRefresh: true });
                } else {
                    // Refresh failed, logout user
                    this.clearTokens();
                    window.location.reload();
                    throw new Error('Session expired. Please login again.');
                }
            }

            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new Error(data.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Refresh access token
    async refreshAccessToken() {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) return false;

        try {
            const response = await this.request(CONFIG.ENDPOINTS.AUTH.REFRESH, {
                method: 'POST',
                body: JSON.stringify({ refresh_token: refreshToken }),
                skipAuth: true,
                skipRefresh: true
            });

            if (response.access_token) {
                this.setAccessToken(response.access_token);
                if (response.refresh_token) {
                    this.setRefreshToken(response.refresh_token);
                }
                return true;
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    // GET request
    async get(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'GET' });
    }

    // POST request
    async post(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // PUT request
    async put(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // DELETE request
    async delete(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'DELETE' });
    }

    // Authentication APIs
    async getGoogleAuthUrl() {
        return this.get(CONFIG.ENDPOINTS.AUTH.GOOGLE_LOGIN, { skipAuth: true });
    }

    async getCurrentUser() {
        return this.get(CONFIG.ENDPOINTS.AUTH.ME);
    }

    async logout() {
        try {
            await this.post(CONFIG.ENDPOINTS.AUTH.LOGOUT);
        } finally {
            this.clearTokens();
        }
    }

    // Company APIs
    async listCompanies(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.get(`${CONFIG.ENDPOINTS.COMPANIES.LIST}?${query}`);
    }

    async createCompany(data) {
        return this.post(CONFIG.ENDPOINTS.COMPANIES.CREATE, data);
    }

    async getCompany(id) {
        return this.get(CONFIG.ENDPOINTS.COMPANIES.GET(id));
    }

    async updateCompany(id, data) {
        return this.put(CONFIG.ENDPOINTS.COMPANIES.UPDATE(id), data);
    }

    async deleteCompany(id) {
        return this.delete(CONFIG.ENDPOINTS.COMPANIES.DELETE(id));
    }

    async getCompanyStats(id) {
        return this.get(CONFIG.ENDPOINTS.COMPANIES.STATS(id));
    }

    // User APIs
    async listUsers(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.get(`${CONFIG.ENDPOINTS.USERS.LIST}?${query}`);
    }

    async getUser(id) {
        return this.get(CONFIG.ENDPOINTS.USERS.GET(id));
    }

    async updateUser(id, data) {
        return this.put(CONFIG.ENDPOINTS.USERS.UPDATE(id), data);
    }

    async updateUserPermissions(id, data) {
        return this.put(CONFIG.ENDPOINTS.USERS.PERMISSIONS(id), data);
    }

    async deactivateUser(id) {
        return this.post(CONFIG.ENDPOINTS.USERS.DEACTIVATE(id));
    }

    async activateUser(id) {
        return this.post(CONFIG.ENDPOINTS.USERS.ACTIVATE(id));
    }

    // Device APIs
    async getMyDevices() {
        return this.get(CONFIG.ENDPOINTS.DEVICES.MY_DEVICES);
    }

    async linkDevice(deviceCode) {
        return this.post(CONFIG.ENDPOINTS.DEVICES.LINK, { device_code: deviceCode });
    }

    async deleteDevice(id) {
        return this.delete(CONFIG.ENDPOINTS.DEVICES.DELETE(id));
    }

    // Invitation APIs
    async listInvitations() {
        return this.get(CONFIG.ENDPOINTS.INVITATIONS.LIST);
    }

    async sendInvitation(data) {
        return this.post(CONFIG.ENDPOINTS.INVITATIONS.SEND, data);
    }

    async cancelInvitation(id) {
        return this.delete(CONFIG.ENDPOINTS.INVITATIONS.CANCEL(id));
    }

    // Health APIs
    async checkHealth() {
        return this.get(CONFIG.ENDPOINTS.HEALTH.BASIC, { skipAuth: true });
    }

    async getDetailedHealth() {
        return this.get(CONFIG.ENDPOINTS.HEALTH.DETAILED);
    }
}

// Create global API instance
const api = new ApiClient();
