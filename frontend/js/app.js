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

        controls.setupReloadMapButton(async () => {
            console.log('🔄 Reloading map and stations...');
            mapView.reloadTiles();
            
            // Reload stations from API
            try {
                const stations = await fetchStations();
                const uniqueStations = buildUniqueStationGroups(stations);
                mapView.clearStations();
                mapView.renderStations(uniqueStations);
                controls.populateStations(stations);
                
                // Clear any previous selections since stations may have changed
                document.getElementById('start-search').value = '';
                document.getElementById('end-search').value = '';
                document.getElementById('start-station-id').value = '';
                document.getElementById('end-station-id').value = '';
                document.getElementById('suggestions-dropdown').innerHTML = '';
                document.getElementById('end-suggestions-dropdown').innerHTML = '';
                
                console.log('✓ Stations reloaded:', uniqueStations.length);
            } catch (error) {
                console.error('❌ Failed to reload stations:', error);
            }
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
                console.log('📤 Sending request to:', `${CONFIG.API_BASE_URL}/api/find-path`);
                const response = await fetch(`${CONFIG.API_BASE_URL}/api/find-path`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                console.log('📥 Response received:', response.status, response.statusText);
                console.log('Response headers:', {
                    'content-type': response.headers.get('content-type'),
                    'content-length': response.headers.get('content-length')
                });

                if (!response.ok) {
                    const errorData = await response.text();
                    console.error('❌ Error response body:', errorData);
                    throw new Error(errorData || 'Server error');
                }

                const result = await response.json();
                console.log('✓ Route received from server:', result);
                console.log('Route status:', result.status);
                console.log('Route object:', result.route);
                if (result.route) {
                    console.log('pathCoords:', result.route.pathCoords);
                    console.log('Number of coords:', result.route.pathCoords ? result.route.pathCoords.length : 0);
                }

                if (result && result.route && result.route.pathCoords && result.route.pathCoords.length > 0) {
                    console.log('✅ Drawing route with pathCoords:', result.route.pathCoords);
                    mapView.drawPath({
                        coords: result.route.pathCoords,
                        stationIds: result.route.path || [],
                        details: result.route.details || []
                    });
                    controls.showResults(result.route);
                } else {
                    console.warn('⚠️ No valid route or pathCoords in response');
                    console.warn('result:', result);
                    console.warn('result.route:', result.route);
                    console.warn('result.route.pathCoords:', result.route?.pathCoords);
                    controls.showResults(null);
                }
            } catch (error) {
                console.error('❌ Error while requesting route:', error);
                console.error('Error stack:', error.stack);
                alert('Error: ' + error.message);
            }
        });

        console.log('=== App Initialization Completed ===');
    } catch (error) {
        console.error('❌ Unexpected error during initialization:', error);
        alert('Unexpected error: ' + error.message);
    }
};

init();
