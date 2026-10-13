# Hệ thống thanh toán: tiền đi qua những bước nào?

**Bấm “Mua” chỉ là dấu hiệu bắt đầu.** Sau đó là một chuỗi bước ghi nhận, gọi nhà cung cấp thanh toán, cập nhật số dư và đối soát; mỗi bước đều phải để lại dấu vết để sau này kiểm chứng được.

![Sáu thẻ dọc: người mua bấm Mua và tạo sự kiện thanh toán; dịch vụ thanh toán ghi sự kiện và tách thành các lệnh thanh toán; bộ thực thi lưu lệnh rồi gọi nhà cung cấp thanh toán PSP; ví người bán được cập nhật số tiền; sổ cái ghi thêm bản ghi mới; mỗi đêm đối soát với tệp quyết toán của PSP hoặc ngân hàng. Chú thích: mỗi bước lưu dấu vết, đối soát bắt chỗ lệch.](../../diagrams/sd-12-010-main.svg)

## Đọc hình

**1–2.** Bấm “Mua” tạo một **sự kiện thanh toán** gửi tới dịch vụ thanh toán, nơi lưu nó lại. Một giỏ hàng có thể gồm nhiều người bán, nên sự kiện được tách thành nhiều **lệnh thanh toán**, mỗi lệnh một người bán.

**3.** Bộ thực thi lưu lệnh rồi gọi **PSP** (nhà cung cấp dịch vụ thanh toán) để trừ thẻ.

**4–5.** Khi PSP báo thành công, dịch vụ thanh toán cập nhật **ví** của người bán và ghi vào **sổ cái**: ví cho biết số dư hiện tại, sổ cái giữ lịch sử.

**6.** Mỗi đêm PSP hoặc ngân hàng gửi **tệp quyết toán**; hệ thống đối chiếu với sổ sách của mình để tìm chỗ lệch.

## Giới hạn cần nhớ

Gọi PSP qua mạng có thể hết thời gian chờ mà ta không biết thẻ đã bị trừ hay chưa. Gửi lại mù quáng có thể trừ khách hai lần. Mỗi lệnh cần **khóa chống trùng** (idempotency key) và quy trình tra lại trạng thái trước khi thử lại.

## Nhìn hình trả lời

Lệnh gọi PSP bị hết thời gian chờ. Nên gửi lại ngay, hay làm gì trước?

<details>
<summary>Xem đáp án</summary>

Không gửi lại mù quáng. Gửi lại cùng khóa chống trùng, hoặc tra trạng thái của lệnh đó ở PSP; nếu PSP đã xử lý thì không trừ lần hai.

</details>

<details>
<summary>Xem sâu hơn: sổ cái, ví, trạng thái và đối soát</summary>

- **Sổ cái chỉ thêm:** thường chỉ ghi thêm bản ghi mới và ghi kép (mỗi giao dịch có bút toán đối ứng). Sai sót được sửa bằng bút toán điều chỉnh, không xóa bản ghi cũ.
- **Ví khác sổ cái:** ví là số dư hiện tại để dùng nhanh; sổ cái là lịch sử đầy đủ để kiểm toán và dựng lại số dư.
- **Trạng thái:** mỗi lệnh đi qua các trạng thái (mới, đang xử lý, thành công, thất bại) và chỉ chuyển theo quy tắc.
- **Đối soát:** tệp quyết toán liệt kê giao dịch trong ngày; so với sổ nội bộ để tìm giao dịch thiếu, thừa hoặc lệch số tiền.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/payment-system.md): luồng sự kiện thanh toán, lệnh thanh toán, ví, sổ cái và tệp quyết toán.
- [Stripe — Idempotent requests](https://docs.stripe.com/api/idempotent_requests): khóa chống trùng khi thử lại yêu cầu.
- [IETF — Idempotency-Key HTTP header (bản nháp)](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/): đề xuất chuẩn hóa khóa chống trùng.
- [Wikipedia — Double-entry bookkeeping](https://en.wikipedia.org/wiki/Double-entry_bookkeeping): ghi sổ kép, bút toán đối ứng.

Đã đọc bài nguồn ngày 2026-10-13. Các tài liệu chính thức ở trên là nơi review kỹ thuật cần đối chiếu: trong đợt viết này chúng chưa được mở, nên các tuyên bố kỹ thuật chưa được xem là đã kiểm chứng. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-12-010.json).
