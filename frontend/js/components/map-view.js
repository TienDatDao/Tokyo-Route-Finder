import { CONFIG } from '../config.js';

export class MapView {
    constructor(elementId) {
        console.log('MapView: Initializing map in element:', elementId);
        
        const container = document.getElementById(elementId);
        if (!container) {
            throw new Error(`Map container #${elementId} not found`);
        }
        
        console.log('MapView: Container size before init:', container.clientWidth, 'x', container.clientHeight);
        
        // Initialize the map
        this.map = L.map(elementId, {
            center: CONFIG.MAP_CENTER,
            zoom: CONFIG.DEFAULT_ZOOM,
            zoomControl: true,
            attributionControl: true,
            preferCanvas: false
        });
        
        this.currentPathLayer = null;
        this.stationsLayer = L.layerGroup();
        this.stationsLayer.addTo(this.map);

        // Add OpenStreetMap tiles with proper configuration
        console.log('MapView: Adding OpenStreetMap tile layer...');
        const tileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            minZoom: 0,
            maxZoom: 19,
            tms: false,
            crossOrigin: true,
            noWrap: false
        });
        
        tileLayer.on('loading', () => {
            console.log('MapView: Tiles loading...');
        });
        
        tileLayer.on('load', () => {
            console.log('MapView: Tiles loaded successfully');
        });
        
        tileLayer.on('tileerror', (e) => {
            console.warn('MapView: Tile error for:', e.tile.src);
        });
        
        tileLayer.addTo(this.map);

        // Force map to recalculate its size
        console.log('MapView: Invalidating map size...');
        this.map.invalidateSize(true);
        
        // Store reference for external access
        window.mapViewInstance = this;
        
        // Listen for map to be ready
        this.map.on('ready', () => {
            console.log('MapView: Map is ready');
        });
        
        this.map.on('load', () => {
            console.log('MapView: Map load event fired');
        });
        
        console.log('MapView: Initialization complete');
    }

    renderStations(stations) {
        // Clear previous station markers
        this.stationsLayer.clearLayers();
        
        console.log('MapView: Rendering', stations.length, 'stations');
        
        let rendered = 0;
        let errors = 0;
        
        stations.forEach(station => {
            try {
                // stations.json uses [lng, lat] format, but Leaflet needs [lat, lng]
                const lat = station.coord[1];
                const lng = station.coord[0];
                const name = station.title?.en || station.name || station.id;
                
                // Validate coordinates
                if (isNaN(lat) || isNaN(lng)) {
                    errors++;
                    return;
                }
                
                // Create circular marker for each station
                const marker = L.circleMarker([lat, lng], {
                    radius: 5,
                    fillColor: '#2f3542',
                    color: '#fff',
                    weight: 1,
                    opacity: 0.8,
                    fillOpacity: 0.7
                });
                
                // Add popup with station name (English)
                marker.bindPopup(`<strong>${name}</strong><br/><small>${station.railway || ''}</small>`);
                
                // Bind tooltip for hover effect
                marker.bindTooltip(name, { sticky: true });
                
                marker.addTo(this.stationsLayer);
                rendered++;
            } catch (error) {
                console.error('MapView: Error rendering station:', error);
                errors++;
            }
        });
        
        console.log('MapView: Successfully rendered', rendered, 'stations,', errors, 'errors');
        
        // Fit map to bounds if we have stations
        if (rendered > 0) {
            try {
                const bounds = this.stationsLayer.getBounds();
                if (bounds.isValid()) {
                    this.map.fitBounds(bounds, { padding: [50, 50] });
                    console.log('MapView: Map fitted to station bounds');
                }
            } catch (e) {
                console.warn('MapView: Could not fit bounds:', e);
            }
        }
    }

    drawPath(coordinates) {
        if (this.currentPathLayer) this.map.removeLayer(this.currentPathLayer);
        this.currentPathLayer = L.polyline(coordinates, { color: '#ff4757', weight: 5 }).addTo(this.map);
        this.map.fitBounds(this.currentPathLayer.getBounds());
    }

    /**
     * Reload/refresh the map tiles
     */
    reloadTiles() {
        console.log('MapView: Reloading tiles...');
        
        // Invalidate size to ensure map recalculates
        this.map.invalidateSize(true);
        
        // Re-pan to center and zoom
        this.map.setView(CONFIG.MAP_CENTER, CONFIG.DEFAULT_ZOOM);
        
        // Redraw all tile layers
        this.map.eachLayer(layer => {
            if (layer instanceof L.TileLayer) {
                layer.redraw();
            }
        });
        
        console.log('MapView: Tiles reloaded');
    }
}