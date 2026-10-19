# Ngôn ngữ lập trình nào "xanh" nhất?

**Một nhóm nghiên cứu đã dựng sẵn khung đo thời gian chạy, bộ nhớ và năng lượng cho cùng mười bài toán ở nhiều ngôn ngữ; muốn tin một bảng xếp hạng "xanh" thì phải đọc cách đo trước.**
Bài nguồn chỉ nêu câu hỏi, một đoạn tóm tắt nghiên cứu và một tấm ảnh bảng so sánh. Bài này giữ câu hỏi đó, không dùng ảnh nên không chép bảng xếp hạng, và tự mô tả cách đo dựa vào kho mã mà nhóm nghiên cứu công bố.

![Ba nhóm thẻ xếp dọc. Bộ bài đo: mười bài toán chuẩn lấy từ Computer Language Benchmarks Game, và 28 thư mục ngôn ngữ trong kho mã, mỗi bài một thư mục con. Bốn thao tác của mỗi bài, theo thứ tự: biên dịch, chạy thử để kiểm kết quả, đo năng lượng bằng khung RAPL, đo bộ nhớ đỉnh. Đọc thận trọng, ba ý: số liệu phụ thuộc máy và trình biên dịch; mười bài toán không phải ứng dụng của bạn; bài này không nêu ngôn ngữ nào xanh nhất.](../../diagrams/sd-10-004-main.svg)

## Từ viết tắt

- **RAPL** (Running Average Power Limit) — giới hạn công suất trung bình chạy: tên khung đo năng lượng mà kho mã dùng, đọc năng lượng tiêu thụ từ các thanh ghi của bộ xử lý; việc nó đọc thanh ghi của phần cứng là kiến thức chung của người biên soạn.

## Đọc hình

Phần dưới dựa vào tệp README của kho mã công bố cùng nghiên cứu, không dựa vào đoạn tóm tắt trong bài nguồn.

**Bộ bài đo.** Kho mã chứa mười bài toán chuẩn (benchmark), mỗi bài đã được viết sẵn cho 28 ngôn ngữ; mã được lấy nguyên từ Computer Language Benchmarks Game. Thư mục chính có 28 thư mục con, mỗi ngôn ngữ một thư mục, và trong đó mỗi bài toán một thư mục con có tệp Makefile.

**Bốn thao tác.** Mỗi Makefile phải có bốn luật, một luật cho mỗi thao tác. `compile` nói cách biên dịch bài đó (ngôn ngữ thông dịch có thể để trống). `run` nói cách chạy, dùng để thử xem bài có chạy không lỗi và cho ra kết quả mong đợi. `measure` nói cách dùng khung RAPL để đo năng lượng của việc chạy đó. `mem` chạy lại việc đó nhưng có theo dõi đỉnh bộ nhớ.

**Kết quả đo.** Kết quả ghi thành một tệp cho mỗi ngôn ngữ; mỗi dòng có tên bài toán, năng lượng tính bằng joule cho gói bộ xử lý, bộ xử lý, bộ xử lý đồ họa và bộ nhớ, rồi thời gian chạy tính bằng mili giây. README lưu ý việc có số đo cho bộ xử lý đồ họa hay bộ nhớ hay không tùy kiến trúc của máy, vì đó là yêu cầu của chính RAPL.

**Đọc thận trọng.** Số đo phụ thuộc máy và các trình biên dịch dùng để đo; README chỉ dẫn tới một trang riêng nơi công bố kết quả của một lần đo cùng cấu hình máy và trình biên dịch. Mười bài toán chỉ là mười bài toán, không đại diện cho chương trình của bạn.

## Giới hạn cần nhớ

Bài nguồn ghi hai con số khác nhau cho số ngôn ngữ: "28 ngôn ngữ" ở câu mở đầu, còn đoạn tóm tắt được trích ghi "hai mươi bảy". README của kho mã ghi 28 thư mục ngôn ngữ; bài này chỉ nói "28 thư mục ngôn ngữ trong kho", và nếu cần trích số chính xác thì hãy mở bài báo gốc.
Bảng xếp hạng nằm trong ảnh của bài nguồn, bài này không dùng và cũng chưa đối chiếu được, nên không nêu ngôn ngữ nào "xanh nhất". Câu hỏi trong tiêu đề vì thế được trả lời bằng cách đọc cách đo, không bằng một cái tên.
Kết luận rằng ngôn ngữ nhanh hơn thì tốn ít năng lượng hơn, hay ngược lại, chỉ đúng trong khuôn khổ các bài toán đã đo; đây là cảnh báo chung của người biên soạn.

## Nhìn hình trả lời

Đội bạn chọn ngôn ngữ cho một dịch vụ chạy liên tục và muốn tiết kiệm điện. Dựa trên bài này, hai việc nên làm trước khi tin một bảng xếp hạng ngôn ngữ "xanh" là gì?

<details>
<summary>Xem đáp án</summary>

Thứ nhất, hỏi bảng đó đo bằng cách nào: những thao tác nào đã được chạy (biên dịch, chạy, đo năng lượng, đo đỉnh bộ nhớ), trên máy và trình biên dịch nào, vì số đo phụ thuộc vào đó.
Thứ hai, kiểm tra mười bài toán đã đo có giống việc của dịch vụ mình không, và mở bài báo gốc để kiểm các chi tiết như số ngôn ngữ.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một đoạn dẫn ngắn kèm trích nguyên văn phần tóm tắt của nghiên cứu. Bài này chỉ giữ câu hỏi và hướng đọc thận trọng; không dịch hay diễn đạt lại phần tóm tắt đó mà mô tả cách đo từ README của kho mã nghiên cứu.
Hình tách ba phần: bộ bài đo, bốn thao tác và các lưu ý khi đọc. Bài không đọc bài báo gốc nên không biết bảng số liệu của nó.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-are-the-greenest-programming-languages.md): câu hỏi về ngôn ngữ "xanh" nhất.
- [Energy-Languages — README tại commit cố định](https://github.com/greensoftwarelab/Energy-Languages/blob/1356528173d6bb07fb2512037c0ed8e2279ce440/README.md): mười bài toán, 28 ngôn ngữ, bốn thao tác, khung RAPL và định dạng kết quả. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-19. Chưa đọc bài báo gốc của nghiên cứu; câu giải nghĩa RAPL trong mục từ viết tắt và lưu ý về phạm vi kết quả là của người biên soạn.
Bài viết và hình được thiết kế độc lập.
