# YouTube và VCU: con chip riêng cho việc chuyển mã video

**Mỗi phút có hơn 500 giờ video được tải lên YouTube, và mỗi video phải được chuyển mã ra nhiều độ phân giải; theo bài nguồn, YouTube làm riêng một loại chip, VCU, cho việc này.**
Bài này đi theo đúng câu hỏi của bài nguồn: vì sao chuyển mã bằng phần mềm không còn đủ, và VCU được xếp vào trung tâm dữ liệu theo những lớp nào.

![Hai khung và một khung ghi nhớ. Khung một, vì sao cần chip riêng: mỗi video được chuyển mã ra nhiều bản, với ví dụ của nguồn là 720p cho điện thoại, 1080p cho máy tính xách tay, 4K cho màn hình lớn; lượng video tải lên tăng mạnh trong đại dịch; chuyển mã bằng phần mềm trở nên chậm và tốn. Khung hai, VCU xếp theo lớp: một cụm có nhiều máy chủ tăng tốc bằng VCU; mỗi máy chủ có nhiều khay tăng tốc; mỗi khay có nhiều thẻ VCU; mỗi thẻ có bộ mã hóa, bộ giải mã. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-02-012-main.svg)

## Từ viết tắt

- **VCU** (Video Coding Unit) — bộ chuyển mã video, bài nguồn gọi là Video transCoding Unit: chip YouTube làm riêng để giải mã và mã hóa lại video ở quy mô trung tâm dữ liệu.
- **GPU** (Graphics Processing Unit) — bộ xử lý đồ họa: chip chuyên cho tính toán đồ họa, cũng được dùng nhiều cho học máy.
- **TPU** (Tensor Processing Unit) — bộ xử lý tensor: chip Google làm riêng cho các phép tính của học máy.
- **COVID** (COronaVIrus Disease) — bệnh do virus corona; COVID-19 là đại dịch bắt đầu từ cuối năm 2019, khi nhiều người phải ở nhà.

## Đọc hình

**Vì sao cần chip riêng.** Theo bài nguồn, YouTube phải chuyển mã video gốc ra nhiều mức nén để hợp với từng thiết bị, với ví dụ: điện thoại (720p), máy tính xách tay (1080p), tivi độ phân giải cao (4K). Nói chính xác hơn, 720p, 1080p và 4K là độ phân giải, tức số điểm ảnh của mỗi khung hình; mức nén là chuyện khác, do tốc độ bit và chuẩn mã hóa quyết định. Cùng một độ phân giải có thể có nhiều bản với tốc độ bit khác nhau, trình phát tự chuyển giữa các bản theo đường mạng, và một video tải lên ở 1080p không thể thành bản 4K thật. Ví dụ theo thiết bị của nguồn chỉ là cách nói đơn giản, không phải quy tắc cố định. Người sáng tạo tải lên một lượng video rất lớn mỗi phút, và trong đại dịch COVID-19 lượng xem video còn tăng mạnh vì người ta ở nhà. Chuyển mã bằng phần mềm trở nên chậm và tốn kém, nên cần một "bộ não" làm riêng cho mã hóa và giải mã video.

**VCU xếp theo lớp.** Giống như GPU hay TPU dùng cho đồ họa hay học máy, YouTube làm VCU cho xử lý video ở quy mô trung tâm dữ liệu:
- Mỗi cụm có một số máy chủ tăng tốc bằng VCU.
- Mỗi máy chủ có nhiều khay tăng tốc.
- Mỗi khay có nhiều thẻ VCU.
- Mỗi thẻ có bộ mã hóa, bộ giải mã và các phần khác.

Cụm VCU tạo ra video ở các độ phân giải khác nhau và lưu vào kho lưu trữ đám mây. Theo bài nguồn, thiết kế mới này, công bố năm 2021, cho hiệu quả tính toán tốt hơn 20 tới 33 lần so với hệ thống tối ưu trước đó.

## Giới hạn cần nhớ

"20 tới 33 lần" là con số bài nguồn nêu, so với hệ thống trước đó của chính YouTube; bài nguồn không nói đo bằng thước nào (mỗi đồng chi phí, mỗi đơn vị điện hay mỗi máy). Bài nguồn cũng không nói việc nào vẫn chạy bằng phần mềm. Tài liệu YouTube công bố năm 2021 chưa được mở để đối chiếu.

## Nhìn hình thử trả lời

Một video 10 phút được tải lên. Vì sao YouTube không chỉ lưu đúng bản gốc rồi phát lại cho mọi người xem?

<details>
<summary>Xem đáp án</summary>

Vì mỗi thiết bị và mỗi đường mạng cần một bản khác nhau: mạng yếu cần bản nhẹ (độ phân giải hoặc tốc độ bit thấp hơn), màn hình lớn với mạng tốt nhận bản nét hơn. Bản gốc cần được chuyển mã ra nhiều bản, và việc đó nhân lên với hơn 500 giờ video mỗi phút, nên chuyển mã là phần việc khổng lồ mà VCU được làm ra để gánh.

</details>

<details>
<summary>Xem sâu hơn: khi nào đáng làm chip riêng</summary>

- Một phép tính lặp lại với khối lượng cực lớn và gần như không đổi theo thời gian.
- Phần mềm chạy trên chip thông dụng đã được tối ưu mà vẫn chậm hoặc tốn.
- Đủ quy mô để chi phí thiết kế chip được chia trên rất nhiều việc.

Đây là nhận xét chung của người biên soạn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-youtube-handle-massive-video-content-upload.md): lượng video tải lên, lý do cần chip riêng, các lớp của cụm VCU và mức cải thiện 20 tới 33 lần.

Đã đọc nguồn ngày 2026-10-19. Tài liệu gốc YouTube công bố năm 2021 chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.
