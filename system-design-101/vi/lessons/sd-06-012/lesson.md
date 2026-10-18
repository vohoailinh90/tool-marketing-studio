# Sàn chứng khoán độ trễ thấp: làm ít hơn trên đường găng

**Muốn một lệnh mua bán đi qua sàn thật nhanh, nguyên tắc là làm ít hơn trên đường găng: chuỗi việc mà lệnh bắt buộc phải đi qua. Bớt việc, bớt chặng mạng, không đụng đĩa, và để mỗi việc chính do một luồng giữ, không phải tranh khóa với luồng khác.**
Ý cuối nghe lạ nhất, nên bài này đo thử nó: khóa và việc chuyển tin giữa các luồng tốn bao nhiêu.

![Ba khung. Khung một, đường găng của một lệnh: nhận lệnh; kiểm tra rủi ro bắt buộc; khớp lệnh; gửi kết quả. Khung hai, làm ít hơn trên đường găng: việc không bắt buộc như ghi báo cáo chuyển ra ngoài; các thành phần đặt chung một máy để bớt chặng mạng; không ghi đĩa trên đường găng; mỗi việc chính do một luồng giữ, không khóa, không đổi ngữ cảnh. Khung ba, đo trên một máy: tăng một bộ đếm 500 triệu lần mất 1,25 giây, có khóa mất 3,6 đến 4,8 giây, hai luồng tranh khóa mất 40 giây; chuyển một tin qua lại giữa hai luồng bằng vòng chờ bận mất khoảng 250 nano giây, bằng khóa và biến điều kiện mất khoảng 26 micro giây.](../../diagrams/sd-06-012-main.svg)

## Từ viết tắt

- **CPU** (Central Processing Unit) — bộ xử lý trung tâm: phần chạy lệnh của máy tính; máy thử có 4 lõi, mỗi luồng có thể được "ghim" vào một lõi.
- **CAS** (Compare And Swap) — so sánh rồi hoán đổi: lệnh máy đổi một giá trị trong bộ nhớ chỉ khi nó vẫn đúng như mong đợi, dùng thay khóa trong các thuật toán không khóa.

## Đọc hình

**Đường găng.** Với một sàn khớp lệnh, đường găng bắt đầu khi lệnh vào bộ quản lý lệnh, đi qua các bước kiểm tra rủi ro bắt buộc, được khớp với lệnh đối ứng, và kết thúc khi kết quả đi ra. Việc gì không bắt buộc (ghi báo cáo, thống kê, lưu trữ lâu dài) thì làm ở chỗ khác, để không cộng vào thời gian chờ của lệnh.

**Bốn cách làm ít hơn.** Ít việc hơn trên đường găng; mỗi việc nhanh hơn; ít chặng mạng hơn (bài nguồn đặt mọi thành phần chung một máy lớn, trao đổi qua bộ nhớ dùng chung); không đụng đĩa. Bài nguồn còn cho các thành phần chính chạy một luồng, mỗi luồng ghim vào một CPU, để không có đổi ngữ cảnh và không có khóa.

**Vì sao khóa đắt.** Bài kỹ thuật về Disruptor (thư viện do nhóm kỹ sư của một sàn giao dịch viết) giải thích: khi nhiều luồng tranh một khóa, hệ điều hành phải phân xử bằng cách đổi ngữ cảnh, tạm dừng luồng đang chờ; trong lúc đó bộ nhớ đệm của CPU có thể mất dữ liệu đang dùng. Họ đo một vòng tăng bộ đếm 500 triệu lần bằng Java: 300 ms với một luồng, 10.000 ms khi thêm khóa, 224.000 ms khi hai luồng tranh khóa. Kết luận của họ: lý tưởng là chỉ một luồng sở hữu mọi lần ghi vào một tài nguyên.

## Đo lại trên máy này

Ngày 2026-10-18, bài viết lại phép thử đó bằng C (gcc 13.3, `-O2`) trên một máy ảo 4 lõi Xeon 2,1 GHz.

| Tăng một bộ đếm 500 triệu lần | Thời gian |
|---|---|
| Một luồng, không khóa | 1,25 giây |
| Một luồng, có khóa (không ai tranh) | 3,6–4,8 giây |
| Hai luồng tranh một khóa | khoảng 40 giây |

Hướng giống hệt bài về Disruptor: thêm khóa đã chậm, tranh khóa chậm hơn hàng chục lần. Thời gian tuyệt đối khác vì khác ngôn ngữ và máy.

Phép thử thứ hai đo thời gian **chuyển một tin qua lại** giữa hai luồng ghim vào hai lõi, 200.000 lần. Khi luồng nhận chờ bận (liên tục đọc một biến cho tới khi thấy tin), một vòng đi về có trung vị khoảng 250 ns. Khi dùng khóa và biến điều kiện (luồng nhận ngủ, hệ điều hành đánh thức khi có tin), trung vị khoảng 26 µs, chậm hơn khoảng 100 lần. Đó là lý do sàn độ trễ thấp chấp nhận để một lõi CPU quay tròn chờ việc: đổi lại, không phải chờ hệ điều hành đánh thức.

## Giới hạn cần nhớ

Chờ bận đốt trọn một lõi CPU kể cả khi không có việc, và chỉ đáng khi số lõi đủ dùng; ghim luồng vào lõi trên máy ảo không bảo đảm lõi đó không bị chia cho máy khác. Gom mọi thứ vào một máy cũng nghĩa là máy đó hỏng thì cả sàn dừng, nên cần phương án dự phòng. Những lựa chọn này hợp với bài toán mà vài micro giây đáng giá; với phần lớn hệ thống web, một kiến trúc thông thường đơn giản hơn nhiều.

## Nhìn hình trả lời

Một đồng nghiệp đề nghị ghi mỗi lệnh khớp xuống cơ sở dữ liệu và chờ ghi xong rồi mới trả kết quả, "cho chắc". Theo nguyên tắc của bài, nên làm gì thay thế?

<details>
<summary>Xem đáp án</summary>

Ghi cơ sở dữ liệu là việc chạm đĩa và có thể qua mạng, nên đặt nó trên đường găng là cộng thẳng thời gian đó vào mỗi lệnh. Theo nguyên tắc của bài, đưa việc ghi ra ngoài đường găng: luồng khớp lệnh đặt kết quả lên bus sự kiện, một thành phần khác nghe bus và ghi xuống cơ sở dữ liệu.
Cái giá cần nói rõ: phải có cách khác bảo đảm không mất lệnh nếu máy hỏng trước khi kịp ghi (ví dụ nhật ký hoặc bản sao ở máy khác); "làm sau" không có nghĩa là "không cần".

</details>

<details>
<summary>Xem sâu hơn: điều đã thêm so với bài nguồn, và một kết quả lệch</summary>

Bài nguồn nêu nguyên tắc và một thiết kế (một máy lớn, bộ nhớ dùng chung, luồng đơn ghim vào CPU). Bài này thêm lý do khóa đắt từ bài kỹ thuật về Disruptor và đo lại hai điều trên một máy.
Một kết quả không khớp bài về Disruptor: trên máy này, vòng tăng bộ đếm bằng CAS một luồng mất 6,2 giây, chậm hơn khóa không ai tranh (3,6–4,8 giây), trong khi bài về Disruptor đo CAS nhanh hơn khóa. Bài không đi sâu vì sao; có thể do cách thư viện C cài khóa không tranh chấp và cách viết vòng CAS trong phép thử.
Bài không đo một sàn thật và không nêu độ trễ của sàn nào.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/low-latency-stock-exchange.md): nguyên tắc làm ít hơn trên đường găng, đường găng của một lệnh, thiết kế một máy với luồng đơn ghim vào CPU.
- [Disruptor — bài kỹ thuật, tại commit cố định](https://github.com/LMAX-Exchange/disruptor/blob/c871ca49826a6be7ada6957f6fbafcfecf7b1f87/src/docs/asciidoc/en/disruptor.adoc): mục "The Cost of Locks" (đổi ngữ cảnh, bảng thời gian tăng bộ đếm), mục về CAS, và nguyên tắc một luồng sở hữu mọi lần ghi.

Đã đọc nguồn ngày 2026-10-18 từ bản clone của từng kho; thử nghiệm chạy cùng ngày. Bài viết và hình được thiết kế độc lập.
