// Application State
const app = {
    currentPage: 'overview',
    currentUser: null,
    loading: false
};

// UI Helper Functions
function showLoading() {
    document.getElementById('loading-overlay').classList.remove('hidden');
    app.loading = true;
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.add('hidden');
    app.loading = false;
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');

    toastMessage.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.remove('hidden');

    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

function showLoginPage() {
    document.getElementById('login-page').classList.remove('hidden');
    document.getElementById('dashboard-page').classList.add('hidden');
}

function showDashboardPage() {
    document.getElementById('login-page').classList.add('hidden');
    document.getElementById('dashboard-page').classList.remove('hidden');
}

// Initialize App
async function initApp() {
    console.log('Initializing app...');

    // Check if user is already logged in
    const token = api.getAccessToken();
    if (token) {
        try {
            showLoading();
            const user = await api.getCurrentUser();
            app.currentUser = user;
            await loadUserData();
            showDashboardPage();
            loadPage('overview');
        } catch (error) {
            console.error('Failed to load user:', error);
            api.clearTokens();
            showLoginPage();
        } finally {
            hideLoading();
        }
    } else {
        showLoginPage();
    }

    setupEventListeners();
}

// Setup Event Listeners
function setupEventListeners() {
    // Google Login Button
    document.getElementById('google-login-btn').addEventListener('click', handleGoogleLogin);

    // Manual Token Login
    document.getElementById('manual-login-btn').addEventListener('click', handleManualLogin);

    // Logout Button
    document.getElementById('logout-btn').addEventListener('click', handleLogout);

    // Navigation Items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            loadPage(page);
        });
    });

    // Refresh Button
    document.getElementById('refresh-btn').addEventListener('click', () => {
        loadPage(app.currentPage);
    });

    // Handle OAuth callback
    handleOAuthCallback();
}

// Handle Google Login
async function handleGoogleLogin() {
    try {
        showLoading();
        const response = await api.getGoogleAuthUrl();

        if (response.auth_url) {
            // Redirect to Google OAuth
            window.location.href = response.auth_url;
        }
    } catch (error) {
        hideLoading();
        showToast('Failed to initiate Google login: ' + error.message, 'error');
    }
}

// Handle Manual Token Login
async function handleManualLogin() {
    const token = document.getElementById('manual-token').value.trim();

    if (!token) {
        showToast('Please enter an access token', 'error');
        return;
    }

    try {
        showLoading();
        api.setAccessToken(token);

        const user = await api.getCurrentUser();
        app.currentUser = user;
        await loadUserData();

        showToast('Logged in successfully!', 'success');
        showDashboardPage();
        loadPage('overview');
    } catch (error) {
        api.clearTokens();
        showToast('Invalid token: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Handle OAuth Callback
function handleOAuthCallback() {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');

    if (code) {
        console.log('OAuth callback detected, code:', code);
        showToast('OAuth callback detected. Please exchange code for token manually.', 'warning');
        // In a production app, you would exchange the code for tokens here
    }
}

// Handle Logout
async function handleLogout() {
    try {
        showLoading();
        await api.logout();
        showToast('Logged out successfully', 'success');
        showLoginPage();
        app.currentUser = null;
    } catch (error) {
        showToast('Logout failed: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Load User Data
async function loadUserData() {
    if (!app.currentUser) return;

    // Update UI with user info
    document.getElementById('user-name').textContent = app.currentUser.full_name;
    document.getElementById('user-role').textContent = app.currentUser.role;

    if (app.currentUser.profile_picture_url) {
        document.getElementById('user-avatar').src = app.currentUser.profile_picture_url;
    }
}

// Load Page Content
async function loadPage(pageName) {
    app.currentPage = pageName;

    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        if (item.dataset.page === pageName) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // Update page title
    const titles = {
        overview: 'Overview',
        companies: 'Companies',
        users: 'Users',
        devices: 'Devices',
        invitations: 'Invitations'
    };
    document.getElementById('page-title').textContent = titles[pageName] || pageName;

    // Load page content
    const contentArea = document.getElementById('content-area');

    try {
        showLoading();

        switch (pageName) {
            case 'overview':
                await loadOverviewPage(contentArea);
                break;
            case 'companies':
                await loadCompaniesPage(contentArea);
                break;
            case 'users':
                await loadUsersPage(contentArea);
                break;
            case 'devices':
                await loadDevicesPage(contentArea);
                break;
            case 'invitations':
                await loadInvitationsPage(contentArea);
                break;
            default:
                contentArea.innerHTML = '<p>Page not found</p>';
        }
    } catch (error) {
        contentArea.innerHTML = `
            <div class="empty-state">
                <div class="icon">❌</div>
                <h3>Error Loading Page</h3>
                <p>${error.message}</p>
            </div>
        `;
    } finally {
        hideLoading();
    }
}

// Load Overview Page
async function loadOverviewPage(container) {
    const health = await api.getDetailedHealth();

    container.innerHTML = `
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Status</h3>
                <div class="value">${health.status.toUpperCase()}</div>
                <div class="label">System Health</div>
            </div>
            <div class="stat-card">
                <h3>Database</h3>
                <div class="value">${health.database}</div>
                <div class="label">Connection Status</div>
            </div>
            <div class="stat-card">
                <h3>Environment</h3>
                <div class="value">${health.environment.toUpperCase()}</div>
                <div class="label">Current Mode</div>
            </div>
            <div class="stat-card">
                <h3>Version</h3>
                <div class="value">${health.version}</div>
                <div class="label">API Version</div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h2>System Components</h2>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Component</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${Object.entries(health.components).map(([key, value]) => `
                            <tr>
                                <td>${key.charAt(0).toUpperCase() + key.slice(1)}</td>
                                <td>
                                    <span class="badge ${value === 'operational' ? 'badge-success' : 'badge-danger'}">
                                        ${value}
                                    </span>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

// Load Companies Page
async function loadCompaniesPage(container) {
    const companies = await api.listCompanies();

    if (companies.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">🏢</div>
                <h3>No Companies Yet</h3>
                <p>Create your first company to get started</p>
                <button class="btn-primary" onclick="createCompany()">Create Company</button>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h2>All Companies</h2>
                <button class="btn-secondary" onclick="createCompany()">+ New Company</button>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Subdomain</th>
                            <th>Users</th>
                            <th>Devices</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${companies.map(company => `
                            <tr>
                                <td><strong>${company.name}</strong></td>
                                <td>${company.subdomain || '-'}</td>
                                <td>${company.current_users} / ${company.max_users}</td>
                                <td>${company.current_devices} / ${company.max_devices}</td>
                                <td>
                                    <span class="badge ${company.is_active ? 'badge-success' : 'badge-danger'}">
                                        ${company.is_active ? 'Active' : 'Inactive'}
                                    </span>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

// Load Users Page
async function loadUsersPage(container) {
    const users = await api.listUsers();

    container.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h2>All Users</h2>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Role</th>
                            <th>Status</th>
                            <th>Last Login</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${users.map(user => `
                            <tr>
                                <td><strong>${user.full_name}</strong></td>
                                <td>${user.email}</td>
                                <td>
                                    <span class="badge badge-success">
                                        ${user.role.replace('_', ' ').toUpperCase()}
                                    </span>
                                </td>
                                <td>
                                    <span class="badge ${user.is_active ? 'badge-success' : 'badge-danger'}">
                                        ${user.is_active ? 'Active' : 'Inactive'}
                                    </span>
                                </td>
                                <td>${user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

// Load Devices Page
async function loadDevicesPage(container) {
    const devices = await api.getMyDevices();

    if (devices.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">📺</div>
                <h3>No Devices Linked</h3>
                <p>Link a device using the pairing code from your TV</p>
                <button class="btn-primary" onclick="linkDevice()">Link Device</button>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h2>My Devices</h2>
                <button class="btn-secondary" onclick="linkDevice()">+ Link Device</button>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Device Name</th>
                            <th>Status</th>
                            <th>Last Seen</th>
                            <th>Linked At</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${devices.map(device => `
                            <tr>
                                <td><strong>${device.device_name}</strong></td>
                                <td>
                                    <span class="badge ${device.is_online ? 'badge-success' : 'badge-danger'}">
                                        ${device.is_online ? 'Online' : 'Offline'}
                                    </span>
                                </td>
                                <td>${device.last_seen ? new Date(device.last_seen).toLocaleString() : 'Never'}</td>
                                <td>${device.created_at ? new Date(device.created_at).toLocaleDateString() : '-'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

// Load Invitations Page
async function loadInvitationsPage(container) {
    const invitations = await api.listInvitations();

    container.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h2>Invitations</h2>
                <button class="btn-secondary" onclick="sendInvitation()">+ Send Invitation</button>
            </div>
            <div class="table-container">
                ${invitations.length === 0 ? `
                    <div class="empty-state">
                        <div class="icon">✉️</div>
                        <h3>No Invitations</h3>
                        <p>Send your first invitation to add team members</p>
                    </div>
                ` : `
                    <table>
                        <thead>
                            <tr>
                                <th>Email</th>
                                <th>Role</th>
                                <th>Status</th>
                                <th>Expires At</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${invitations.map(inv => `
                                <tr>
                                    <td>${inv.email}</td>
                                    <td>
                                        <span class="badge badge-success">
                                            ${inv.role.toUpperCase()}
                                        </span>
                                    </td>
                                    <td>
                                        <span class="badge ${inv.status === 'pending' ? 'badge-warning' : 'badge-success'}">
                                            ${inv.status}
                                        </span>
                                    </td>
                                    <td>${new Date(inv.expires_at).toLocaleString()}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `}
            </div>
        </div>
    `;
}

// Placeholder functions for actions
function createCompany() {
    showToast('Create Company modal would open here', 'info');
}

function linkDevice() {
    const code = prompt('Enter the 4-digit pairing code from your TV:');
    if (code) {
        api.linkDevice(code)
            .then(() => {
                showToast('Device linked successfully!', 'success');
                loadPage('devices');
            })
            .catch(error => {
                showToast('Failed to link device: ' + error.message, 'error');
            });
    }
}

function sendInvitation() {
    showToast('Send Invitation modal would open here', 'info');
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}
