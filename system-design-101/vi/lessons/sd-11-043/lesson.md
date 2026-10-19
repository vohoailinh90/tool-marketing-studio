# CAP, BASE, SOLID, KISS: bốn từ viết tắt, và một thử nghiệm với CAP

**Bốn từ viết tắt này thuộc hai thế giới khác nhau: CAP và BASE nói về dữ liệu trải trên nhiều máy, SOLID và KISS nói về cách viết và tổ chức mã. Điểm dễ hiểu sai nhất là CAP, vì mạng đứt là chuyện chắc chắn xảy ra, nên câu hỏi thật là "khi mạng đứt, bạn chọn trả lời hay chọn đúng".**
Bài chạy một mô phỏng hai bản sao dữ liệu trong lúc mạng đứt để thấy lựa chọn đó cụ thể ra sao, rồi giải thích BASE, SOLID và KISS ngắn gọn.

![Bốn khung. Khung một, CAP: khi mạng đứt phải chọn giữa trả lời đúng hoặc từ chối, và trả lời nhanh nhưng có thể cũ. Khung hai, mô phỏng hai bản sao khi mạng đứt: hệ thống ưu tiên đúng từ chối ba lượt đọc, hệ thống ưu tiên trả lời trả giá trị cũ ba lượt rồi hội tụ. Khung ba, BASE: sẵn sàng cơ bản, trạng thái mềm, nhất quán cuối cùng. Khung bốn, SOLID là năm nguyên tắc về mã; KISS là giữ cho đơn giản.](../../diagrams/sd-11-043-main.svg)

## Từ viết tắt

- **CAP** (Consistency, Availability, Partition) — nhất quán, sẵn sàng, phân mảnh mạng (chữ P là "chịu được phân mảnh mạng", partition tolerance): ba tính chất mà định lý CAP nói một kho dữ liệu phân tán không thể cùng lúc bảo đảm đầy đủ khi mạng đứt.
- **BASE** (Basically Available, Soft state, Eventual consistency) — sẵn sàng cơ bản, trạng thái mềm, nhất quán cuối cùng: nguyên tắc nới lỏng hơn ACID, ưu tiên trả lời được và chấp nhận dữ liệu tạm thời lệch giữa các bản sao.
- **ACID** (Atomicity, Consistency, Isolation, Durability) — nguyên tử, nhất quán, cô lập, bền vững: bốn bảo đảm của một giao dịch trong cơ sở dữ liệu quan hệ.
- **SOLID** (Single responsibility, Open-closed, Liskov substitution, Interface segregation, Dependency inversion) — năm nguyên tắc thiết kế mã hướng đối tượng, mỗi chữ cái là đầu của một nguyên tắc.
- **KISS** (Keep It Simple, Stupid) — hãy giữ cho đơn giản: nguyên tắc nói hầu hết hệ thống chạy tốt nhất khi được giữ đơn giản.

## Đọc hình

**CAP.** Bài nguồn phát biểu: một kho dữ liệu phân tán chỉ cung cấp được hai trong ba bảo đảm: nhất quán (mỗi lượt đọc nhận được lượt ghi gần nhất hoặc một lỗi), sẵn sàng (mỗi yêu cầu nhận được trả lời), và chịu được phân mảnh mạng (hệ thống vẫn chạy khi mạng lỗi). Nguồn cũng nhắc định lý này bị chỉ trích là quá hẹp, và đừng dùng nó để xếp cơ sở dữ liệu vào nhóm "ưu tiên nhất quán" hay "ưu tiên sẵn sàng"; vì lỗi mạng chắc chắn xảy ra trong hệ thống phân tán, hệ thống nào cũng phải đối phó với nó. Nguồn dẫn một bài của Martin Kleppmann về chuyện này; bài này không đọc được bài đó từ máy biên soạn nên chỉ nhắc lại như lời của nguồn.

**BASE.** Mô hình ACID của cơ sở dữ liệu quan hệ quá chặt với một số kho không quan hệ, nên nguyên tắc BASE nới ra: chọn sẵn sàng thay vì nhất quán, và trạng thái sẽ nhất quán sau một lúc.

**SOLID.** Năm nguyên tắc: mỗi đơn vị mã một trách nhiệm; mở cho mở rộng, đóng với sửa đổi; lớp con thay được lớp cha; nhiều giao diện nhỏ thay cho một giao diện lớn; phụ thuộc vào trừu tượng. Nguồn mô tả từng nguyên tắc bằng một câu.

**KISS.** Nguồn nói nguyên tắc này được Hải quân Mỹ ghi nhận lần đầu năm 1960. Bài không kiểm lời đó.

## Thử: mô phỏng CAP với hai bản sao

Ngày 2026-10-19, người biên soạn viết một mô phỏng thời gian ảo: hai bản sao A và B của một giá trị `x` (ban đầu 0), mạng giữa hai bản đứt từ giây 3 đến hết giây 6. Máy khách ghi `x = 1` vào A từ giây 4 (thử lại mỗi giây nếu bị từ chối) và đọc `x` từ B mỗi giây từ giây 4 đến giây 9, sáu lượt đọc. Sau khi mạng nối lại, B được sao từ A.

- **Ưu tiên nhất quán (từ chối khi không chắc).** Một lượt ghi cần cả hai bản, nên ba lần thử ghi đầu (giây 4, 5, 6) bị từ chối; ba lượt đọc trong lúc đứt cũng bị từ chối. Sau khi nối lại, lượt ghi qua được và cả ba lượt đọc còn lại trả giá trị mới nhất (1). Không có lượt đọc nào trả giá trị cũ, nhưng nửa số lượt đọc không có câu trả lời.
- **Ưu tiên sẵn sàng (luôn trả lời).** Lượt ghi vào A thành công ngay ở giây 4. Ba lượt đọc từ B trong lúc đứt trả 0, giá trị cũ; B chưa nhận được thay đổi. Sau khi nối lại B được sao và ba lượt đọc còn lại trả 1. Không lượt đọc nào bị từ chối, nhưng nửa số lượt cho giá trị cũ.

Đây là hình dạng của lựa chọn: lúc mạng đứt, một hệ thống đổi câu trả lời lỗi lấy tính đúng, hệ thống kia đổi tính đúng tạm thời lấy câu trả lời. Phần "sau khi nối lại, B hội tụ về giá trị mới" chính là ý "nhất quán cuối cùng" của BASE. Mô phỏng đơn giản hóa mạnh: chỉ hai bản, một giá trị, một lần đứt, sao chép tức thì khi nối lại; nó minh họa chứ không chứng minh định lý.

## Giới hạn cần nhớ

Cách phát biểu CAP và các phê bình của nó ở đây theo bài nguồn, chưa đối chiếu với bài báo gốc về định lý; mô phỏng không thay cho chứng minh. Các nguyên tắc SOLID và KISS được nêu ngắn như nguồn; bài không kiểm lịch sử của chúng và không cho ví dụ mã. Bốn từ viết tắt này không cùng cấp độ: không nên đặt CAP cạnh KISS như hai lựa chọn của cùng một quyết định.

## Nhìn hình trả lời

Một ứng dụng đặt vé phải chọn giữa "từ chối đặt vé khi hai trung tâm dữ liệu mất liên lạc" và "vẫn nhận đặt vé rồi đối chiếu sau". Theo thử nghiệm trên, mỗi lựa chọn đổi cái gì lấy cái gì?

<details>
<summary>Xem đáp án</summary>

Từ chối đặt vé giữ cho dữ liệu đúng (không bán trùng ghế) và đổi lấy việc một số người dùng nhận lỗi trong lúc mạng đứt. Vẫn nhận đặt vé giữ cho dịch vụ luôn trả lời và đổi lấy khả năng hai bên cùng bán một ghế, phải xử lý khi đối chiếu. Cách nào hợp tùy nghiệp vụ; đây là suy luận từ mô phỏng, không phải quy tắc của nguồn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn gồm một hình và bốn đoạn ngắn cho CAP, BASE, SOLID, KISS. Bài này giữ bốn đoạn nhưng tách hai nhóm (dữ liệu và mã), nêu rõ rằng chúng khác cấp độ, và thêm một mô phỏng cho CAP.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/cap-base-solid-kiss-what-do-these-acronyms-mean.md): phát biểu CAP, BASE, SOLID, KISS và lời chỉ trích; các lời này theo nguồn, chưa kiểm với bài gốc. Mô phỏng và lời bình là của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Mô phỏng là của người biên soạn; chưa đối chiếu bài báo gốc về CAP, BASE, SOLID (không mở được từ máy biên soạn).
Bài viết và hình được thiết kế độc lập.
