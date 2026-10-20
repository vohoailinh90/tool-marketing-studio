# Sáu loại cơ sở dữ liệu, sáu câu tóm tắt: câu nào giữ được, câu nào cần sửa

**Tóm mỗi loại cơ sở dữ liệu trong một câu thì dễ nhớ, nhưng một câu sai sẽ đưa bạn tới sai công cụ.** Bài nguồn tóm sáu loại trong sáu câu. Bài này đặt từng câu cạnh hướng dẫn "Understand data models" của Azure Architecture Center, và thử câu về kho trong bộ nhớ trên Redis.

![Ba khung. Khung một, ba câu giữ được: cơ sở dữ liệu quan hệ làm được gần như mọi việc nhưng mở rộng ngang thường phải chia shard; kho trong bộ nhớ nhanh và có trần bộ nhớ; kho chuỗi thời gian ghi nối tiếp theo thời gian, coi chừng số series. Khung hai, ba câu cần sửa: đồ thị mạnh ở quan hệ nhiều tầng, nút và cạnh vẫn có thuộc tính; kho tài liệu chứa tài liệu JSON vẫn được sửa, dữ liệu lớn không đổi là việc của kho đối tượng; kho cột rộng mạnh ở ghi nhiều và dữ liệu thưa, phân tích lớn là loại khác. Khung ba, Redis trần 8 MiB, 20.000 giá trị 1.000 byte: noeviction ghi được 6.732 khóa rồi báo lỗi; allkeys-lru ghi đủ nhưng xóa 13.291 khóa cũ; mặc định không đặt trần; RDB và AOF lưu xuống đĩa.](../../diagrams/sd-04-021-main.svg)

## Từ viết tắt

- **JSON** (JavaScript Object Notation) — định dạng dữ liệu dạng chữ gồm các cặp tên và giá trị lồng nhau; kho tài liệu thường lưu mỗi tài liệu theo định dạng này.
- **MB** (MegaByte) — megabyte: một triệu byte; dùng để nói cỡ một tệp ảnh hay video.
- **MiB** (Mebibyte) — mebibyte: 1.048.576 byte; trần bộ nhớ trong thử nghiệm là 8 MiB.
- **RDB** (Redis DataBase) — cách Redis lưu xuống đĩa bằng ảnh chụp toàn bộ dữ liệu theo chu kỳ.
- **AOF** (Append Only File) — cách Redis lưu xuống đĩa bằng một tệp ghi nối tiếp mọi lệnh ghi, phát lại khi khởi động.

## Đọc hình

**Khung 1 · Ba câu giữ được.**

- **Quan hệ: "gần như việc gì cũng giải được".** Hướng dẫn Azure ghi điểm mạnh là giao dịch nhất quán trên nhiều dòng, phép nối phức tạp và ràng buộc chặt; khi cần nhiều thực thể cùng đổi trong một giao dịch, nó chọn loại này. Điều cần thêm vào câu tóm tắt: muốn mở rộng ngang thường phải chia shard hoặc chia partition.
- **Trong bộ nhớ: "nhanh, cỡ dữ liệu có hạn".** Đúng, và thử nghiệm ở khung 3 cho thấy "có hạn" là một con số bạn đặt, cùng một quyết định bạn phải chọn khi chạm tới nó.
- **Chuỗi thời gian: "lưu và quản lý dữ liệu có dấu thời gian".** Đúng nhưng mỏng. Hướng dẫn Azure nói rõ hơn: ghi nối tiếp với tốc độ cao, truy vấn theo khung thời gian, và phải quản lý số tổ hợp nhãn (xem bài về cơ sở dữ liệu chuỗi thời gian).

**Khung 2 · Ba câu cần sửa.**

- **Đồ thị: "quan hệ phức tạp giữa các đối tượng phi cấu trúc".** Phần "quan hệ" đúng: hướng dẫn Azure nói đồ thị mạnh ở việc đi theo quan hệ với độ sâu thay đổi. Phần "phi cấu trúc" thì không: dữ liệu là nút và cạnh, và cả hai đều có thuộc tính như cột của bảng.
- **Tài liệu: "tốt cho dữ liệu lớn, không đổi".** Đây là chỗ lệch nhất. Hướng dẫn Azure xếp kho tài liệu vào loại dữ liệu cỡ nhỏ đến vừa, hợp với ứng dụng làm việc với JSON có hình dạng thay đổi dần, như danh mục sản phẩm hay hồ sơ người dùng. Tài liệu vẫn được sửa sau khi ghi: hướng dẫn còn cảnh báo tài liệu quá lớn thì các lần sửa từng phần tranh nhau. "Dữ liệu lớn, ít khi đổi" là mô tả của kho đối tượng.
- **Cột rộng: "dùng cho dữ liệu lớn, phân tích, báo cáo".** Đúng một phần. Hướng dẫn Azure mô tả kho cột rộng là nơi ghi nhiều, dữ liệu thưa, như số liệu từ thiết bị, và phải thiết kế khóa dòng từ đầu. Còn quét lượng lớn dữ liệu lịch sử để tổng hợp thì nó xếp vào một loại riêng: kho phân tích.

**Khung 3 · Thử: Redis chạm trần 8 MiB.** Đặt `maxmemory` là 8 MiB rồi ghi 20.000 giá trị, mỗi giá trị 1.000 byte, với hai chính sách:

| Chính sách khi chạm trần | Lệnh ghi thành công | Khóa còn lại | Khóa đầu tiên còn không | Khóa bị xóa |
|---|---|---|---|---|
| `noeviction` | 6.732, lệnh thứ 6.733 bị từ chối | 6.732 | còn | 0 |
| `allkeys-lru` | đủ 20.000 | 6.709 | mất | 13.291 |

Với `noeviction`, Redis trả lỗi `OOM command not allowed when used memory > 'maxmemory'` và giữ nguyên dữ liệu cũ. Với `allkeys-lru`, mọi lệnh ghi đều thành công nhưng Redis lặng lẽ xóa các khóa lâu không dùng. Cùng một trần, một bên mất khả năng ghi, một bên mất dữ liệu cũ: chọn bên nào tùy bạn dùng nó làm bộ nhớ đệm hay làm nơi lưu chính.

Hai điều nữa từ tài liệu Redis: trên máy 64 bit, mặc định `maxmemory` bằng 0, tức không giới hạn dữ liệu; và "trong bộ nhớ" không có nghĩa là tắt máy mất hết, vì Redis có thể lưu xuống đĩa bằng RDB, AOF hoặc cả hai.

## Giới hạn cần nhớ

- Hướng dẫn Azure nhắc rằng một dịch vụ có thể cung cấp nhiều mô hình cùng lúc; chọn mô hình hợp nhất thay vì ghép nhiều mô hình làm khó vận hành. Tên loại là điểm khởi đầu, không phải câu trả lời.
- Thử nghiệm chỉ kiểm câu về kho trong bộ nhớ, trên Redis 7.0.15. Các câu còn lại được đối chiếu với tài liệu, không đo.

## Nhìn hình trả lời

Một nhóm định lưu ảnh và video người dùng tải lên (vài trăm MB mỗi tệp, tải lên xong không sửa) vào một kho tài liệu, vì đọc được câu "kho tài liệu tốt cho dữ liệu lớn, không đổi". Nhìn khung 2: nên lưu ở đâu, và kho tài liệu hợp với phần nào của bài toán?

<details>
<summary>Xem đáp án</summary>

Tệp lớn, ghi một lần, không sửa là việc của kho đối tượng. Kho tài liệu hợp với phần mô tả của mỗi tệp: tên, người tải, thẻ, trạng thái duyệt; đó là dữ liệu nhỏ, có cấu trúc thay đổi dần và được sửa khi, chẳng hạn, trạng thái duyệt đổi.
Đây là cách chia của người biên soạn theo bảng so sánh trong hướng dẫn Azure.

</details>

<details>
<summary>Xem sâu hơn: điều chỉnh so với bài nguồn</summary>

Bài nguồn liệt kê sáu loại, mỗi loại một câu. Bài này giữ ba câu (kèm điều kiện), sửa ba câu: đồ thị không làm việc với đối tượng "phi cấu trúc"; "dữ liệu lớn, không đổi" là mô tả của kho đối tượng chứ không phải kho tài liệu; kho cột rộng khác kho phân tích.
Bài nguồn cũng nêu S3 và Ceph trong danh sách cơ sở dữ liệu; theo hướng dẫn Azure, đó là kho đối tượng, một mô hình lưu trữ riêng.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-you-decide-which-type-of-database-to-use.md): sáu loại cơ sở dữ liệu, mỗi loại một câu.
- [Azure Architecture Center — Understand data models, tại commit cố định](https://github.com/MicrosoftDocs/architecture-center/blob/8e2c239344ee753a88856800b4210a3e27ac1036/docs/data-guide/technology-choices/understand-data-store-models.md): định nghĩa, điểm mạnh, điều cần cân nhắc của từng mô hình và hai bảng so sánh. Đọc từ bản clone của kho.
- Tài liệu Redis, tại commit cố định: [giới hạn bộ nhớ và chính sách xóa khóa](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/develop/reference/eviction/index.md), [lưu xuống đĩa](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/operate/oss_and_stack/management/persistence.md).

Đã đọc nguồn và chạy thử nghiệm ngày 2026-10-18 với Redis 7.0.15 và redis-py 8.1.0 trên một máy.
Bài viết và hình được thiết kế độc lập.
