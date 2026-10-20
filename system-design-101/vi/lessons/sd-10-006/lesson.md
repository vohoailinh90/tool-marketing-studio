# Chạy C, C++ và Rust trong trình duyệt bằng WebAssembly

**Trình duyệt vốn chỉ nạp được JavaScript; WebAssembly thêm loại mã thứ hai, nhỏ gọn và gần mã máy, để C, C++, Rust và một số ngôn ngữ khác chạy được trên trang web.**
Điều đáng nắm không nằm ở chuyện "nhanh hơn" mà ở cách hai loại mã chia việc và gọi nhau.

![Ba nhóm thẻ xếp dọc. Từ mã nguồn đến trang web, bốn bước: viết bằng ngôn ngữ cấp cao như C, C++ hoặc Rust; trình biên dịch xuất tệp nhị phân WASM; trình duyệt biên dịch tệp đó thành một Module; JavaScript tạo Instance rồi gọi hàm xuất. Bốn khái niệm trong trình duyệt: Module là bản nhị phân đã biên dịch và không giữ trạng thái; Memory là vùng byte liền kề có thể lớn dần; Table là mảng tham chiếu như tham chiếu tới hàm; Instance là một Module cùng trạng thái lúc chạy. Khung cuối nêu ba điều cần nhớ: WASM bổ sung cho JavaScript chứ không thay thế; WASM không chạm DOM trực tiếp mà gọi qua JavaScript; mã WASM thường không viết tay.](../../diagrams/sd-10-006-main.svg)

## Từ viết tắt

- **WASM** (Web ASseMbly) — viết tắt của WebAssembly: định dạng mã nhị phân nhỏ gọn mà trình duyệt nạp và chạy; mã C, C++ hay Rust được biên dịch ra định dạng này.
- **MDN** (Mozilla Developer Network) — tên cũ của MDN Web Docs, bộ tài liệu tra cứu công nghệ web do Mozilla và cộng đồng viết; bài dùng nó để đối chiếu.
- **DOM** (Document Object Model) — mô hình đối tượng tài liệu: cách trình duyệt biểu diễn trang web thành các đối tượng mà mã có thể đọc và sửa.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: tập hàm mà một thành phần mở ra để thành phần khác gọi; ở đây là các hàm JavaScript dùng để tạo và gọi mô-đun WASM.
- **HTML** (HyperText Markup Language) — ngôn ngữ đánh dấu siêu văn bản: định dạng mô tả cấu trúc một trang web.

## Đọc hình

**Từ mã nguồn tới trang web.** Tài liệu của Mozilla nhấn mạnh rằng WASM không chủ yếu để viết tay: người ta thường viết bằng một ngôn ngữ cấp cao có kiểu tĩnh rồi nhờ trình biên dịch xuất ra WASM.
1. Viết hoặc tái dùng mã C, C++ hay Rust. Tài liệu cũng nói các ngôn ngữ có bộ nhớ tự dọn rác được hỗ trợ.
2. Trình biên dịch nhắm tới WASM. Trình biên dịch Clang xuất được WASM khi chọn đích `wasm32`; Rust có chuỗi công cụ riêng. Với ứng dụng C/C++ lớn, công cụ Emscripten làm nhiều hơn: nó mô phỏng các API nền tảng mà mã đang gọi và sinh thêm mã JavaScript "dán" cùng một trang HTML để chạy thử.
3. Trình duyệt nạp tệp nhị phân và biên dịch nó thành mã máy; kết quả là một `Module`.
4. JavaScript tạo `Instance` từ `Module` rồi gọi các hàm mà nó mở ra, các hàm này hiện ra như hàm JavaScript bình thường.

**Bốn khái niệm.** Chúng khớp từng cái một với giao diện JavaScript của WASM:
- `Module`: bản nhị phân đã được trình duyệt biên dịch. Nó không giữ trạng thái nên có thể chia sẻ giữa các cửa sổ và luồng nền; nó khai báo những gì cần nhập vào và những gì mở ra, giống một mô-đun JavaScript chuẩn.
- `Memory`: vùng đệm byte liền kề có thể lớn dần, nơi các lệnh truy cập bộ nhớ mức thấp đọc và ghi.
- `Table`: mảng tham chiếu có thể lớn dần, ví dụ tham chiếu tới hàm. Những thứ này không được để thành byte thô trong `Memory`, vì lý do an toàn và khả chuyển.
- `Instance`: một `Module` ghép với toàn bộ trạng thái nó dùng lúc chạy: `Memory`, `Table` và các giá trị nhập vào.

**Hai chiều gọi.** JavaScript gọi đồng bộ các hàm mà `Instance` mở ra. Ngược lại, mã WASM gọi đồng bộ các hàm JavaScript mà ta truyền vào làm giá trị nhập khi tạo `Instance`. Cả hai loại mã chạy trong cùng máy ảo của trình duyệt.

**Bốn mục tiêu thiết kế.** Tài liệu liệt kê: nhanh, gọn và khả chuyển; có dạng văn bản để đọc và gỡ lỗi; chạy trong môi trường cách ly và tuân theo chính sách cùng nguồn gốc và quyền như mã web khác; không phá vỡ web hiện có.

## Giới hạn cần nhớ

- WASM bổ sung cho JavaScript chứ không thay thế. Theo tài liệu, JavaScript mạnh ở chỗ linh hoạt, kiểu động, không cần biên dịch và có hệ sinh thái lớn; WASM mạnh ở chỗ định dạng nhị phân gọn, chạy gần tốc độ mã gốc cho các ngôn ngữ có mô hình bộ nhớ mức thấp.
- Mã WASM hiện không truy cập `DOM` trực tiếp. Việc chạm vào trang web phải đi qua một hàm JavaScript được truyền vào, và đó cũng là lý do Emscripten sinh mã dán JavaScript.
- "Gần tốc độ mã gốc" là cách tài liệu mô tả mục tiêu của WASM. Bài này không đo tốc độ, nên đừng đọc nó thành con số; tốc độ thực tế tùy việc và tùy trình duyệt.
- Tài liệu nêu hai điểm nghẽn mà WASM nhắm tới: các việc nặng như trò chơi 3D, thực tế ảo và thực tế tăng cường, thị giác máy tính, xử lý ảnh và video; và chi phí tải, phân tích, biên dịch của ứng dụng JavaScript rất lớn, nhất là trên thiết bị ít tài nguyên.
- WASM ra đời cho web nhưng tài liệu ghi rằng nó còn nhiều công dụng ngoài trình duyệt. Bài này không đi vào phần đó.

## Nhìn hình trả lời

Một nhóm có thư viện xử lý ảnh viết bằng Rust và muốn gọi nó từ trang web. Họ cần làm những bước nào để gọi được hàm đầu tiên? Và nếu hàm đó phải cập nhật một phần tử trên trang thì mã nào thực hiện việc cập nhật?

<details>
<summary>Xem đáp án</summary>

Họ biên dịch thư viện bằng chuỗi công cụ Rust nhắm tới WASM, nạp tệp nhị phân trong trang để có `Module`, tạo `Instance` bằng giao diện JavaScript rồi gọi hàm mà nó mở ra như một hàm JavaScript.
Việc cập nhật phần tử trang vẫn do JavaScript làm, vì mã WASM không truy cập `DOM` trực tiếp. Cách làm thông thường là truyền một hàm JavaScript vào làm giá trị nhập để mã WASM gọi tới.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn chỉ có một ảnh minh họa và vài đoạn ngắn về WASM, về việc tái dùng thư viện mã gốc và về điện toán đám mây, điện toán biên. Bài này không dùng ảnh và không theo thứ tự đó; từ bài nguồn chỉ giữ chủ đề và ba tên ngôn ngữ.
Toàn bộ lời giải thích, gồm đường biên dịch, bốn khái niệm `Module`, `Memory`, `Table`, `Instance`, hai chiều gọi, các mục tiêu thiết kế và giới hạn về `DOM`, được viết lại từ tài liệu MDN tại commit cố định. Các nhận định của bài nguồn về serverless và khởi động tức thì không được nêu lại vì chưa đối chiếu với tài liệu nào; lời giải thích về hiệu năng cũng lấy theo cách nói của tài liệu MDN.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/is-it-possible-to-run-c-c++-or-rust-on-a-web-browser.md): chỉ dùng để lấy chủ đề và tên các ngôn ngữ.
- [MDN — WebAssembly, tổng quan](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/webassembly/index.md) và [khái niệm](https://github.com/mdn/content/blob/a1aa79c09717761fc72c20bac94bb9c430ed487a/files/en-us/webassembly/guides/concepts/index.md): đích biên dịch, mục tiêu, bốn khái niệm, hai chiều gọi, Emscripten, giới hạn về `DOM`. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-19. Mọi lời giải thích lấy từ hai trang MDN nêu trên; câu hỏi cuối bài là ví dụ tự đặt.
Bài viết và hình được thiết kế độc lập.
