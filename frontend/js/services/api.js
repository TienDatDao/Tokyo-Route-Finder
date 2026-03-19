import { CONFIG } from '../config.js';
import { stationsData } from '../data/stations-data.js';

export const fetchStations = async () => {
    try {
        // Try to fetch from JSON file (works with HTTP server)
        const response = await fetch(CONFIG.STATION_DATA_PATH);
        if (!response.ok) throw new Error("Unable to load station data from file");
        const data = await response.json();
        console.log("Stations loaded from file:", data.length);
        return data;
    } catch (error) {
        // Fallback to imported data (works with direct file:// opening)
        console.warn("Fetch failed, using fallback data:", error.message);
        console.log("Fallback stations loaded:", stationsData.length);
        return stationsData;
    }
};