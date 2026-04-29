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

        this.map.createPane('routePane');
        this.map.getPane('routePane').style.zIndex = 400;
        this.map.createPane('markerPane');
        this.map.getPane('markerPane').style.zIndex = 650;

        this.currentPathLayer = null;
        this.stationsLayer = L.layerGroup().addTo(this.map);
        this.routeMarkersLayer = L.layerGroup().addTo(this.map);
        this.startMarkerLayer = L.layerGroup().addTo(this.map);
        this.endMarkerLayer = L.layerGroup().addTo(this.map);
        this.routeMarkers = new Map();
        this.stationCoordinates = new Map();

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
    /**
     * @param {Array} coord - [lng, lat]
     * @param {string} name - Tên ga
     * @param {string} type - 'start' hoặc 'end'
     */
    focusOnStation(coord, name, type) {
        if (!coord) return;

        const latLng = [coord[1], coord[0]]; // [lng, lat] -> [lat, lng]

        // Xác định màu sắc và layer dựa trên loại điểm (start/end)
        const isStart = type === 'start';
        const markerColor = isStart ? '#ff4757' : '#2e86de'; // Đỏ cho start, Xanh cho end
        const targetLayer = isStart ? this.startMarkerLayer : this.endMarkerLayer;

        // 1. Xóa điểm cũ của riêng layer đó để không bị chồng chất điểm
        targetLayer.clearLayers();

        // 2. Tạo marker mới, to gấp 1.5 lần (radius: 7.5)
        const highlightMarker = L.circleMarker(latLng, {
            radius: 7.5,
            fillColor: markerColor,
            color: '#ffffff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.9,
            pane: 'markerPane'
        });

        // Hiển thị popup với tiền tố Start/End để người dùng dễ phân biệt
        const popupLabel = isStart ? 'Start' : 'Destination';
        highlightMarker.bindPopup(`<strong>${popupLabel}: ${name}</strong>`).openPopup();

        highlightMarker.addTo(targetLayer);

        // 3. Hiệu ứng bay đến vị trí ga (Zoom mức 16)
        this.map.flyTo(latLng, 16, {
            animate: true,
            duration: 1.0,
            easeLinearity: 0.25
        });
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
                marker.bindPopup(`<strong>${name}</strong>`);

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

    clearRoute() {
        if (this.currentPathLayer) {
            this.map.removeLayer(this.currentPathLayer);
            this.currentPathLayer = null;
        }
        if (this.routeMarkersLayer) {
            this.routeMarkersLayer.clearLayers();
        }
    }

    drawPath(routeData) {
        this.clearRoute();
        if (!routeData) return;

        let coordinates = [];
        let details = [];
        if (Array.isArray(routeData)) {
            coordinates = routeData;
        } else if (routeData.coords && Array.isArray(routeData.coords)) {
            coordinates = routeData.coords;
            details = Array.isArray(routeData.details) ? routeData.details : [];
        }

        if (!Array.isArray(coordinates) || coordinates.length === 0) return;

        const latLngs = coordinates.map(coord => [coord[0], coord[1]]);
        const stationIds = Array.isArray(routeData.stationIds) ? routeData.stationIds : [];
        const importantSteps = (Array.isArray(details) ? details : []).filter(step => ['Board', 'Transfer', 'Arrive'].includes(step.action));
        const importantIds = new Set(importantSteps.map(step => step.station_id));
        const detailByStation = new Map((Array.isArray(details) ? details : []).map(step => [step.station_id, step]));

        this.currentPathLayer = L.polyline(latLngs, {
            color: '#3a4185',
            weight: 5,
            opacity: 0.85,
            pane: 'routePane'
        }).addTo(this.map);

        latLngs.forEach((latLng, index) => {
            const stationId = stationIds[index] || null;
            const isStart = index === 0;
            const isEnd = index === latLngs.length - 1;
            const step = stationId ? detailByStation.get(stationId) : null;
            const isTransfer = step?.action === 'Transfer';
            const isImportant = isStart || isEnd || isTransfer;

            const markerOptions = {
                radius: isImportant ? 7 : 4,
                fillColor: isStart ? '#ff4757' : isEnd ? '#1e90ff' : isTransfer ? '#2ecc71' : '#95a5a6',
                color: isImportant ? '#ffffff' : '#7f8c8d',
                weight: isImportant ? 2 : 1,
                opacity: isImportant ? 1 : 0.5,
                fillOpacity: isImportant ? 0.95 : 0.35,
                pane: 'markerPane'
            };

            const dot = L.circleMarker(latLng, markerOptions);
            if (step?.station_name) {
                const label = isStart ? 'Ga xuất phát' : isEnd ? 'Ga đích' : isTransfer ? 'Đổi tuyến' : 'Ga trung gian';
                dot.bindTooltip(`${label}: ${step.station_name}`, { sticky: true });
            }
            dot.addTo(this.routeMarkersLayer);
        });

        if (this.currentPathLayer.getBounds().isValid()) {
            this.map.fitBounds(this.currentPathLayer.getBounds(), { padding: [40, 40] });
        }
    }

    focusOnRouteStation(coord) {
        if (!coord || coord.length < 2) return;
        const latLng = [coord[0], coord[1]];
        this.map.flyTo(latLng, 15, {
            animate: true,
            duration: 1.0,
            easeLinearity: 0.25
        });
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