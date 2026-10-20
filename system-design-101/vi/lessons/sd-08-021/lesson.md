# MVC, MVP, MVVM, VIPER: cùng một nút bấm, bốn cách chia việc, và luật nằm ở đâu

**Bài nguồn là một hình và năm gạch đầu dòng: mẫu nào cũng có khung nhìn và (hầu hết) có mô hình, còn "bộ điều khiển", "bộ trình bày" hay "mô hình khung nhìn" là người dịch đứng giữa. Bài này giữ đúng ý đó, đối chiếu MVC với tài liệu của Apple và MVVM với tài liệu của Microsoft, rồi viết cùng một màn hình nhỏ theo bốn mẫu để thấy cái luật "nút Trừ tắt khi bằng 0" nằm ở đâu, và muốn thử nó thì phải dựng những gì.**

![Ba khung. Khung một, bốn mẫu chia việc giữa khung nhìn và mô hình: MVC, bộ điều khiển nối khung nhìn với mô hình; MVP, bộ trình bày giữ luật và khung nhìn chỉ hiện; MVVM, mô hình khung nhìn giữ luật và khung nhìn chỉ buộc vào; VIPER, thêm bộ tương tác, thực thể và bộ điều hướng. Khung hai, thử trên một nút bấm: mẫu giữa biết hai trường của khung nhìn ở MVC, một hàm ở MVP và VIPER, không gì ở MVVM; thử luật nút Trừ, MVVM không cần khung nhìn giả; thêm nút Đặt lại sửa 8 đến 11 dòng ở cả bốn mẫu. Khung ba, đồ chơi nhỏ, MVP và VIPER chưa có tài liệu độc lập để đối chiếu.](../../diagrams/sd-08-021-main.svg)

## Từ viết tắt

- **MVC** (Model View Controller) — mô hình, khung nhìn, bộ điều khiển: ba vai trong một ứng dụng; bộ điều khiển là người trung gian giữa khung nhìn và mô hình.
- **MVP** (Model View Presenter) — mô hình, khung nhìn, bộ trình bày: bộ trình bày là người dịch, khung nhìn càng ít việc càng tốt.
- **MVVM** (Model View ViewModel) — mô hình, khung nhìn, mô hình khung nhìn: người dịch là mô hình khung nhìn, khung nhìn chỉ buộc (bind) vào các thuộc tính của nó.
- **VIPER** (View Interactor Presenter Entity Router) — khung nhìn, bộ tương tác, bộ trình bày, thực thể, bộ điều hướng: năm vai; thực thể là dữ liệu thuần, bộ tương tác giữ luật nghiệp vụ.

## Đọc hình

| Mẫu | Người dịch giữa khung nhìn và mô hình | Theo nguồn và tài liệu | Phép thử trong bài |
|---|---|---|---|
| MVC | Bộ điều khiển | Nguồn: mẫu cũ nhất, gần 50 năm. Apple: bộ điều khiển là trung gian, khung nhìn biết thay đổi của mô hình qua nó | bộ điều khiển cầm các trường của khung nhìn |
| MVP | Bộ trình bày | Nguồn: một người dịch như bộ điều khiển; chưa có tài liệu độc lập để đối chiếu | bộ trình bày chỉ gọi một hàm `show` |
| MVVM | Mô hình khung nhìn | Microsoft: khung nhìn biết mô hình khung nhìn, nó biết mô hình, không ngược lại; thử mô hình khung nhìn không cần khung nhìn | mô hình khung nhìn không nhắc tới khung nhìn |
| VIPER | Bộ trình bày và bộ tương tác ("thực thể" thay cho mô hình) | Nguồn: thực thể thay cho mô hình; chưa có tài liệu độc lập để đối chiếu | năm lớp, luật nghiệp vụ tách khỏi luật hiển thị |

Cả bốn đều có chung một khung nhìn lo hiển thị và nhận thao tác, và chung một chỗ chứa dữ liệu nghiệp vụ. Nguồn nói thẳng lý do các biến thể ra đời: người dịch viết rất khó giữ gọn, nên người ta đề xuất thêm cách chia. Nguồn còn nhắc `MVVM-C` ở câu hỏi mở đầu nhưng không giải thích nó, nên bài này không bàn.

## Thử: một màn hình, bốn cách chia

Ngày 2026-10-19, Python 3.13.16. Cùng một màn hình đếm: nút Cộng, nút Trừ, dòng chữ "Count: n", và luật nút Trừ chỉ bật khi n lớn hơn 0 (n không xuống dưới 0). Viết bốn lần, mỗi lần theo một mẫu, dài 18 đến 27 dòng, rồi đếm bằng chương trình (kết quả giống nhau ở cả ba lần chạy).

| Mẫu | Số lớp | Số dòng | Mẫu giữa biết gì về khung nhìn | Dựng gì để thử luật nút Trừ |
|---|---|---|---|---|
| MVC | 3 | 19 | hai trường: `text`, `minus_enabled` | mô hình, bộ điều khiển, và một khung nhìn giả có hai trường đó |
| MVP | 3 | 18 | một hàm: `show` | mô hình, bộ trình bày, và một khung nhìn giả có hàm `show` |
| MVVM | 3 | 21 | không gì (không nhắc tới khung nhìn) | mô hình, mô hình khung nhìn; không cần khung nhìn giả |
| VIPER | 5 | 27 | một hàm: `show` | thực thể, bộ tương tác, bộ trình bày, và một khung nhìn giả có hàm `show` |

Rồi thêm một nút Đặt lại (về 0, chỉ bật khi n lớn hơn 0) vào cả bốn và đếm phần phải sửa:

| Mẫu | Lớp phải sửa | Dòng thêm cộng dòng bỏ |
|---|---|---|
| MVC | 3 trên 3, và hàm dựng | 8 |
| MVP | 3 trên 3, và hàm dựng | 11 |
| MVVM | 3 trên 3, và hàm dựng | 8 |
| VIPER | 3 trên 5, và hàm dựng (thực thể không đổi) | 11 |

Đọc được hai điều. Một, thời gian từ lúc bấm tới lúc dòng chữ đổi chỉ cỡ 0,3 đến 0,8 micro giây ở cả bốn mẫu và đổi thứ tự giữa các lần chạy, nên không có gì để so về tốc độ. Hai, cái khác nhau là bề mặt giữa khung nhìn và phần còn lại: mẫu giữa của MVC phải biết tên các trường của khung nhìn, mẫu giữa của MVP và VIPER chỉ biết một hàm `show`, còn mô hình khung nhìn của MVVM không biết khung nhìn tồn tại, nên luật nút Trừ thử được mà không cần giả khung nhìn nào. Điều này khớp với lời khuyên của Microsoft: cho mô hình khung nhìn quyết định lệnh nào đang dùng được và buộc khung nhìn vào đó, đừng bật hay tắt phần tử giao diện trong mã của khung nhìn. VIPER tách luật "không xuống dưới 0" (bộ tương tác) khỏi luật "nút Trừ bật hay tắt" (bộ trình bày), nên thực thể không phải sửa khi thêm nút, nhưng đổi lại là 5 lớp thay vì 3.

## Giới hạn cần nhớ

Đây là đồ chơi 18 đến 27 dòng do người biên soạn tự viết, nên các con số đếm (số lớp, số dòng sửa) cho thấy hình dạng của sự đánh đổi chứ không nói gì về một ứng dụng thật với hàng chục màn hình, mạng và dữ liệu bất đồng bộ. Có nhiều cách viết mỗi mẫu; bản MVC ở đây theo mô tả của Apple (bộ điều khiển cập nhật khung nhìn), chưa thử dạng khung nhìn tự quan sát mô hình. Tài liệu Microsoft nói về MVVM trong một khung ứng dụng đa nền tảng cụ thể, và tài liệu Apple là bản đã được ghi là lưu trữ, "có thể không phản ánh cách làm hiện nay". MVP và VIPER chỉ được đối chiếu với nguồn: chưa đọc được tài liệu độc lập nào về hai mẫu này.

## Nhìn hình trả lời

Nhóm bạn muốn thử bằng chương trình luật "nút Trừ tắt khi bằng 0" mà không dựng giao diện thật. Theo bảng đo trên, ở mẫu nào bạn chẳng cần viết khung nhìn giả nào, và ở mẫu nào bạn phải dựng nhiều đối tượng nhất?

<details>
<summary>Xem đáp án</summary>

MVVM: mô hình khung nhìn không nhắc tới khung nhìn, nên chỉ cần dựng mô hình và mô hình khung nhìn rồi đọc `minus_enabled`. VIPER dựng nhiều nhất trong bốn mẫu (thực thể, bộ tương tác, bộ trình bày) và vẫn cần một khung nhìn giả có hàm `show`. Đó là cái giá của việc tách luật nghiệp vụ khỏi luật hiển thị, chứ không phải lỗi của mẫu.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một hình kèm năm gạch đầu dòng ngắn, không có ví dụ và không có số đo. Bài này giữ nguyên ý của năm gạch đó, thêm hai tài liệu độc lập cho MVC và MVVM, và thay "người dịch khó viết" bằng một màn hình đếm nhỏ viết bốn lần để thấy luật nằm ở đâu.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/mvc-mvp-mvvm-viper-patterns.md): năm gạch đầu dòng về bốn mẫu.
- [Apple — Model-View-Controller (Cocoa Core Competencies, tài liệu lưu trữ)](https://developer.apple.com/library/archive/documentation/General/Conceptual/DevPedia-CocoaCore/MVC.html): ba vai, bộ điều khiển là trung gian. Đọc ngày 2026-10-19.
- [Microsoft — Model-View-ViewModel (tài liệu kiến trúc ứng dụng đa nền tảng)](https://github.com/dotnet/docs/blob/main/docs/architecture/maui/mvvm.md): khung nhìn, mô hình khung nhìn, thử không cần khung nhìn, cách bật tắt phần tử giao diện. Đọc bản nhánh chính ngày 2026-10-19.

Đã đọc nguồn ngày 2026-10-19. Các phép thử là của người biên soạn.
Bài viết và hình được thiết kế độc lập.
