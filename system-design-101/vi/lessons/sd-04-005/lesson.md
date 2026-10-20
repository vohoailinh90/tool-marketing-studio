# Avro: đổi lược đồ mà dữ liệu cũ vẫn đọc được

**Dữ liệu sống lâu hơn chương trình đã ghi ra nó: bảng thêm cột, bỏ cột, đổi kiểu, còn tệp cũ vẫn nằm đó.**
Avro giải chuyện này bằng hai lược đồ: lược đồ của người ghi đi kèm dữ liệu, lược đồ của người đọc nằm trong chương trình mới, và một bộ luật cố định nói khi nào hai lược đồ ghép được với nhau.

![Ba khung. Khung một là ba bước: ghi hai khách hàng vào một tệp container của Avro, phần đầu tệp chứa lược đồ v1 gồm id, name, phone; ứng dụng mới đọc bằng lược đồ v2 khai id kiểu long, bỏ phone và thêm email có giá trị mặc định; Avro so hai lược đồ, ghép trường theo tên, bỏ qua phone và điền email bằng giá trị mặc định. Khung hai, những thay đổi vẫn đọc được: thêm trường có giá trị mặc định, bỏ một trường, đổi int sang long, đổi thứ tự trường. Khung ba, những thay đổi báo lỗi: thêm trường không có giá trị mặc định, đổi int sang string.](../../diagrams/sd-04-005-main.svg)

## Từ viết tắt

- **JSON** (JavaScript Object Notation) — định dạng văn bản ghi dữ liệu thành cặp tên và giá trị; lược đồ Avro được viết bằng JSON.
- **gRPC** (gRPC Remote Procedure Calls) — một khung gọi hàm từ xa giữa các dịch vụ; bài nguồn đem nó ra so với Avro.
- **ASCII** (American Standard Code for Information Interchange) — bảng mã chữ cái và ký hiệu cơ bản cho máy tính; bốn byte đầu của tệp Avro là ba chữ ASCII `Obj` và số 1.

## Đọc hình

**Khung 1 · Một tệp, hai lược đồ.** Theo đặc tả Avro, dữ liệu mã hóa nhị phân không mang tên trường hay kiểu, nên không có lược đồ thì không đọc được.
Vì thế tệp container (object container file) của Avro luôn ghi lược đồ của người ghi vào phần đầu tệp, ở mục `avro.schema` bằng JSON; mọi bản ghi trong tệp đều theo lược đồ đó.
Chương trình mới đưa thêm lược đồ của mình, và Avro "giải" sự khác nhau theo luật trong mục Schema Resolution của đặc tả.

**Khung 2 và 3 · Luật ghép.** Trường được ghép theo **tên**, không theo vị trí. Trường người ghi có mà người đọc không có thì bị bỏ qua.
Trường người đọc có mà người ghi không có thì lấy giá trị mặc định; không có mặc định thì báo lỗi. Kiểu chỉ được đổi theo hướng nâng mà đặc tả cho phép, ví dụ int lên long, float hay double.

## Thử nghiệm: một tệp cũ, bốn lược đồ đọc

Ghi hai khách hàng bằng lược đồ v1 (`id` kiểu int, `name`, `phone`) vào một tệp container, bằng thư viện `avro` 1.12.2 của dự án Apache Avro cho Python. Tệp dài 244 byte và bắt đầu bằng `Obj` cùng số 1.

| Lược đồ đọc | Kết quả |
|---|---|
| Không đưa, dùng lược đồ trong tệp | đọc đủ `id`, `name`, `phone` |
| v2: đảo thứ tự, `id` thành long, bỏ `phone`, thêm `email` mặc định `""` | đọc được; `phone` biến mất, `email` rỗng |
| v3: thêm `email` không có mặc định | lỗi `SchemaResolutionException: No default value for field email` |
| v4: `id` thành string | lỗi `SchemaResolutionException: Schemas do not match` |

## Giới hạn cần nhớ

Luật chỉ bảo đảm *đọc được*, không bảo đảm *đúng nghĩa*. Đổi tên trường mà không khai alias thì Avro coi đó là bỏ trường cũ và thêm trường mới, và dữ liệu cũ của trường đó lặng lẽ thành giá trị mặc định.
Giá trị mặc định cũng phải có nghĩa với nghiệp vụ: `email` rỗng có thể làm hỏng một bước gửi thư phía sau. Cần kiểm thử chuyển đổi trên dữ liệu thật trước khi đổi lược đồ.

## Nhìn hình trả lời

Đội dữ liệu muốn thêm trường `country` vào lược đồ khách hàng và đọc lại các tệp Avro của năm ngoái bằng chương trình mới. Cần làm gì để không bị lỗi, và nên chọn giá trị mặc định thế nào?

<details>
<summary>Xem đáp án</summary>

Khai `country` kèm một giá trị mặc định trong lược đồ đọc; tệp cũ không có trường này nên mọi bản ghi cũ nhận giá trị mặc định, như `email` ở lược đồ v2. Thiếu mặc định thì đọc báo lỗi như lược đồ v3.
Giá trị mặc định nên là thứ nói rõ "không biết", ví dụ khai `country` là union của null và string với mặc định null, thay vì đoán một quốc gia cụ thể làm sai dữ liệu cũ.

</details>

<details>
<summary>Xem sâu hơn: điều chỉnh so với bài nguồn</summary>

Bài nguồn nói Avro "tự động sinh lược đồ dựa trên các cột" khi xuất dữ liệu. Đặc tả Avro không nói vậy: việc dựng lược đồ từ một bảng là của công cụ xuất dữ liệu, còn Avro quy định lược đồ phải đi kèm tệp và cách hai lược đồ được ghép khi đọc.
Bài nguồn còn so Avro với gRPC và Thrift; bài này không so vì chưa đọc đặc tả của hai hệ đó.

Khai union cho trường có thể vắng (như `["null", "string"]`) cũng theo đặc tả. Đặc tả bản 1.11.1 đòi giá trị mặc định của union thuộc nhánh *đầu tiên*, nên null thường đứng trước; bản 1.12.0 nới thành nhánh khớp đầu tiên. Đặt null trước thì đúng với cả hai bản.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/smooth-data-migration-with-avro.md): lược đồ nằm cùng dữ liệu trong tệp container, giúp chuyển dữ liệu cũ và mới sang kho khác.
- [Apache Avro — Specification, tại commit cố định](https://github.com/apache/avro/blob/3a207fa6e87c535b95eafca4cf5a6ef524d77df2/doc/content/en/docs/++version++/Specification/_index.md): dữ liệu nhị phân không mang tên trường, tệp container và mục `avro.schema`, luật Schema Resolution, nâng kiểu, alias, giá trị mặc định của union (so với bản 1.11.1 và 1.12.0 lưu trong cùng kho). Đọc từ bản clone của kho.

Đã đọc nguồn và chạy thử nghiệm ngày 2026-10-18 bằng thư viện `avro` 1.12.2 cho Python.
Bài viết và hình được thiết kế độc lập.
