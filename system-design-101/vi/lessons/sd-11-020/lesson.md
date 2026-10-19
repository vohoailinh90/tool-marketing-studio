# Sáu nguyên tắc chịu lỗi, và phép tính vì sao dư thừa có tác dụng

**Chịu lỗi không có nghĩa là không bao giờ hỏng; nghĩa là khi một thành phần hỏng thì người dùng vẫn được phục vụ, hoặc ít nhất thấy một hệ thống chậm đi thay vì biến mất.** Sáu nguyên tắc thường gặp đều xoay quanh hai việc: có sẵn bản thay thế, và biết đổi sang nó đúng lúc.

![Ba khung. Khung một, có bản sao để thay: sao chép dữ liệu, dư thừa thành phần, cân bằng tải. Khung hai, phản ứng khi hỏng: chuyển sang dự phòng, giảm chức năng thay vì sập hẳn, giám sát và cảnh báo. Khung ba, phép tính: hai bản 99% chạy song song cho 99,99%, ba phần 99,9% nối tiếp chỉ còn khoảng 99,7%.](../../diagrams/sd-11-020-main.svg)

## Đọc hình

**Có sẵn bản thay thế (khung một).**

- **Sao chép (replication)**: giữ nhiều bản của cùng dữ liệu hay dịch vụ ở nhiều nơi, để mất một nơi thì còn nơi khác. Cái giá là phải giữ các bản khớp nhau.
- **Dư thừa (redundancy)**: có thêm thành phần chưa cần dùng ngay, sẵn sàng thay thế. Khác sao chép ở chỗ nó nói về thành phần (máy, đường mạng, nguồn điện), không chỉ về dữ liệu.
- **Cân bằng tải (load balancing)**: chia lượng việc vào cho nhiều máy, để không máy nào là điểm hỏng duy nhất. Nếu bản thân bộ cân bằng chỉ có một cái thì chỗ hỏng duy nhất chỉ dời sang đó, nên nó cũng cần dư thừa.

**Phản ứng khi hỏng (khung hai).**

- **Chuyển dự phòng (failover)**: phát hiện bản chính hỏng và chuyển việc sang bản dự phòng, tự động thì mới nhanh. Chuyển không tức thời: có thời gian phát hiện và thời gian chuyển, trong đó người dùng vẫn có thể thấy lỗi.
- **Giảm chức năng có kiểm soát (graceful degradation)**: khi một phần hỏng, tắt bớt tính năng phụ để giữ tính năng chính (trang bán hàng vẫn đặt được đơn khi phần gợi ý sản phẩm hỏng).
- **Giám sát và cảnh báo (monitoring, alerting)**: không thấy lỗi thì không chữa được; cũng không chuyển dự phòng đúng lúc được nếu không đo sức khỏe.

## Tính thử: vì sao dư thừa có tác dụng

Độ sẵn sàng là tỷ lệ thời gian một thành phần hoạt động. Một năm có khoảng 8760 giờ.

| Độ sẵn sàng | Thời gian ngừng mỗi năm |
|---|---|
| 99% | khoảng 87,6 giờ (3,65 ngày) |
| 99,9% | khoảng 8,76 giờ |
| 99,99% | khoảng 52,6 phút |

Hai phép tính cho thấy dư thừa làm gì, nếu các thành phần hỏng **độc lập** với nhau:

- **Song song** (chỉ cần một cái sống): độ sẵn sàng chung = 1 − (1 − a)². Hai bản 99% cho 1 − 0,01² = 0,9999, tức 99,99%. Ba bản cho 99,9999%.
- **Nối tiếp** (cần tất cả cùng sống): độ sẵn sàng chung = tích các độ sẵn sàng. Ba phần mỗi phần 99,9% cho 0,999³ ≈ 0,9970, tức khoảng 99,7%, kém hơn từng phần.

Vì vậy một chuỗi dài nối tiếp thì yếu hơn mắt xích yếu nhất, và dư thừa ở những mắt xích đó là cách rẻ nhất để kéo lên.

## Giới hạn cần nhớ

Phép tính song song chỉ đúng khi các bản hỏng độc lập. Hai máy cùng chạy một phiên bản phần mềm có lỗi, cùng nằm trong một phòng máy mất điện, hay cùng phụ thuộc một cơ sở dữ liệu thì có thể hỏng cùng lúc, và lợi ích thật nhỏ hơn con số 99,99%. Phép tính cũng bỏ qua thời gian chuyển dự phòng. Còn dư thừa có chi phí thật: thêm máy, thêm việc giữ bản sao đồng bộ, thêm chỗ có thể sai.

## Nhìn hình trả lời

Một dịch vụ chạy hai máy ở hai nơi, nhưng cả hai cùng đọc và ghi vào một cơ sở dữ liệu duy nhất. Hai máy này cho độ sẵn sàng cao hơn một máy đến đâu?

<details>
<summary>Xem đáp án</summary>

Chỉ phần máy chủ ứng dụng được dư thừa; cơ sở dữ liệu vẫn là một mắt xích đơn nối tiếp với chúng. Độ sẵn sàng chung bị chặn trên bởi độ sẵn sàng của cơ sở dữ liệu: nếu nó 99,9% thì cả hệ thống không thể hơn 99,9%, dù hai máy ứng dụng cộng lại đạt 99,99%.
Đây là suy luận của người biên soạn từ phép tính nối tiếp ở trên.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn liệt kê sáu nguyên tắc, mỗi nguyên tắc một câu định nghĩa. Bài này giữ tên sáu nguyên tắc nhưng gom chúng thành hai nhóm (bản thay thế và phản ứng khi hỏng), rồi thêm phép tính song song và nối tiếp cùng giới hạn của nó. Công thức là toán thuần; chưa đối chiếu với trang của một nhà cung cấp đám mây cụ thể.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/a-cheat-sheet-for-designing-fault-tolerant-systems.md): sáu nguyên tắc. Cách nhóm, phép tính và đáp án là của người biên soạn.
- [AWS Well-Architected — Reliability Pillar: Availability](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/availability.html): công thức độ sẵn sàng nối tiếp và song song. Kiến thức chung, chưa mở lại trong phiên viết.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.
