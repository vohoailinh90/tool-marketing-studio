# Mười tám mẫu thiết kế của nguồn: mười bốn mẫu, tìm trong thư viện chuẩn của Python

**Bài nguồn là một hình liệt kê mười tám mẫu thiết kế, mỗi mẫu có một biệt danh ngắn ("Family Creator", "Universal Plug", "Time Capsule"...). Bài này lấy mười bốn mẫu trong số đó (bỏ bốn mẫu đã có bài riêng trong nhóm này) rồi tìm từng mẫu trong thư viện chuẩn Python 3.13: chín mẫu có ví dụ rõ, hai gần đúng, ba chưa tìm được, kèm ba phép đo cho thấy mỗi mẫu tốn hay tiết kiệm gì.**

![Ba khung. Khung một, tìm mười bốn mẫu trong thư viện chuẩn Python 3.13: chín mẫu có ví dụ rõ là bộ chuyển tiếp, thành phần, bộ trang trí, mặt tiền, mẫu dùng chung, đại diện, bộ lặp, bản lưu trạng thái và người thăm; hai mẫu gần đúng là lệnh và người quan sát; ba mẫu chưa tìm được là nhà máy trừu tượng, cầu nối và người trung gian. Khung hai, ba phép đo: bọc một hàm bằng bộ trang trí thêm khoảng 55 đến 60 nano giây mỗi lần gọi, đại diện yếu thêm khoảng 13 nano giây mỗi lần truy cập, dùng chung chuỗi giảm từ 53,3 triệu xuống 8,5 triệu byte. Khung ba, giới hạn của cách tìm.](../../diagrams/sd-08-011-main.svg)

## Đọc hình

Biệt danh ở cột hai là của bài nguồn; cột ba và bốn do phép thử trong Python 3.13.16 ngày 2026-10-19. Định nghĩa của từng mẫu chỉ là biệt danh của nguồn cộng một dòng giải thích của người biên soạn, chưa đối chiếu với cuốn sách gốc về mẫu thiết kế.

| Mẫu | Biệt danh của nguồn | Chỗ gặp trong thư viện chuẩn | Kết quả thử |
|---|---|---|---|
| Abstract Factory | Family Creator | chưa tìm được ví dụ chắc chắn | — |
| Adapter | Universal Plug | `io.TextIOWrapper` nối một luồng byte thành luồng chữ | đọc ra `'xin chào\n'`, `.buffer` vẫn là luồng gốc |
| Bridge | Function Connector | chưa tìm được ví dụ chắc chắn | — |
| Composite | Tree Builder | phần tử của `xml.etree.ElementTree`: nút chứa nút cùng loại | duyệt cây `a, b, c` bằng một vòng lặp |
| Decorator | Customizer | hàm bọc, `functools.wraps` | tên hàm được giữ, hàm gốc ở `__wrapped__` |
| Facade | One-Stop-Shop | `shutil.make_archive`: một lời gọi che việc duyệt thư mục và ghi tệp nén | cho ra tệp `z.zip` có nội dung |
| Flyweight | Space Saver | số nguyên nhỏ dùng chung, `sys.intern` cho chuỗi | `256 is 256` đúng, `257 is 257` sai; hai chuỗi bằng nhau thành một đối tượng sau `sys.intern` |
| Proxy | Stand-In Actor | `weakref.proxy` | truy cập `.v` qua đại diện được; khi đối tượng đã mất thì báo `ReferenceError` |
| Command | Task Wrapper | gần đúng: `functools.partial` gói một hàm với đối số | `partial(pow, 2, 10)()` cho 1024 |
| Iterator | Collection Explorer | giao thức `__iter__` và `__next__` | `list(Countdown(3))` cho `[3, 2, 1]` |
| Mediator | Communication Hub | chưa tìm được ví dụ chắc chắn | — |
| Memento | Time Capsule | `random.getstate` và `random.setstate` | đặt lại trạng thái thì ba số ngẫu nhiên giống hệt lần trước |
| Observer | News Broadcaster | gần đúng: `weakref.finalize` đăng ký một hàm được gọi khi đối tượng bị thu hồi | hàm đăng ký chạy đúng một lần |
| Visitor | Skillful Guest | `ast.NodeVisitor` gọi `visit_` cộng tên lớp của nút | đếm được 4 tên trong `a = b + c * d` |

Tổng kết cách tìm: chín mẫu có ví dụ rõ (Adapter, Composite, Decorator, Facade, Flyweight, Proxy, Iterator, Memento, Visitor), hai gần đúng (Command, Observer), ba chưa tìm được (Abstract Factory, Bridge, Mediator). "Gần đúng" nghĩa là có một công cụ làm phần lớn việc của mẫu nhưng không đúng cấu trúc mà sách mô tả.

## Thử: ba mẫu tốn hay tiết kiệm gì

Cùng ngày, trên một máy ảo 4 lõi, Python 3.13.16, một triệu lần mỗi phép đo, lấy lượt nhanh nhất trong bảy lượt, ba lần chạy.

| Phép đo | Kết quả |
|---|---|
| Gọi một hàm trơn so với hàm bọc bởi một bộ trang trí | 42 đến 53 nano giây so với 102 đến 105 nano giây, tức thêm khoảng 55 đến 60 nano giây mỗi lần gọi |
| Đọc thuộc tính `o.v` so với qua `weakref.proxy(o).v` | 25 đến 26 nano giây so với 38 đến 40 nano giây, thêm khoảng 13 nano giây |
| Một triệu chuỗi chỉ có 1.000 giá trị khác nhau, mỗi chuỗi tạo riêng so với dùng chung một bản (kiểu Flyweight) | 53,3 triệu byte so với 8,5 triệu byte, trong cả ba lần chạy |

Hai mẫu đầu là cái giá của một tầng gián tiếp; mẫu thứ ba là phần thưởng của việc dùng chung: nhớ rằng 8,5 triệu byte vẫn gồm một danh sách tám triệu byte các con trỏ, nên phần tiết kiệm nằm ở các chuỗi, không ở danh sách.

## Giới hạn cần nhớ

Mỗi mẫu chỉ có một ví dụ do người biên soạn chọn; điều đó không chứng minh tác giả thư viện chủ ý theo mẫu nào, và ba mẫu chưa tìm được không có nghĩa Python không dùng chúng (phép tìm chỉ xem một phần thư viện chuẩn, không xem mã bên thứ ba). Định nghĩa các mẫu chưa đối chiếu với cuốn sách gốc. Ba phép đo chạy trên một máy, bằng những đoạn rất nhỏ: con số tuyệt đối thuộc về máy đó, và phép đo bộ trang trí cộng thêm chi phí của lời gọi bọc bên trong. Biệt danh của nguồn là cách nhớ, không phải định nghĩa.

## Nhìn hình trả lời

Bạn muốn mọi hàm xử lý đơn hàng tự ghi lại thời gian chạy mà không sửa thân hàm nào. Mẫu nào trong mười bốn mẫu giúp, trong Python làm bằng gì, và phải trả giá gì?

<details>
<summary>Xem đáp án</summary>

Decorator: viết một hàm bọc nhận hàm gốc, đo thời gian rồi gọi hàm gốc, và dùng `functools.wraps` để giữ tên hàm. Trên máy thử, mỗi lần gọi thêm khoảng 55 đến 60 nano giây, nên không đáng lo với hàm xử lý đơn hàng nhưng đáng cân nhắc với hàm gọi hàng triệu lần mỗi giây.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một hình và danh sách mười tám mẫu kèm biệt danh. Bài này giữ biệt danh, bỏ bốn mẫu không xét, tìm một chỗ gặp cho mỗi mẫu còn lại bằng phép thử có thể chạy lại, nói rõ ba mẫu chưa tìm được và thêm ba phép đo chi phí.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/18-key-design-patterns-every-developer-should-know.md): mười tám mẫu và biệt danh.
- [Python 3.13 — thư viện chuẩn](https://docs.python.org/3.13/library/index.html): `io`, `functools`, `weakref`, `shutil`, `ast`, `random`, `xml.etree.ElementTree`; mã nguồn đọc từ bản cài đặt trên máy thử.

Đã đọc nguồn ngày 2026-10-19. Các phép thử là của người biên soạn.
Bài viết và hình được thiết kế độc lập.
