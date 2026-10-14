# Cần bao nhiêu người chuyên kiểm thử: đọc từ số đo của chính đội

"Một lập trình viên cần bao nhiêu kiểm thử viên?" không có đáp án chung. Nhưng đội nào cũng đo được vài con số cho biết kiểm thử đang giúp hay đang nghẽn, và từ đó thấy việc nào còn thiếu người chuyên trách. Bài nêu bốn số đo và điều mỗi số gợi ý.

![Bốn số đo để quyết định kiểm thử cần gì: tỉ lệ thay đổi gây lỗi ở môi trường thật cho biết lỗi nào lọt qua, thời gian chờ kết quả test cho biết lập trình viên có chạy test hay không, tỉ lệ test chập chờn cho biết kết quả có đáng tin không, và phần việc máy khó làm như khám phá và trải nghiệm cho biết nơi người chuyên kiểm thử bổ sung nhiều nhất.](../../diagrams/sd-13-003-main.svg)

**Đọc hình:** thẻ 1 là kết quả người dùng thấy; thẻ 2 và 3 cho biết bộ test có dùng được không; thẻ 4 là phần việc ngoài tầm của test tự động.

## Từ viết tắt

- **DORA** (DevOps Research and Assessment) — chương trình nghiên cứu và đánh giá DevOps; các thước đo DORA đo tốc độ và độ ổn định khi giao phần mềm.
- **DevOps** (Development and Operations) — phát triển và vận hành: cách tổ chức công việc để việc viết phần mềm và việc vận hành nó gắn với nhau, thay vì giao cho hai nhóm tách rời.

## Nhìn hình thử trả lời

Đội bạn có 10 lập trình viên và chưa có ai chuyên kiểm thử. Bộ test chạy 90 phút, và cứ vài lần lại đỏ rồi xanh khi chạy lại. Thuê một kiểm thử viên có phải việc đầu tiên nên làm không?

<details>
<summary>Xem đáp án</summary>

Chưa chắc. Hai số đo giữa cho thấy vấn đề nằm ở chính bộ test: 90 phút khiến lập trình viên ít chạy nó trước khi gộp mã, và test đỏ rồi xanh khi chạy lại làm mọi người quen bỏ qua kết quả đỏ. Hãy rút ngắn thời gian chạy, cách ly rồi sửa test chập chờn trước. Sau đó nhìn lại tỉ lệ thay đổi gây lỗi ở môi trường thật để biết còn thiếu loại kiểm thử nào, ví dụ khám phá hay dùng thử, rồi mới quyết định thêm người.

</details>

## Giới hạn cần nhớ

Số đo chỉ gợi ý, không thay cho phán đoán: đội vài người có thể chưa đủ dữ liệu, và con số bị méo khi dùng để chấm điểm từng người. Bài không đưa tỉ lệ lập trình viên trên kiểm thử viên "chuẩn" vì không có con số chung cho mọi sản phẩm. Với sản phẩm mà lỗi gây hại lớn (thiết bị y tế, thanh toán), quy định ngành có thể đòi quy trình kiểm thử và phê duyệt riêng.

<details>
<summary>Xem sâu hơn</summary>

- **Thay đổi gây lỗi:** đếm số lần phát hành phải vá gấp, hoàn tác hay sửa lại, chia cho tổng số lần phát hành trong cùng kỳ. DORA (DevOps Research and Assessment — chương trình nghiên cứu và đánh giá DevOps) gọi chỉ số này là tỉ lệ thay đổi gây lỗi (change fail rate: phần trăm lần triển khai gây lỗi ở môi trường thật) và đo cùng thời gian khôi phục sau một lần triển khai lỗi. Đọc kèm loại lỗi lọt qua (giao diện, tích hợp, hiệu năng, dữ liệu), vì mỗi loại cần cách kiểm thử khác nhau.
- **Thời gian chờ:** tháp kiểm thử (test pyramid) của Martin Fowler gợi ý có nhiều test nhỏ, nhanh ở đáy và ít test chạy qua toàn hệ thống ở đỉnh; bộ test chậm thường do dồn quá nhiều vào các test đầu-cuối. Nên rút ngắn thời gian chờ trước khi thêm người, vì người mới cũng phải chờ cùng bộ test đó.
- **Test chập chờn:** test lúc xanh lúc đỏ khi mã không đổi khiến mọi người quen bỏ qua test đỏ. Fowler khuyên cách ly chúng khỏi bộ test chính để bộ chính luôn đáng tin, rồi sửa từng cái.
- **Việc máy khó làm:** kiểm thử khám phá là người vừa tìm hiểu sản phẩm vừa tự thiết kế và chạy phép thử; trải nghiệm người dùng và khả năng truy cập cũng cần con người đánh giá. Nếu ba số đo đầu ổn mà lỗi thuộc các loại này vẫn lọt ra, đó là lúc cân nhắc người chuyên trách.
- **Chưa có số đo:** bắt đầu bằng ghi lại hai thứ: mỗi lần phát hành có phải vá gấp không, và từ lúc đẩy mã đến lúc có kết quả test là bao lâu. Hai con số này đủ cho thấy xu hướng sau vài tuần.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/paradigm-shift-how-developer-to-tester-ratio-changed-from-11-to-1001.md).
- DORA: [lịch sử và định nghĩa các chỉ số phân phối phần mềm](https://dora.dev/guides/dora-metrics/history/).
- Martin Fowler: [TestPyramid](https://martinfowler.com/bliki/TestPyramid.html), [Eradicating Non-Determinism in Tests](https://martinfowler.com/articles/nonDeterminism.html).
