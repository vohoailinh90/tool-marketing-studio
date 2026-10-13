# Tỉ lệ lập trình viên và kiểm thử viên thay đổi thế nào

Vai trò kiểm thử riêng nhỏ đi ở nhiều nơi, nhưng không phải ở mọi nơi. Điều quyết định là chi phí của một lỗi lọt ra ngoài và việc sửa nó nhanh đến đâu.

![Hai thẻ so sánh: khi lỗi sửa rẻ và quay lui nhanh thì kiểm thử chuyển dần sang người viết mã dựa trên công cụ tự động; khi lỗi gây hại lớn hoặc khó thu hồi thì vẫn cần kiểm thử độc lập.](../../diagrams/sd-13-003-main.svg)

**Đọc hình:** không có con số cố định; bài này không dùng tỉ lệ cụ thể vì chúng chỉ là cách kể xu hướng của từng tác giả.

## Nhìn hình thử trả lời

Phần mềm điều khiển thiết bị y tế cập nhật được qua mạng. Có nên bỏ kiểm thử độc lập vì "vá nhanh được"?

<details>
<summary>Xem đáp án</summary>

Không. Việc vá nhanh không bù được tác hại nếu lỗi gây nguy hiểm trước khi kịp vá. Với hậu quả lớn, kiểm thử độc lập vẫn đáng chi.

</details>

## Giới hạn cần nhớ

Nguồn kể xu hướng này qua các mốc thập niên và tỉ lệ dev:test của một số công ty công nghệ lớn, dựa trên bài của Carlos Arguelles. Bài này không lặp lại các mốc và tỉ lệ đó vì chúng là kinh nghiệm cá nhân, không phải thống kê ngành, và chưa được đối chiếu với bản gốc.

<details>
<summary>Xem sâu hơn</summary>

- **Điều kiện để chuyển được:** pipeline kiểm thử tự động, giám sát sau phát hành, khả năng quay lui. Thiếu những điều này thì bỏ vai trò kiểm thử riêng chỉ đẩy rủi ro sang người dùng.
- **Công cụ dùng chung:** khung kiểm thử, môi trường thử và dữ liệu mẫu do một nhóm nền tảng cung cấp giúp người viết mã tự viết test mà không phải dựng lại từ đầu.
- **Kiến thức kiểm thử** vẫn cần được truyền: đào tạo, rà soát test, tư vấn từ người có chuyên môn.
- **Điều bài không khẳng định:** không nói tổ chức cụ thể nào nên giảm hay tăng kiểm thử viên.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/paradigm-shift-how-developer-to-tester-ratio-changed-from-11-to-1001.md).
- Bài gốc của tác giả được nguồn nhắc tới: "The Paradigm Shifts with Different Dev:Test Ratios" (Carlos Arguelles). Bài này chưa đọc lại bản đó.
