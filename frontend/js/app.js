import { MapView } from './components/map-view.js';
import { UIControls } from './components/controls.js';
import { fetchStations } from './services/api.js';
import { findOptimalPath } from './services/routing-engine.js';

const init = async () => {
    try {
        console.log('=== App Initialization Started ===');
        
        // Check if Leaflet is loaded
        if (typeof L === 'undefined') {
            console.error('❌ Leaflet library not loaded!');
            alert('Error: Leaflet library failed to load');
            return;
        }
        console.log('✓ Leaflet v' + L.version + ' loaded');

        // Check if map container exists
        const mapContainer = document.getElementById('map');
        if (!mapContainer) {
            console.error('❌ Map container (#map) not found!');
            alert('Error: Map container not found in DOM');
            return;
        }
        console.log('✓ Map container found');
        console.log('  Computed size: ' + window.getComputedStyle(mapContainer).width + ' x ' + window.getComputedStyle(mapContainer).height);

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

        // Wait a moment for map to initialize
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Force map to recalculate
        mapView.map.invalidateSize(true);
        console.log('✓ Map size invalidated');

        console.log('📍 Creating UIControls...');
        const controls = new UIControls();
        console.log('✓ UIControls created');

        // Setup reload map button
        controls.setupReloadMapButton(() => {
            console.log('🔄 Reload button clicked');
            mapView.reloadTiles();
        });

        console.log('📍 Fetching stations...');
        const stations = await fetchStations();
        if (!stations || stations.length === 0) {
            console.error('❌ No stations loaded!');
            alert('Error: Failed to load station data');
            return;
        }
        console.log('✓ Stations fetched: ' + stations.length);

        // 1. Display stations on the map
        console.log('📍 Rendering ' + stations.length + ' stations on map...');
        try {
            mapView.renderStations(stations);
            console.log('✓ Stations rendered on map');
        } catch (error) {
            console.error('❌ Error rendering stations:', error);
        }
        
        // 2. Populate station options in select boxes
        console.log('📍 Populating UIControls...');
        controls.populateStations(stations);
        console.log('✓ UIControls populated');

        // 3. Listen for route search requests
        controls.onSearchRequested((data) => {
            console.log('🔍 Finding route from', data.startId, 'to', data.endId);
            // data contains: startId, endId, priority
            const result = findOptimalPath(stations, data.startId, data.endId, data.priority);
            
            if (result) {
                // Draw the route on the map
                mapView.drawPath(result.path);
                
                // Display time/cost information on sidebar
                controls.showResults(result);
            }
        });

        console.log('✅ === App Initialization Complete ===');
        console.log('Map should be visible now with ' + stations.length + ' stations');
        
    } catch (error) {
        console.error('❌ === INITIALIZATION ERROR ===');
        console.error(error);
        console.error('Stack:', error.stack);
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