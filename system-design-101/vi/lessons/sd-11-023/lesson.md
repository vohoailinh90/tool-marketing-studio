# Bộ phiên bản: dựng lại hôm nay cũng ra đúng kết quả của hôm qua

**Một gói phần mềm chạy được hôm nay chưa chắc dựng lại được y như cũ vào tuần sau, nếu mỗi lần dựng lại lấy "bản mới nhất" của các thư viện nó dùng.** Hệ thống dựng của Amazon, tên Brazil, giải việc này bằng một "bộ phiên bản" (version set): một danh sách phiên bản đã chốt cho riêng một dịch vụ. Bài này lấy ý tưởng đó, thử nó trên một mô hình nhỏ, và nói rõ chỗ bài không kiểm chứng được.

![Hai khung. Khung một, bốn bước dựng một gói phần mềm: khai báo phụ thuộc, chọn một bộ phiên bản, dựng cục bộ hoặc từ xa, ra sản phẩm có phiên bản. Khung hai, thử nghiệm nhỏ: dựng theo phiên bản mới nhất thì sau khi thư viện B ra bản 2.0 kết quả dựng đổi và hỏng; dựng theo bộ phiên bản đã chụp thì kết quả giữ nguyên.](../../diagrams/sd-11-023-main.svg)

## Từ viết tắt

- **DAG** (Directed Acyclic Graph) — đồ thị có hướng không chu trình: mạng các nút nối nhau bằng mũi tên, đi theo mũi tên không bao giờ quay lại chỗ cũ; ở đây là sơ đồ "gói nào cần gói nào".

## Đọc hình

**Bốn bước (khung một).** Người viết mã khai báo trong một tệp cấu hình ngắn gói cần những gói nào và ràng buộc phiên bản (ngôn ngữ, phiên bản, phụ thuộc, cách xử lý xung đột). Công cụ dựng đọc khai báo đó như một DAG của các phụ thuộc, lấy các gói từ bộ phiên bản của dịch vụ, rồi gọi công cụ dựng riêng của ngôn ngữ để ra sản phẩm. Theo bài nguồn, ngoài dựng cục bộ còn có một dịch vụ dựng từ xa (chọn bộ phiên bản rồi dựng, bằng tay hoặc tự động khi có commit mới), mỗi lần dựng được chụp lại và sản phẩm được đánh phiên bản.

**Bộ phiên bản là gì.** Là tập các phiên bản gói đã chốt, như một "không gian riêng" của dịch vụ: khi thêm một phụ thuộc mới, nó cũng phải được đưa vào không gian riêng đó. Bài nguồn nói thêm một bộ mặc định tên "live" là không gian chung nơi ai cũng đưa lên phiên bản nào tùy ý. Hai tên gọi và cách vận hành chi tiết đó là mô tả của nguồn; Brazil là công cụ nội bộ của Amazon và bài chưa tìm được tài liệu công khai nào để đối chiếu.

**Ý tưởng chung ngoài Amazon.** Chốt phiên bản chính xác của mọi phụ thuộc, kể cả phụ thuộc gián tiếp, là thứ nhiều công cụ công khai làm theo cách của chúng: tệp khóa của npm, tệp tổng kiểm của Go, tệp khóa của Cargo, tệp khóa của Bazel. Điểm chung: dựng lại đọc danh sách đã chốt thay vì tự chọn lại.

## Thử: "bản mới nhất" so với bộ đã chụp

Ngày 2026-10-19, một chương trình Python nhỏ, không có mạng. Gói A cần gói B với ràng buộc "bản nhỏ hơn 2". Ngày thứ nhất B có bản 1.0 và 1.1. Hai cách dựng:

| Ngày | Dựng theo bản mới nhất | Dựng theo bộ đã chụp ở ngày 1 |
|---|---|---|
| Ngày 1 | A 1.0 + B 1.1, tương thích | A 1.0 + B 1.1, tương thích |
| Ngày 2, sau khi B ra 2.0 | A 1.0 + B 2.0, **vi phạm ràng buộc** | A 1.0 + B 1.1, tương thích |

Mã của A không đổi một dòng giữa hai ngày; chỉ có "bản mới nhất" đổi, và với nó, dựng lại hôm sau cho ra thứ khác hôm trước. Bộ đã chụp thì không phụ thuộc việc ai đó đưa bản mới lên.

## Giới hạn cần nhớ

Mô hình chỉ có hai gói và một ràng buộc, nên không nói gì về xung đột phiên bản phức tạp (hai gói cần hai phiên bản chính khác nhau của một gói thứ ba) hay quy mô một công ty. Chốt phiên bản cũng có cái giá riêng: bộ đã chụp không tự nhận bản vá bảo mật, nên cần một việc có chủ ý là cập nhật nó định kỳ. Mọi điều về Brazil lấy từ bài nguồn và chưa đối chiếu được.

## Nhìn hình trả lời

Hai dịch vụ cùng dùng thư viện B. Dịch vụ X muốn nâng B lên 2.0 ngay, dịch vụ Y chưa sẵn sàng. Nếu mỗi dịch vụ có bộ phiên bản riêng, chuyện này có làm được không?

<details>
<summary>Xem đáp án</summary>

Làm được: X cập nhật bộ phiên bản của mình lên B 2.0 và dựng lại, còn bộ của Y vẫn giữ B 1.1 cho tới khi Y quyết định nâng. Cái giá là hai dịch vụ chạy hai phiên bản của B một thời gian, như bài về một kho hay nhiều kho đã nói.
Đây là suy luận của người biên soạn từ mô hình trên.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn mô tả Brazil: tệp cấu hình dựng, bộ phiên bản riêng và bộ "live" chung, dịch vụ dựng từ xa trên vài loại máy. Bài này giữ phần ý tưởng (bộ phiên bản) và bỏ chi tiết loại máy, rồi thêm một thử nghiệm riêng để thấy tác dụng. Các ví dụ công cụ công khai (tệp khóa) là kiến thức chung của người biên soạn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-amazon-build-system-work.md): mô tả Brazil, bộ phiên bản, dịch vụ dựng từ xa. Thử nghiệm và đáp án là của người biên soạn.
- [Go — Modules Reference](https://go.dev/ref/mod): chốt phiên bản phụ thuộc trong công cụ công khai. Kiến thức chung, chưa mở lại trong phiên viết.
- [npm — package-lock.json](https://docs.npmjs.com/cli/configuring-npm/package-lock-json): tệp khóa phụ thuộc. Kiến thức chung, chưa mở lại trong phiên viết.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.
