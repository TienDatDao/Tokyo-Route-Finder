import { CONFIG } from '../config.js';
import { stationsData } from '../data/stations-data.js';

export const fetchStations = async () => {
    try {
        // Try to fetch from backend API first
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/stations`);
        if (!response.ok) throw new Error("Unable to load station data from API");
        const data = await response.json();
        console.log("Stations loaded from API:", data.length);
        return data;
    } catch (error) {
        // Fallback to JSON file
        try {
            const response = await fetch(CONFIG.STATION_DATA_PATH);
            if (!response.ok) throw new Error("Unable to load station data from file");
            const data = await response.json();
            console.log("Stations loaded from file:", data.length);
            return data;
        } catch (fallbackError) {
            // Final fallback to imported data
            console.warn("Both API and file failed, using fallback data:", error.message, fallbackError.message);
            console.log("Fallback stations loaded:", stationsData.length);
            return stationsData;
        }
    }
};