# Năm mẫu thiết kế đầu tiên, tìm trong thư viện chuẩn của Python

**Bài nguồn là một bảng tóm tắt các mẫu thiết kế, mở đầu bằng năm mẫu: Factory, Builder, Prototype, Singleton và Chain of Responsibility. Một mẫu thiết kế là cách đặt tên cho một lời giải đã lặp lại nhiều lần; bài này tìm từng mẫu trong mã có thật của Python 3.13 để thấy nó trông thế nào ngoài sách.**

![Ba khung. Khung một, năm mẫu và chỗ gặp trong thư viện chuẩn Python: nhà máy là cách thay hàm tạo bản ghi nhật ký; người xây là bộ dựng cây thẻ lồng nhau từng bước; nguyên mẫu là việc sao chép đối tượng có móc riêng; đơn thể duy nhất là bộ ghi nhật ký gốc; chuỗi trách nhiệm là bộ ghi nhật ký đi ngược lên cha. Khung hai, thử với ba bộ ghi lồng nhau: lỗi đi qua ba bộ xử lý theo thứ tự, thông tin chỉ qua hai, và dừng lan lên thì chỉ còn hai bộ đầu. Khung ba, đếm tên trong thư viện chuẩn: 16 tên có chữ Factory, 11 chữ Builder, 1 chữ Singleton nhưng không thuộc mẫu, 0 chữ Prototype.](../../diagrams/sd-08-008-main.svg)

## Đọc hình

Định nghĩa ngắn của từng mẫu dưới đây là kiến thức chung của người biên soạn (bài nguồn chỉ nêu tên); phần "chỗ gặp" được kiểm trên mã nguồn của Python 3.13.

| Mẫu | Ý của mẫu | Chỗ gặp trong thư viện chuẩn |
|---|---|---|
| Factory | Giao việc tạo đối tượng cho một hàm, để bên gọi không chọn lớp cụ thể | `logging.setLogRecordFactory`: thay hàm tạo bản ghi nhật ký |
| Builder | Dựng đối tượng phức tạp từng bước | `xml.etree.ElementTree.TreeBuilder`: gọi `start`, `data`, `end`, `close` |
| Prototype | Tạo đối tượng mới bằng cách sao chép một đối tượng có sẵn | `copy.copy` và `copy.deepcopy`, có móc `__copy__` |
| Singleton | Chỉ có đúng một đối tượng | `logging.root` (bộ ghi nhật ký gốc), và `None` |
| Chain of Responsibility | Chuyển yêu cầu dọc một chuỗi cho tới khi có bên xử lý | `Logger.callHandlers` đi từ bộ ghi con lên cha |

## Thử: kiểm từng chỗ gặp bằng một đoạn chương trình

Ngày 2026-10-19, Python 3.13.16. Kết quả chạy:

- **Singleton.** `type(None)() is None` cho `True`; `logging.getLogger() is logging.root` cho `True`. Cùng tên thì cùng một bộ ghi (`getLogger("a") is getLogger("a")` là `True`), nhưng bộ con `a.b` khác bộ cha `a`: mỗi tên có một đối tượng, nên đây là "một đối tượng cho mỗi tên", không phải một đối tượng duy nhất cho cả chương trình.
- **Chain of Responsibility.** Dựng ba bộ ghi lồng nhau `svc.db` (con), `svc` (giữa), gốc (`root`), mỗi bộ có một bộ xử lý đếm; bộ xử lý của `svc.db` chỉ nhận mức lỗi trở lên. Ghi một dòng mức thông tin ở `svc.db`: thứ tự xử lý là `svc`, rồi `root` (hai bộ). Ghi mức lỗi: `svc.db`, `svc`, `root` (ba bộ, từ con lên gốc). Đặt `propagate = False` ở `svc` rồi ghi lỗi: chỉ còn `svc.db`, `svc`. Đây đúng là một chuỗi, với điều kiện dừng ở giữa chuỗi.
- **Prototype.** Một lớp có `__copy__` trả về bản sao có danh sách riêng: sau `y = copy.copy(x)` và thêm phần tử vào `y`, `x.items` vẫn là `[1, 2]` còn `y.items` là `[1, 2, 3]`.
- **Builder.** Gọi `start("a")`, `start("b")`, `data("hi")`, `end("b")`, `end("a")` trên `TreeBuilder` rồi `close()` cho cây `<a><b>hi</b></a>`.
- **Factory.** Thay hàm tạo bản ghi bằng một hàm gắn thêm thuộc tính `tag`: bản ghi tới bộ xử lý mang thuộc tính đó.

## Thử: mẫu hiện diện nhiều hơn là mang tên

Cùng ngày, một chương trình đếm tên lớp và hàm (không tính thư mục kiểm thử) trong thư viện chuẩn có chứa chữ tên mẫu. Kết quả: Factory 16 tên (ví dụ `getLogRecordFactory`, `create_eager_task_factory`), Builder 11 tên (ví dụ `TreeBuilder`, `EnvBuilder`), Chain 11 tên nhưng không tên nào thuộc mẫu (như `ChainMap`, `get_unverified_chain`), Singleton 1 tên không liên quan (`visit_MatchSingleton`, của bộ duyệt cây cú pháp), Prototype 0 tên. Nghĩa là Prototype, Singleton và Chain of Responsibility đều có mặt trong thư viện chuẩn, nhưng không dưới tên đó.

## Giới hạn cần nhớ

Phần tìm trong mã chỉ cho thấy mỗi mẫu có một ví dụ, không chứng minh các tác giả thư viện chủ ý theo mẫu nào. Định nghĩa các mẫu là kiến thức chung, chưa đối chiếu với cuốn sách gốc về mẫu thiết kế; nên đọc chúng như gợi ý. `logging.root` và `getLogger` cho thấy Singleton dễ bị hiểu hẹp: ở đây là một đối tượng cho mỗi tên. Phép đếm tên là phép đếm chuỗi chữ, nên bỏ sót mọi chỗ dùng mẫu mà không đặt tên theo mẫu (như `copy.copy`) và đếm nhầm các chữ trùng hợp.

## Nhìn hình trả lời

Bạn muốn mọi chỗ trong ứng dụng ghi nhật ký vào cùng một tệp nhưng mô-đun `db` chỉ cần ghi thêm lỗi vào tệp riêng. Mẫu nào trong năm mẫu giúp, và dùng thế nào trong thư viện `logging`?

<details>
<summary>Xem đáp án</summary>

Chain of Responsibility: gắn bộ xử lý ghi tệp chung vào bộ ghi gốc, gắn thêm một bộ xử lý ghi tệp riêng mức lỗi vào bộ ghi `db`. Một dòng lỗi ở `db` đi qua bộ xử lý của `db` rồi lan lên gốc, nên có mặt ở cả hai tệp; nếu muốn lỗi của `db` chỉ nằm ở tệp riêng thì đặt `propagate = False` ở `db`.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một hình bảng tóm tắt kèm danh sách vài tên mẫu ("và nhiều mẫu khác"). Bài này giữ năm tên được nêu, giải nghĩa từng mẫu bằng một dòng và thay hình bảng tóm tắt bằng chỗ gặp có thể kiểm trong mã Python, cùng một phép đếm tên để thấy mẫu hiện diện mà không mang tên.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/design-patterns-cheat-sheet-part-1-and-part-2.md): tên năm mẫu đầu của bảng tóm tắt.
- [Python 3.13 — mô-đun logging, copy và xml.etree.ElementTree](https://docs.python.org/3.13/library/logging.html): mã nguồn đọc từ bản cài đặt trên máy thử.

Đã đọc nguồn ngày 2026-10-19. Các phép thử là của người biên soạn.
Bài viết và hình được thiết kế độc lập.
