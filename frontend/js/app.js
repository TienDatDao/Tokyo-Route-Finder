import { MapView } from './components/map-view.js';
import { UIControls } from './components/controls.js';
import { fetchStations } from './services/api.js';
import { CONFIG } from './config.js';

const calculateAverageCoord = (coords) => {
    if (!coords || coords.length === 0) return null;
    const sum = coords.reduce((acc, coord) => {
        return [acc[0] + coord[0], acc[1] + coord[1]];
    }, [0, 0]);
    return [sum[0] / coords.length, sum[1] / coords.length];
};

const buildUniqueStationGroups = (stations) => {
    const groups = new Map();

    stations.forEach(station => {
        const name = station.title?.en || station.name || station.id;
        const normalized = name.trim().toLowerCase();

        if (!groups.has(normalized)) {
            groups.set(normalized, {
                id: station.id,
                name,
                stationIds: [station.id],
                coords: [station.coord]
            });
        } else {
            const existing = groups.get(normalized);
            existing.stationIds.push(station.id);
            existing.coords.push(station.coord);
        }
    });

    return Array.from(groups.values()).map(group => ({
        id: group.id,
        name: group.name,
        stationIds: group.stationIds,
        coord: calculateAverageCoord(group.coords)
    }));
};

const init = async () => {
    try {
        console.log('=== App Initialization Started ===');

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

        const uniqueStations = buildUniqueStationGroups(stations);
        mapView.renderStations(uniqueStations);
        controls.populateStations(stations);

        controls.onSearchRequested(async (data) => {
            console.log('🔍 Requesting route from server:', data.startName, 'to', data.endName, 'criteria:', data.criteria);
            
            try {
                const response = await fetch(`${CONFIG.API_BASE_URL}/api/find-path`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || errorData.error || 'Server error');
                }

                const result = await response.json();
                console.log('✓ Route received from server:', result);

                if (result && result.route) {
                    mapView.drawPath({
                        coords: result.route.pathCoords || [],
                        stationIds: result.route.path || [],
                        details: result.route.details || []
                    });
                    controls.showResults(result.route);
                } else {
                    controls.showResults(null);
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