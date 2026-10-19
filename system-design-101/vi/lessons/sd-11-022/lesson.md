# Mã định danh duy nhất: 64 bit chia theo thời gian, máy và số thứ tự

**Nhiều máy cùng tạo bản ghi mới cần cho mỗi bản ghi một mã không trùng, mà không phải hỏi nhau mỗi lần.** Một cách làm quen thuộc là ghép ba thứ vào một số 64 bit: thời điểm, máy đang tạo, và số thứ tự trong cùng một thời điểm. Bài này dựng cách đó, thử, và nói chỗ nó yếu.

![Hai khung. Khung một, mã 64 bit chia thành ba phần: 41 bit thời gian tính bằng mili giây, 10 bit số hiệu máy, 12 bit số thứ tự trong cùng một mili giây. Khung hai, thử nghiệm: hai máy sinh 400000 mã đều khác nhau và tăng dần theo máy, một mili giây tối đa 4096 mã mỗi máy, đồng hồ lùi thì máy sinh mã từ chối.](../../diagrams/sd-11-022-main.svg)

## Từ viết tắt

- **ID** (IDentifier) — mã định danh: một giá trị dùng để phân biệt bản ghi này với bản ghi khác.
- **UUID** (Universally Unique IDentifier) — mã định danh duy nhất toàn cầu: mã 128 bit, tạo ra không cần phối hợp giữa các máy; phiên bản 4 chủ yếu là số ngẫu nhiên.
- **NTP** (Network Time Protocol) — giao thức đồng bộ giờ qua mạng: cách thường dùng để giữ đồng hồ các máy gần nhau; bài này nhắc vì đồng hồ lệch hay bị chỉnh lùi.

## Đọc hình

**Điều kiện cần.** Bốn điều thường được đòi: duy nhất trên toàn hệ thống, xấp xỉ theo thứ tự thời gian (mã mới nằm sau mã cũ để chỉ mục cơ sở dữ liệu ghi gọn), là số (nhỏ gọn, so sánh nhanh), và vừa 64 bit (một số nguyên thông thường). Phải sinh nhanh, không có điểm nghẽn.

**Ba phần của mã (kiểu Snowflake của Twitter).** Từ bit cao xuống thấp: 41 bit thời gian tính bằng mili giây kể từ một mốc do bạn chọn (2^41 mili giây xấp xỉ 69,7 năm, nên mốc nên chọn gần ngày bắt đầu dùng); 10 bit số hiệu máy (tối đa 1024 máy sinh mã); 12 bit số thứ tự (tối đa 4096 mã mỗi máy trong một mili giây). Còn một bit dấu để trống, nên mã luôn dương. Hai máy khác số hiệu không bao giờ sinh trùng; cùng một máy thì thời gian khác nhau hoặc số thứ tự khác nhau. Thông lượng tối đa của một máy là 4096 × 1000 = khoảng 4,1 triệu mã mỗi giây.

## Thử: viết bộ sinh mã nhỏ

Ngày 2026-10-19, một chương trình Python nhỏ dựng đúng ba phần trên (một tiến trình, một luồng, đồng hồ thật). Kết quả:

| Phép thử | Kết quả |
|---|---|
| Hai máy (số hiệu 1 và 2), mỗi máy 200000 mã | 400000 mã, đều khác nhau |
| Mã của từng máy theo thứ tự sinh | tăng dần chặt |
| Đồng hồ giả đứng yên, sinh 4096 mã | 4096 mã khác nhau; mã thứ 4097 buộc phải chờ sang mili giây sau |
| Đồng hồ giả bị chỉnh lùi 1 mili giây | bộ sinh từ chối và báo lỗi |
| Mã UUID phiên bản 4 để so | 128 bit, không có thứ tự thời gian |

Dòng thứ tư là điểm yếu quan trọng nhất: nếu bộ sinh cứ dùng đồng hồ thì sau một lần đồng hồ bị chỉnh lùi (thường do đồng bộ giờ), nó có thể sinh lại đúng những mã đã dùng. Bộ sinh trong thử nghiệm chọn từ chối; cách khác là chờ cho tới khi đồng hồ đuổi kịp. Cách chống này chỉ đúng khi bộ sinh còn nhớ mốc thời gian lớn nhất nó đã dùng: mốc đó thường nằm trong bộ nhớ, nên sau một lần khởi động lại lúc đồng hồ vẫn chậm hơn mốc cũ, bộ sinh có thể phát lại đúng thời gian và số thứ tự cũ dưới cùng số hiệu máy. Muốn an toàn phải lưu mốc ra nơi bền, hoặc chờ qua mốc cũ khi khởi động, hoặc không cho số hiệu máy cũ dùng lại.

## Giới hạn cần nhớ

Số hiệu máy phải được cấp không trùng; việc đó cần một nơi phối hợp (tệp cấu hình, dịch vụ đăng ký), và hai máy lỡ nhận cùng số hiệu sẽ sinh trùng mã. "Xấp xỉ theo thời gian" chỉ đúng chừng nào đồng hồ các máy không lệch nhiều: mã của máy có đồng hồ chậm sẽ nằm trước mã của máy nhanh dù sinh sau. Mã còn tiết lộ thời điểm tạo và nhịp tạo, điều có thể không mong muốn với dữ liệu nhạy cảm. Thử nghiệm chỉ mô phỏng đồng hồ lùi trong một lần chạy, không mô phỏng khởi động lại bộ sinh. Thử nghiệm không kiểm tra nhiều luồng chạy cùng một bộ sinh (cần khóa) và không đo thông lượng thật.

Nếu bạn không cần đúng 64 bit hay thứ tự thời gian, một UUID phiên bản 4 không cần phối hợp gì, nhưng tính duy nhất của nó chỉ là xác suất: hai máy sinh độc lập vẫn có thể trùng với xác suất rất nhỏ, nên nếu cần bảo đảm tuyệt đối thì vẫn phải có ràng buộc duy nhất ở nơi lưu và thử lại khi bị từ chối; còn nếu cần thứ tự thời gian với 128 bit thì có các định dạng khác, chẳng hạn UUID phiên bản 7 gắn thời điểm ở phần đầu.

## Nhìn hình trả lời

Một dịch vụ sinh mã cho 1500 máy. Cách chia 10 bit số hiệu máy trong hình còn đủ không, và có hai cách xử lý nào?

<details>
<summary>Xem đáp án</summary>

Không đủ: 10 bit chỉ cho 1024 số hiệu. Một cách là bớt bit ở phần khác để thêm bit cho số hiệu máy (ví dụ giảm số bit thứ tự, đổi lấy ít mã hơn mỗi mili giây), cách khác là chỉ một nhóm máy nhỏ hơn trực tiếp sinh mã, các máy còn lại xin mã từ nhóm đó.
Đây là suy luận của người biên soạn từ cấu tạo ba phần.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn nêu năm yêu cầu cho mã định danh ở mạng xã hội rồi không đi vào chi tiết cách làm. Bài này giữ năm yêu cầu, thêm một cách làm cụ thể (ba phần 41, 10 và 12 bit), một thử nghiệm riêng và các giới hạn của nó. Cấu tạo bit lấy từ hiểu biết chung về Snowflake của Twitter, chưa mở lại trang gốc.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/unique-id-generator.md): các yêu cầu cho mã định danh. Cách làm, thử nghiệm và đáp án là của người biên soạn.
- [Twitter — Snowflake (kho lưu trữ)](https://github.com/twitter-archive/snowflake): cấu tạo 41, 10 và 12 bit. Kiến thức chung, không mở được tệp trong phiên viết.
- [RFC 9562 — Universally Unique IDentifiers](https://www.rfc-editor.org/rfc/rfc9562.html): UUID phiên bản 4 và 7. Kiến thức chung, chưa mở lại trong phiên viết.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.
