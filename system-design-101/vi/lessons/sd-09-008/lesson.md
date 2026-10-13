# CPU 100%: bắt đầu từ bằng chứng

Ứng dụng chậm và biểu đồ CPU đạt 100%. Đây là dấu hiệu cần quan sát, chưa phải tên lỗi. Trước khi sửa code hoặc tăng máy, hãy xác định CPU được đo cho toàn máy, một core, một process hay giới hạn của container.

![Xác định phạm vi: Một core hay cả máy?; Tìm nơi tiêu tốn: process → thread; Lấy mẫu thực thi: profiler · stack; Đối chiếu tải: request · job · bản phát hành.](../../diagrams/sd-09-008-main.svg)

**Đọc hình:** Các thẻ là các bước hoặc góc nhìn của ví dụ; đọc từ trên xuống. Mũi tên chỉ thứ tự đọc, không biểu diễn luồng mạng hoặc sự phụ thuộc bắt buộc.

Dùng `top` để tìm process bận, rồi lấy profile phù hợp runtime. Nếu cùng một đoạn code xuất hiện liên tục, kiểm tra vòng lặp, busy waiting hoặc thuật toán tốn chi phí. Nếu nhiều request đều dùng CPU hợp lý, có thể lượng công việc đã vượt năng lực xử lý.

Chín hướng điều tra là: vòng lặp không kết thúc; tác vụ nền; lưu lượng tăng; tính toán nặng; áp lực bộ nhớ dẫn tới công việc quản lý bộ nhớ; nhiều process tranh CPU; busy waiting; biểu thức chính quy có chi phí cao; process không mong đợi hoặc mã độc. Đây là giả thuyết để kiểm tra, không phải chín kết luận rút ra từ một con số.

## Nhìn hình thử trả lời

Thêm sleep vào mọi request để CPU giảm có chứng minh nguyên nhân đã được xử lý không?

<details>
<summary>Xem đáp án</summary>

Không. CPU có thể giảm trong khi độ trễ tăng và thông lượng giảm. Cần so với mục tiêu dịch vụ và profile.

</details>

## Giới hạn cần nhớ

Thiếu RAM không luôn làm CPU đạt 100%. Swap và chờ I/O có thể làm máy chậm theo cơ chế khác; đọc cả memory, I/O và load.

<details>
<summary>Xem sâu hơn</summary>

Trên máy nhiều core, phần trăm process có thể vượt 100% tùy công cụ. Load average cũng không đồng nghĩa CPU utilization: trên Linux nó còn tính công việc trong trạng thái chờ không ngắt được.

</details>

## Nguồn đối chiếu

- [Chủ đề ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-9-cases-behind-100-cpu-usage.md). Bài viết và hình này được thiết kế độc lập; không dịch thân bài hoặc sử dụng ảnh nguồn.
- [top](https://man7.org/linux/man-pages/man1/top.1.html).
- [proc: loadavg](https://man7.org/linux/man-pages/man5/proc_loadavg.5.html).
- [Linux perf](https://www.kernel.org/doc/html/latest/admin-guide/perf-security.html).
