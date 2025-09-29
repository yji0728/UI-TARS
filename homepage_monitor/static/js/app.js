// Homepage Monitoring System JavaScript

// Global variables
let refreshInterval;
let isAutoRefresh = false;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Homepage Monitor initialized');
    
    // Auto-refresh every 30 seconds if on dashboard
    if (window.location.pathname === '/' || window.location.pathname === '/index') {
        startAutoRefresh();
    }
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Check all sites function
function checkAllSites() {
    const button = event.target.closest('a');
    const originalText = button.innerHTML;
    
    // Show loading state
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 검사 중...';
    button.classList.add('disabled');
    
    fetch('/api/check_all')
        .then(response => response.json())
        .then(data => {
            console.log('Check all completed:', data);
            
            // Show success message
            showNotification('모든 사이트 검사가 완료되었습니다.', 'success');
            
            // Refresh page after short delay
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        })
        .catch(error => {
            console.error('Error checking sites:', error);
            showNotification('검사 중 오류가 발생했습니다.', 'error');
        })
        .finally(() => {
            // Reset button state
            button.innerHTML = originalText;
            button.classList.remove('disabled');
        });
}

// Show notification function
function showNotification(message, type = 'info') {
    const alertTypes = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    };
    
    const alertClass = alertTypes[type] || 'alert-info';
    
    const alertHTML = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // Insert at the top of main content
    const main = document.querySelector('main .container');
    if (main) {
        main.insertAdjacentHTML('afterbegin', alertHTML);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = main.querySelector('.alert');
            if (alert) {
                new bootstrap.Alert(alert).close();
            }
        }, 5000);
    }
}

// Auto-refresh functionality
function startAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    
    refreshInterval = setInterval(() => {
        refreshDashboardData();
    }, 30000); // 30 seconds
    
    isAutoRefresh = true;
    console.log('Auto-refresh started');
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
    isAutoRefresh = false;
    console.log('Auto-refresh stopped');
}

// Refresh dashboard data without full page reload
function refreshDashboardData() {
    fetch('/api/sites')
        .then(response => response.json())
        .then(sites => {
            updateSitesTable(sites);
        })
        .catch(error => {
            console.error('Error refreshing sites data:', error);
        });
    
    fetch('/api/alerts')
        .then(response => response.json())
        .then(alerts => {
            updateAlertsPanel(alerts.slice(0, 10)); // Latest 10 alerts
        })
        .catch(error => {
            console.error('Error refreshing alerts data:', error);
        });
}

// Update sites table
function updateSitesTable(sites) {
    const tbody = document.querySelector('table tbody');
    if (!tbody) return;
    
    let html = '';
    for (const [siteId, site] of Object.entries(sites)) {
        const lastCheck = site.last_check ? 
            site.last_check.substring(0, 19).replace('T', ' ') : 
            '<span class="text-muted">미검사</span>';
            
        const statusBadge = site.status === 'active' ? 
            '<span class="badge bg-success">활성</span>' : 
            '<span class="badge bg-secondary">비활성</span>';
            
        const urlDisplay = site.url.length > 50 ? 
            site.url.substring(0, 50) + '...' : 
            site.url;
        
        html += `
            <tr>
                <td>${site.name}</td>
                <td>
                    <a href="${site.url}" target="_blank" class="text-decoration-none">
                        ${urlDisplay}
                    </a>
                </td>
                <td>${statusBadge}</td>
                <td>${lastCheck}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <a href="/check_site/${siteId}" class="btn btn-outline-primary" title="검사">
                            <i class="fas fa-search"></i>
                        </a>
                        <a href="/set_baseline/${siteId}" class="btn btn-outline-warning" title="기준 설정">
                            <i class="fas fa-camera"></i>
                        </a>
                        <a href="/remove_site/${siteId}" class="btn btn-outline-danger" title="삭제"
                           onclick="return confirm('정말로 이 사이트를 삭제하시겠습니까?')">
                            <i class="fas fa-trash"></i>
                        </a>
                    </div>
                </td>
            </tr>
        `;
    }
    
    tbody.innerHTML = html;
}

// Update alerts panel
function updateAlertsPanel(alerts) {
    const alertsContainer = document.querySelector('.card-body');
    if (!alertsContainer) return;
    
    if (alerts.length === 0) {
        alertsContainer.innerHTML = `
            <div class="text-center py-3">
                <i class="fas fa-check-circle fa-2x text-success mb-2"></i>
                <p class="text-muted mb-0">모든 사이트가 안전합니다</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    alerts.forEach(alert => {
        const timestamp = alert.timestamp.substring(0, 19).replace('T', ' ');
        const similarity = (alert.similarity_score * 100).toFixed(1);
        
        html += `
            <div class="alert alert-danger alert-sm mb-2">
                <strong>${alert.site_name}</strong><br>
                <small>${timestamp}</small><br>
                <small>유사도: ${similarity}%</small>
            </div>
        `;
    });
    
    html += `
        <div class="text-center">
            <a href="/alerts" class="btn btn-outline-primary btn-sm">
                모든 알림 보기
            </a>
        </div>
    `;
    
    alertsContainer.innerHTML = html;
}

// Format date and time
function formatDateTime(isoString) {
    if (!isoString) return '미검사';
    
    const date = new Date(isoString);
    return date.toLocaleString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Calculate similarity color class
function getSimilarityColorClass(score) {
    if (score >= 0.8) return 'similarity-high';
    if (score >= 0.5) return 'similarity-medium';
    return 'similarity-low';
}

// URL validation
function validateURL(url) {
    try {
        new URL(url);
        return true;
    } catch (e) {
        return false;
    }
}

// Form validation for add site
function validateAddSiteForm() {
    const form = document.querySelector('form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        const url = document.getElementById('url').value;
        const name = document.getElementById('name').value;
        
        if (!url || !name) {
            e.preventDefault();
            showNotification('URL과 사이트 이름을 모두 입력해주세요.', 'error');
            return;
        }
        
        if (!validateURL(url)) {
            e.preventDefault();
            showNotification('올바른 URL 형식을 입력해주세요. (예: https://example.com)', 'error');
            return;
        }
    });
}

// Initialize form validation
if (window.location.pathname === '/add_site') {
    document.addEventListener('DOMContentLoaded', validateAddSiteForm);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+R for refresh
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        if (typeof checkAllSites === 'function') {
            checkAllSites();
        }
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            bootstrap.Modal.getInstance(modal)?.hide();
        });
    }
});

// Handle visibility change (pause auto-refresh when tab is not active)
document.addEventListener('visibilitychange', function() {
    if (document.hidden && isAutoRefresh) {
        stopAutoRefresh();
    } else if (!document.hidden && window.location.pathname === '/') {
        startAutoRefresh();
    }
});

// Clean up on page unload
window.addEventListener('beforeunload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});

console.log('Homepage Monitor app.js loaded successfully');