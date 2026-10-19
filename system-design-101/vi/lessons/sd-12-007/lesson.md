# Phát trực tiếp: video được cắt thành đoạn vài giây rồi đẩy ra ngay

**Phát trực tiếp khác phát video thường ở chỗ không có tệp hoàn chỉnh: video được thu, nén, cắt thành những đoạn dài vài giây rồi đẩy ra người xem ngay khi từng đoạn xong, nên độ trễ chỉ vài giây.**
Độ dài của đoạn là núm vặn chính: đoạn càng ngắn thì độ trễ càng thấp, nhưng số tệp càng nhiều.

![Ba khung. Khung một, từ máy quay tới máy chủ: thu hình và tiếng, mã hóa và nén, cắt thành đoạn ngắn, tạo nhiều mức bitrate. Khung hai, từ máy chủ tới người xem: đẩy ra máy chủ biên của CDN, máy của người xem giải mã và phát, lưu bản ghi để xem lại. Khung ba, ba giao thức thường gặp: RTMP đẩy từ phía người phát, HLS và DASH chia video thành đoạn tải qua HTTP.](../../diagrams/sd-12-007-main.svg)

## Từ viết tắt

- **CDN** (Content Delivery Network) — mạng phân phối nội dung: nhiều máy chủ đặt gần người xem, giữ bản sao video để người xem tải từ máy gần nhất.
- **RTMP** (Real-Time Messaging Protocol) — giao thức nhắn tin thời gian thực: giao thức dùng để đẩy luồng video từ phía người phát lên máy chủ.
- **HLS** (HTTP Live Streaming) — phát trực tiếp qua HTTP: cách chia video thành đoạn nhỏ kèm một danh sách đoạn (playlist).
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: giao thức web mà trình phát dùng để tải từng đoạn video.
- **DASH** (Dynamic Adaptive Streaming over HTTP) — phát thích ứng động qua HTTP: chuẩn quốc tế cho cách chia đoạn tương tự HLS.
- **RFC** (Request For Comments) — tài liệu xin ý kiến: loạt văn bản kỹ thuật của Internet; RFC 8216 mô tả HLS.

## Đọc hình

**Từ máy quay tới máy chủ.** Máy quay và micro thu hình và tiếng; dữ liệu thô quá lớn nên được nén và mã hóa, thường bằng H.264. Video đã mã hóa được cắt thành các đoạn ngắn; đoạn nào xong là đẩy đi được, không phải đợi hết buổi phát. Máy chủ phát cần phục vụ nhiều thiết bị và mạng khác nhau, nên cùng một video được mã hóa thành nhiều mức bitrate, cách này gọi là phát thích ứng (Adaptive Bitrate Streaming): người xem mạng yếu lấy mức thấp, mạng khỏe lấy mức cao.

**Từ máy chủ tới người xem.** Các đoạn được đẩy ra máy chủ biên của CDN, và hàng triệu người xem tải từ máy chủ ở gần mình thay vì từ một nơi duy nhất. Máy của người xem giải nén, giải mã rồi phát. Nếu cần xem lại, các đoạn được lưu vào kho để người xem yêu cầu sau.

**Giao thức.** RTMP thường dùng ở chặng đầu, từ người phát lên máy chủ. HLS và DASH thường dùng ở chặng cuối, tới người xem; cả hai chia video thành đoạn tải qua HTTP và hỗ trợ phát thích ứng.

## Thử nghiệm với ffmpeg

Ngày 2026-10-19, người biên soạn dùng ffmpeg 6.1.1 (bộ mã hóa x264) tạo video thử 36 giây, 640x360, 30 hình mỗi giây, khoảng 800 kbit/s, rồi xuất HLS với hai độ dài đoạn. Mỗi đoạn bắt đầu bằng một khung hình khóa (cứ 2 hoặc 6 giây đặt một khung khóa) để cắt đúng chỗ.

| Độ dài đoạn | Số đoạn | Kích thước trung bình mỗi đoạn |
|---|---|---|
| 2 giây | 18 | 230.874 byte |
| 6 giây | 6 | 689.302 byte |

Danh sách đoạn là một tệp văn bản: dòng `#EXT-X-TARGETDURATION` ghi độ dài đoạn lớn nhất, mỗi đoạn có một dòng `#EXTINF:2.000000,` rồi tên tệp. Thử thêm ba mức bitrate cho đoạn video 12 giây: mức 300 kbit/s ra 523.204 byte, mức 800 kbit/s ra 1.344.952 byte, mức 2000 kbit/s ra 3.288.308 byte; mỗi mức là một lần mã hóa riêng, nên ba mức tốn gấp ba công mã hóa. Xuất DASH cũng ra các đoạn (`chunk-stream0-00001.m4s`) cùng một tệp mô tả (`dash.mpd`) có mẫu đặt tên đoạn.

Về độ trễ, người biên soạn nhớ rằng chuẩn HLS (RFC 8216, mục 6.3.3) khuyên máy phát không chọn đoạn bắt đầu cách cuối danh sách chưa tới ba lần độ dài đoạn; nếu đúng thì đoạn 2 giây cho độ trễ tối thiểu cỡ 6 giây và đoạn 6 giây cỡ 18 giây. Con số này là suy ra từ trí nhớ, chưa đối chiếu với văn bản chuẩn.

## Giới hạn cần nhớ

Bài nguồn nói các thiết bị Apple chỉ nhận HLS và DASH không hỗ trợ thiết bị Apple. Đó là cách nói đơn giản hóa; bài này không đối chiếu và không dựa vào nó. Thử nghiệm chỉ đo kích thước và số đoạn của video thử, không đo độ trễ thật, không chạy máy chủ biên hay trình phát, và hình thử là hình tổng hợp nên kích thước đoạn không phản ánh video thật. Chuyện video họp trực tuyến dùng giao thức khác để có độ trễ thấp hơn, bài nguồn có nhắc, bài này không đi sâu.

## Nhìn hình trả lời

Một nền tảng muốn giảm độ trễ nên đổi độ dài đoạn từ 6 giây xuống 2 giây. Thử nghiệm cho thấy cái giá nào?

<details>
<summary>Xem đáp án</summary>

Số đoạn gấp ba (18 đoạn thay vì 6 cho 36 giây), nên số tệp, số danh sách cập nhật và số yêu cầu của người xem đều nhiều hơn. Và mỗi đoạn phải bắt đầu ở khung hình khóa, nên khung khóa dày hơn, thường tốn thêm dung lượng cho cùng chất lượng.
Phần về khung hình khóa tốn dung lượng là kiến thức chung của người biên soạn, thử nghiệm trên không đo.

</details>

<details>
<summary>Xem sâu hơn: điều đã bổ sung so với bài nguồn</summary>

Bài nguồn có tám bước đánh số và một danh sách giao thức. Bài này gom bước thành hai chặng, bỏ qua câu về thiết bị Apple, và thêm thử nghiệm với ffmpeg về độ dài đoạn và các mức bitrate.

</details>

<details>
<summary>Xem chương trình thử nghiệm</summary>

Các lệnh dưới đây (bash và `ffmpeg` 6.1.1 có `libx264`) đã tạo ra các con số về số đoạn và kích thước. Số đoạn và kích thước trung bình của đoạn 2 giây và 6 giây chạy lại ra đúng như trong bài. Kích thước ba bản bitrate có thể lệch vài nghìn byte giữa các lần chạy vì bộ mã hóa chạy nhiều luồng, nhưng thứ tự và tỷ lệ giữa ba bản không đổi. Chạy trong một thư mục trống.

```bash
# ffmpeg 6.1.1 với libx264; video thử nghiệm 640x360, 30 hình/giây, kèm âm thanh sin
for seg in 2 6; do
  ffmpeg -hide_banner -loglevel error -y -f lavfi -i testsrc2=size=640x360:rate=30 -f lavfi -i sine=frequency=440:sample_rate=44100 \
    -t 36 -c:v libx264 -preset veryfast -b:v 800k -g $((30*seg)) -keyint_min $((30*seg)) -sc_threshold 0 -c:a aac -b:a 64k \
    -f hls -hls_time $seg -hls_playlist_type vod -hls_segment_filename "s${seg}_%03d.ts" "p${seg}.m3u8"
  echo "đoạn $seg giây: $(ls s${seg}_*.ts | wc -l) đoạn"
  ls -l s${seg}_*.ts | awk '{s+=$5; n++} END{print "trung bình", s/n, "byte"}'
done
# thang bitrate: ba bản của cùng 12 giây video
for br in 300 800 2000; do
  ffmpeg -hide_banner -loglevel error -y -f lavfi -i testsrc2=size=640x360:rate=30 -t 12 -c:v libx264 -preset veryfast \
    -b:v ${br}k -maxrate ${br}k -bufsize $((br*2))k -an -g 60 -keyint_min 60 -sc_threshold 0 \
    -f hls -hls_time 2 -hls_playlist_type vod -hls_segment_filename "r${br}_%03d.ts" "r${br}.m3u8"
  echo "bản ${br}k: $(cat r${br}_*.ts | wc -c) byte cho 12 giây"
done
# cùng nguồn xuất theo chuẩn có tệp mô tả (mpd) và các đoạn .m4s
ffmpeg -hide_banner -loglevel error -y -f lavfi -i testsrc2=size=640x360:rate=30 -t 12 -c:v libx264 -preset veryfast \
  -b:v 800k -g 60 -keyint_min 60 -sc_threshold 0 -an -f dash -seg_duration 2 dash.mpd
```

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/live-streaming-explained.md): các bước từ thu hình tới phát, ba giao thức RTMP, HLS, DASH.
- Thử nghiệm của người biên soạn với ffmpeg 6.1.1 (ngày 2026-10-19): bảng đoạn và các mức bitrate.
- RFC 8216 (HTTP Live Streaming), mục 6.3.3, về khoảng cách tới cuối danh sách (nhớ lại từ chuẩn; chưa mở được trang trong phiên này).

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.
