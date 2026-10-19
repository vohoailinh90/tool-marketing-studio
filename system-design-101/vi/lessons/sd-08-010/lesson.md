# Tám khái niệm lập trình hướng đối tượng, thử từng cái trong Python

**Bài nguồn là một hình về tám khái niệm lập trình hướng đối tượng kèm vài đoạn giới thiệu, nhưng phần chữ không gọi tên tám khái niệm đó và hình không đọc được lúc viết. Bài này vì vậy chọn tám khái niệm thường được dạy (lớp, đối tượng, đóng gói, trừu tượng, kế thừa, đa hình, thành phần, giao diện), thử từng khái niệm trong Python 3.13 và đo hai điều hay bị đoán sai về chi phí.**

![Ba khung. Khung một, tám khái niệm: lớp, đối tượng, đóng gói, trừu tượng, kế thừa, đa hình, thành phần và giao diện. Khung hai, thử trong Python 3.13: biến đóng gói gạch dưới vẫn gán được từ ngoài, tên hai gạch dưới chỉ bị đổi tên và vẫn đọc được, lớp trừu tượng không tạo được đối tượng, vịt gõ không cần kế thừa mà vẫn dùng chung mã. Khung ba, đo thời gian: gọi phương thức cách 1, 5 hay 20 tầng kế thừa đều khoảng 24 đến 26 nano giây, và gọi đa hình trên 100 đối tượng mất 3,8 đến 4,0 micro giây so với 7,8 đến 8,2 micro giây khi tự rẽ nhánh bằng kiểm tra kiểu.](../../diagrams/sd-08-010-main.svg)

## Từ viết tắt

- **OOP** (Object-Oriented Programming) — lập trình hướng đối tượng: cách viết chương trình bằng các đối tượng, mỗi đối tượng gói dữ liệu và việc làm với dữ liệu đó.

## Đọc hình

Danh sách tám khái niệm dưới đây là lựa chọn của người biên soạn, chưa đối chiếu với hình của bài nguồn. Ý của từng khái niệm được kiểm bằng tài liệu chính thức của Python và bằng chương trình thử.

| Khái niệm | Ý | Chỗ kiểm trong Python |
|---|---|---|
| Lớp (class) | Khuôn mô tả dữ liệu và việc làm | Biến của lớp dùng chung cho mọi đối tượng, biến của đối tượng thì riêng |
| Đối tượng (object) | Vật dựng ra từ lớp | Hai đối tượng cùng một lớp, mỗi cái có dữ liệu riêng |
| Đóng gói (encapsulation) | Giấu chi tiết, buộc truy cập qua phương thức để giữ luật | Python không có biến riêng tư thực sự: gạch dưới chỉ là quy ước |
| Trừu tượng (abstraction) | Chỉ lộ cách dùng, giấu cách làm | Lớp trừu tượng khai báo phương thức bắt buộc, không tạo được đối tượng |
| Kế thừa (inheritance) | Lớp con dùng lại và sửa lớp cha | Thuộc tính không có ở lớp con thì được tìm ở lớp cha |
| Đa hình (polymorphism) | Cùng một lời gọi, mỗi đối tượng làm theo cách của mình | Mọi phương thức đều có thể bị lớp con ghi đè |
| Thành phần (composition) | Đối tượng chứa đối tượng khác thay vì kế thừa | `Car` giữ một `Engine` |
| Giao diện (interface) | Bộ phương thức mà bên dùng được phép trông cậy | Lớp trừu tượng, hoặc "vịt gõ": có phương thức là dùng được |

## Thử: từng khái niệm một

Ngày 2026-10-19, Python 3.13.16. Kết quả chạy:

- **Lớp và đối tượng.** Với `Dog.kind = "canine"` và `self.name` đặt trong hàm khởi tạo: hai đối tượng `Fido` và `Buddy` cùng thấy `canine`, tên thì riêng; đổi `Dog.kind` một lần thì cả hai cùng thấy giá trị mới.
- **Đóng gói.** `deposit(-1)` bị từ chối bằng một lỗi, nhưng `a._balance = -999` từ bên ngoài được chấp nhận. Với `__secret`, truy cập `a.__secret` báo `AttributeError`, nhưng `a._Account__secret` đọc được giá trị 1: tên chỉ bị đổi, không bị khoá. Tài liệu Python nói thẳng rằng biến riêng tư thật sự không tồn tại; tên hai gạch dưới là cơ chế "đổi tên" để lớp con không đè nhầm tên.
- **Trừu tượng.** Tạo `Shape()` (lớp có phương thức trừu tượng `area`) báo `TypeError`; hai lớp con `Sq` và `Circ` tạo được và `describe` của lớp cha gọi đúng `area` của từng lớp con (4,00 và 3,14).
- **Kế thừa và đa hình.** Phương thức `run` của lớp cha gọi `self.step()` và nhận được kết quả của lớp con (`derived`): trong Python mọi phương thức đều có thể bị ghi đè.
- **Giao diện bằng vịt gõ.** Một lớp `Duck` không kế thừa `Shape`, chỉ có `area` và `describe`, vẫn dùng chung mã (`isinstance(Duck(), Shape)` là `False`). Đây là phép thử cho thấy "giao diện" trong Python có thể là một thoả thuận về tên phương thức, không nhất thiết là một lớp cha.
- **Thành phần.** `Car(Engine()).go()` gọi `engine.start()` và cho `engine on`; `Car` chứa `Engine` nhưng không phải là một `Engine`.

## Thử: hai điều đoán về chi phí

Ba lần chạy, mỗi lần lấy lượt nhanh nhất trong bảy lượt, một triệu lần gọi:

| Điều đo | Kết quả |
|---|---|
| Gọi một phương thức khai báo ở tầng trên cùng của chuỗi kế thừa 1 tầng, 5 tầng, 20 tầng | 23,5 đến 25,5 nano giây ở cả ba mức, không tăng theo số tầng |
| Gọi `m()` của 100 đối tượng thuộc hai lớp (đa hình) | 3,78 đến 3,95 micro giây |
| Cùng việc đó nhưng tự rẽ nhánh bằng `isinstance` | 7,80 đến 8,22 micro giây |

Kết quả: kế thừa sâu không làm lời gọi chậm hơn đáng kể ở phép thử này, và để đối tượng tự chọn cách làm (đa hình) không chậm hơn việc tự rẽ nhánh, mà còn nhanh hơn khoảng hai lần ở đây.

## Giới hạn cần nhớ

Danh sách tám khái niệm là lựa chọn của người biên soạn; bài nguồn có thể chọn khác. Mọi phép thử chạy trên Python, nơi đóng gói là quy ước và giao diện có thể là vịt gõ; ở Java hay C++ cùng khái niệm có thể được ngôn ngữ ép chặt hơn. Phép đo chỉ cho ba mức tầng kế thừa trong một chuỗi đơn, không xét đa kế thừa, và là thời gian một lời gọi rất ngắn trên một máy: con số tuyệt đối thuộc về máy đó. Phép đo không nói kế thừa sâu là thiết kế tốt: chi phí thời gian không tăng không có nghĩa chi phí đọc hiểu không tăng.

## Nhìn hình trả lời

Đồng nghiệp bảo "ở Python mình khai báo `_balance` là đã đóng gói rồi". Phép thử nào ở trên cho thấy điều đó chưa đủ, và nên làm gì để luật "số tiền gửi phải dương" luôn đúng?

<details>
<summary>Xem đáp án</summary>

Phép thử đóng gói: `a._balance = -999` từ bên ngoài vẫn được nhận, vì gạch dưới chỉ là quy ước. Để luật luôn đúng, mọi thay đổi phải đi qua phương thức như `deposit` (nơi có kiểm tra), và nhóm làm việc thoả thuận không chạm vào thuộc tính gạch dưới từ ngoài; nếu cần chặt hơn thì dùng thuộc tính chỉ đọc (`property`) cho số dư.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một hình và vài đoạn giới thiệu chung (OOP có từ thập niên 1960, phổ biến những năm 1990 với Java và C++). Bài này giữ ý của các đoạn đó, chọn tám khái niệm và thay hình bằng phép thử trong mã cùng hai phép đo thời gian.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/8-key-oop-concepts-every-developer-should-know.md): phần chữ giới thiệu; hình không đọc được.
- [Python — hướng dẫn về lớp (classes)](https://github.com/python/cpython/blob/7dbc7975db8e34db8be8e4a10bd10784ab49b07a/Doc/tutorial/classes.rst): biến lớp và biến đối tượng, kế thừa, mọi phương thức đều ghi đè được, biến riêng tư và đổi tên.
- [Python — bảng thuật ngữ (glossary)](https://github.com/python/cpython/blob/7dbc7975db8e34db8be8e4a10bd10784ab49b07a/Doc/glossary.rst): vịt gõ và lớp cơ sở trừu tượng.

Đã đọc nguồn ngày 2026-10-19. Các phép thử là của người biên soạn.
Bài viết và hình được thiết kế độc lập.
