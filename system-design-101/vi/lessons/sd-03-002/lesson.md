# Các thuật ngữ dữ liệu cốt lõi

**Sáu thuật ngữ này hay bị trộn lẫn vì chúng không cùng loại.** Chúng trả lời bốn câu hỏi khác nhau:
dữ liệu nằm ở đâu, được lưu bằng lớp nào, đi bằng đường nào và ai chịu trách nhiệm.

![Bốn nhóm câu hỏi xếp dọc. Chứa ở đâu: data lake giữ dữ liệu thô nhiều dạng, data warehouse giữ dữ liệu đã tích hợp để phân tích, data mart là phần riêng cho một nhóm. Chứa bằng gì: Delta Lake là lớp lưu trữ thêm giao dịch ACID. Di chuyển thế nào: data pipeline. Ai chịu trách nhiệm: data mesh, một cách tổ chức chứ không phải sản phẩm để cài.](../../diagrams/sd-03-002-main.svg)

## Đọc hình

**1 · Chứa ở đâu?**
**Data lake** giữ dữ liệu ở dạng gốc, có cấu trúc lẫn không có, để dùng khi cần.
**Data warehouse** giữ dữ liệu đã tích hợp từ nhiều nguồn, phục vụ báo cáo và phân tích lịch sử.
**Data mart** thường là phần của kho dành riêng cho một nhóm, như tài chính hay marketing.

**2 · Chứa bằng gì?** **Delta Lake** là lớp lưu trữ mã nguồn mở đặt trên kho lưu trữ tệp.
Nó thêm giao dịch ACID cho dữ liệu trong lake, để có thể dựng kiến trúc lakehouse.

**3 · Di chuyển thế nào?** **Data pipeline** là chuỗi bước lấy dữ liệu từ nguồn, biến đổi rồi chuyển tới nơi dùng.
Bài về đường ống dữ liệu trong cùng nhóm đi sâu hơn vào các giai đoạn của nó.

**4 · Ai chịu trách nhiệm?** **Data mesh** không phải công cụ. Đó là cách tổ chức: mỗi miền nghiệp vụ
sở hữu dữ liệu của mình và cung cấp nó như một sản phẩm, trên nền tảng dùng chung với quy tắc quản trị chung.

## Giới hạn cần nhớ

Ranh giới giữa các từ không cứng. Một hệ thống có thể dùng cả lake lẫn warehouse, và một sản phẩm cụ thể
có thể làm nhiều việc. Khi gặp một thuật ngữ, hãy hỏi nó đang nói về nơi chứa, lớp lưu, đường đi
hay cách tổ chức. Giao dịch ACID của Delta Lake cũng dựa vào những đảm bảo mà hệ lưu trữ bên dưới cung cấp.

## Nhìn hình trả lời

Một công ty muốn mỗi phòng ban tự chịu trách nhiệm về dữ liệu của mình. Thuật ngữ nào mô tả cách làm đó,
và đó có phải một sản phẩm để mua không?

<details>
<summary>Xem đáp án</summary>

Data mesh. Không: nó là cách tổ chức và trách nhiệm, không phải một công cụ cài đặt được.

</details>

<details>
<summary>Xem sâu hơn: lake chỉ chứa dữ liệu phi cấu trúc?</summary>

Không hẳn. Mô tả của Google Cloud nói lake chứa dữ liệu có cấu trúc, bán cấu trúc và phi cấu trúc ở dạng gốc.
Phần “phi cấu trúc” là điểm hay được nhấn mạnh, nhưng không phải giới hạn của lake.

Data mesh thường được tóm tắt bằng bốn nguyên tắc: miền sở hữu dữ liệu, dữ liệu như một sản phẩm,
nền tảng tự phục vụ và quản trị liên hợp. Đây là cách nhìn của người đề xuất khái niệm, không phải tiêu chuẩn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/key-data-terms.md): danh sách sáu thuật ngữ.
- [Google Cloud — Data lake là gì](https://cloud.google.com/learn/what-is-a-data-lake): kho tập trung cho dữ liệu có cấu trúc, bán cấu trúc và phi cấu trúc ở dạng gốc.
- [Google Cloud — Data warehouse là gì](https://cloud.google.com/learn/what-is-a-data-warehouse): hệ thống doanh nghiệp để phân tích và báo cáo dữ liệu từ nhiều nguồn.
- [Delta Lake — README](https://github.com/delta-io/delta/blob/72b563515251e26a51571d80d62661a3af3b2835/README.md): lớp lưu trữ mã nguồn mở cho lakehouse; ACID dựa vào hệ lưu trữ bên dưới.
- [Dehghani — Data Mesh Principles and Logical Architecture](https://martinfowler.com/articles/data-mesh-principles.html): bốn nguyên tắc. Trang này không mở được trong môi trường biên soạn; nội dung đối chiếu qua trích đoạn tìm kiếm.

Đã đọc nguồn ngày 2026-10-13. Bài viết và hình được thiết kế độc lập. Không giữ mô tả “data lake là dữ liệu
phi cấu trúc” của bài nguồn vì tài liệu của Google Cloud mô tả rộng hơn.
