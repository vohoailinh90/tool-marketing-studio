# Ứng dụng mười hai yếu tố: mười hai quy tắc gom thành ba nhóm

**Mười hai yếu tố là mười hai quy tắc để xây ứng dụng chạy tốt trên đám mây: dễ dựng, dễ thay thế, dễ nhân bản. Đứng riêng thì mỗi quy tắc dễ thành khẩu hiệu; gom theo việc nó giải, chúng thành ba nhóm.** Bài này gom lại, thử một quy tắc trong nhóm hay bị phá nhất, và nói chỗ bộ quy tắc cũ đi.

![Ba khung, mỗi khung bốn quy tắc của ứng dụng mười hai yếu tố. Khung một: một mã nguồn, khai báo phụ thuộc, cấu hình trong môi trường, dịch vụ phụ trợ gắn vào. Khung hai: tách dựng, phát hành, chạy; tiến trình không giữ trạng thái; mở cổng mạng; mở rộng bằng thêm tiến trình. Khung ba: tiến trình dễ bỏ, môi trường phát triển giống chạy thật, nhật ký là dòng sự kiện, việc quản trị chạy một lần.](../../diagrams/sd-11-027-main.svg)

## Từ viết tắt

- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: giao thức ứng dụng web dùng để nhận yêu cầu qua một cổng mạng (quy tắc về mở cổng nói tới nó).

## Đọc hình

**Nhóm một: mã, phụ thuộc, cấu hình (1 đến 4).** Cùng nhìn vào "cái gì đi cùng ứng dụng". *Codebase*: một mã nguồn được quản lý phiên bản, sinh ra nhiều bản triển khai (kiểm thử, thật). *Dependencies*: khai báo đầy đủ và chính xác mọi phụ thuộc, và cách ly chúng, để không có gì "lọt vào" từ máy xung quanh. *Config*: mọi thứ khác nhau giữa các bản triển khai (địa chỉ cơ sở dữ liệu, khóa) tách hẳn khỏi mã, và đặt trong biến môi trường. *Backing services*: cơ sở dữ liệu, hàng đợi, dịch vụ gửi thư là tài nguyên gắn vào; đổi cái này sang cái khác chỉ là đổi cấu hình, không đổi mã.

**Nhóm hai: dựng và chạy (5 đến 8).** Cùng nhìn vào "ứng dụng chạy thế nào". *Build, release, run*: dựng ra gói, ghép gói với cấu hình thành bản phát hành, rồi chạy; ba giai đoạn tách bạch. *Processes*: ứng dụng chạy thành một hay nhiều tiến trình không giữ trạng thái, mọi thứ cần bền nằm trong dịch vụ phụ trợ. *Port binding*: ứng dụng tự đủ, tự mở HTTP ra một cổng mạng, không nhờ máy chủ web nào được cắm vào. *Concurrency*: muốn xử lý nhiều hơn thì chạy thêm tiến trình.

**Nhóm ba: vận hành (9 đến 12).** Cùng nhìn vào "ứng dụng sống và chết thế nào". *Disposability*: khởi động nhanh, nhận tín hiệu dừng thì tắt êm, để thay thế tiến trình bất cứ lúc nào. *Dev/prod parity*: giữ môi trường phát triển, kiểm thử và thật gần nhau, về thời gian, người làm và công cụ. *Logs*: coi nhật ký là dòng sự kiện ra đầu ra chuẩn; môi trường chạy lo thu gom. *Admin processes*: việc quản trị như di chuyển cơ sở dữ liệu chạy như tiến trình một lần, cùng mã, cùng cấu hình.

## Thử: vì sao "tiến trình không giữ trạng thái"

Ngày 2026-10-19, một chương trình Python nhỏ: một bộ chia tải xoay vòng giữa hai tiến trình, người dùng thêm 10 món vào giỏ qua 10 yêu cầu.

| Giỏ hàng giữ ở đâu | Người dùng thấy |
|---|---|
| Trong bộ nhớ của từng tiến trình | 5 món ở tiến trình này, 5 món ở tiến trình kia; mỗi lần hỏi thấy một giỏ khác nhau |
| Trong một dịch vụ phụ trợ dùng chung | 10 món, bất kể tiến trình nào trả lời |

Đó là lý do quy tắc 6 đi cùng quy tắc 8: muốn thêm tiến trình để chịu tải, hay thay tiến trình bị hỏng (quy tắc 9), tiến trình phải thay thế được cho nhau, nên dữ liệu bền không được nằm trong một tiến trình.

## Giới hạn cần nhớ

Bộ quy tắc ra đời cho ứng dụng web chạy theo kiểu dịch vụ; không phải mọi ứng dụng (một công cụ dòng lệnh, một trò chơi, một hệ có trạng thái như cơ sở dữ liệu) hợp mọi quy tắc. Mười hai yếu tố cũng nói "cái gì", ít nói "làm thế nào" với đủ công cụ: bài chưa đối chiếu với bản phát biểu mới của dự án (đã được mở nguồn), mà chỉ với phần mô tả chính. Mô phỏng chỉ có hai tiến trình và một bộ chia tải xoay vòng.

## Nhìn hình trả lời

Một ứng dụng ghi tệp tải lên của người dùng vào ổ đĩa của máy đang chạy, rồi chạy thêm một bản thứ hai để chịu tải. Quy tắc nào bị phá, và sửa thế nào?

<details>
<summary>Xem đáp án</summary>

Quy tắc 6 (tiến trình không giữ trạng thái): tệp nằm trên ổ của một máy nên bản thứ hai không thấy, và khi máy bị thay thì tệp mất. Sửa bằng cách đưa tệp vào một dịch vụ phụ trợ dùng chung (kho đối tượng, ổ mạng), quy tắc 4, để mọi tiến trình đọc cùng một chỗ.
Đây là suy luận của người biên soạn từ hai quy tắc.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn liệt kê mười hai yếu tố theo số thứ tự, mỗi yếu tố một dòng. Bài này giữ tên mười hai yếu tố nhưng gom thành ba nhóm theo vấn đề chúng giải, và thêm một thử nghiệm riêng. Phần giải thích viết lại từ trang chính thức của dự án (đã đọc bản trong kho, commit ghi ở nguồn đối chiếu).

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/the-12-factor-app.md): mười hai yếu tố. Cách gom nhóm, thử nghiệm và đáp án là của người biên soạn.
- [The Twelve-Factor App — kho nội dung tại commit 3ad5a5f](https://github.com/twelve-factor/twelve-factor/tree/3ad5a5f36312cc8ad876abae1bd691acd790d4d1/content): mười hai tệp mô tả từng yếu tố. Đã đọc tiêu đề và các đoạn mở đầu của từng tệp.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.
