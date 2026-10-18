# Hàng đợi chặn và hàng đợi không chặn

**Hàng đợi chặn bắt luồng phải chờ khi khóa đang bị giữ; hàng đợi không chặn báo ngay là bị từ chối. Khác biệt đó quyết định thời gian chờ và nguy cơ khóa chết.**
Bài nguồn bắt đầu từ chính bộ từ vựng hay gây nhầm: chặn, không chặn, bị bỏ đói, không bỏ đói, không chờ. Bài này đọc từng từ rồi nói cách làm hàng đợi không chặn.

![Bốn nhóm xếp dọc. Hàng đợi chặn, một chuỗi tin: luồng A lấy khóa và truy cập hàng đợi; luồng B xin truy cập; hàng đợi bắt B đợi tới khi khóa được nhả. Hàng đợi không chặn, một chuỗi tin: luồng B xin truy cập; hàng đợi từ chối ngay; luồng A truy cập và làm xong trong số bước nhất định. Hai tính chất: không bị bỏ đói nghĩa là không luồng nào bị chặn mãi khỏi tài nguyên chia sẻ; wait-free nghĩa là mọi luồng hoàn thành việc trong số bước hữu hạn. Khung cuối nêu ba lợi ích của hàng đợi không chặn: không treo luồng, không khóa chết và cài đặt bằng CAS.](../../diagrams/sd-10-010-main.svg)

## Từ viết tắt

- **CAS** (Compare And Swap) — so sánh rồi đổi: thao tác chỉ ghi giá trị mới nếu giá trị hiện tại vẫn đúng như luồng vừa đọc; nếu không, luồng thử lại. Hàng đợi không chặn trong bài dùng nó thay cho khóa.
- **JDK** (Java Development Kit) — bộ công cụ phát triển Java: gói gồm thư viện chuẩn và công cụ để viết, chạy chương trình Java; bài trích mã nguồn của nó để đối chiếu.

## Đọc hình

**Chặn.** Thuật toán chặn dùng khóa. Luồng A lấy khóa trước; nếu A bị tạm dừng khi đang giữ khóa, luồng B có thể phải chờ rất lâu và có thể bị bỏ đói.

**Không chặn.** Thuật toán không chặn cho luồng A truy cập hàng đợi nhưng A phải làm xong trong một số bước nhất định. Luồng B vẫn có thể bị bỏ đói vì bị từ chối.

**Khác biệt chính.** Thuật toán chặn giữ B lại cho tới khi khóa được nhả. Thuật toán không chặn báo cho B biết truy cập bị từ chối, và B tự quyết làm gì tiếp.

**Hai tính chất.** Bị bỏ đói (starvation) là khi một luồng không giành được quyền truy cập tài nguyên chia sẻ nên không tiến lên được; không bị bỏ đói (starvation-free) nghĩa là tình trạng đó không xảy ra. Wait-free nghĩa là mọi luồng hoàn thành việc trong số bước hữu hạn. Nguồn gói lại: wait-free bằng không chặn cộng không bị bỏ đói.

**Cài đặt.** Hàng đợi không chặn có thể dựng bằng CAS (Compare And Swap).

**Hai lợi ích.** Luồng không bị treo: B nhận phản hồi ngay, nên độ trễ của luồng giảm nhiều. Không có khóa chết (deadlock): A và B không chờ khóa được nhả nên không thể kẹt lẫn nhau.

**Gặp lại trong thư viện Java.** `BlockingQueue` là hàng đợi có thêm các thao tác chờ hàng đợi có phần tử khi lấy và chờ có chỗ khi thêm; `LinkedBlockingQueue` dùng `ReentrantLock`. `ConcurrentLinkedQueue` thì ghi trong tài liệu là dùng một thuật toán không chặn hiệu quả, và mã của nó cập nhật con trỏ bằng `compareAndSet`.

## Giới hạn cần nhớ

Không chặn không có nghĩa là mọi luồng đều thành công: theo nguồn, B vẫn có thể bị bỏ đói vì liên tục bị từ chối. Nó chỉ đổi cách B biết mình bị từ chối: nhận phản hồi ngay thay vì đợi khóa.
Bài nguồn dùng "không chặn" theo nghĩa của nó (A phải làm xong trong số bước nhất định); các tài liệu khác có thể chia các mức nhỏ hơn và đặt tên khác, và bài này không bàn tới chúng. Bài nguồn cũng không đưa mã hay số đo.

## Nhìn hình trả lời

Luồng A đang giữ khóa của một hàng đợi chặn thì bị hệ điều hành tạm dừng. Luồng B xin truy cập thì chuyện gì xảy ra? Với hàng đợi không chặn thì khác ở chỗ nào?

<details>
<summary>Xem đáp án</summary>

Với hàng đợi chặn, B phải đợi tới khi khóa được nhả, và vì A giữ khóa lúc bị dừng nên B có thể chờ rất lâu và bị bỏ đói.
Với hàng đợi không chặn, B được báo ngay là bị từ chối và tự quyết làm gì tiếp, không bị treo.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh và hai phần chính: so sánh các thuật ngữ rồi cách cài đặt bằng CAS, sau đó là hai lợi ích. Hình ở đây vẽ lại phần so sánh chặn và không chặn thành hai chuỗi tin giữa luồng A, hàng đợi và luồng B; bài không dùng ảnh nguồn.
Mục "Gặp lại trong thư viện Java" lấy từ mã nguồn JDK tại commit cố định ở mục nguồn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/blocking-vs-non-blocking-queue.md): chặn và không chặn, bỏ đói, wait-free, CAS, hai lợi ích.
- [OpenJDK — BlockingQueue](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/concurrent/BlockingQueue.java), [LinkedBlockingQueue](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/concurrent/LinkedBlockingQueue.java) và [ConcurrentLinkedQueue](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/concurrent/ConcurrentLinkedQueue.java): hàng đợi chặn dùng khóa, hàng đợi không chặn dùng so sánh rồi đổi. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-18. Giải nghĩa CAS trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.
