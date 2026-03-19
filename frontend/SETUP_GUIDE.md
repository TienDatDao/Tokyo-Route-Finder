# Tokyo Route Finder - Setup & Structure Guide

## ✅ Fixed Issues

### 1. **Added Missing Header Element**
- Added `<header>` tag to index.html with the app title
- Header provides visual context and uses existing header.css styling

### 2. **Fixed Layout Structure**
- **Old Problem**: Absolute positioning with `overflow: hidden` was clipping dropdown suggestions
- **Solution**: 
  - Changed to flexbox layout for `#app-container`
  - Updated sidebar to use `flex: display` instead of absolute positioning
  - Changed map container to use `flex: 1` instead of absolute positioning
  - Set `#sidebar` to `overflow: visible` to prevent dropdown clipping

### 3. **CSS Layout Architecture**
```
<header> (height: 60px)
  ↓
<div id="app-container"> (flexbox row, height: calc(100vh - 60px))
  ├─ <aside id="sidebar"> (width: 350px, flex-shrink: 0)
  │   ├─ Search inputs with dropdowns
  │   ├─ Route options (time/cost)
  │   ├─ Find Route button
  │   └─ Results panel
  │
  └─ <main id="map"> (flex: 1)
      └─ Leaflet map displaying Tokyo stations
```

## 📁 File Structure

```
frontend/
├── index.html                 # Main HTML with header + app-container
├── css/
│   ├── main.css              # CSS imports organizer
│   ├── base/
│   │   ├── variables.css     # CSS variables (colors, sizes)
│   │   └── reset.css         # Global reset styles
│   ├── layout/
│   │   ├── header.css        # Header styling (60px blue bar)
│   │   ├── sidebar.css       # Sidebar layout (350px left panel)
│   │   └── map-container.css # Map styling (flex: 1)
│   └── components/
│       ├── buttons.css       # Button styles
│       ├── inputs.css        # Input + dropdown styles
│       ├── cards.css         # Card components
│       └── modal.css         # Modal dialogs
├── js/
│   ├── app.js                # Main initialization
│   ├── config.js             # Configuration (Tokyo coords, colors)
│   ├── components/
│   │   ├── map-view.js       # Leaflet map initialization & rendering
│   │   └── controls.js       # UI controls (search, route selection)
│   ├── services/
│   │   ├── api.js            # Fetch stations (with fallback)
│   │   └── routing-engine.js # Route calculation (placeholder)
│   └── data/
│       └── stations-data.js  # 2499 Tokyo stations module
├── assets/
│   └── data/
│       ├── stations.json     # 2499 stations source data
│       ├── railway.json      # Railway/line info
│       ├── station_groups.json
│       └── train_types.json
├── test-server.html          # Comprehensive testing page
└── debug.html                # Debug console
```

## 🗺️ Map Display Flow

```
1. index.html loads
   ↓
2. DOMContentLoaded → app.js init()
   ↓
3. Create MapView('map')
   ├─ L.map('map').setView([35.6895, 139.6917], 12)
   ├─ L.tileLayer (OpenStreetMap)
   └─ L.layerGroup() for stations
   ↓
4. Create UIControls()
   ├─ Initialize search inputs
   ├─ Setup event listeners
   └─ Prepare dropdowns
   ↓
5. fetchStations()
   ├─ Try: fetch('./assets/data/stations.json')
   └─ Fallback: import stationsData (2499 entries)
   ↓
6. mapView.renderStations(stations)
   ├─ Clear existing markers
   ├─ For each station:
   │   ├─ Create L.circleMarker([lat, lng])
   │   ├─ Add popup with English name
   │   └─ Add tooltip for hover
   └─ Add markers to stationsLayer
   ↓
7. controls.populateStations(stations)
   ├─ Store in this.allStations
   └─ Ready for search/autocomplete
   ↓
8. User interaction
   ├─ Click start-search input
   ├─ Type station name
   ├─ showSuggestions() filters and renders dropdown
   ├─ Select station from list
   └─ Hidden input stores station ID
```

## 🔍 Testing and Verification

### Option 1: Quick Browser Test
1. Open `frontend/index.html` directly in browser
2. Should see:
   - Blue header "🗾 Tokyo Route Finder"
   - Left sidebar with search boxes
   - Dark map on the right with station markers
   - Stations appear as small dark circles

### Option 2: Comprehensive Test Page
1. Open `frontend/test-server.html` in browser
2. Automatically runs tests to verify:
   - ✓ HTML structure complete
   - ✓ All modules load correctly
   - ✓ 2499 stations loaded
   - ✓ MapView initializes
   - ✓ Stations render on map
   - ✓ UIControls ready

### Option 3: With HTTP Server
```bash
# Windows (PowerShell)
cd frontend
python -m http.server 8000
# Then open http://localhost:8000

# Or use any other HTTP server
```

## 🎯 Key Features

- **English Display**: All station names shown in English (from `title.en`)
- **Autocomplete Search**: Real-time filtering as user types
- **2499 Tokyo Stations**: Complete metro/train network coverage
- **Fallback Loading**: Works both with HTTP server and direct file:// access
- **Responsive Layout**: Sidebar + map fills entire viewport
- **Smooth Animations**: Dropdown slides down with fade effect

## ⚙️ Configuration

Edit `frontend/js/config.js`:
```javascript
MAP_CENTER: [35.6895, 139.6917]  // Tokyo center
DEFAULT_ZOOM: 12                  // Map zoom level
STATION_DATA_PATH: './assets/data/stations.json'
COLORS: {
    PATH: '#ff4757',              // Red route line
    STATION: '#2f3542'            // Dark blue station markers
}
```

## 📋 Component Details

### MapView (`components/map-view.js`)
- Initializes Leaflet map centered on Tokyo
- Renders stations as circle markers
- Draws polyline for calculated routes
- Shows popups with station info

### UIControls (`components/controls.js`)
- Manages start/end station search inputs
- Real-time autocomplete with dropdown
- Validates route selection
- Displays route results (time, cost)

### API Service (`services/api.js`)
- Loads stations from stations.json or fallback module
- Handles both HTTP fetch and ES6 import approaches

### Routing Engine (`services/routing-engine.js`)
- Currently returns dummy route data
- Ready for A* or Dijkstra implementation

## 🐛 Troubleshooting

### Map not showing?
1. Check browser console (F12) for errors
2. Verify Leaflet CSS/JS loaded from CDN
3. Confirm `#map` element exists in DOM
4. Check CSS height/width properties

### Stations not visible?
1. Check console for "Stations loaded: 2499" message
2. Verify `renderStations()` called
3. Confirm circle markers have correct colors
4. Check zoom level (12 should show stations)

### Search dropdown not appearing?
1. Click search input to focus
2. Check console for "showSuggestions" calls
3. Verify dropdown `.active` class applied
4. Check z-index and positioning (should be 1001)

### Fetch failing?
1. This is expected with file:// protocol
2. Fallback to stationsData module (2499 stations)
3. Use HTTP server for full fetch functionality
