# CAP, BASE, SOLID và KISS nói về điều gì?

Các chữ viết tắt này thuộc những phạm vi khác nhau. CAP là kết quả về hệ lưu trữ phân tán: khi có network partition, không thể đồng thời bảo đảm linearizability và availability theo định nghĩa của định lý cho mọi yêu cầu liên quan.

![CAP: Partition: C/A không cùng đủ: C ở đây là linearizability; BASE: Available • soft • eventual: Điều kiện hội tụ phải rõ; SOLID + KISS: Nguyên tắc cấu trúc mã: Giữ giải pháp đơn giản.](../../diagrams/sd-11-043-main.svg)

**Đọc hình:** Các khung tóm tắt vai trò hoặc lựa chọn để đối chiếu. Các con số và tình huống trong bài là ví dụ minh họa, trừ khi ghi rõ cách tính.

BASE thường diễn đạt Basically Available, Soft state, Eventual consistency. Nó hướng tới chấp nhận trạng thái tạm thời chưa đồng nhất trong một số thiết kế; eventual consistency cần điều kiện cập nhật và hội tụ phù hợp. Nó không phải luật rằng mọi NoSQL đều bỏ ACID.

SOLID gồm single responsibility, open/closed, Liskov substitution, interface segregation và dependency inversion, hướng tới cấu trúc mã dễ thay đổi. KISS nhắc chọn giải pháp đơn giản đáp ứng bài toán.

Với bán vé, CAP giúp hỏi hành vi khi các vùng không liên lạc; SOLID giúp tổ chức mã kiểm tra đặt vé. Không dùng một acronym để thay phân tích nhu cầu hoặc phân loại cả sản phẩm DB bằng một nhãn.

## Từ viết tắt

- **CAP** (Consistency, Availability, Partition) — nhất quán, sẵn sàng, chịu phân vùng: định lý nói khi mạng bị chia cắt, hệ phân tán không giữ được cả nhất quán lẫn sẵn sàng; trong bài, chữ C ở đây là linearizability.
- **BASE** (Basically Available, Soft state, Eventual consistency) — sẵn sàng ở mức cơ bản, trạng thái mềm, nhất quán sau cùng: cách nhìn của nhiều hệ phân tán khi chấp nhận dữ liệu chưa khớp ngay giữa các bản sao.
- **SOLID** (Single responsibility, Open-closed, Liskov substitution, Interface segregation, Dependency inversion) — năm nguyên tắc thiết kế hướng đối tượng: một lý do thay đổi cho mỗi thành phần, mở cho mở rộng nhưng đóng với sửa đổi, kiểu con thay được kiểu cha, giao diện nhỏ gọn, phụ thuộc vào trừu tượng; bài dùng SOLID để tổ chức mã kiểm tra đặt vé.
- **KISS** (Keep It Simple, Stupid) — giữ cho đơn giản: nguyên tắc nên chọn thiết kế đơn giản nhất đáp ứng được yêu cầu.
- **ACID** (Atomicity, Consistency, Isolation, Durability) — bốn tính chất của một giao dịch đáng tin: làm trọn hoặc không làm, giữ dữ liệu hợp lệ, các giao dịch không lẫn vào nhau, đã ghi thì không mất; bài nói NoSQL không có luật rằng mọi hệ đều bỏ ACID.
- **NoSQL** (Not only SQL) — tên chung cho các cơ sở dữ liệu không theo mô hình bảng quan hệ, như kho tài liệu hay kho khóa–giá trị; nhãn NoSQL không đủ để phân loại cả sản phẩm DB.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; chữ SQL nằm trong tên NoSQL.
- **DB** (DataBase) — cơ sở dữ liệu: nơi lưu dữ liệu có tổ chức để ghi và tìm lại; đừng phân loại cả sản phẩm DB bằng một nhãn viết tắt.
- **SRP** (Single Responsibility Principle) — nguyên tắc một trách nhiệm: một thành phần chỉ nên có một lý do để thay đổi.
- **LSP** (Liskov Substitution Principle) — nguyên tắc thay thế Liskov: kiểu con phải dùng được ở nơi kiểu cha mà không phá hợp đồng hành vi.
- **SLO** (Service Level Objective) — mục tiêu mức dịch vụ: con số cam kết về độ tin cậy, như tỉ lệ yêu cầu thành công trong một khoảng thời gian; bài nói availability trong CAP khác tỷ lệ uptime hay SLO thông thường.

## Nhìn hình thử trả lời

Network partition xảy ra nhưng vẫn yêu cầu mọi phía bán đúng cùng một ghế và luôn trả kết quả thành công. Có bảo đảm cả hai không?

<details>
<summary>Xem đáp án</summary>

Không theo giả định CAP và yêu cầu nhất quán chặt này; cần từ chối/chờ ở một phía hoặc chấp nhận hành vi nhất quán khác.

</details>

## Giới hạn cần nhớ

CAP không phải lựa chọn tùy ý “hai trong ba” trong mọi lúc. Availability trong CAP khác tỷ lệ uptime/SLO thông thường.

<details>
<summary>Xem sâu hơn</summary>

SRP liên quan một lý do thay đổi, LSP liên quan giữ hợp đồng hành vi khi thay kiểu. Áp dụng nguyên tắc qua ví dụ thực tế, tránh tạo abstraction chỉ để đủ chữ.

</details>

## Nguồn đối chiếu

- [Mục chủ đề ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/cap-base-solid-kiss-what-do-these-acronyms-mean.md).
- [www.comp.nus.edu.sg — BrewersConjecture-SigAct.pdf](https://www.comp.nus.edu.sg/~gilbert/pubs/BrewersConjecture-SigAct.pdf).
- [Is Design Dead?](https://martinfowler.com/articles/designDead.html).

Bài giải thích và hình được biên soạn độc lập; không dùng ảnh nguồn. Các tài liệu kỹ thuật trên là điểm đối chiếu cho review, không phải chứng nhận mọi claim đã được kiểm chứng.
