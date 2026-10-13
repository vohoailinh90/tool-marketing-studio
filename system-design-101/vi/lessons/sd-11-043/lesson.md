# CAP, BASE, SOLID và KISS nói về điều gì?

Các chữ viết tắt này thuộc những phạm vi khác nhau. CAP là kết quả về hệ lưu trữ phân tán: khi có network partition, không thể đồng thời bảo đảm linearizability và availability theo định nghĩa của định lý cho mọi yêu cầu liên quan.

![CAP: Partition: C/A không cùng đủ: C ở đây là linearizability; BASE: Available • soft • eventual: Điều kiện hội tụ phải rõ; SOLID + KISS: Nguyên tắc cấu trúc mã: Giữ giải pháp đơn giản.](../../diagrams/sd-11-043-main.svg)

**Đọc hình:** Các khung tóm tắt vai trò hoặc lựa chọn để đối chiếu. Các con số và tình huống trong bài là ví dụ minh họa, trừ khi ghi rõ cách tính.

BASE thường diễn đạt Basically Available, Soft state, Eventual consistency. Nó hướng tới chấp nhận trạng thái tạm thời chưa đồng nhất trong một số thiết kế; eventual consistency cần điều kiện cập nhật và hội tụ phù hợp. Nó không phải luật rằng mọi NoSQL đều bỏ ACID.

SOLID gồm single responsibility, open/closed, Liskov substitution, interface segregation và dependency inversion, hướng tới cấu trúc mã dễ thay đổi. KISS nhắc chọn giải pháp đơn giản đáp ứng bài toán.

Với bán vé, CAP giúp hỏi hành vi khi các vùng không liên lạc; SOLID giúp tổ chức mã kiểm tra đặt vé. Không dùng một acronym để thay phân tích nhu cầu hoặc phân loại cả sản phẩm DB bằng một nhãn.

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
