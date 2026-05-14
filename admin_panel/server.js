const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
const { execSync } = require('child_process');

const app = express();
const PORT = 5001;

app.use(cors());
app.use(bodyParser.json());
app.use(express.static('public'));

// Biến lưu incident hiện tại
let currentIncidents = [];

// API: Lấy danh sách tất cả các ga và tuyến
app.get('/api/stations-and-lines', (req, res) => {
    try {
        const pythonScript = path.join(__dirname, '..', 'data_system', 'get_stations_lines.py');
        const result = execSync(`python "${pythonScript}"`, { encoding: 'utf-8' });
        // Extract JSON from output (skip logging messages)
        const jsonMatch = result.match(/\{[\s\S]*\}/);
        if (!jsonMatch) {
            throw new Error('No JSON found in Python output');
        }
        const data = JSON.parse(jsonMatch[0]);
        res.json(data);
    } catch (error) {
        console.error('Error getting stations and lines:', error);
        res.status(500).json({ error: error.message });
    }
});

// API: Áp dụng incident (khóa/mở ga hoặc cấm tuyến)
app.post('/api/apply-incident', (req, res) => {
    try {
        const { action, target_id, type } = req.body;

        // Xác thực input
        if (!action || !target_id || !type) {
            return res.status(400).json({ error: 'Missing required fields: action, target_id, type' });
        }

        if (!['STATION_CLOSED', 'LINE_MAINTENANCE'].includes(type)) {
            return res.status(400).json({ error: 'Invalid incident type' });
        }

        if (action === 'apply') {
            // Thêm incident nếu chưa tồn tại
            const exists = currentIncidents.some(inc => inc.target_id === target_id && inc.type === type);
            if (!exists) {
                currentIncidents.push({
                    incident_id: `${Date.now()}`,
                    type: type,
                    target_id: target_id
                });
            }
        } else if (action === 'remove') {
            // Xóa incident
            currentIncidents = currentIncidents.filter(inc => !(inc.target_id === target_id && inc.type === type));
        } else {
            return res.status(400).json({ error: 'Invalid action. Use "apply" or "remove"' });
        }

        // Rebuild graph với incidents mới
        const rebuildSuccess = rebuildGraph();
        
        if (!rebuildSuccess) {
            return res.status(500).json({ error: 'Failed to rebuild graph' });
        }

        res.json({
            status: 'SUCCESS',
            message: `Incident ${action}ed successfully`,
            activeIncidents: currentIncidents
        });
    } catch (error) {
        console.error('Error applying incident:', error);
        res.status(500).json({ error: error.message });
    }
});

// API: Lấy danh sách incident hiện tại
app.get('/api/active-incidents', (req, res) => {
    res.json({
        incidents: currentIncidents,
        count: currentIncidents.length
    });
});

// API: Reset tất cả incidents
app.post('/api/reset-incidents', (req, res) => {
    try {
        currentIncidents = [];
        const rebuildSuccess = rebuildGraph();
        
        if (!rebuildSuccess) {
            return res.status(500).json({ error: 'Failed to rebuild graph after reset' });
        }
        
        res.json({
            status: 'SUCCESS',
            message: 'All incidents reset',
            activeIncidents: currentIncidents
        });
    } catch (error) {
        console.error('Error resetting incidents:', error);
        res.status(500).json({ error: error.message });
    }
});

// Hàm rebuild graph từ Python
function rebuildGraph() {
    try {
        const pythonScript = path.join(__dirname, '..', 'data_system', 'rebuild_graph.py');
        const incidentsJson = JSON.stringify(currentIncidents);
        
        console.log('🔧 Rebuilding graph with incidents:', incidentsJson);
        
        // Gọi Python script để rebuild graph với incidents hiện tại
        const result = execSync(`python "${pythonScript}" '${incidentsJson.replace(/'/g, "'\\''")}'`, { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] });
        
        console.log('📊 Python output:', result.substring(0, 200));
        
        // Extract JSON from output (skip logging messages)
        const jsonMatch = result.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            const response = JSON.parse(jsonMatch[0]);
            console.log('✅ Graph rebuilt successfully:', response.message);
            console.log(`📍 Nodes: ${response.graph_nodes}, Edges: ${response.graph_edges}`);
            return true;
        } else {
            console.log('⚠️ No JSON found in Python output');
            return false;
        }
    } catch (error) {
        console.error('❌ Error rebuilding graph:', error.message);
        console.error('Stack:', error.stack);
        return false;
    }
}

app.listen(PORT, () => {
    console.log(` Admin Panel Server running at http://localhost:${PORT}`);
});

