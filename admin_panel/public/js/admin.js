// Cache dữ liệu
let stationsData = {};
let linesData = [];

// Khởi tạo
document.addEventListener('DOMContentLoaded', () => {
    loadStationsAndLines();
    refreshIncidents();
    setInterval(refreshIncidents, 5000); // Refresh mỗi 5 giây
});

// Load danh sách ga và tuyến từ server
async function loadStationsAndLines() {
    try {
        const response = await fetch('/api/stations-and-lines');
        const data = await response.json();
        
        stationsData = data.stations || {};
        linesData = data.lines || [];

        // Cập nhật số liệu thống kê
        document.getElementById('total-stations').textContent = Object.keys(stationsData).length;
        document.getElementById('total-lines').textContent = linesData.length;

        updateTargetOptions();
    } catch (error) {
        console.error('Error loading data:', error);
        showMessage('error', 'Không thể tải dữ liệu từ server');
    }
}

// Cập nhật danh sách mục tiêu dựa trên loại sự cố
function updateTargetOptions() {
    const incidentType = document.getElementById('incident-type').value;
    const targetList = document.getElementById('target-list');

    targetList.innerHTML = '';

    if (incidentType === 'STATION_CLOSED') {
        // Hiển thị danh sách ga
        Object.keys(stationsData).forEach(stationId => {
            const option = document.createElement('option');
            option.value = stationId;
            option.textContent = `${stationsData[stationId]} (${stationId})`;
            targetList.appendChild(option);
        });
    } else if (incidentType === 'LINE_MAINTENANCE') {
        // Hiển thị danh sách tuyến
        linesData.forEach(line => {
            const option = document.createElement('option');
            option.value = line;
            option.textContent = line;
            targetList.appendChild(option);
        });
    }
}

// Áp dụng incident
async function applyIncident() {
    const incidentType = document.getElementById('incident-type').value;
    const targetId = document.getElementById('target-id').value;

    if (!incidentType || !targetId) {
        showMessage('error', 'Vui lòng chọn loại sự cố và mục tiêu');
        return;
    }

    try {
        const response = await fetch('/api/apply-incident', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: 'apply',
                type: incidentType,
                target_id: targetId
            })
        });

        const result = await response.json();

        if (response.ok) {
            showMessage('success', `✓ Đã áp dụng sự cố cho ${targetId}`);
            document.getElementById('incident-type').value = '';
            document.getElementById('target-id').value = '';
            updateTargetOptions();
            refreshIncidents();
            // Reload page to reflect changes in map (if applicable)
            setTimeout(() => location.reload(), 1000);
        } else {
            showMessage('error', result.error || 'Lỗi khi áp dụng sự cố');
        }
    } catch (error) {
        console.error('Error applying incident:', error);
        showMessage('error', 'Lỗi khi áp dụng sự cố');
    }
}

// Xóa một incident
async function removeIncident(targetId, incidentType) {
    try {
        const response = await fetch('/api/apply-incident', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: 'remove',
                type: incidentType,
                target_id: targetId
            })
        });

        const result = await response.json();

        if (response.ok) {
            showMessage('success', `✓ Đã xóa sự cố cho ${targetId}`);
            refreshIncidents();
            // Reload page to reflect changes in map (if applicable)
            setTimeout(() => location.reload(), 1000);
        } else {
            showMessage('error', result.error || 'Lỗi khi xóa sự cố');
        }
    } catch (error) {
        console.error('Error removing incident:', error);
        showMessage('error', 'Lỗi khi xóa sự cố');
    }
}

// Reset tất cả incidents
async function resetIncidents() {
    if (!confirm('Bạn chắc chắn muốn xóa TẤT CẢ các sự cố?')) return;

    try {
        const response = await fetch('/api/reset-incidents', {
            method: 'POST'
        });

        const result = await response.json();

        if (response.ok) {
            showMessage('success', '✓ Đã reset tất cả sự cố');
            refreshIncidents();
            // Reload page to reflect changes in map (if applicable)
            setTimeout(() => location.reload(), 1000);
        } else {
            showMessage('error', result.error || 'Lỗi khi reset sự cố');
        }
    } catch (error) {
        console.error('Error resetting incidents:', error);
        showMessage('error', 'Lỗi khi reset sự cố');
    }
}

// Refresh danh sách incidents đang hoạt động
async function refreshIncidents() {
    try {
        const response = await fetch('/api/active-incidents');
        const data = await response.json();
        const incidentsList = document.getElementById('incidents-list');

        // Cập nhật số lượng sự cố hoạt động
        document.getElementById('active-count').textContent = data.count;

        if (data.incidents.length === 0) {
            incidentsList.innerHTML = '<p class="empty-state">Không có sự cố nào</p>';
            return;
        }

        incidentsList.innerHTML = data.incidents.map(incident => {
            const targetName = incident.type === 'STATION_CLOSED' 
                ? stationsData[incident.target_id] || incident.target_id
                : incident.target_id;

            const typeLabel = incident.type === 'STATION_CLOSED' ? '🚫 Đóng Cửa Ga' : '🔧 Bảo Trì Tuyến';

            return `
                <div class="incident-item">
                    <div class="info">
                        <span class="type">${typeLabel}</span>
                        <div class="target">${targetName}</div>
                    </div>
                    <button class="btn btn-remove" onclick="removeIncident('${incident.target_id}', '${incident.type}')">
                        ✕ Xóa
                    </button>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error refreshing incidents:', error);
    }
}

// Hiển thị message
function showMessage(type, text) {
    const messageEl = document.getElementById('apply-message');
    messageEl.className = `message show ${type}`;
    messageEl.textContent = text;

    setTimeout(() => {
        messageEl.classList.remove('show');
    }, 4000);
}
