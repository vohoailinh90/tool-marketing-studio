# Kiến trúc Twitter 2022 so với 2012: đọc từ mã nguồn mở của chính Twitter

**Bài nguồn chỉ có một hình, nên bài này không kể lại hình đó; nó đọc những gì Twitter tự công bố trong mã nguồn mở: các công cụ thời đầu, rồi đường đi của dòng tin Home ở bản mã mở sau này.**
Bạn sẽ thấy hai thứ đổi: cách chia dữ liệu và gọi dịch vụ, và cách chọn tweet cho từng người.

![Ba khung. Khung một, công cụ thời đầu theo README của Twitter: Gizzard, khung dựng kho dữ liệu phân tán; FlockDB, kho đồ thị quan hệ, tháng 4 năm 2010 có hơn 13 tỷ cạnh; Snowflake, bản đầu phát hành năm 2010; Finagle, hệ gọi dịch vụ từ xa cho JVM. Khung hai, năm chặng dựng dòng tin For You: lấy ứng viên, gắn khoảng 6000 đặc trưng, chấm điểm bằng mô hình, lọc, trộn nội dung khác. Khung ba: ba điều nguồn không nói.](../../diagrams/sd-02-030-main.svg)

## Từ viết tắt

- **RPC** (Remote Procedure Call) — gọi thủ tục từ xa: một dịch vụ gọi hàm của dịch vụ khác qua mạng như gọi hàm trong cùng chương trình; Finagle là hệ làm việc này.
- **JVM** (Java Virtual Machine) — máy ảo Java: môi trường chạy chương trình Java và Scala, hai ngôn ngữ mà các công cụ trong bài viết bằng.
- **DB** (DataBase) — cơ sở dữ liệu: kho lưu dữ liệu có tổ chức; có trong tên FlockDB.
- **ID** (IDentifier) — mã định danh: số hoặc chuỗi phân biệt một tweet hay một người dùng với mọi cái khác.
- **ML** (Machine Learning) — học máy: dùng mô hình học từ dữ liệu để chấm điểm; ở đây là mô hình chấm điểm tweet cho dòng tin.

## Đọc hình

**Vì sao không đọc từ hình nguồn.** Tệp nguồn của bài chỉ gồm một hình và câu hỏi "What's changed over the past 10 years?!" (thay đổi gì trong mười năm qua), không có chữ giải thích. Người biên soạn không mở được hình đó, nên bài không nói hình vẽ gì. Phần dưới lấy từ README của kho mã nguồn mở của Twitter, ghim theo commit.

**Khung một: công cụ thời đầu.**
- **Gizzard.** README tả đây là khung viết bằng Scala để dựng kho dữ liệu phân tán chịu lỗi. Twitter đã làm nhiều kho dữ liệu riêng, thấy chúng giống nhau nhiều chỗ nên tách phần chung ra thành khung này. Dự án đã không còn được bảo trì.
- **FlockDB.** Kho đồ thị phân tán, lưu danh sách kề: ai theo dõi ai, ai chặn ai. Mỗi cạnh được ghi theo cả hai chiều để trả lời được "ai theo dõi A" lẫn "A theo dõi ai". README nêu: tính đến tháng 4 năm 2010, cụm FlockDB của Twitter giữ hơn 13 tỷ cạnh, đỉnh 20 nghìn lượt ghi và 100 nghìn lượt đọc mỗi giây. Nó cố ý không làm truy vấn đi nhiều bước.
- **Snowflake.** README nói bản đầu phát hành năm 2010, dựa trên Apache Thrift và có trước Finagle; bản đầu đã được ngưng, Twitter viết lại bản dùng nội bộ.
- **Finagle.** Hệ RPC mở rộng được cho JVM, để dựng máy chủ chịu nhiều kết nối đồng thời. README ghi nó vẫn chạy thật ở Twitter và vẫn được phát triển.

**Khung hai: dòng tin Home ở bản mã mở.** Home Mixer là dịch vụ chính dựng và phát dòng tin Home, viết trên khung Product Mixer bằng Scala. Với tab For You, README nêu các chặng:
1. Lấy ứng viên từ nhiều nguồn: chỉ mục tìm kiếm Earlybird, đồ thị người dùng và tweet, dịch vụ gợi ý theo dõi.
2. Gắn khoảng 6000 đặc trưng cần cho việc xếp hạng.
3. Chấm điểm và xếp hạng bằng mô hình ML.
4. Lọc và áp quy tắc: đa dạng tác giả, cân bằng trong và ngoài mạng theo dõi, bỏ tweet đã xem, bỏ nội dung bị chặn hoặc tắt tiếng.
5. Trộn thêm nội dung không phải tweet, như quảng cáo hay gợi ý theo dõi.

Tab Following thì đơn giản hơn: tweet của người bạn theo dõi, theo thứ tự thời gian mới nhất trước. Mô hình chấm điểm được phục vụ bằng Navi, viết bằng Rust. README của kho nói chỉ mục Earlybird là nguồn của khoảng một nửa số tweet ở tab For You; Earlybird chia chỉ mục thành ba cụm (thời gian thực khoảng 7 ngày gần nhất, tweet được bảo vệ, và kho lưu trữ), mỗi cụm chia nhiều phần và có bản sao.

## Giới hạn cần nhớ

Bài này không chứng minh cái gì "có năm 2012" hay "có năm 2022". Chỉ hai mốc năm nằm trong nguồn: FlockDB (số liệu tháng 4 năm 2010) và bản đầu của Snowflake (2010). README của các kho khác không ghi năm; commit được ghim vào ngày 2025-09-03 cho kho thuật toán, nên đó là bản mã mở tại thời điểm ghim, không phải ảnh chụp năm 2022. Bài cũng không có số liệu quy mô của chính Twitter ngoài FlockDB, không có sơ đồ đầy đủ, và không đối chiếu được bài của blog kỹ thuật Twitter (máy của người biên soạn không mở được các trang đó). Hình nguồn có thể nói thêm những điều không có ở đây.

## Nhìn hình thử trả lời

Vì sao dòng tin For You lấy ứng viên từ nhiều nguồn rồi mới xếp hạng, thay vì chỉ lấy tweet của những người bạn theo dõi?

<details>
<summary>Xem đáp án</summary>

README của Home Mixer mô tả For You là tweet hay nhất từ người bạn theo dõi cộng với nội dung gợi ý từ ngoài mạng theo dõi, nên phải gom từ nhiều nguồn: tìm kiếm cho tweet trong mạng, đồ thị tương tác và dịch vụ gợi ý cho tweet ngoài mạng. Chặng sau đó gắn đặc trưng, chấm điểm và lọc để chọn ra phần đáng hiển thị. Tab Following chỉ cần một nguồn, tweet của người bạn theo dõi theo thời gian, nên đơn giản hơn.

</details>

<details>
<summary>Xem sâu hơn: vì sao FlockDB lưu mỗi cạnh hai lần</summary>

- Một cạnh "A theo dõi B" được ghi một hàng xuôi (A tới B) và một hàng ngược (B từ A), theo README.
- Nhờ vậy hỏi "ai theo dõi B" cũng đọc thẳng được một dãy liền nhau, thay vì quét hết mọi cạnh. Đây là cách giải thích của người biên soạn, README chỉ nói cả hai hướng đều được lưu và truy vấn được.
- Cái giá là ghi gấp đôi dữ liệu; đây cũng là suy luận của người biên soạn, không phải câu của README.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/twitter-architecture-2022-vs-2012.md): tựa và câu hỏi duy nhất; nội dung chính là một hình.
- [Twitter — Home Mixer](https://github.com/twitter/the-algorithm/blob/c54bec0d4e029fe34926ef3258a86ccacc0d0182/home-mixer/README.md): các chặng dựng dòng tin Home, khoảng 6000 đặc trưng, tab For You và Following.
- [Twitter — thuật toán gợi ý, README gốc](https://github.com/twitter/the-algorithm/blob/c54bec0d4e029fe34926ef3258a86ccacc0d0182/README.md): thành phần của For You, Earlybird là nguồn khoảng một nửa số tweet.
- [Twitter — Earlybird](https://github.com/twitter/the-algorithm/blob/c54bec0d4e029fe34926ef3258a86ccacc0d0182/src/java/com/twitter/search/README.md): ba cụm chỉ mục, chia phần và bản sao.
- [Twitter — Navi](https://github.com/twitter/the-algorithm/blob/c54bec0d4e029fe34926ef3258a86ccacc0d0182/navi/README.md): phục vụ mô hình bằng Rust.
- [Twitter — FlockDB](https://github.com/twitter/flockdb/blob/d0e72e889ec669e3eb79d2e66219514182a6dd5b/README.md): đồ thị quan hệ, số liệu tháng 4 năm 2010.
- [Twitter — Gizzard](https://github.com/twitter/gizzard/blob/9b84325490185f1fa29cb4c9116b39eea374f345/README.markdown): khung dựng kho dữ liệu phân tán.
- [Twitter — Snowflake](https://github.com/twitter/snowflake/blob/ec40836e3f47af92cf0c83cbb4187c529d7e7fa5/README.md): bản đầu năm 2010, có trước Finagle.
- [Twitter — Finagle](https://github.com/twitter/finagle/blob/ca472deb355c7d3b8d7eb077223991e8c8f4ad8b/README.md): hệ RPC cho JVM.

Đã đọc nguồn ngày 2026-10-20. Các bài trên blog kỹ thuật của Twitter không mở được từ môi trường biên soạn nên chưa đối chiếu.
Bài viết và hình được thiết kế độc lập.
