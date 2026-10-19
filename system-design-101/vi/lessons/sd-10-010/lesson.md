# Hàng đợi chặn và hàng đợi không chặn

**Hàng đợi chặn bắt luồng đứng đợi khi việc chưa làm được ngay; hàng đợi không chặn không bắt ai đợi mà để luồng thua một lượt thì thử lại. Khác biệt đó quyết định chuyện treo luồng và khóa chết.**
Bài nguồn bắt đầu từ chính bộ từ vựng hay gây nhầm: chặn, không chặn, không bị bỏ đói, wait-free. Bài này giữ đúng các tên đó, rồi giải thích từng ý bằng mã nguồn và tài liệu của thư viện Java.

![Bốn nhóm xếp dọc. Hàng đợi chặn, một chuỗi tin: luồng B lấy phần tử nhưng hàng đang trống nên phải đợi; luồng A thêm một phần tử; hàng đợi giao phần tử cho B. Hàng đợi không chặn, một chuỗi tin: luồng A gắn nút cuối bằng CAS; luồng B cùng lúc gắn nút bằng CAS; B thua CAS, đọc lại rồi thử tiếp. Hai tính chất: không bị bỏ đói nghĩa là luồng nào cũng có lúc được truy cập tài nguyên chia sẻ; wait-free nghĩa là mỗi luồng xong việc trong số bước hữu hạn. Khung cuối nêu ba điều cần nhớ về hàng đợi không chặn: không treo luồng, không có khóa nên không khóa chết, dựng bằng CAS.](../../diagrams/sd-10-010-main.svg)

## Từ viết tắt

- **CAS** (Compare And Swap) — so sánh rồi đổi: thao tác chỉ ghi giá trị mới nếu giá trị hiện tại vẫn đúng như luồng vừa đọc; nếu không, nó báo thất bại và luồng tự quyết làm gì tiếp. Hàng đợi không chặn trong bài dùng nó thay cho khóa.
- **JDK** (Java Development Kit) — bộ công cụ phát triển Java: gói gồm thư viện chuẩn và công cụ để viết, chạy chương trình Java; bài trích mã nguồn của nó để đối chiếu.

## Đọc hình

Cả cách kể bằng hai chuỗi tin lẫn lời giải thích dưới đây là của người biên soạn, dựa vào mã nguồn của JDK; chỉ có tên các khái niệm là của bài nguồn.

**Chặn.** Tài liệu của `BlockingQueue` mô tả đây là hàng đợi có thêm các thao tác đợi hàng đợi có phần tử khi lấy, và đợi có chỗ trống khi thêm. Với việc chưa làm được ngay, giao diện này có bốn kiểu: ném ngoại lệ, trả một giá trị đặc biệt (`null` hoặc `false`), chặn luồng cho tới khi làm được (`put` và `take`), hoặc chặn tối đa một khoảng thời gian rồi bỏ cuộc. Tài liệu nói các thao tác xếp hàng đạt hiệu quả nguyên tử nhờ khóa nội bộ hoặc cách kiểm soát đồng thời khác. Trong hình, B gọi lấy khi hàng đang trống nên phải đợi; khi A thêm một phần tử thì B mới được giao nó.

**Cài đặt bằng khóa.** Chú thích trong mã của `LinkedBlockingQueue` cho biết lớp này là một biến thể của thuật toán hàng đợi hai khóa: một khóa `putLock` cho phía thêm, một khóa `takeLock` cho phía lấy, cả hai là `ReentrantLock`. Luồng đang giữ một khóa thì luồng khác cần khóa đó phải đợi.

**Không chặn.** Lớp `ConcurrentLinkedQueue` ghi trong tài liệu là dùng một thuật toán không chặn hiệu quả, dựa trên bài báo của Michael và Scott. Mã của `offer` cho thấy cách làm: luồng đọc nút cuối, rồi dùng CAS (`compareAndSet`) để gắn nút mới vào sau nút đó. Nếu CAS thất bại vì luồng khác vừa gắn trước, chú thích trong mã ghi "lost CAS race", luồng đọc lại và lặp lại vòng thử. Không có luồng nào bị bắt đợi một khóa; hàm `offer` cũng không bao giờ trả `false` vì hàng không có giới hạn.

**Hai tính chất.** Bị bỏ đói (starvation) là khi một luồng không giành được quyền truy cập tài nguyên chia sẻ nên không tiến lên được; không bị bỏ đói nghĩa là điều đó không xảy ra. Wait-free nghĩa là mỗi luồng xong việc trong số bước hữu hạn. Đây là các định nghĩa chung, không nằm trong tài liệu JDK, nên chúng là kiến thức chung của người biên soạn.

**Gặp lại trong thư viện Java.** Cả hai loại đều có sẵn: `LinkedBlockingQueue` là hàng đợi chặn dùng hai khóa, còn `ConcurrentLinkedQueue` là hàng đợi không chặn dùng CAS.

## Giới hạn cần nhớ

Không chặn không có nghĩa là mọi luồng đều xong mọi lượt ngay: trong vòng lặp của `offer`, một luồng thua CAS phải thử lại, và chú thích trong mã không hứa nó thắng sau bao nhiêu lượt. Bài nguồn viết wait-free bằng không chặn cộng không bị bỏ đói; bài này không lặp lại công thức đó vì không kiểm được nó trong tài liệu JDK, và theo kiến thức chung của người biên soạn các mức đảm bảo này còn được chia nhỏ hơn.
Hàng đợi chặn cũng không bắt mọi thao tác phải đợi: `BlockingQueue` có sẵn kiểu trả `null` hoặc `false` ngay. Bài không so sánh tốc độ hai loại và không có mã.

## Nhìn hình trả lời

Luồng B gọi lấy phần tử từ một hàng đợi chặn đang trống. Chuyện gì xảy ra với B? Còn nếu hai luồng cùng gắn nút vào hàng đợi không chặn, luồng thua làm gì?

<details>
<summary>Xem đáp án</summary>

Với hàng đợi chặn, B bị chặn lại và đợi tới khi có phần tử, tức khi một luồng khác thêm vào.
Với hàng đợi không chặn, luồng thua CAS không đợi ai: nó đọc lại nút cuối rồi thử gắn tiếp.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh và ba phần: so sánh thuật ngữ, cách cài đặt bằng CAS, hai lợi ích. Bài này chỉ giữ tên các khái niệm; không dịch hay diễn đạt lại các câu của nguồn mà giải thích từng ý từ tài liệu và mã của `BlockingQueue`, `LinkedBlockingQueue`, `ConcurrentLinkedQueue` và `AtomicInteger` trong JDK (tại commit cố định ở mục nguồn), còn các định nghĩa bỏ đói và wait-free là kiến thức chung của người biên soạn.
Hình kể lại bằng hai chuỗi tin theo hành vi của thư viện, không theo ví dụ luồng A giữ khóa của nguồn; bài không dùng ảnh nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/blocking-vs-non-blocking-queue.md): tên các khái niệm: chặn, không chặn, không bị bỏ đói, wait-free, CAS.
- [OpenJDK — BlockingQueue](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/concurrent/BlockingQueue.java), [LinkedBlockingQueue](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/concurrent/LinkedBlockingQueue.java), [ConcurrentLinkedQueue](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/concurrent/ConcurrentLinkedQueue.java) và [AtomicInteger](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/concurrent/atomic/AtomicInteger.java): bốn kiểu thao tác, hai khóa, vòng thử lại bằng CAS, ý nghĩa của `compareAndSet`. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-19. Định nghĩa bị bỏ đói và wait-free là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.
