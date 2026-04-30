import { stationsData } from '../../frontend/js/data/stations-data.js';

// Configuration
const STORAGE_KEY = 'tokyo_admin_overrides';

// State
let stations = [];
let edges = [];
let overrides = {
    stations: {}, // { stationId: { blocked: bool, banned: bool } }
    edges: {}    // { edgeId: { costAdjustment: number } }
};

// Initialize
const init = async () => {
    loadOverrides();
    stations = stationsData;
    edges = await generateEdges();
    
    setupTabSwitching();
    setupSearch();
    renderStations();
    renderEdges();
    
    document.getElementById('save-all-btn').addEventListener('click', saveAll);
};

const loadOverrides = () => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
        overrides = JSON.parse(saved);
    }
};

const generateEdges = async () => {
    // In a real app, we'd fetch railway.json
    // For now, let's try to fetch it if possible, or use a fallback
    try {
        const response = await fetch('../../frontend/assets/data/railway.json');
        if (!response.ok) throw new Error('Could not load railway.json');
        const railways = await response.json();
        
        const edgeList = [];
        const seenEdges = new Set();

        railways.forEach(line => {
            for (let i = 0; i < line.stations.length - 1; i++) {
                const s1 = line.stations[i];
                const s2 = line.stations[i+1];
                const edgeId = [s1, s2].sort().join('--');
                
                if (!seenEdges.has(edgeId)) {
                    seenEdges.add(edgeId);
                    edgeList.push({
                        id: edgeId,
                        lineName: line.title.en,
                        lineColor: line.color,
                        stationA: s1,
                        stationB: s2,
                        baseCost: 100 // Default cost
                    });
                }
            }
        });
        return edgeList;
    } catch (err) {
        console.warn('Using fallback edges:', err);
        return [];
    }
};

// Tab Switching
const setupTabSwitching = () => {
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');
    const tabTitle = document.getElementById('tab-title');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const tab = item.dataset.tab;
            
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');
            
            tabContents.forEach(c => c.classList.remove('active'));
            document.getElementById(`${tab}-tab`).classList.add('active');
            
            tabTitle.textContent = tab === 'stations' ? 'Station Management' : 'Edge Cost Adjustments';
        });
    });
};

// Search
const setupSearch = () => {
    const searchBox = document.getElementById('search-box');
    searchBox.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        filterData(query);
    });
};

const filterData = (query) => {
    const activeTab = document.querySelector('.nav-item.active').dataset.tab;
    if (activeTab === 'stations') {
        renderStations(query);
    } else {
        renderEdges(query);
    }
};

// Rendering
const renderStations = (query = '') => {
    const list = document.getElementById('stations-list');
    list.innerHTML = '';
    
    stations
        .filter(s => s.title.toLowerCase().includes(query))
        .slice(0, 50) // Limit for performance
        .forEach(s => {
            const id = s.title; // Using title as ID if real ID is missing in stations-data
            const sOverride = overrides.stations[id] || { blocked: false, banned: false };
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${s.title}</strong></td>
                <td><small>${id}</small></td>
                <td>${s.coord[0].toFixed(3)}, ${s.coord[1].toFixed(3)}</td>
                <td class="actions-cell">
                    <button class="btn-icon btn-block-transfer ${sOverride.blocked ? 'active' : ''}" onclick="toggleStationProp('${id}', 'blocked')">
                        ${sOverride.blocked ? 'Unblock Transfer' : 'Block Transfer'}
                    </button>
                    <button class="btn-icon btn-ban ${sOverride.banned ? 'active' : ''}" onclick="toggleStationProp('${id}', 'banned')">
                        ${sOverride.banned ? 'Unban' : 'Ban Station'}
                    </button>
                </td>
            `;
            list.appendChild(tr);
        });
};

const renderEdges = (query = '') => {
    const list = document.getElementById('edges-list');
    list.innerHTML = '';
    
    edges
        .filter(e => e.lineName.toLowerCase().includes(query) || e.stationA.toLowerCase().includes(query) || e.stationB.toLowerCase().includes(query))
        .slice(0, 50)
        .forEach(e => {
            const eOverride = overrides.edges[e.id] || { costAdjustment: 0 };
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><span style="color: ${e.lineColor}">●</span> ${e.lineName}</td>
                <td><small>${e.stationA.split('.').pop()}</small></td>
                <td><small>${e.stationB.split('.').pop()}</small></td>
                <td>${e.baseCost}</td>
                <td>
                    <input type="number" class="cost-input" value="${eOverride.costAdjustment}" 
                        onchange="updateEdgeCost('${e.id}', this.value)">
                </td>
            `;
            list.appendChild(tr);
        });
};

// Global handlers (for simplicity in string-based HTML)
window.toggleStationProp = (id, prop) => {
    if (!overrides.stations[id]) overrides.stations[id] = { blocked: false, banned: false };
    overrides.stations[id][prop] = !overrides.stations[id][prop];
    renderStations(document.getElementById('search-box').value);
};

window.updateEdgeCost = (id, value) => {
    if (!overrides.edges[id]) overrides.edges[id] = { costAdjustment: 0 };
    overrides.edges[id].costAdjustment = parseInt(value) || 0;
};

const saveAll = () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(overrides));
    showToast('Settings saved successfully!');
};

const showToast = (msg) => {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
};

init();
