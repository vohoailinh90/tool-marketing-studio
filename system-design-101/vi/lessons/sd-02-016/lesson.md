# Airbnb: từ Monorail tới bốn tầng dịch vụ

**Theo bài nguồn, Airbnb bắt đầu bằng một khối nguyên Ruby on Rails tên Monorail, rồi khi tăng trưởng quá nhanh thì chuyển sang kiến trúc hướng dịch vụ với bốn tầng: dịch vụ dữ liệu, dữ liệu dẫn xuất, tầng giữa và trình bày.**
Bài này đi theo hai câu hỏi: vì sao phải rời khối nguyên, và bốn tầng dịch vụ mới chia việc thế nào.

![Một khung trước, một khung sau và một khung ghi nhớ. Trước: Monorail, một khối nguyên Ruby on Rails lo cả phía máy khách lẫn máy chủ, gặp vấn đề khi Airbnb tăng trưởng quá nhanh. Sau: máy khách gửi yêu cầu tới một cổng, cổng chuyển tới các dịch vụ xếp thành bốn tầng từ dưới lên: dịch vụ dữ liệu là lối vào duy nhất để đọc ghi dữ liệu; dịch vụ dữ liệu dẫn xuất đọc từ dịch vụ dữ liệu và áp logic nghiệp vụ cơ bản; dịch vụ tầng giữa giữ logic nghiệp vụ quan trọng không hợp hai tầng dưới; dịch vụ trình bày gộp dữ liệu từ các tầng khác và áp logic riêng cho giao diện. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-02-016-main.svg)

## Từ viết tắt

- **SOA** (Service-Oriented Architecture) — kiến trúc hướng dịch vụ: hệ thống được chia thành nhiều dịch vụ nối lỏng với nhau qua mạng, thay vì một chương trình lớn.

## Đọc hình

**Trước: Monorail.** Theo bài nguồn, Airbnb có mặt ở hơn 200 quốc gia, đã giúp 4 triệu chủ nhà đón hơn 1,5 tỷ lượt khách. Ban đầu nó là một khối nguyên viết bằng Ruby on Rails, nội bộ gọi là Monorail. Khối nguyên này là một tầng duy nhất, lo cả phần máy khách lẫn phần máy chủ. Khi Airbnb tăng trưởng quá nhanh, Monorail bắt đầu gặp vấn đề, và Airbnb chuyển dần sang SOA.

**Sau: bốn tầng dịch vụ.** Với Airbnb, SOA là một mạng các dịch vụ nối lỏng: máy khách gửi yêu cầu tới một cổng, cổng chuyển yêu cầu tới nhiều dịch vụ và cơ sở dữ liệu. Các loại dịch vụ, từ dưới lên:
- Dịch vụ dữ liệu: tầng dưới cùng, lối vào cho mọi thao tác đọc và ghi trên các thực thể dữ liệu.
- Dịch vụ dữ liệu dẫn xuất: đọc từ dịch vụ dữ liệu và áp logic nghiệp vụ cơ bản.
- Dịch vụ tầng giữa: giữ logic nghiệp vụ quan trọng không hợp đặt ở hai tầng dưới.
- Dịch vụ trình bày: gộp dữ liệu từ mọi dịch vụ khác và áp thêm logic riêng cho giao diện.

Sau khi chuyển xong, Monorail bị bỏ hẳn, mọi thao tác đọc ghi chuyển sang các dịch vụ mới.

## Giới hạn cần nhớ

Bài nguồn không nói Monorail gặp vấn đề cụ thể gì, cuộc chuyển kéo dài bao lâu, hay có bao nhiêu dịch vụ. Các con số về quốc gia, chủ nhà và lượt khách là của bài nguồn, không kèm năm. Lý do chia bốn tầng ở phần dưới là cách đọc của người biên soạn.

## Nhìn hình thử trả lời

Một dịch vụ trình bày cần thông tin một căn phòng. Theo hình, nó có nên đọc thẳng cơ sở dữ liệu không? Nếu không thì đọc qua đâu?

<details>
<summary>Xem đáp án</summary>

Không. Dịch vụ dữ liệu là lối vào cho mọi thao tác đọc ghi trên dữ liệu, nên dịch vụ trình bày lấy thông tin qua các tầng dưới (dịch vụ dữ liệu, có thể qua dịch vụ dẫn xuất hay tầng giữa), rồi gộp lại cho giao diện.

</details>

<details>
<summary>Xem sâu hơn: vì sao có một lối vào dữ liệu duy nhất</summary>

- Đổi cách lưu một thực thể chỉ phải sửa một dịch vụ, không phải mọi nơi đang đọc thẳng cơ sở dữ liệu.
- Quy tắc kiểm tra dữ liệu nằm ở một chỗ.
- Cái giá: mỗi yêu cầu đi qua nhiều dịch vụ hơn, nên chậm hơn và nhiều chỗ có thể hỏng hơn.

Đây là nhận xét chung của người biên soạn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/airbnb-artchitectural-evolution.md): Monorail, lý do chuyển sang SOA và bốn loại dịch vụ.

Đã đọc nguồn ngày 2026-10-19. Tài liệu kỹ thuật của Airbnb chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.
