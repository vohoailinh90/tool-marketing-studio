# Một kho hay nhiều kho: mỗi cách trả giá ở đâu

**Mã nguồn của nhiều dịch vụ có thể nằm chung một kho (monorepo) hoặc mỗi dịch vụ một kho riêng (nhiều kho, còn gọi là polyrepo).** Cả hai chạy được ở công ty lớn lẫn nhỏ; khác nhau ở chỗ cái giá nằm đâu: một kho trả bằng công cụ và kỷ luật chung, nhiều kho trả bằng việc phối hợp giữa các kho.

![Hai khung. Khung một, một kho chung cho mọi dịch vụ: một thay đổi chạm nhiều dịch vụ nằm trong một commit, mọi dịch vụ dùng cùng phiên bản thư viện, cần công cụ build biết cái gì đổi, mỗi thư mục cần người sở hữu. Khung hai, mỗi dịch vụ một kho: quyền truy cập và cấu hình build riêng, mỗi đội tự chọn lúc nâng phiên bản, đổi chung nhiều dịch vụ cần nhiều thay đổi nối nhau, chuẩn chất lượng có thể lệch nhau.](../../diagrams/sd-11-018-main.svg)

## Đọc hình

**Một kho chung.** Mọi dịch vụ là các thư mục trong cùng một kho. Hệ quả đầu tiên là một thay đổi chạm nhiều dịch vụ (đổi chữ ký của một hàm dùng chung, chẳng hạn) có thể nằm trọn trong một commit, nên sau commit đó không có dịch vụ nào còn dùng bản cũ. Hệ quả thứ hai là cả kho thường dùng chung một phiên bản của mỗi thư viện: nâng một lần, mọi nơi cùng lên. Cái giá: một kho rất lớn cần công cụ build biết đồ thị phụ thuộc để chỉ build và chạy kiểm thử phần bị ảnh hưởng (Bazel của Google và Buck của Meta là hai công cụ như vậy), và cần cơ chế nói thư mục nào thuộc về ai, vì ai cũng nhìn thấy mọi thứ.

**Mỗi dịch vụ một kho.** Ranh giới của kho trùng ranh giới của dịch vụ, nên quyền truy cập, cấu hình build và lịch phát hành đặt riêng cho từng kho. Mỗi đội chọn lúc nâng phiên bản thư viện theo lịch của mình. Cái giá: khi thay đổi phải chạm nhiều dịch vụ thì mỗi kho cần một thay đổi riêng, và phải phối hợp thứ tự (đổi bên cung cấp, phát hành, rồi từng bên dùng nâng phiên bản). Trong lúc đó, các dịch vụ có thể cùng chạy những phiên bản khác nhau của một thư viện.

## Tính thử: đổi một hàm dùng chung cho ba dịch vụ

Giả sử một thư viện nội bộ đổi chữ ký hàm, và ba dịch vụ A, B, C đều gọi hàm đó.

| | Một kho | Ba kho dịch vụ + một kho thư viện |
|---|---|---|
| Số thay đổi phải viết và xét duyệt | 1 | 4 (thư viện, rồi A, B, C) |
| Thứ tự bắt buộc | Không (cùng một commit) | Thư viện phát hành trước, các bên dùng nâng sau |
| Có lúc hệ thống ở trạng thái lẫn lộn | Không | Có, đến khi A, B, C đều nâng xong |

Đây là phép đếm theo lập luận, không phải đo ở một công ty thật. Nó cũng không nói "một kho tốt hơn": bảng chỉ ra rằng đổi chung là việc mà một kho làm rẻ hơn, còn việc mà nhiều kho làm rẻ hơn (để một đội đổi và phát hành mà không chờ ai) không nằm trong bảng.

## Giới hạn cần nhớ

Bài báo của hai kỹ sư Google về việc dồn mã vào một kho cũng nói thẳng cái giá: phải đầu tư công cụ riêng, và kho lớn khiến việc tìm mã, giữ mã khỏe mạnh khó hơn. Mức đầu tư đó hợp lý với công ty làm công cụ của riêng mình, không mặc nhiên hợp với đội nhỏ. Công cụ cũng không khóa bạn vào một lựa chọn: Bazel vẫn dùng được cho nhiều kho. Và "một kho" khác với "một khối": các dịch vụ trong một kho vẫn có thể triển khai riêng.

## Nhìn hình trả lời

Một đội sáu người có hai dịch vụ, hiếm khi đổi chung, và chỉ dùng công cụ build có sẵn của ngôn ngữ. Nên chọn một kho hay hai kho?

<details>
<summary>Xem đáp án</summary>

Hai kho thường đủ: cái lợi lớn nhất của một kho (đổi chung trong một commit) hiếm khi cần tới, trong khi cái giá của nó (công cụ build theo đồ thị phụ thuộc, quản lý sở hữu thư mục) có thật. Nếu sau này hai dịch vụ bắt đầu đổi cùng nhau liên tục, đó là tín hiệu để xem lại, và gộp kho là việc làm được.
Đây là suy luận của người biên soạn, không phải kết quả đo.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn so sánh hai cách theo từng mặt (cấu trúc thư mục, phụ thuộc, chuẩn kiểm duyệt, công cụ) và nêu tên các công ty. Bài này không lặp lại danh sách công ty; nó chỉ giữ hai trục có thể tính được, là số thay đổi cho một đổi chung và việc ai quyết định lúc nâng phiên bản. Những điều về Google lấy từ bài báo của chính Google, chưa đọc lại trong phiên viết.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/monorepo-vs.md): chủ đề và tên các công cụ build. Bảng đếm và đáp án là của người biên soạn.
- [Potvin, Levenberg — Why Google Stores Billions of Lines of Code in a Single Repository (Communications of the ACM, 2016)](https://dl.acm.org/doi/10.1145/2854146): lợi ích và cái giá của một kho ở Google. Kiến thức chung, chưa mở lại trong phiên viết.
- [Tài liệu Bazel](https://bazel.build/): công cụ build dựa trên đồ thị phụ thuộc. Kiến thức chung, chưa mở lại trong phiên viết.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.
