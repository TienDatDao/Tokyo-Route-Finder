/**
 * Lớp UIControls quản lý tất cả các tương tác người dùng trên Sidebar
 */
export class UIControls {
    constructor() {
        // Start Station
        this.startSearchInput = document.getElementById('start-search');
        this.startSuggestionsDropdown = document.getElementById('suggestions-dropdown');
        this.startStationId = document.getElementById('start-station-id');

        // End Station
        this.endSearchInput = document.getElementById('end-search');
        this.endSuggestionsDropdown = document.getElementById('end-suggestions-dropdown');
        this.endStationId = document.getElementById('end-station-id');

        // Other controls
        this.btnFindPath = document.getElementById('find-path-btn');
        this.resultPanel = document.getElementById('result-info');
        this.priorityRadios = document.getElementsByName('priority');

        // Debug: Check if all elements exist
        console.log('=== UIControls Constructor ===');
        console.log('startSearchInput:', this.startSearchInput ? '✓' : '✗');
        console.log('startSuggestionsDropdown:', this.startSuggestionsDropdown ? '✓' : '✗');
        console.log('endSearchInput:', this.endSearchInput ? '✓' : '✗');
        console.log('endSuggestionsDropdown:', this.endSuggestionsDropdown ? '✓' : '✗');

        this.allStations = [];
        this.selectedStartStation = null;
        this.selectedEndStation = null;

        if (this.startSearchInput) this.setupStationSearch('start');
        if (this.endSearchInput) this.setupStationSearch('end');
    }

    /**
     * Đổ dữ liệu ga tàu vào các thẻ Select
     * @param {Array} stations - Danh sách các ga tàu từ API
     */
    populateStations(stations) {
        if (!stations) return;

        this.allStations = stations;
        console.log('Stations loaded:', stations.length); // Debug
    }

    /**
     * Setup map reload button
     */
    setupReloadMapButton(callback) {
        const reloadBtn = document.getElementById('reload-map-btn');
        if (!reloadBtn) return;

        reloadBtn.addEventListener('click', () => {
            console.log('Reload map button clicked');
            if (callback) callback();
        });
    }

    /**
     * Setup autocomplete search for station (both start and end)
     */
    setupStationSearch(stationType) {
        const searchInput = stationType === 'start' ? this.startSearchInput : this.endSearchInput;
        const dropdown = stationType === 'start' ? this.startSuggestionsDropdown : this.endSuggestionsDropdown;

        if (!searchInput || !dropdown) {
            console.error(`[${stationType}] Missing DOM elements`);
            return;
        }

        console.log(`[${stationType}] Setting up station search`);

        // Input event for autocomplete suggestions
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.trim();
            console.log(`[${stationType}] Input event:`, searchTerm);
            this.showSuggestions(stationType, searchTerm);
        });

        // Focus event to show all stations
        searchInput.addEventListener('focus', (e) => {
            console.log(`[${stationType}] Focus event. Stations available:`, this.allStations.length);
            if (this.allStations.length > 0) {
                this.showSuggestions(stationType, e.target.value.trim());
            } else {
                console.log(`[${stationType}] Waiting for station data to load...`);
            }
        });

        // Blur event to hide suggestions after a short delay
        searchInput.addEventListener('blur', (e) => {
            console.log(`[${stationType}] Blur event`);
            setTimeout(() => {
                dropdown.classList.remove('active');
            }, 200);
        });

        // Click away to hide suggestions
        document.addEventListener('click', (e) => {
            if (e.target !== searchInput && !dropdown.contains(e.target)) {
                dropdown.classList.remove('active');
            }
        });
    }

    /**
     * Show suggestions dropdown for a station type
     */
    showSuggestions(stationType, searchTerm) {
        const searchInput = stationType === 'start' ? this.startSearchInput : this.endSearchInput;
        const dropdown = stationType === 'start' ? this.startSuggestionsDropdown : this.endSuggestionsDropdown;
        const stationIdInput = stationType === 'start' ? this.startStationId : this.endStationId;

        // Only show suggestions if we have data loaded
        if (this.allStations.length === 0) {
            return;
        }

        const filtered = searchTerm.length === 0
            ? this.allStations
            : this.allStations.filter(station => {
                const name = station.title?.en || station.name || station.id;
                return name.toLowerCase().includes(searchTerm.toLowerCase());
            });

        // Build HTML for suggestions - limit to 100 items for performance
        let html = '';
        const displayCount = Math.min(filtered.length, 100);

        if (filtered.length === 0) {
            html = '<div class="suggestion-empty">No stations found</div>';
        } else {
            html = filtered.slice(0, displayCount).map((station) => {
                const name = station.title?.en || station.name || station.id;
                return `<div class="suggestion-item" data-id="${station.id}" data-name="${name}">${name}</div>`;
            }).join('');

            if (filtered.length > 100) {
                html += `<div class="suggestion-empty" style="font-size: 0.8rem; color: #ccc;">...showing 100 of ${filtered.length}</div>`;
            }
        }

        dropdown.innerHTML = html;
        dropdown.classList.add('active');

        // Add click handlers to suggestion items
        dropdown.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                const stationId = item.getAttribute('data-id');
                const stationName = item.getAttribute('data-name');

                searchInput.value = stationName;
                stationIdInput.value = stationId;

                // 1. Tìm object nhà ga trong danh sách allStations để lấy tọa độ
                const stationData = this.allStations.find(s => s.id === stationId);

                if (stationType === 'start') {
                    this.selectedStartStation = { id: stationId, name: stationName };
                } else {
                    this.selectedEndStation = { id: stationId, name: stationName };
                }

                // 2. Gọi MapViewInstance để di chuyển bản đồ đến ga vừa chọn
                // Lưu ý: MapView.js đã gán instance vào window.mapViewInstance
                if (stationData && stationData.coord && window.mapViewInstance) {
                    window.mapViewInstance.focusOnStation(
                        stationData.coord,
                        stationName,
                        stationType // Biến này có sẵn trong hàm showSuggestions
                    );
                }

                dropdown.classList.remove('active');
            });
        });
    }

    /**
     * Lắng nghe sự kiện click nút tìm đường
     * @param {Function} callback - Hàm sẽ được gọi khi người dùng nhấn nút
     */
    onSearchRequested(callback) {
        this.btnFindPath.addEventListener('click', () => {
            // Use selected stations or get from hidden inputs
            const startId = this.selectedStartStation ? this.selectedStartStation.id : this.startStationId.value;
            const endId = this.selectedEndStation ? this.selectedEndStation.id : this.endStationId.value;

            if (!startId) {
                alert('Please select a starting station');
                return;
            }

            if (!endId) {
                alert('Please select an ending station');
                return;
            }

            const searchData = {
                startId: startId,
                endId: endId,
                priority: this.getSelectedPriority()
            };

            // Hiệu ứng loading nhẹ cho nút bấm
            this.setLoading(true);

            // Gọi hàm callback từ app.js truyền sang
            callback(searchData);

            setTimeout(() => this.setLoading(false), 500);
        });
    }

    /**
     * Lấy tiêu chí ưu tiên hiện tại (Thời gian/Giá tiền)
     */
    getSelectedPriority() {
        let selected = 'time';
        this.priorityRadios.forEach(radio => {
            if (radio.checked) selected = radio.value;
        });
        return selected;
    }

    /**
     * Hiển thị kết quả tính toán lên màn hình
     */
    showResults(data) {
        if (!data) {
            this.resultPanel.innerHTML = `<p style="color:red">Unable to find route!</p>`;
            return;
        }

        this.resultPanel.innerHTML = `
            <div class="result-card">
                <h3>Optimal Route</h3>
                <p>⏱ <strong>Time:</strong> ${data.totalTime} min</p>
                <p>💰 <strong>Fare:</strong> ${data.totalCost} ¥</p>
                <small>Route passes ${data.path.length} stations</small>
            </div>
        `;
    }

    setLoading(isLoading) {
        this.btnFindPath.disabled = isLoading;
        this.btnFindPath.innerText = isLoading ? 'Calculating...' : 'Find Route';
    }
}