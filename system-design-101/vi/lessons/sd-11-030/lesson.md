# Giám sát đám mây: chín khía cạnh, và vì sao cảnh báo là khâu dễ sai nhất

**Giám sát không phải một công cụ mà là một đường đi: dữ liệu được thu thập, lưu, phân tích, đưa tới người cần biết, và kết quả quay lại sửa chính cách giám sát.** Bài nguồn gọi chín khía cạnh này trong một bảng so sánh các nhà cung cấp đám mây lớn và công cụ mã nguồn mở. Bài này giữ tên chín khía cạnh, xếp chúng theo đường đi của dữ liệu, và thử một khâu hay hỏng nhất: ngưỡng cảnh báo.

![Hai khung. Khung một, chín khía cạnh của giám sát hệ thống đám mây, xếp theo đường đi của dữ liệu: thu thập, lưu trữ, phân tích, cảnh báo, hiển thị, báo cáo và tuân thủ, tự động hóa, tích hợp, vòng phản hồi. Khung hai, thử nghiệm: một chỉ số ồn có hai sự cố 20 và 15 phút; cảnh báo ngay mẫu đầu vượt ngưỡng báo 38 lần, 32 lần sai; yêu cầu ba mẫu liên tiếp báo 4 lần, không sai lần nào.](../../diagrams/sd-11-030-main.svg)

## Từ viết tắt

- **SLA** (Service Level Agreement) — thỏa thuận mức dịch vụ: cam kết bằng văn bản về mức chất lượng một dịch vụ phải giữ, ví dụ phần trăm thời gian hoạt động; báo cáo tuân thủ thường dựa vào số đo giám sát.

## Đọc hình

**Chín khía cạnh theo đường đi.** *Data Collection* (thu thập): lấy số đo, nhật ký và sự kiện từ nhiều nguồn để có cơ sở ra quyết định. *Data Storage* (lưu trữ): giữ dữ liệu an toàn để phân tích và tham chiếu về sau. *Data Analysis* (phân tích): rút ra điều hữu ích để hành động. *Alerting* (cảnh báo): báo ngay khi có sự kiện nghiêm trọng hay bất thường. *Visualization* (hiển thị): trình bày dữ liệu ở dạng dễ hiểu.

**Bốn khía cạnh còn lại.** *Reporting and Compliance* (báo cáo và tuân thủ): lập báo cáo và chứng minh đáp ứng quy định. *Automation* (tự động hóa): làm các việc lặp lại bằng quy trình tự động. *Integration* (tích hợp): nối và trao đổi dữ liệu giữa các hệ thống và công cụ. *Feedback Loops* (vòng phản hồi): tinh chỉnh chiến lược liên tục dựa trên phản hồi và phân tích hiệu năng.

**Bảng so sánh của nguồn.** Bài nguồn là một hình bảng so sánh ba nhà cung cấp đám mây lớn và các công cụ mã nguồn mở hay bên thứ ba, theo chín khía cạnh trên. Nội dung các ô của hình không có trong văn bản nguồn, nên bài này không nêu tên công cụ nào cho khía cạnh nào.

## Thử: một ngưỡng cảnh báo quá nhạy

Ngày 2026-10-19, một chương trình Python nhỏ. Một chỉ số đo mỗi phút trong 1440 phút (một ngày), bình thường quanh 50 với độ ồn 15; hai sự cố thật kéo giá trị lên quanh 95: một sự cố 20 phút, một sự cố 15 phút. Ngưỡng cảnh báo 80. Ba quy tắc:

| Quy tắc | Số cảnh báo | Cảnh báo sai (ngoài sự cố) | Bắt được sự cố | Trễ so với lúc sự cố bắt đầu |
|---|---|---|---|---|
| Một mẫu vượt ngưỡng | 38 | 32 | 2 trên 2 | 2 và 0 phút |
| Ba mẫu liên tiếp vượt ngưỡng | 4 | 0 | 2 trên 2 | 4 và 4 phút |
| Năm mẫu liên tiếp vượt ngưỡng | 3 | 0 | 2 trên 2 | 6 và 6 phút |

Cảnh báo ngay khi một mẫu vượt ngưỡng nhanh hơn vài phút nhưng kèm 32 cảnh báo sai trong một ngày; một đội trực nhận 32 cảnh báo sai sẽ dần ngừng tin cảnh báo. Đòi nhiều mẫu liên tiếp loại hết cảnh báo sai, đổi lại trễ thêm vài phút. Mỗi khía cạnh khác (lưu, hiển thị, báo cáo) tự nó không sửa được lỗi này, vì nó nằm ở khâu cảnh báo.

## Giới hạn cần nhớ

Dữ liệu là chuỗi sinh bằng nhiễu ngẫu nhiên có chủ đích, không phải đo từ hệ thật; hạt giống khác cho con số khác (ngưỡng nhạy luôn sinh nhiều cảnh báo sai hơn, còn số cụ thể thì đổi). Thử nghiệm chỉ bàn một chỉ số và một loại quy tắc, không bàn tới cảnh báo theo tốc độ đốt ngân sách lỗi hay phát hiện bất thường bằng mô hình. Bài này cũng không đối chiếu bảng so sánh công cụ của hình nguồn.

## Nhìn hình trả lời

Một đội đặt cảnh báo theo mức "một mẫu vượt ngưỡng" và nhận 32 cảnh báo sai mỗi ngày. Họ quyết định tắt hết cảnh báo phát ra ban đêm. Chín khía cạnh nào đang bị phá, và thay đổi nào sửa tận gốc?

<details>
<summary>Xem đáp án</summary>

Khâu cảnh báo bị phá (người trực không còn tin nó), và vòng phản hồi không được dùng (không ai quay lại sửa quy tắc sau mỗi cảnh báo sai). Sửa tận gốc là đổi quy tắc, ví dụ yêu cầu vài mẫu liên tiếp như trong thử nghiệm, thay vì tắt cảnh báo ban đêm, vì khi đó sự cố thật ban đêm cũng không ai biết.
Đây là suy luận của người biên soạn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn liệt kê chín khía cạnh với một câu mô tả mỗi khía cạnh, kèm một bảng so sánh công cụ chỉ có trong hình. Bài này giữ chín tên và mô tả, xếp theo đường đi của dữ liệu, thêm thử nghiệm ngưỡng cảnh báo, và không đưa nội dung bảng so sánh.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/cloud-monitoring-cheat-sheet.md): chín khía cạnh giám sát. Cách xếp, thử nghiệm và đáp án là của người biên soạn.
- [Google SRE Book — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/): bàn về cảnh báo và độ ồn. Chưa mở lại trong phiên viết (không mở được trang từ môi trường); kiến thức chung của người biên soạn.

- Chương trình tạo các con số của bài: `brainstorm/system-design-101-vi/experiments/sd-11-030.py` (chạy được, có kiểm tra đúng giá trị ghi trong bài).

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.
