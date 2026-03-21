import { MapView } from './components/map-view.js';
import { UIControls } from './components/controls.js';
import { fetchStations } from './services/api.js';
// Bạn có thể giữ hoặc bỏ import này nếu không dùng tìm đường offline nữa
// import { findOptimalPath } from './services/routing-engine.js'; 

const init = async () => {
    try {
        console.log('=== App Initialization Started ===');

        // ... (Giữ nguyên phần kiểm tra Leaflet và Map container) ...

        console.log('📍 Creating MapView...');
        let mapView;
        try {
            mapView = new MapView('map');
            console.log('✓ MapView created successfully');
        } catch (error) {
            console.error('❌ Failed to create MapView:', error.message);
            alert('Error: Failed to initialize map - ' + error.message);
            return;
        }

        await new Promise(resolve => setTimeout(resolve, 100));
        mapView.map.invalidateSize(true);

        console.log('📍 Creating UIControls...');
        const controls = new UIControls();
        console.log('✓ UIControls created');

        controls.setupReloadMapButton(() => {
            mapView.reloadTiles();
        });

        console.log('📍 Fetching stations...');
        const stations = await fetchStations();
        if (!stations || stations.length === 0) {
            console.error('❌ No stations loaded!');
            return;
        }

        mapView.renderStations(stations);
        controls.populateStations(stations);

        // --- PHẦN THAY ĐỔI CHÍNH TẠI ĐÂY ---
        // 3. Lắng nghe yêu cầu tìm đường và gửi tới Server Python
        controls.onSearchRequested(async (data) => {
            console.log('🔍 Requesting route from server:', data.startId, 'to', data.endId);
            
            try {
                // Gọi API tới server Flask (mặc định port 5000)
                const response = await fetch('http://localhost:5000/api/find-path', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data) // data chứa: startId, endId, priority
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Server error');
                }

                const result = await response.json();
                console.log('✓ Route received from server:', result);

                if (result && result.path) {
                    // 1. Vẽ đường đi lên bản đồ (Sử dụng tọa độ từ BE trả về)
                    mapView.drawPath(result.path);

                    // 2. Hiển thị thông tin thời gian/chi phí lên sidebar
                    controls.showResults(result);
                }

            } catch (error) {
                console.error('❌ API Error:', error);
                alert('Không thể tìm đường: ' + error.message);
            }
        });

        console.log('✅ === App Initialization Complete ===');

    } catch (error) {
        console.error('❌ === INITIALIZATION ERROR ===');
        console.error(error);
        alert('Fatal error: ' + error.message);
    }
};

// Wait for DOM to be fully loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    // DOM is already loaded
    init();
}