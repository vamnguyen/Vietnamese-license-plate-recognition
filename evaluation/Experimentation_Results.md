# Báo cáo Kết quả Thực nghiệm

Tài liệu này tổng hợp kết quả đánh giá thực nghiệm cho hai giai đoạn: Phát hiện biển số (LPD) và Nhận diện ký tự (OCR/LPR).

## 1. Giai đoạn 1: Phát hiện biển số (License Plate Detection)

Mô hình được đánh giá trên tập validation bao gồm **1652** ảnh.
Cấu hình đánh giá:

- Model: YOLOv5m
- Image Size: 320x320
- Conf Threshold: 0.001
- IoU Threshold: 0.6

**Kết quả (từ quá trình huấn luyện - best epoch):**

| Metric         | Giá trị    | Giải thích                                                      |
| -------------- | ---------- | --------------------------------------------------------------- |
| **Precision**  | **0.993**  | Tỷ lệ dự đoán đúng trên tổng số dự đoán (TP / (TP + FP))        |
| **Recall**     | **0.996**  | Tỷ lệ phát hiện được trên tổng số ground truth (TP / (TP + FN)) |
| **mAP@0.5**    | **0.994**  | Mean Average Precision tại ngưỡng IoU 0.5                       |
| **F1-Score\*** | **0.9945** | Trung bình điều hòa của Precision và Recall                     |

_\*F1-Score được tính theo công thức:_ `2 * (Precision * Recall) / (Precision + Recall)`

> **Nhận xét**: Mô hình đạt độ chính xác và độ nhạy rất cao (>99%), cho thấy khả năng phát hiện vị trí biển số cực kỳ chính xác trong các điều kiện ánh sáng và góc chụp khác nhau của tập dataset.

---

## 2. Giai đoạn 2: Nhận diện biển số (Optical Character Recognition)

Mô hình được đánh giá trên tập validation bao gồm **767** ảnh biển số đã được crop.
Đánh giá dựa trên 2 độ đo chính theo yêu cầu:

1. **Character Accuracy**: Độ chính xác theo từng ký tự.
2. **Plate Accuracy**: Độ chính xác tuyệt đối theo từng biển số (đúng toàn bộ chuỗi ký tự).

**Kết quả thực nghiệm:**

| Metric                     | Kết quả    | Chi tiết                                 |
| -------------------------- | ---------- | ---------------------------------------- |
| **Tổng số biển số**        | 767        | Số lượng ảnh đầu vào cho OCR             |
| **Tổng số ký tự**          | 6720       | Tổng số ký tự trong ground truth         |
| **Số ký tự đúng**          | 6321       | Số ký tự model nhận diện khớp với nhãn   |
| **Số biển đúng hoàn toàn** | 631        | Số biển số nhận diện đúng 100% các ký tự |
| **Character Accuracy**     | **94.06%** | (6321 / 6720)                            |
| **Plate Accuracy**         | **82.27%** | (631 / 767)                              |

> **Nhận xét**:
>
> - **Character Accuracy (94.06%)** phản ánh khả năng nhận diện tốt các ký tự riêng lẻ của mô hình.
> - **Plate Accuracy (82.27%)** thấp hơn do tiêu chuẩn khắt khe (sai 1 ký tự coi như sai cả biển). Các lỗi chủ yếu có thể đến từ sự nhầm lẫn giữa các ký tự có hình dạng giống nhau (ví dụ: 8 và B, 0 và D) hoặc do ảnh bị mờ/nhòe/nghiêng quá mức.

## Tổng kết

Hệ thống cho thấy hiệu năng tốt trên tập dữ liệu thử nghiệm:

- Khả năng tìm biển số (Detection) gần như tuyệt đối (~99%).
- Khả năng đọc biển số (Recognition) đạt mức khá tốt (đúng trọn vẹn ~82% số biển, đúng ~94% số ký tự).
