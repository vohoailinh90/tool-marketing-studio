# Rủi ro khi triển khai và cách giảm

Triển khai thất bại theo vài cách quen thuộc. Gọi tên đúng rủi ro trước rồi mới chọn cơ chế sẽ hiệu quả hơn là chọn một "chiến lược" rồi hy vọng.

![Năm rủi ro và cách giảm: lỗi chỉ lộ ở tải thật thì mở traffic từng nấc, hai phiên bản gặp nhau thì giữ tương thích hai chiều và đổi dữ liệu theo nhiều bước, không biết bản mới tốt hay xấu thì đặt ngưỡng chấp nhận từ trước, rút lại quá chậm thì tập và đo thời gian rút lại, và thay đổi gói quá lớn thì chia nhỏ.](../../diagrams/sd-13-020-main.svg)

**Đọc hình:** bài không nhằm xếp hạng cơ chế; mỗi rủi ro có thể giảm bằng nhiều cơ chế, và cơ chế nào cũng có giá.

## Nhìn hình thử trả lời

Bản mới thêm một cột bắt buộc vào bảng, trong khi bản cũ vẫn đang chạy. Chuyện gì xảy ra nếu triển khai dần từng nhóm máy?

<details>
<summary>Xem đáp án</summary>

Tùy cách thêm cột. Nếu cột bắt buộc không có giá trị mặc định, bản cũ ghi những dòng thiếu cột đó nên lỗi. Nếu cột có giá trị mặc định hợp lệ thì lệnh ghi cũ vẫn chạy được và cơ sở dữ liệu điền mặc định. Thứ tự lỗi còn phụ thuộc cơ sở dữ liệu: với PostgreSQL, thêm cột `NOT NULL` không có mặc định vào bảng đã có dòng bị từ chối ngay ở lệnh migration, vì các dòng hiện có sẽ nhận null, nên lỗi đến trước cả lúc triển khai; lỗi ở lệnh ghi của bản cũ chỉ xuất hiện khi bảng còn rỗng, hoặc khi ràng buộc được siết sau khi đã điền dữ liệu mà bản cũ vẫn đang ghi. Cách an toàn là thêm cột ở dạng tùy chọn (hoặc có mặc định tương thích) trước, điền dữ liệu cho các dòng cũ, chuyển ứng dụng sang dùng cột đó, rồi mới siết thành bắt buộc ở bước sau (mở rộng rồi thu gọn).

</details>

## Giới hạn cần nhớ

Không cơ chế giảm rủi ro nào thay được kiểm thử trước khi triển khai. Mỗi cơ chế có giá: mở traffic từng nấc cần giám sát tốt, giữ bản trước sẵn sàng cần thêm tài nguyên hoặc công dọn dẹp, và đổi dữ liệu theo nhiều bước kéo dài thời gian hoàn tất. Ví dụ về cột bắt buộc nói theo PostgreSQL; cơ sở dữ liệu khác có thể xử lý lúc thêm cột khác đi.

<details>
<summary>Xem sâu hơn</summary>

- **Mở traffic từng nấc:** canary hay các kiểu tương tự; điều kiện dừng nên định trước bằng số đo, không bằng cảm giác.
- **Tương thích hai chiều:** mẫu "mở rộng rồi thu gọn" (parallel change): thêm cái mới song song, chuyển người dùng, rồi mới bỏ cái cũ.
- **Ngưỡng chấp nhận:** lấy từ mục tiêu mức dịch vụ (Service Level Objective, SLO) để so số đo của bản mới với bản đối chứng.
- **Rút lại:** có nhiều cách, từ chuyển lại traffic về môi trường cũ đến triển khai lại bản trước; cách nào cũng nên được tập trước khi cần.
- **Bản nhỏ:** thay đổi nhỏ dễ tìm nguyên nhân khi lỗi, và là một thói quen được nghiên cứu DORA (DevOps Research and Assessment — chương trình nghiên cứu và đánh giá DevOps) liên hệ với hiệu quả giao phần mềm tốt hơn.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-to-deploy-services.md).
- Martin Fowler: [ParallelChange](https://martinfowler.com/bliki/ParallelChange.html), [CanaryRelease](https://martinfowler.com/bliki/CanaryRelease.html).
- Google SRE Workbook (SRE là Site Reliability Engineering — kỹ thuật độ tin cậy của hệ thống): [canarying releases](https://sre.google/workbook/canarying-releases/). DORA: [working in small batches](https://dora.dev/capabilities/working-in-small-batches/). PostgreSQL: [INSERT](https://www.postgresql.org/docs/current/sql-insert.html), [ALTER TABLE](https://www.postgresql.org/docs/current/ddl-alter.html).
