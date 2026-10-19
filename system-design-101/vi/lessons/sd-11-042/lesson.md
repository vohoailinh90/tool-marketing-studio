# Mười lăm khái niệm khi thiết kế hệ thống: chia theo việc, và đếm xem tài liệu ôn thi nói gì

**Mười lăm khái niệm của bài nguồn dễ bị đọc như một danh sách ngang hàng, nhưng chúng trả lời bốn câu hỏi khác nhau: làm cái gì, dựng thế nào, giữ cho sống ra sao, và đưa vào đời thế nào.**
Bài xếp mười lăm khái niệm theo bốn câu hỏi đó, rồi đếm xem một tài liệu ôn phỏng vấn nổi tiếng nhắc tới từng khái niệm bao nhiêu lần để thấy khái niệm nào hay bị bỏ quên.

![Năm khung. Khung một, làm cái gì: thu thập yêu cầu, thiết kế miền, thiết kế trải nghiệm người dùng. Khung hai, dựng thế nào: kiến trúc hệ thống, thiết kế dữ liệu, khả năng mở rộng, hiệu năng. Khung ba, giữ cho sống: độ tin cậy, tính sẵn sàng, bảo mật, khả năng bảo trì, kiểm thử. Khung bốn, đưa vào đời: ước tính chi phí, tài liệu, kế hoạch di chuyển. Khung năm, đếm trong một tài liệu ôn phỏng vấn: khả năng mở rộng 104 lần, kiến trúc 70 lần; sáu khái niệm chỉ được nhắc không quá một lần.](../../diagrams/sd-11-042-main.svg)

## Đọc hình

Bài nguồn liệt kê mười lăm khái niệm khi thiết kế hệ thống và dặn lưu lại để tra cứu. Giữ nguyên tên và dùng cách chia của người biên soạn (không phải của nguồn):

| Câu hỏi | Khái niệm (tên ở nguồn) |
|---|---|
| Làm cái gì | Requirement gathering; Domain design; User experience design |
| Dựng thế nào | System architecture; Data design; Scalability; Performance |
| Giữ cho sống | Reliability; Availability; Security; Maintainability; Testing |
| Đưa vào đời | Cost estimation; Documentation; Migration plan |

Một khái niệm có thể nằm ở nhiều nhóm (bảo mật cũng là yêu cầu, chi phí cũng ảnh hưởng kiến trúc); cách chia chỉ để nhớ khi nào thì cần nghĩ tới.

## Thử: đếm trong tài liệu ôn phỏng vấn

Ngày 2026-10-19, người biên soạn đọc tệp README của kho `donnemartin/system-design-primer` ở commit `ae9bbd7` (15.799 từ) và đếm số lần xuất hiện của mỗi khái niệm, không phân biệt hoa thường, bằng các mẫu sau: `requirement`, `architecture`, `database` hoặc `schema` (cho thiết kế dữ liệu), `domain` không đi trước `name` (để bỏ hệ thống tên miền), `scalab`, `reliab`, `availab`, `performance`, `secur`, `maintainab`, `\btest`, `user experience` hoặc `ux`, `\bcost`, `documentation`, `migrat`.

| Khái niệm | Số lần | Khái niệm | Số lần |
|---|---|---|---|
| Scalability | 104 | Domain design | 5 |
| Data design | 95 | Reliability | 4 |
| System architecture | 70 | Cost estimation | 4 |
| Availability | 63 | Requirement gathering | 1 |
| Performance | 33 | Testing | 1 |
| Security | 14 | User experience | 1 |
| Maintainability | 0 | Documentation | 0 |
| Migration plan | 0 | | |

Sáu khái niệm chỉ được nhắc không quá một lần: khả năng bảo trì, tài liệu, di chuyển (0), thu thập yêu cầu, kiểm thử và trải nghiệm người dùng (1). Bốn khái niệm đứng đầu (mở rộng, dữ liệu, kiến trúc, sẵn sàng) chiếm phần lớn.

## Giới hạn cần nhớ

Đếm từ khóa không đo độ phủ ý tưởng. Cụ thể, "thu thập yêu cầu" xuất hiện một lần theo từ khóa, nhưng bước đầu của cách làm bài phỏng vấn trong cùng tài liệu là "nêu ca sử dụng, ràng buộc và giả định", chính là thu thập yêu cầu dưới tên khác; phép đếm bỏ sót điều đó. Mẫu `database` tăng điểm cho "thiết kế dữ liệu" vì tài liệu có nhiều chủ đề về cơ sở dữ liệu. Tài liệu được chọn vì nổi tiếng và hướng tới phỏng vấn, nên nó phản ánh thứ người ta hay hỏi chứ không phải thứ một hệ thống thật cần. Cách chia bốn nhóm là của người biên soạn.

## Nhìn hình trả lời

Nhóm bạn sắp bàn giao một hệ thống cho một đội khác. Trong mười lăm khái niệm, hai khái niệm nào của nhóm "đưa vào đời" và "giữ cho sống" bạn kiểm trước, và vì sao?

<details>
<summary>Xem đáp án</summary>

Tài liệu (Documentation) và khả năng bảo trì (Maintainability): người nhận cần biết hệ thống làm gì và sửa nó thế nào. Đây là hai khái niệm mà phép đếm cho thấy tài liệu ôn thi gần như không nhắc, nên dễ bị bỏ khi chỉ ôn theo thứ người ta hay hỏi. Đáp án là suy luận của người biên soạn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một hình và danh sách mười lăm khái niệm. Bài này giữ nguyên mười lăm tên, chia thành bốn nhóm theo câu hỏi mà chúng trả lời, và thêm một phép đếm trên tài liệu ôn phỏng vấn để thấy khái niệm nào ít được nhắc.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/a-cheat-sheet-for-system-designs.md): mười lăm khái niệm. Cách chia nhóm và phép đếm là của người biên soạn.
- [donnemartin/system-design-primer tại commit ae9bbd7](https://github.com/donnemartin/system-design-primer/blob/ae9bbd7b02d90b9866215de185217d33f39ab733/README.md): tệp dùng để đếm; đọc ngày 2026-10-19.

Đã đọc nguồn ngày 2026-10-19. Phép đếm là của người biên soạn.
Bài viết và hình được thiết kế độc lập.
