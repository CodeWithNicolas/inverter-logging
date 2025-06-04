// Dashboard Configuration
const CONFIG = {
    API_BASE_URL: 'http://192.168.1.101:8080', // Local gateway endpoint (updated IP)
    REFRESH_INTERVAL: 10000, // 10 seconds
    TIMEOUT: 10000 // 10 seconds (increased for cross-origin requests)
};

// Dashboard State
let lastUpdateTime = null;
let isOnline = false;
let refreshInterval = null;

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌞 Solar Dashboard Initializing...');
    initializeDashboard();
});

function initializeDashboard() {
    // Start data fetching
    fetchAllData();
    
    // Set up periodic refresh
    refreshInterval = setInterval(fetchAllData, CONFIG.REFRESH_INTERVAL);
    
    // Handle visibility change (pause when tab is hidden)
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    console.log(`📊 Dashboard started with ${CONFIG.REFRESH_INTERVAL/1000}s refresh interval`);
}

function handleVisibilityChange() {
    if (document.hidden) {
        console.log('🔄 Tab hidden - pausing updates');
        if (refreshInterval) {
            clearInterval(refreshInterval);
            refreshInterval = null;
        }
    } else {
        console.log('🔄 Tab visible - resuming updates');
        fetchAllData();
        if (!refreshInterval) {
            refreshInterval = setInterval(fetchAllData, CONFIG.REFRESH_INTERVAL);
        }
    }
}

async function fetchAllData() {
    try {
        console.log('📡 Fetching live data...');
        updateStatus('Connecting...', false);
        
        // Fetch all data in parallel
        const [deviceInfo, liveData] = await Promise.all([
            fetchWithTimeout('/device/info'),
            fetchWithTimeout('/data/live')
        ]);
        
        // Update UI with fresh data
        updateDeviceInfo(deviceInfo);
        updateLiveData(liveData);
        updateStatus('Online', true);
        
        lastUpdateTime = new Date();
        updateLastUpdateTime();
        
        console.log('✅ Data updated successfully');
        
    } catch (error) {
        console.error('❌ Error fetching data:', error);
        updateStatus('Connection Error', false);
        showErrorState();
    }
}

async function fetchWithTimeout(endpoint) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), CONFIG.TIMEOUT);
    
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`, {
            signal: controller.signal,
            headers: {
                'Accept': 'application/json',
                'Cache-Control': 'no-cache'
            }
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        clearTimeout(timeoutId);
        throw error;
    }
}

function updateDeviceInfo(data) {
    if (!data) return;
    
    updateElement('manufacturer', data.manufacturer || 'Unknown');
    updateElement('model', data.model || 'Unknown');
    updateElement('serial', data.serial_number || 'Unknown');
    updateElement('firmware', data.version || 'Unknown');
}

function updateLiveData(data) {
    if (!data) return;
    
    // Process Model 101 (Inverter data)
    const model101 = data.model_101;
    if (model101 && model101.points) {
        const points = model101.points;
        
        // Main power display
        const currentPower = points.W || 0;
        updateElement('current-power', formatNumber(currentPower, 0));
        updatePowerStatus(currentPower);
        
        // Stats grid
        const totalEnergy = points.WH ? (points.WH / 1000).toFixed(1) : '0.0';
        updateElement('total-energy', `${formatNumber(totalEnergy)} kWh`);
        updateElement('grid-frequency', formatNumber(points.Hz, 2) + ' Hz');
        updateElement('temperature', formatNumber(points.TmpCab, 1) + ' °C');
        updateElement('power-factor', formatNumber(points.PF, 2));
        
        // Technical details - DC Input
        updateElement('dc-voltage', formatNumber(points.DCV, 1) + ' V');
        updateElement('dc-current', formatNumber(points.DCA, 1) + ' A');
        updateElement('dc-power', formatNumber(points.DCW, 0) + ' W');
        
        // Technical details - AC Output
        updateElement('ac-voltage', formatNumber(points.PhV || points.ACV, 1) + ' V');
        updateElement('ac-current', formatNumber(points.ACA, 1) + ' A');
        updateElement('ac-power', formatNumber(points.W, 0) + ' W');
    }
}

function updateElement(id, value, animate = true) {
    const element = document.getElementById(id);
    if (!element) return;
    
    const oldValue = element.textContent;
    if (oldValue !== value) {
        element.textContent = value;
        
        if (animate) {
            element.classList.add('value-updated');
            setTimeout(() => element.classList.remove('value-updated'), 500);
        }
    }
}

function updatePowerStatus(power) {
    const statusElement = document.getElementById('power-status');
    const powerCard = document.querySelector('.main-power');
    
    if (!statusElement || !powerCard) return;
    
    if (power > 0) {
        statusElement.textContent = '⚡ Generating Power';
        powerCard.classList.remove('error-card');
    } else {
        statusElement.textContent = '🌙 No Generation (Night/Standby)';
        powerCard.classList.remove('error-card');
    }
}

function updateStatus(message, online) {
    const statusText = document.getElementById('status-text');
    const statusDot = document.getElementById('status-dot');
    
    if (statusText) statusText.textContent = message;
    
    if (statusDot) {
        statusDot.className = `status-dot ${online ? 'online' : 'offline'}`;
    }
    
    isOnline = online;
}

function updateLastUpdateTime() {
    const element = document.getElementById('last-updated');
    if (!element || !lastUpdateTime) return;
    
    const timeString = lastUpdateTime.toLocaleTimeString();
    element.textContent = timeString;
}

function showErrorState() {
    // Show error values
    const errorElements = [
        'current-power', 'total-energy', 'grid-frequency', 'temperature',
        'power-factor', 'dc-voltage', 'dc-current', 'dc-power',
        'ac-voltage', 'ac-current', 'ac-power'
    ];
    
    errorElements.forEach(id => {
        updateElement(id, '---', false);
    });
    
    // Update power status
    const statusElement = document.getElementById('power-status');
    if (statusElement) {
        statusElement.textContent = '⚠️ Connection Lost';
    }
    
    // Add error styling to main power card
    const powerCard = document.querySelector('.main-power');
    if (powerCard) {
        powerCard.classList.add('error-card');
    }
}

function formatNumber(value, decimals = 0) {
    if (value === null || value === undefined || value === '' || isNaN(value)) {
        return '---';
    }
    
    const num = parseFloat(value);
    if (isNaN(num)) return '---';
    
    return num.toLocaleString(undefined, {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

// Error handling for unhandled promise rejections
window.addEventListener('unhandledrejection', function(event) {
    console.error('🚨 Unhandled promise rejection:', event.reason);
    updateStatus('System Error', false);
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});

// Expose functions for debugging
window.solarDashboard = {
    fetchAllData,
    updateStatus,
    CONFIG,
    isOnline: () => isOnline,
    lastUpdate: () => lastUpdateTime
}; 