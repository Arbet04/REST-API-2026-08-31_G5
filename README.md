# Image Processing Workshop — Edge & Corner Detection (REST API + Flask)

โปรเจกต์นี้ทำตามโจทย์ Workshop ครบทั้ง 4 ข้อ:
1. Backend (Flask) 1 เครื่อง + Frontend (HTML/JS) 1 เครื่อง
2. Service รับไฟล์ภาพจาก Client แล้วประมวลผล (Edge Detection / Corner Detection) ที่ฝั่ง Server ด้วย OpenCV
3. ส่งภาพผลลัพธ์กลับไปให้ Client แสดงผล
4. สื่อสารกันผ่าน REST API (Flask)

```
image-processing-workshop/
├── backend/
│   ├── app.py           # Flask REST API server
│   └── requirements.txt
├── frontend/
│   └── index.html        # หน้าเว็บอัปโหลดภาพ + แสดงผลลัพธ์
└── README.md
```

## วิธีรัน

### 1) เครื่อง Server — รัน Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

จะได้ REST API ที่ `http://<server-ip>:5000` พร้อม endpoints:

| Method | Endpoint        | หน้าที่                                   |
|--------|-----------------|--------------------------------------------|
| GET    | `/api/health`   | เช็คว่า server พร้อมใช้งาน                 |
| POST   | `/api/process`  | รับไฟล์ภาพ (`image`) + `operation` (`edge` หรือ `corner`) แล้วส่งภาพผลลัพธ์กลับ (PNG) |

ถ้าจะทดสอบข้ามเครื่อง ให้หา IP ของเครื่อง server ด้วย `ipconfig` (Windows) หรือ `ifconfig`/`ip addr` (Mac/Linux) เช่น `192.168.1.100`

### 2) เครื่อง Client — เปิด Frontend

```bash
cd frontend
python -m http.server 8000
```

แล้วเปิดเบราว์เซอร์ไปที่ `http://localhost:8000`
- ช่อง **Backend URL** ให้ใส่ URL ของเครื่อง server เช่น `http://192.168.1.100:5000`
- เลือกไฟล์ภาพ, เลือก operation (`Edge Detection` หรือ `Corner Detection`)
- กด **Upload & Process** → ภาพต้นฉบับกับภาพผลลัพธ์จะแสดงเทียบกัน

## หลักการประมวลผลที่ใช้
- **Edge Detection** → Canny edge detector (`cv2.Canny`) บนภาพ grayscale ที่เบลอด้วย Gaussian ก่อน เพื่อลด noise
- **Corner Detection** → Harris corner detector (`cv2.cornerHarris`) แล้ว mark มุมที่เจอเป็นสีแดงทับบนภาพต้นฉบับ

ทั้งสอง endpoint ผ่านการทดสอบแล้วว่าทำงานได้จริง (health check คืน 200, process คืนภาพ PNG ทั้งสอง operation)

## ต่อยอด (ถ้าต้องการ)
- เพิ่ม parameter ปรับ threshold ของ Canny หรือ sensitivity ของ Harris จากฝั่ง frontend
- เพิ่ม operation อื่น ๆ เช่น Sobel, Laplacian
- ทำ error handling เพิ่มเติม เช่น จำกัดขนาด/ชนิดไฟล์ที่อัปโหลด
