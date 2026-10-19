# Bốn cách chờ khi thử lại: tăng đều hay gấp đôi, có ngẫu nhiên hay không

**Khi một lần gọi hỏng vì lỗi tạm thời, thử lại thường đúng; nhưng nếu mọi máy khách cùng chờ một khoảng như nhau rồi cùng thử lại, chúng dồn vào máy chủ đúng lúc nó đang yếu.** Có bốn cách chọn khoảng chờ. Bài này tách hai lựa chọn nhỏ của chúng (tăng đều hay gấp đôi, có ngẫu nhiên hay không) và đo từng cái trên một mô phỏng, thay vì chỉ nói "nên dùng gấp đôi cộng ngẫu nhiên".

![Hai khung. Khung một, bốn cách chờ giữa các lần thử lại, mỗi cách một thẻ: chờ tăng đều, tăng đều cộng ngẫu nhiên, tăng gấp đôi, tăng gấp đôi cộng ngẫu nhiên. Khung hai, mô phỏng 1000 máy khách cùng thử lại vào một máy chủ nhận 100 yêu cầu mỗi bước: hai cách không ngẫu nhiên khiến 100 máy bỏ cuộc sau 5400 yêu cầu; cách cộng ngẫu nhiên đưa tất cả vào xong chỉ sau 2560 yêu cầu.](../../diagrams/sd-11-029-main.svg)

## Từ viết tắt

- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: giao thức web dùng để gọi một dịch vụ qua mạng; bài nói tới lỗi và việc thử lại của lời gọi kiểu này.

## Đọc hình

**Tăng đều.** Khoảng chờ tăng một lượng cố định sau mỗi lần thất bại (2, 4, 6, 8 bước). Dễ hiểu, dễ làm. Nhưng nếu rất nhiều máy khách cùng bắt đầu một lúc thì chúng cũng thử lại cùng lúc, và có thể gây "bão thử lại" khi tải cao.

**Tăng đều cộng ngẫu nhiên.** Vẫn tăng đều, nhưng mỗi khoảng chờ thêm một đoạn ngẫu nhiên. Nhờ vậy các lần thử lại rải ra theo thời gian. Phần cơ bản vẫn chỉ tăng đều nên nếu khoảng ngẫu nhiên nhỏ so với phần cơ bản thì vẫn có thể có nhiều máy khách thử lại gần nhau.

**Gấp đôi.** Khoảng chờ nhân đôi sau mỗi lần thất bại (2, 4, 8, 16 bước), thường có trần. Giãn các lần thử rất nhanh nên hợp với tải cao. Chỗ yếu: nếu thử lại ngay có thể đã thành công thì cách này bắt chờ lâu không cần thiết.

**Gấp đôi cộng ngẫu nhiên.** Gấp đôi rồi trộn thêm ngẫu nhiên, hoặc cộng thêm một đoạn ngẫu nhiên, hoặc nhân với một hệ số ngẫu nhiên. Giảm thêm khả năng đụng nhau, đổi lại có lúc chờ lâu hơn cần thiết nếu phần ngẫu nhiên lớn.

## Thử: 1000 máy khách cùng thất bại

Ngày 2026-10-19, một chương trình Python nhỏ. Cả 1000 máy khách gửi yêu cầu đầu tiên ở bước 0; máy chủ nhận được tối đa 100 yêu cầu mỗi bước, phần dư bị từ chối, và máy khách thử lại tối đa 8 lần. Khoảng chờ cơ bản 2 bước, trần 64 bước. "Cộng ngẫu nhiên" là cộng một số ngẫu nhiên từ 0 đến đúng khoảng chờ cơ bản; "ngẫu nhiên hoàn toàn" là chọn ngẫu nhiên từ 0 đến khoảng chờ cơ bản.

| Cách chờ | Xong | Bỏ cuộc | Tổng số yêu cầu gửi | Bước hoàn tất | Đợt lớn nhất sau bước 0 |
|---|---|---|---|---|---|
| Tăng đều | 900 | 100 | 5400 | 72 | 900 |
| Tăng đều cộng ngẫu nhiên | 1000 | 0 | 2560 | 22 | 326 |
| Gấp đôi | 900 | 100 | 5400 | 254 | 900 |
| Gấp đôi cộng ngẫu nhiên | 1000 | 0 | 2560 | 26 | 326 |
| Gấp đôi, ngẫu nhiên hoàn toàn | 1000 | 0 | 3128 | 23 | 574 |

Cả hai cách không có ngẫu nhiên cho ra cùng 5400 yêu cầu và đợt thử lại 900 máy một lúc, vì mọi máy khách bắt đầu cùng bước nên thời điểm thử lại của chúng trùng nhau. Chính ngẫu nhiên mới bẻ gãy sự trùng đó. Ở mô phỏng này, tăng đều hay gấp đôi chỉ khác ở thời gian hoàn tất của cách không ngẫu nhiên (72 so với 254 bước), còn khi có ngẫu nhiên thì hai cách gần như ngang nhau (22 và 26 bước).

## Giới hạn cần nhớ

Mô phỏng chỉ có một máy chủ cố định 100 yêu cầu mỗi bước, mọi máy khách bắt đầu cùng lúc, và nhận yêu cầu thất bại là do quá tải chứ không do lỗi khác; trần thử lại 8 lần khiến "bỏ cuộc" là kết quả của giới hạn đó. Hệ thật có tải tới liên tục, lỗi có nguyên nhân khác nhau, và gói dưới các tầng khác. Hai con số nhỏ (22 và 26 bước) khác nhau có thể chỉ do hạt giống ngẫu nhiên, nên bài không kết luận cách nào trong hai cách cộng ngẫu nhiên tốt hơn. Bài này đi cùng bài về xử lý lỗi khi gọi web nhưng không lặp lại nó: ở đây chỉ nói về khoảng chờ, không nói khi nào nên thử lại hay khi nào lời gọi an toàn để lặp.

## Nhìn hình trả lời

Một dịch vụ dùng cách "gấp đôi", không ngẫu nhiên, và máy chủ phía sau hỏng đúng một phút rồi tự khỏi. Hàng nghìn máy khách bắt đầu thử cùng lúc. Chuyện gì có thể xảy ra sau khi máy chủ khỏi?

<details>
<summary>Xem đáp án</summary>

Các máy khách bắt đầu cùng lúc nên thử lại theo cùng một lịch (2, 4, 8, 16... bước), nên chúng dồn thành từng đợt lớn đúng vào các mốc này. Sau khi máy chủ khỏi, đợt gần nhất có thể vẫn lớn đến mức làm nó quá tải lần nữa. Thêm ngẫu nhiên làm các đợt tan ra.
Đây là suy luận từ mô phỏng của người biên soạn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn mô tả bốn cách, mỗi cách có ưu điểm và nhược điểm, nhưng không đưa số đo. Bài này giữ bốn cách và tên của chúng, tách thành hai lựa chọn nhỏ và thêm mô phỏng. Phần nhận định "bão thử lại" và "đụng nhau" của nguồn được kiểm tra bằng mô phỏng, không bằng tài liệu bên ngoài.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-we-retry-on-failures.md): bốn cách chờ và ưu nhược điểm. Mô phỏng, bảng và đáp án là của người biên soạn.
- [AWS Architecture Blog — Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/): so sánh cách gấp đôi với các kiểu ngẫu nhiên. Chưa mở lại trong phiên viết (không mở được trang từ môi trường); kiến thức chung của người biên soạn.

- Chương trình tạo các con số của bài: `brainstorm/system-design-101-vi/experiments/sd-11-029.py` (chạy được, có kiểm tra đúng giá trị ghi trong bài).

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.
