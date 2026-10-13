# Phát trực tiếp video hoạt động thế nào?

**Phát trực tiếp là gửi video đi khi nó vẫn đang được quay.** Người xem thấy hình sau một độ trễ từ vài giây tới vài chục giây, tùy cách thiết kế.

![Bảy thẻ dọc: quay hình và thu âm thanh; nén và mã hóa, hình bằng bộ mã hóa video như H.264 còn tiếng bằng bộ mã hóa âm thanh như AAC; gửi lên máy chủ bằng giao thức đưa vào như RTMP; tạo nhiều mức chất lượng cho cùng nội dung; cắt thành các đoạn dài vài giây; CDN đẩy đoạn tới máy chủ biên gần người xem; trình phát tải đoạn, chọn mức phù hợp, giải mã và phát. Chú thích: muốn xem lại thì lưu các đoạn vào kho.](../../diagrams/sd-12-007-main.svg)

## Đọc hình

**1–3. Từ máy người phát lên máy chủ.** Hình được nén bằng bộ mã hóa video như H.264, còn tiếng được mã hóa riêng bằng bộ mã hóa âm thanh như AAC (H.264 chỉ lo phần hình); nén như vậy làm dung lượng nhỏ đi nhiều. Hai luồng được ghép chung rồi gửi lên máy chủ bằng một giao thức đưa vào như RTMP.

**4–5. Chuẩn bị cho nhiều người xem.** Máy chủ tạo cùng nội dung ở nhiều mức chất lượng (bitrate) và cắt mỗi mức thành đoạn ngắn, mỗi đoạn vài giây.

**6–7. Tới người xem.** Các đoạn được đẩy tới máy chủ biên của CDN; trình phát ở máy người xem tải từng đoạn qua HTTP, giải mã và phát. Nó đo tốc độ tải để chuyển giữa các mức chất lượng: mạng yếu thì xuống mức thấp để khỏi bị đứng hình.

## Giới hạn cần nhớ

Độ trễ phụ thuộc độ dài đoạn và số đoạn trình phát đệm sẵn: đoạn dài thì ổn định hơn nhưng trễ hơn. Muốn trễ chỉ vài giây trở xuống cần biến thể độ trễ thấp (như Low-Latency HLS) hoặc giao thức khác như WebRTC, và phải đánh đổi bằng chi phí hoặc độ ổn định.

## Nhìn hình trả lời

Người xem mạng yếu bị đứng hình liên tục. Hệ thống đã chuẩn bị sẵn gì ở bước 4 để tránh điều đó?

<details>
<summary>Xem đáp án</summary>

Nhiều mức chất lượng cho cùng một nội dung. Trình phát có thể chuyển sang mức bitrate thấp hơn ở đoạn kế tiếp khi mạng chậm.

</details>

<details>
<summary>Xem sâu hơn: RTMP, HLS, DASH và WebRTC</summary>

- **RTMP** có gốc từ thời Flash; ngày nay thường còn dùng để **đưa** luồng từ phần mềm của người phát lên máy chủ, ít khi dùng để phát cho người xem.
- **HLS** (do Apple đề xuất) và **MPEG-DASH** là hai cách **phát** theo đoạn qua HTTP, đều hỗ trợ bitrate thích ứng. HLS được thiết bị Apple hỗ trợ sẵn; khả năng phát DASH phụ thuộc trình phát và thiết bị.
- **WebRTC** hướng tới độ trễ rất thấp, hợp với hội thoại hai chiều; mở rộng cho lượng người xem rất lớn khó và đắt hơn so với phát qua CDN.
- Muốn xem lại, lưu các đoạn (hoặc bản ghi hoàn chỉnh) vào kho để người xem lấy sau.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/live-streaming-explained.md): các bước từ camera tới người xem và các giao thức thường gặp.
- [RFC 8216 — HTTP Live Streaming](https://www.rfc-editor.org/rfc/rfc8216.html): phát theo đoạn qua HTTP và các mức chất lượng.
- [Apple — HTTP Live Streaming](https://developer.apple.com/streaming/): tài liệu của nhà đề xuất HLS.
- [DASH Industry Forum](https://dashif.org/): MPEG-DASH và hướng dẫn triển khai.
- [W3C — WebRTC](https://www.w3.org/TR/webrtc/): truyền thời gian thực độ trễ thấp.
- [ITU-T H.264 — tóm tắt](https://www.itu.int/dms_pubrec/itu-t/rec/h/T-REC-H.264-202408-I%21%21SUM-HTM-E.htm): H.264 là chuẩn mã hóa hình ảnh động (video).

Đã đọc bài nguồn ngày 2026-10-13. Các tài liệu chính thức ở trên là nơi review kỹ thuật cần đối chiếu: trong đợt viết này chúng chưa được mở, nên các tuyên bố kỹ thuật chưa được xem là đã kiểm chứng. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn. Trạng thái và giới hạn kiểm chứng lưu trong [metadata JSON](../../metadata/sd-12-007.json).
