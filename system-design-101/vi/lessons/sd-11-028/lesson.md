# Năm cách sinh mã định danh duy nhất, và mỗi cách trả giá ở đâu

**Một hệ thống nhiều máy cần mỗi bản ghi có một mã không trùng ai, mà không phải hỏi một máy trung tâm cho mỗi mã.** Có năm cách quen thuộc: UUID, Snowflake, cột tự tăng của cơ sở dữ liệu, đoạn mã lấy theo lô, và bộ đếm trong Redis. Bài này đặt chúng cạnh nhau theo bốn câu hỏi, rồi thử bằng số một câu hỏi tưởng nhỏ nhưng tốn thật: mã mới rơi vào đâu trong chỉ mục.

![Hai khung. Khung một, năm cách sinh mã định danh duy nhất, mỗi cách một thẻ: UUID sinh ngẫu nhiên ở từng máy, Snowflake ghép thời gian, máy và số thứ tự, cột tự tăng của cơ sở dữ liệu, đoạn mã lấy theo lô từ cơ sở dữ liệu, bộ đếm trong Redis. Khung hai, thử nghiệm: chèn 20000 mã vào một chỉ mục có thứ tự; mã UUID ngẫu nhiên rơi trung bình trước khoảng 5000 mã đã có, mã tự tăng luôn rơi cuối, mã ghép thời gian gần cuối.](../../diagrams/sd-11-028-main.svg)

## Từ viết tắt

- **UUID** (Universally Unique IDentifier) — mã định danh duy nhất toàn cầu: mã 128 bit, dạng phổ biến nhất sinh ngẫu nhiên và không cần hỏi máy nào khác.
- **ID** (IDentifier) — mã định danh: dãy ký tự hay số dùng để phân biệt một bản ghi với mọi bản ghi khác.

## Đọc hình

**UUID.** Mã 128 bit, mỗi máy tự sinh, không gọi dịch vụ nào. Đổi lại, nó không tăng dần theo thứ tự sinh, nên khi dùng làm khóa của một chỉ mục có thứ tự thì mã mới rơi vào chỗ ngẫu nhiên (xem thử nghiệm). Nó cũng không bảo đảm tuyệt đối không trùng, chỉ làm cho việc trùng cực kỳ khó xảy ra.

**Snowflake.** Mã 64 bit ghép thời gian, mã máy và số thứ tự, bit đầu để trống cho mã luôn dương. Mỗi máy sinh tại chỗ nên nhanh và mở rộng được; mã gần tăng dần theo thời gian. Cách ghép chi tiết có nhiều biến thể, ví dụ thêm mã trung tâm dữ liệu vào phần mã máy để duy nhất trên toàn cầu.

**Cột tự tăng của cơ sở dữ liệu.** Hầu hết cơ sở dữ liệu có sẵn cột tự đếm, và chính cơ sở dữ liệu xử lý chuyện nhiều người xin cùng lúc, nên mã duy nhất trong một bảng. Giá phải trả: mỗi mã cần một lần gọi qua mạng, và con số lộ thông tin kinh doanh. Nếu dùng làm mã người dùng, đối thủ nhìn mã mới nhất là đoán được số người đã đăng ký.

**Đoạn mã lấy theo lô.** Mỗi máy chủ cấp mã xin cơ sở dữ liệu cả một đoạn (ví dụ 1000 mã), rồi phát dần từ bộ nhớ. Cơ sở dữ liệu ít bị gọi hơn nhiều. Phần dưới sẽ đếm.

**Redis.** Dùng một khóa đếm trong Redis; vì Redis giữ dữ liệu trong bộ nhớ nên nhanh hơn cơ sở dữ liệu. Câu hỏi còn lại là điều gì xảy ra với bộ đếm khi Redis khởi động lại, vì bộ nhớ có thể mất.

## Bốn câu hỏi để chọn

| Cách | Cần gọi qua mạng mỗi mã? | Mã tăng theo thứ tự sinh? | Lộ con số? | Chỗ yếu |
|---|---|---|---|---|
| UUID | Không | Không | Không | Chỉ mục kém, dài 128 bit |
| Snowflake | Không | Gần như | Lộ thời gian sinh | Phụ thuộc đồng hồ, cần cấp mã máy |
| Cột tự tăng | Có | Có | Có | Một điểm nghẽn, lộ số lượng |
| Đoạn mã | Một lần mỗi lô | Trong từng máy | Phần nào | Máy sập thì mất phần lô chưa phát |
| Redis | Có | Có | Có | Bộ đếm phải sống sót qua khởi động lại |

Bảng này là phân tích của người biên soạn từ mô tả của từng cách; mỗi ô là một lựa chọn thiết kế chứ không phải con số đo.

## Thử: mã mới rơi vào đâu

Ngày 2026-10-19, một chương trình Python nhỏ, không có cơ sở dữ liệu thật. Chèn 20000 mã vào một danh sách có thứ tự, thay cho chỉ mục, và đếm có bao nhiêu mã đã có lớn hơn mã mới (số mã mà chỗ chèn phải "dịch" qua).

| Kiểu mã | Trung bình số mã đã có đứng sau mã mới | Số lần chèn không rơi cuối |
|---|---|---|
| UUID ngẫu nhiên 128 bit | 5005 | 19987 trên 20000 |
| Cột tự tăng | 0 | 0 |
| Ghép thời gian, hai máy, mỗi máy một mã mỗi mili giây, đến theo thứ tự ngẫu nhiên | 0,25 | 4998 |

Kích thước thật của chỉ mục và cơ sở dữ liệu nằm ngoài thử nghiệm; con số chỉ cho thấy xu hướng: mã ngẫu nhiên rải khắp chỉ mục, còn mã theo thời gian dồn về cuối.

Hai phép tính nữa trong cùng chương trình. Với UUID ngẫu nhiên, xác suất trùng của một tỷ mã (công thức ngày sinh nhật) khoảng 9,4 × 10⁻²⁰, tức cỡ một phần mười tỷ tỷ, đủ nhỏ để bỏ qua nhưng không bằng không. Với đoạn mã lấy theo lô: 100000 mã cần 100000 lần gọi cơ sở dữ liệu nếu mỗi mã một lần, 1000 lần nếu lô 100, và 100 lần nếu lô 1000. Nhưng nếu máy cấp mã sập sau khi phát 2500 mã của lô 1000, lần khởi động lại xin lô mới và bỏ lại 500 mã chưa phát: mã vẫn duy nhất, chỉ có khoảng trống.

## Giới hạn cần nhớ

Thử nghiệm đếm số mã đứng sau, không đo thời gian chèn thật của một cơ sở dữ liệu. Phép tính trùng giả định UUID ngẫu nhiên đều (bản 4, 122 bit ngẫu nhiên), không áp dụng cho các bản UUID khác. Bài không đo Redis; điều nó nói về Redis và về độ bền của bộ đếm là suy luận từ cách Redis giữ dữ liệu trong bộ nhớ.

## Nhìn hình trả lời

Một đội chọn cột tự tăng làm mã đơn hàng công khai trong đường dẫn. Một khách hàng nhận mã 10450 hôm nay và 10520 tuần sau. Khách hàng đó biết được gì?

<details>
<summary>Xem đáp án</summary>

Khoảng 70 đơn hàng đã được đặt trong tuần đó, tức nhịp kinh doanh của cửa hàng. Đây là ví dụ cùng loại với ví dụ người dùng của bài nguồn: mã tuần tự lộ số lượng. Cách tránh: dùng mã không tuần tự cho phần công khai, hoặc giữ mã tự tăng nội bộ.
Đây là suy luận của người biên soạn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có năm đoạn ngắn, mỗi đoạn một cách. Bài này giữ năm cách, thêm bảng bốn câu hỏi, thử nghiệm vị trí chèn, phép tính trùng và phép đếm đoạn mã. Bài về cấu trúc bit của Snowflake là một bài khác của bộ này.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/explaining-5-unique-id-generators-in-distributed-systems.md): năm cách và ưu nhược điểm. Bảng, thử nghiệm và đáp án là của người biên soạn.
- [RFC 4122 — A Universally Unique IDentifier (UUID) URN Namespace](https://www.rfc-editor.org/rfc/rfc4122): định nghĩa UUID. Chưa mở lại trong phiên viết (không mở được trang từ môi trường); phần về UUID bản 4 là kiến thức chung của người biên soạn.
- [Redis — lệnh INCR](https://redis.io/docs/latest/commands/incr/): bộ đếm nguyên tử. Chưa mở lại trong phiên viết; kiến thức chung của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.
