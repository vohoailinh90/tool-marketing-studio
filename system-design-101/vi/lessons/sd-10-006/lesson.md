# Chạy C, C++ và Rust trong trình duyệt bằng WebAssembly

**WebAssembly cho phép mã viết bằng C, C++ hay Rust chạy ngay trong trình duyệt với hiệu năng gần mã gốc, thay vì chỉ có JavaScript.**
Bài nguồn đặt câu hỏi vì sao nó thu hút nhiều chú ý; bài này trả lời bằng đường đi của mã từ ngôn ngữ gốc tới trang web và những gì nó vẫn chưa làm được.

![Ba nhóm thẻ xếp dọc. Đường đi của mã, bốn bước: viết hoặc dùng sẵn mã C, C++ hay Rust; biên dịch ra mô-đun WASM; trình duyệt tải mô-đun cùng JavaScript; JavaScript gọi hàm trong mô-đun và mã chạy gần tốc độ mã gốc. Trước và sau, hai thẻ: trước đây trình duyệt chỉ tải được JavaScript và gặp vấn đề hiệu năng ở tác vụ nặng; với WASM thì dùng lại được thư viện C, C++ hay Rust có sẵn. Khung cuối nêu ba giới hạn: WASM không tự gọi DOM mà phải qua JavaScript; ý về điện toán đám mây và biên là nhận định của nguồn; WASM bổ sung cho JavaScript chứ không thay thế.](../../diagrams/sd-10-006-main.svg)

## Từ viết tắt

- **WASM** (Web ASseMbly) — viết tắt của WebAssembly: định dạng mã nhị phân nhỏ gọn mà trình duyệt tải về và chạy gần tốc độ mã gốc; mã C, C++ hay Rust được biên dịch ra định dạng này.
- **MDN** (Mozilla Developer Network) — tên cũ của MDN Web Docs, bộ tài liệu tra cứu công nghệ web do Mozilla và cộng đồng viết; bài dùng nó để đối chiếu.
- **DOM** (Document Object Model) — mô hình đối tượng tài liệu: cách trình duyệt biểu diễn trang web thành các đối tượng mà mã có thể đọc và sửa.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: tập hàm mà một chương trình mở ra để chương trình khác gọi, ở đây là các hàm JavaScript dùng để tải và gọi mô-đun WASM.

## Đọc hình

**Đường đi của mã.** Mã gốc viết bằng C, C++ hoặc Rust thường được biên dịch ra mô-đun WASM; WebAssembly cũng có dạng văn bản đọc được nên về nguyên tắc viết tay được, nhưng không chủ yếu dành cho việc đó. Trình duyệt tải mô-đun cùng với JavaScript. JavaScript gọi các hàm mà mô-đun mở ra, và mô-đun chạy với hiệu năng gần mã gốc.

**Trước và sau.** Theo bài nguồn, trước đây trình duyệt chỉ làm việc với JavaScript và hiệu năng không sánh được với mã gốc như C hay C++. Với WASM, ta tái sử dụng các thư viện mã gốc có sẵn, ví dụ thư viện mã hóa và giải mã video viết bằng C++, để chạy trong trình duyệt với hiệu năng gần mã gốc.

**Cho điện toán đám mây và điện toán biên.** Bài nguồn cho rằng điều này mở ra nhiều khả năng ngoài trình duyệt: chạy ứng dụng serverless với ít tài nguyên hơn và khởi động tức thì.

## Giới hạn cần nhớ

WASM không phải thay thế JavaScript. Tài liệu MDN nói nó được thiết kế để bổ sung và chạy cạnh JavaScript. Mã WASM hiện không tự truy cập DOM mà chỉ gọi JavaScript, rồi JavaScript mới gọi các API của trình duyệt.
Bài nguồn giải thích khoảng cách hiệu năng bằng việc JavaScript bị thông dịch; tài liệu MDN nói gọn hơn là JavaScript gặp vấn đề hiệu năng ở các việc nặng như đồ họa 3D hay xử lý ảnh và video. Bài này giữ cách nói của MDN.
Phần về điện toán đám mây và điện toán biên (serverless, khởi động tức thì) là nhận định của bài nguồn, chưa được đối chiếu.

## Nhìn hình trả lời

Một nhóm có sẵn thư viện nén video viết bằng C++ và muốn dùng nó trong trang web. Họ có phải viết lại thư viện bằng JavaScript không? Và khi trang cần cập nhật giao diện, mã nào làm việc đó?

<details>
<summary>Xem đáp án</summary>

Không nhất thiết: họ biên dịch thư viện ra mô-đun WASM, tải cùng JavaScript và gọi các hàm của nó từ JavaScript.
Việc cập nhật giao diện vẫn do JavaScript làm, vì mã WASM không tự truy cập DOM mà phải gọi JavaScript để chạm tới các API của trình duyệt.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh minh họa và vài đoạn ngắn: WASM là gì, trước đây chỉ có JavaScript, WASM cho phép tái sử dụng thư viện mã gốc, ví dụ mã hóa video, rồi nói về điện toán đám mây và biên. Bài này không dùng ảnh.
Bước biên dịch ra mô-đun, việc JavaScript tải và gọi mô-đun, và giới hạn về DOM lấy từ tài liệu MDN tại commit cố định, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/is-it-possible-to-run-c-c++-or-rust-on-a-web-browser.md): WASM, tái sử dụng thư viện mã gốc, ví dụ mã hóa video, điện toán đám mây và biên.
- [MDN — WebAssembly, tổng quan](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/webassembly/index.md) và [khái niệm](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/webassembly/guides/concepts/index.md): đích biên dịch của C, C++, Rust; bổ sung cho JavaScript; không gọi trực tiếp DOM. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-18. Ý về serverless và khởi động tức thì chưa kiểm tra với tài liệu nào.
Bài viết và hình được thiết kế độc lập.
