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

        this.allStations = [];
        this.selectedStartStation = null;
        this.selectedEndStation = null;

        if (this.startSearchInput) this.setupStationSearch('start');
        if (this.endSearchInput) this.setupStationSearch('end');

        if (this.resultPanel) {
            this.resultPanel.addEventListener('click', (event) => {
                const item = event.target.closest('.route-step-clickable');
                if (!item) return;

                const lat = item.dataset.stationLat;
                const lng = item.dataset.stationLng;
                let stationCoords = null;
                if (lat !== undefined && lng !== undefined && lat !== '' && lng !== '') {
                    stationCoords = [parseFloat(lat), parseFloat(lng)];
                }

                if (!stationCoords) {
                    const stationId = item.dataset.stationId;
                    const stationName = item.dataset.stationName ? decodeURIComponent(item.dataset.stationName) : null;
                    stationCoords = this.findStationCoordsById(stationId) || this.findStationCoordsByName(stationName);
                }

                if (stationCoords && window.mapViewInstance) {
                    window.mapViewInstance.focusOnRouteStation(stationCoords);
                }
            });
        }
    }

    buildStationGroups(stations) {
        const groups = new Map();

        stations.forEach(station => {
            const stationName = station.title?.en || station.name || station.id;
            const key = stationName.trim().toLowerCase();
            const existingGroup = groups.get(key);

            if (!existingGroup) {
                groups.set(key, {
                    id: station.id,
                    name: stationName,
                    stationIds: [station.id],
                    coords: [station.coord]
                });
            } else {
                existingGroup.stationIds.push(station.id);
                existingGroup.coords.push(station.coord);
            }
        });

        return Array.from(groups.values()).map(group => {
            const coordSum = group.coords.reduce(
                (acc, coord) => [acc[0] + coord[0], acc[1] + coord[1]],
                [0, 0]
            );
            return {
                id: group.id,
                name: group.name,
                stationIds: group.stationIds,
                coord: [coordSum[0] / group.coords.length, coordSum[1] / group.coords.length]
            };
        });
    }

    populateStations(stations) {
        if (!Array.isArray(stations) || stations.length === 0) return;

        this.allStations = this.buildStationGroups(stations);
        console.log('Stations loaded into autocomplete:', this.allStations.length);
    }

    setupReloadMapButton(callback) {
        const reloadBtn = document.getElementById('reload-map-btn');
        if (!reloadBtn) return;

        reloadBtn.addEventListener('click', () => {
            if (callback) callback();
        });
    }

    setupStationSearch(stationType) {
        const searchInput = stationType === 'start' ? this.startSearchInput : this.endSearchInput;
        const dropdown = stationType === 'start' ? this.startSuggestionsDropdown : this.endSuggestionsDropdown;

        if (!searchInput || !dropdown) return;

        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.trim();
            this.showSuggestions(stationType, searchTerm);
        });

        searchInput.addEventListener('focus', (e) => {
            this.showSuggestions(stationType, e.target.value.trim());
        });

        searchInput.addEventListener('blur', () => {
            setTimeout(() => dropdown.classList.remove('active'), 200);
        });

        document.addEventListener('click', (e) => {
            if (e.target !== searchInput && !dropdown.contains(e.target)) {
                dropdown.classList.remove('active');
            }
        });
    }

    showSuggestions(stationType, searchTerm) {
        const searchInput = stationType === 'start' ? this.startSearchInput : this.endSearchInput;
        const dropdown = stationType === 'start' ? this.startSuggestionsDropdown : this.endSuggestionsDropdown;
        const stationIdInput = stationType === 'start' ? this.startStationId : this.endStationId;

        if (!searchInput || !dropdown || this.allStations.length === 0) {
            return;
        }

        const normalizedSearch = searchTerm.trim().toLowerCase();
        const filtered = normalizedSearch.length === 0
            ? this.allStations
            : this.allStations.filter(station => station.name.toLowerCase().includes(normalizedSearch));

        let html = '';
        const displayCount = Math.min(filtered.length, 100);

        if (filtered.length === 0) {
            html = '<div class="suggestion-empty">Không tìm thấy ga</div>';
        } else {
            html = filtered.slice(0, displayCount).map(station => {
                return `<div class="suggestion-item" data-name="${station.name}">${station.name}</div>`;
            }).join('');

            if (filtered.length > 100) {
                html += `<div class="suggestion-empty" style="font-size: 0.8rem; color: #666;">...hiển thị 100 trên ${filtered.length}</div>`;
            }
        }

        dropdown.innerHTML = html;
        dropdown.classList.add('active');

        dropdown.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                const stationName = item.getAttribute('data-name');
                const stationData = this.allStations.find(s => s.name === stationName);

                if (!stationData) return;

                searchInput.value = stationName;
                stationIdInput.value = stationName;

                const selectedStation = {
                    name: stationName,
                    ids: stationData.stationIds,
                    coord: stationData.coord
                };

                if (stationType === 'start') {
                    this.selectedStartStation = selectedStation;
                } else {
                    this.selectedEndStation = selectedStation;
                }

                if (stationData.coord && window.mapViewInstance) {
                    window.mapViewInstance.focusOnStation(stationData.coord, stationName, stationType);
                }

                dropdown.classList.remove('active');
            });
        });
    }

    onSearchRequested(callback) {
        if (!this.btnFindPath) return;

        this.btnFindPath.addEventListener('click', () => {
            const startName = this.selectedStartStation ? this.selectedStartStation.name : this.startSearchInput?.value.trim();
            const endName = this.selectedEndStation ? this.selectedEndStation.name : this.endSearchInput?.value.trim();

            if (!startName) {
                alert('Vui lòng chọn ga xuất phát');
                return;
            }

            if (!endName) {
                alert('Vui lòng chọn ga đích');
                return;
            }

            const searchData = {
                startName,
                endName,
                criteria: this.getSelectedPriority()
            };

            this.setLoading(true);
            callback(searchData);
            setTimeout(() => this.setLoading(false), 500);
        });
    }

    getSelectedPriority() {
        let selected = 'shortest_time';
        this.priorityRadios.forEach(radio => {
            if (radio.checked) selected = radio.value;
        });
        return selected;
    }

    findStationCoordsById(stationId) {
        if (!stationId || !this.allStations) return null;
        const group = this.allStations.find(station => station.stationIds.includes(stationId));
        return group ? group.coord : null;
    }

    findStationCoordsByName(stationName) {
        if (!stationName || !this.allStations) return null;
        const normalizedName = stationName.trim().toLowerCase();
        const group = this.allStations.find(station => station.name.trim().toLowerCase() === normalizedName);
        return group ? group.coord : null;
    }

    showResults(route) {
        if (!route) {
            this.resultPanel.innerHTML = `<div class="result-card"><p style="color:#d32f2f;">Không tìm thấy tuyến đường phù hợp.</p></div>`;
            return;
        }

        const keySteps = (route.details || []).filter(step => ['Board', 'Transfer', 'Arrive'].includes(step.action));
        const detailRows = keySteps.map((step, index) => {
            const nextStep = keySteps[index + 1] || null;
            const lineLabelValue = step.line && step.line.toLowerCase() !== 'walk'
                ? step.line
                : nextStep && nextStep.line && nextStep.line.toLowerCase() !== 'walk'
                    ? nextStep.line
                    : '';
            const lineLabel = lineLabelValue ? `<strong>${lineLabelValue}</strong>` : '';
            const stationName = step.station_name || 'Unknown';
            const stationNameEscaped = encodeURIComponent(stationName);
            const coords = step.coords || this.findStationCoordsById(step.station_id) || this.findStationCoordsByName(stationName);
            const clickableClass = coords ? 'route-step-clickable' : '';
            const dataAttr = coords ? `data-station-id="${step.station_id}" data-station-name="${stationNameEscaped}" data-station-lat="${coords[0]}" data-station-lng="${coords[1]}"` : '';
            let description = '';

            if (step.action === 'Board') {
                description = `Bắt đầu tại ga <strong>${stationName}</strong>${lineLabel ? `, đi tuyến ${lineLabel}` : ''}`;
            } else if (step.action === 'Transfer') {
                description = `Tại ga <strong>${stationName}</strong>, xuống và chuyển sang tuyến ${lineLabel || '<strong>không rõ</strong>'}`;
            } else {
                description = `Đích đến: <strong>${stationName}</strong>`;
            }

            return `<div class="route-step ${clickableClass}" ${dataAttr}>
                        ${description}
                    </div>`;
        }).join('');

        this.resultPanel.innerHTML = `
            <div class="result-card">
                <h3>Kết quả hành trình</h3>
                <p>⏱ <strong>Thời gian:</strong> ${route.total_time.toFixed(1)} phút</p>
                <p>💰 <strong>Chi phí:</strong> ${route.total_cost.toFixed(0)} ¥</p>
                <p>🔁 <strong>Đổi tuyến:</strong> ${route.transfers}</p>
                <p>📍 <strong>Số ga ghi danh:</strong> ${((route.details || []).filter(step => ['Board', 'Transfer', 'Arrive'].includes(step.action))).length}</p>
            </div>
            <div class="result-card">
                <h3>Hướng dẫn</h3>
                ${detailRows || '<p>Không có bước đường nào.</p>'}
            </div>
        `;
    }

    setLoading(isLoading) {
        if (!this.btnFindPath) return;
        this.btnFindPath.disabled = isLoading;
        this.btnFindPath.innerText = isLoading ? 'Đang tìm...' : 'Find Route';
    }
}