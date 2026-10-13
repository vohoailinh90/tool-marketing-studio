# AI agent là gì?

**Khác biệt giữa một câu trả lời và một agent là vòng lặp hành động.** Trong bài này, “agent” là agent dùng mô hình ngôn ngữ (LLM agent): nó dùng mô hình để chọn
bước kế tiếp, gọi công cụ, nhìn kết quả thật rồi chọn tiếp, cho tới khi xong mục tiêu.

![Vòng lặp dọc. Mục tiêu: đặt lịch họp cho ba người. Bước 1, LLM chọn bước kế tiếp dựa trên mục tiêu, bộ nhớ và kết quả trước. Bước 2, gọi công cụ như API lịch, tìm kiếm, chạy mã. Bước 3, quan sát kết quả thật từ môi trường; một mũi tên đi từ bước 3 trở lại bước 1. Cuối cùng là dừng: xong mục tiêu, hết số lượt cho phép hoặc chờ người duyệt. Ghi chú: thao tác khó hoàn tác nên có người duyệt trước.](../../diagrams/sd-03-006-main.svg)

## Đọc hình

**Mục tiêu.** Người dùng nêu việc cần làm, ví dụ đặt lịch họp cho ba người.

**1 · LLM chọn bước kế tiếp.** Mô hình dựa vào mục tiêu, bộ nhớ (sở thích, kiến thức đã lưu) và kết quả
của bước trước để quyết định làm gì.

**2 · Gọi công cụ.** Agent hành động qua công cụ: API lịch, tìm kiếm, chạy mã.

**3 · Quan sát.** Kết quả thật từ môi trường quay lại vòng lặp. Nhờ đó bước sau dựa trên sự kiện
chứ không dựa trên việc mô hình đoán kết quả của công cụ.

**Dừng.** Vòng lặp kết thúc khi xong mục tiêu, hết số lượt cho phép hoặc cần người duyệt.

Một hệ thống có thể chỉ có một agent, nhiều agent phối hợp hoặc cạnh tranh, hay người làm việc cùng agent.

## Giới hạn cần nhớ

Tự chủ có giá: nhiều lượt gọi mô hình làm chậm và đắt hơn, và sai sót ở một bước có thể cộng dồn qua các bước sau.
Nếu đường đi của công việc đã cố định, một quy trình viết sẵn thường đơn giản, rẻ và dễ kiểm hơn.
Với thao tác khó hoàn tác, như gửi thanh toán hay xóa dữ liệu, cần điểm dừng cho người duyệt và giới hạn số lượt.

## Nhìn hình trả lời

Vì sao agent phải quan sát kết quả của công cụ trước khi chọn bước tiếp, và điều gì giữ vòng lặp khỏi chạy mãi?

<details>
<summary>Xem đáp án</summary>

Để bước sau dựa trên dữ liệu thật thay vì đoán. Điều kiện dừng, như số lượt tối đa hoặc chờ người duyệt,
giữ vòng lặp trong tầm kiểm soát.

</details>

<details>
<summary>Xem sâu hơn: workflow và agent</summary>

Anthropic phân biệt **workflow** — mô hình và công cụ được điều phối theo đường mã viết sẵn — với **agent** —
hệ thống trong đó mô hình tự điều khiển quá trình và việc dùng công cụ. Họ khuyên chọn cách đơn giản nhất đáp ứng
được việc, và chỉ dùng agent khi cần sự linh hoạt mà đường đi cố định không cho được.

Bài nguồn còn liệt kê các loại agent (phản xạ đơn giản, phản xạ dựa trên mô hình, dựa trên mục tiêu,
dựa trên tiện ích, học). Đó là những agent theo nghĩa rộng của ngành AI, và chúng không cần mô hình ngôn ngữ hay vòng lặp gọi công cụ. Bài này chỉ nói về LLM agent; phân loại kia không cần cho ý chính nên bài không đối chiếu và không đưa vào.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-is-an-ai-agent.md): đặc điểm và kiến trúc của agent.
- [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents): định nghĩa workflow và agent; vòng lặp dùng công cụ với phản hồi từ môi trường; đánh đổi độ trễ và chi phí; điểm dừng cho người duyệt và điều kiện dừng.

Đã đọc nguồn ngày 2026-10-13. Trang Anthropic đã được mở và đối chiếu các câu về workflow và agent, vòng lặp dùng công cụ, chi phí và điểm dừng;
phần bộ nhớ và các kiểu hệ thống (một agent, nhiều agent, người cùng làm) lấy từ bài nguồn, chưa đối chiếu.
Bài viết và hình được thiết kế độc lập.
