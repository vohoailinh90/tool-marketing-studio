# SapFix của Meta: máy đề xuất bản sửa, người quyết định

**SapFix tự tìm ra thay đổi làm ứng dụng crash, tự viết vài bản vá, rồi dừng lại chờ người duyệt.** Bài nguồn tóm tắt một bài báo của Meta về công cụ này ở quy mô các ứng dụng Facebook.
Bài này đọc SapFix như một dây chuyền: phát hiện, đề xuất, kiểm thử, và chỗ con người vẫn đứng ở cuối.

![Ba khung xếp dọc. Phát hiện lỗi: lập trình viên gửi Diff để review, SapFix chọn ca kiểm thử từ Sapienz và chạy trên Diff, thấy crash do chính Diff gây ra, sinh vài bản vá ứng viên. Bốn loại bản sửa: theo mẫu, đột biến, hoàn tác toàn bộ, hoàn tác một phần. Người quyết định: chạy kiểm thử trên từng bản build đã vá, gửi một bản ứng viên đi review, người viết thay đổi gây crash duyệt và quyết định nhận hoặc bỏ. Khung cuối: 165 bản vá cho 57 crash trong đợt thử 90 ngày, trung vị 69 phút, sáu ứng dụng lớn.](../../diagrams/sd-02-005-main.svg)

## Từ viết tắt

- **CI** (Continuous Integration) — tích hợp liên tục: quy trình tự động kiểm tra mỗi thay đổi mã trước khi gộp vào mã chung.

## Đọc hình

**Phát hiện.** Lập trình viên gửi một thay đổi (Meta gọi là Diff) để review qua Phabricator, mà bài nguồn gọi là hệ thống CI của Facebook. Theo bài nguồn, SapFix lấy các ca kiểm thử phù hợp từ Sapienz, hệ thống tự thiết kế ca kiểm thử của Facebook, và chạy chúng trên Diff đó.

**Đề xuất.** Khi thấy một crash do Diff gây ra, SapFix thử sinh bản sửa theo bốn kiểu: theo mẫu, đột biến, hoàn tác toàn bộ, hoàn tác một phần. Nó chạy kiểm thử trên từng bản build đã vá để xem bản nào chạy được, giống thử từng mảnh ghép.

**Người quyết định.** SapFix chọn một bản vá ứng viên và gửi đi review qua Phabricator. Người duyệt chính là người đã viết thay đổi gây crash, vì họ hiểu ngữ cảnh nhất; vài kỹ sư khác cũng được theo dõi. Họ có thể nhận bản vá hoặc bỏ đi.

**Con số theo nguồn.** SapFix chạy trên sáu ứng dụng chính của Facebook, mỗi ứng dụng hàng chục triệu dòng mã. Trong đợt thử 90 ngày, nó sinh 165 bản vá cho 57 crash; thời gian trung vị từ lúc phát hiện lỗi tới lúc gửi bản sửa cho người duyệt là 69 phút.

## Giới hạn cần nhớ

Con số 165 bản vá là số bản *được sinh ra*, không phải số bản được chấp nhận; bài nguồn không nói bao nhiêu bản được nhận. Trung bình khoảng 2,9 bản vá cho mỗi crash (165 chia 57), đúng với cách SapFix đưa ra vài ứng viên rồi chọn. Mọi con số là theo bài nguồn; bài báo của Meta chưa được mở để đối chiếu. Cách bài nguồn chia việc giữa hai công cụ (SapFix chọn và chạy ca kiểm thử của Sapienz) cũng chưa được đối chiếu: có thể trong hệ thống thật, Sapienz là bên chạy kiểm thử và tìm ra crash, còn SapFix chỉ bắt đầu từ lúc có crash.
Hoàn tác là bản sửa an toàn nhất nhưng cũng bỏ luôn tính năng mới, nên người duyệt vẫn phải hiểu điều mình nhận.

## Nhìn hình thử trả lời

SapFix gửi cho bạn một bản vá kiểu "hoàn tác toàn bộ" cho thay đổi bạn vừa viết. Bản vá đã qua kiểm thử. Bạn có nên nhận ngay không?

<details>
<summary>Xem đáp án</summary>

Chưa chắc. Qua kiểm thử chỉ có nghĩa là crash đã biến mất trong các ca đã chạy. Hoàn tác toàn bộ cũng gỡ luôn tính năng bạn vừa thêm. Bạn là người hiểu ngữ cảnh nhất, nên việc của bạn là cân: nhận để chặn crash ngay rồi làm lại, hay bỏ và tự sửa đúng chỗ.

</details>

<details>
<summary>Xem sâu hơn: vì sao người duyệt là người viết thay đổi</summary>

Một công cụ tự sửa lỗi có thể đưa ra bản vá đúng về kỹ thuật nhưng sai về ý định. Đặt người viết thay đổi làm người duyệt chính giữ trách nhiệm ở đúng người biết thay đổi đó để làm gì, và biến SapFix thành người đề xuất chứ không phải người quyết định.
Đây là cách đọc của người biên soạn; bài nguồn chỉ nói người đó "thường có ngữ cảnh kỹ thuật tốt nhất".

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/fixing-bugs-automatically-at-meta-scale.md): các bước của SapFix, bốn loại bản sửa và số liệu đợt thử.

Đã đọc nguồn ngày 2026-10-19. Bài báo của Meta về SapFix chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.
