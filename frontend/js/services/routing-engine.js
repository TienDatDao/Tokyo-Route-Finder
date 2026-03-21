/**
 * Gửi dữ liệu lên Backend để tìm đường tối ưu
 */
export const findOptimalPath = async (stations, startId, endId, priority) => {
    console.log("🚀 Đang gửi dữ liệu lên Backend...");

    const url = 'http://127.0.0.1:5000/find-route'; // Địa chỉ Server Python

    const payload = {
        stations: stations, // Toàn bộ file JSON bạn muốn "ném" lên
        startId: startId,
        endId: endId,
        priority: priority
    };

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const result = await response.json();
        console.log("✅ Đã nhận kết quả từ Backend:", result);
        return result;

    } catch (error) {
        console.error("❌ Lỗi khi gọi API Backend:", error);
        alert("Không thể kết nối với Backend. Hãy đảm bảo file Python đang chạy!");
        return null;
    }
};