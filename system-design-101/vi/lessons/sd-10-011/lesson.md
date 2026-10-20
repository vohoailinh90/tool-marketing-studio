# Big endian và little endian: thứ tự byte trong bộ nhớ

**Một số nguyên nhiều byte có thể nằm trong bộ nhớ theo hai thứ tự: byte trọng số thấp nhất trước (little endian) hoặc byte trọng số cao nhất trước (big endian).**
Bài nguồn gọi chung hai kiểu này là thứ tự byte; bài này giữ tên little endian, big endian và câu hỏi vì sao thứ tự byte quan trọng, rồi giải thích bằng ví dụ và lời khuyên trong tài liệu của Python.

![Bốn nhóm xếp dọc. Big endian với số 1023 hay 0x3ff: byte trọng số cao nhất 03 nằm ở địa chỉ thấp nhất, byte trọng số thấp nhất ff ở địa chỉ kế tiếp. Little endian với số 1023: byte trọng số thấp nhất ff nằm ở địa chỉ thấp nhất, byte trọng số cao nhất 03 ở địa chỉ kế tiếp. Dùng ở đâu: little endian ở Intel x86, AMD64 và Apple M1; big endian ở IBM z, nhiều kiến trúc cũ và trong thứ tự mạng. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-011-main.svg)

## Từ viết tắt

- **IBM** (International Business Machines) — tên một hãng máy tính; bài nhắc dòng máy IBM z, một dòng dùng big endian.
- **AMD** (Advanced Micro Devices) — tên một hãng bộ xử lý; AMD64 là tên một kiến trúc x86 64 bit, dùng little endian.
- **IETF** (Internet Engineering Task Force) — lực lượng đặc nhiệm kỹ thuật Internet: tổ chức soạn các chuẩn của Internet; tài liệu Python dẫn một chuẩn của nó khi nói về thứ tự mạng.

## Đọc hình

Tên các thứ tự là của bài nguồn. Ví dụ, danh sách máy và lời khuyên dưới đây lấy từ tài liệu mô-đun `struct` của Python; cách giải thích là của người biên soạn.

**Ví dụ: số 1023.** Tài liệu `struct` dùng chính số này. Viết thập lục phân, 1023 là `0x3ff`, nên khi lưu thành hai byte thì byte trọng số cao nhất là `03` và byte trọng số thấp nhất là `ff`. Hai tên này gọi theo vị trí trong số, không theo việc `03` nhỏ hơn `ff`: byte trọng số cao nhất là byte ở hàng giá trị lớn nhất của số, byte trọng số thấp nhất là byte ở hàng đơn vị. Ở big endian, hai byte nằm theo thứ tự `03 ff`: byte trọng số cao nhất ở địa chỉ thấp nhất. Ở little endian, chúng nằm theo thứ tự `ff 03`: byte trọng số thấp nhất ở địa chỉ thấp nhất. Trong Python, `struct.pack('>h', 1023)` ra `03 ff` và `struct.pack('<h', 1023)` ra `ff 03`.

**Little endian.** Tài liệu `struct` nói thứ tự gốc của máy là big endian hoặc little endian tùy máy chủ; Intel x86, AMD64 và Apple M1 là little endian.

**Big endian.** Cũng theo tài liệu đó, IBM z và nhiều kiến trúc cũ là big endian. Thứ tự mạng (network byte order) luôn là big endian; tài liệu dẫn chuẩn của IETF làm gốc cho điều này, mà bài không đọc trực tiếp.

**Vì sao quan trọng.** Tài liệu `struct` khuyên: khi trao đổi dữ liệu ra ngoài tiến trình, như qua mạng hay lưu trữ, hãy nêu rõ thứ tự byte và đừng giả định nó giống thứ tự gốc của máy mình, vì thứ tự mạng là big endian còn nhiều bộ xử lý phổ biến là little endian. Nhờ nêu rõ, người viết mã không phải bận tâm máy chạy mã là loại nào. Nhân Linux cũng có sẵn các hàm `htonl`, `htons`, `ntohl`, `ntohs` để đổi số giữa dạng mạng và dạng máy (chú thích trong tệp `byteorder/generic.h`).

## Giới hạn cần nhớ

Thứ tự byte nói về cách xếp **byte** của một số trong bộ nhớ, không phải về thứ tự các bit trong một byte.
Bài nguồn nêu thêm PowerPC và Motorola 68k đời cũ là big endian, và nói big endian cũng được dùng khi lưu tệp; các tài liệu đã đọc không có hai điều đó nên bài này không lặp lại. Bài không nói máy nào "nhanh hơn" và không có mã ngoài hai lệnh ví dụ ở trên. Dùng `sys.byteorder` trong Python để biết máy mình dùng kiểu nào.

## Nhìn hình trả lời

Một chương trình trên máy little endian ghi số 1023 thành hai byte rồi gửi nguyên hai byte đó cho một máy big endian. Máy nhận đọc hai byte theo thứ tự của chính nó. Chuyện gì xảy ra?

<details>
<summary>Xem đáp án</summary>

Máy little endian gửi `ff 03`. Máy big endian coi byte đầu tiên là byte trọng số cao nhất nên đọc thành `0xff03`, tức 65283 nếu hiểu là số nguyên không dấu hai byte (phép tính của người biên soạn), thay vì 1023.
Vì thế khi gửi dữ liệu ra ngoài cần nêu rõ thứ tự byte, và thứ tự mạng là big endian.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh và ba phần ngắn: little endian, big endian, vì sao quan trọng. Bài này chỉ giữ các tên đó; không dịch hay diễn đạt lại các câu của nguồn mà dùng ví dụ 1023, danh sách máy và lời khuyên của tài liệu Python `struct` (tại commit cố định ở mục nguồn) cùng chú thích của nhân Linux, và thêm câu hỏi kiểm tra.
Hai chi tiết của nguồn mà các tài liệu đã đọc không có (PowerPC và Motorola 68k, lưu tệp) bị bỏ. Bài không dùng ảnh nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/big-endian-vs-little-endian.md): tên little endian, big endian và câu hỏi vì sao thứ tự byte quan trọng.
- [Python — tài liệu mô-đun struct](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/struct.rst): ví dụ 1023, các máy little endian và big endian, thứ tự mạng, lời khuyên khi trao đổi dữ liệu. Đọc từ kho mã.
- [Linux — include/linux/byteorder/generic.h](https://github.com/torvalds/linux/blob/32c52ec87d6245ee2d12ed5dd509e40062939b50/include/linux/byteorder/generic.h): các hàm đổi giữa dạng mạng và dạng máy. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-19. Phép đổi `ff03` thành 65283 và giải nghĩa IBM, AMD là của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.
