# Ôn phỏng vấn kỹ thuật: từ danh sách tài liệu đến kế hoạch luyện

**Một danh sách tài liệu chưa phải kế hoạch ôn.** Kế hoạch trả lời ba câu hỏi: bạn sắp gặp vòng nào, vòng lặp luyện của vòng đó gồm những gì, và người đưa ra lời gợi ý có lợi gì khi bạn chọn tài liệu đó.

![Năm khung dọc. Một: danh sách tài liệu chưa phải kế hoạch; hãy xác định vòng phỏng vấn trước. Hai: mỗi vòng có một vòng lặp luyện riêng; coding là giải rồi nói to cách nghĩ, thiết kế hệ thống là bốn bước từ yêu cầu đến mở rộng, hành vi là ba đến năm câu chuyện kể theo STAR. Ba: thời gian còn lại quyết định độ sâu; ít thời gian thì học rộng, nhiều thời gian thì học sâu và làm nhiều bài hơn. Bốn: hỏi ai được lợi; cùng một khóa học xuất hiện ở nhiều nơi thì chưa phải bằng chứng độc lập về chất lượng, và README của Handbook có chín lần xuất hiện tham số kiểu mã giới thiệu còn README của Primer không có. Năm: kiểm tra giá, ngày cập nhật và phản hồi nhận được trước khi trả tiền.](../../diagrams/sd-05-005-main.svg)

## Từ viết tắt

- **STAR** (Situation, Task, Action, Result) — tình huống, nhiệm vụ, hành động, kết quả: bốn bước để kể một câu chuyện công việc khi trả lời câu hỏi phỏng vấn hành vi.
- **OOD** (Object-Oriented Design) — thiết kế hướng đối tượng: chia chương trình thành các "đối tượng" có dữ liệu và hành vi riêng; một dạng câu hỏi trong phỏng vấn.

## Đọc hình

Các ý dưới đây rút từ ba tài liệu công khai đọc ngày 2026-10-16: danh sách của bài nguồn ByteByteGo, phần giới thiệu của kho Tech Interview Handbook cùng trang hướng dẫn phỏng vấn hành vi của kho đó, và phần giới thiệu của kho System Design Primer. Bản đọc là nhánh chính lúc đó, không ghim phiên bản.

1. **Vòng nào trước, tài liệu sau.** Bài nguồn xếp tài liệu theo sáu mảng: coding, thiết kế hệ thống, hành vi, thiết kế hướng đối tượng, phỏng vấn thử, tìm việc. Nếu thư mời chỉ nói vòng "thiết kế hệ thống", ba mảng kia có thể để sau. Primer nói thẳng là không cần biết hết mọi thứ, và mức độ đòi hỏi phụ thuộc kinh nghiệm, vị trí, công ty (mục "Study guide").
2. **Mỗi vòng có vòng lặp luyện khác nhau.** *Hành vi:* hướng dẫn của Tech Interview Handbook khuyên tập hợp 3–5 dự án có tác động lớn và có phần đóng góp rõ của bạn, kể mỗi dự án theo STAR, thay vì học thuộc từng câu hỏi; nó cũng nêu ba câu rất hay gặp nên chuẩn bị riêng (tự giới thiệu, dự án tâm đắc nhất, một lần giải quyết xung đột) và khuyên ghi ý chính ra rồi tập nói to, không học thuộc. *Thiết kế hệ thống:* Primer đưa bốn bước: làm rõ trường hợp dùng, ràng buộc và giả định; phác thiết kế tổng thể; đào sâu các thành phần chính; mở rộng và xử lý điểm nghẽn (bài [Làm tốt phỏng vấn thiết kế hệ thống: bảy bước](../sd-05-004/lesson.md) trình bày một khung bảy bước khác để dẫn dắt cuộc trò chuyện). *Coding:* mảng này bài nguồn chỉ liệt kê tên; cách luyện (giải, nói to, đối chiếu lời giải, giải lại) là gợi ý chung của người biên soạn, không phải lấy từ ba tài liệu.
3. **Thời gian quyết định độ sâu.** Bảng "Study guide" của Primer chia ba mức thời gian (ngắn, vừa, dài). Cả ba đều đọc các chủ đề thiết kế hệ thống để có cái nhìn rộng; điểm khác là số bài có lời giải nên làm: một số, nhiều, hầu hết. Nghĩa là thời gian ngắn thì rộng trước, chưa nên dồn vào một đề.
4. **Hỏi ai được lợi.** Danh sách của bài nguồn nêu Grokking the System Design (Design Gurus). README của Tech Interview Handbook cũng giới thiệu khóa học Grokking (cả bản coding lẫn bản thiết kế hệ thống) và khóa System Design Interview của ByteByteGo, kèm các liên kết có tham số. Đếm bằng một lệnh `grep` các tham số kiểu mã giới thiệu (`aff=`, `fpr=`, `afftrack=`, `ref=`): README của Handbook có 9 lần xuất hiện, trang hướng dẫn phỏng vấn hành vi của nó có 5, còn README của Primer không có lần nào. Tham số kiểu này thường dùng để ghi nhận ai giới thiệu một người mua; bài không biết có khoản tiền nào được trả hay không, và không kết luận gì về chất lượng của các khóa học. Điều rút ra là khác: một cái tên khóa học xuất hiện ở hai nơi, mỗi nơi có thể có lý do riêng để nhắc tới nó, thì hai lần nhắc không phải hai lần kiểm chứng độc lập.
5. **Kiểm tra trước khi trả tiền.** Giá, nội dung và sự tồn tại của một tài liệu đổi nhanh. Hỏi: nó còn được cập nhật không, nó dạy bạn luyện hay chỉ cho bạn đọc, bạn có nhận được phản hồi về cách làm của mình không, và có bản miễn phí đủ để thử không.

## Giới hạn cần nhớ

Bài chỉ đọc ba tài liệu và đếm tham số liên kết; không dùng thử từng khóa học, không so sánh chất lượng và không biết các lời gợi ý có trả phí hay không. Các mục tài nguyên còn lại của bài nguồn (khóa học, sách, nền tảng phỏng vấn thử, trang tuyển dụng) không được kiểm còn hoạt động hay còn phù hợp. Vòng lặp luyện cho coding và thiết kế hướng đối tượng, và cách chia thời gian, là ý kiến của người biên soạn.

## Nhìn hình thử trả lời

Bạn có ba tuần, đã giải nhiều bài thuật toán, và vòng sắp tới là thiết kế hệ thống. Theo hình, bạn nên ưu tiên gì, và có nên mua ngay một khóa học được hai nơi cùng nhắc tới không?

<details>
<summary>Xem đáp án</summary>

Ưu tiên học rộng các chủ đề thiết kế hệ thống, tập bốn bước trên một số đề có lời giải, rồi làm thêm đề nếu còn thời gian. Chưa nên mua ngay: hai nơi cùng nhắc một khóa học không phải hai bằng chứng độc lập, nhất là khi có liên kết kiểu mã giới thiệu. Hãy thử bản miễn phí hoặc tài liệu công khai như Primer trước, rồi mới quyết định mua gì để lấp đúng khoảng trống bạn thấy.

</details>

<details>
<summary>Xem sâu hơn: tự kiểm một danh sách, và danh sách bài nguồn nêu</summary>

Tự kiểm một kho tài liệu có liên kết giới thiệu hay không (thay đường dẫn bằng kho bạn quan tâm):

```sh
curl -fsS -o readme.md https://raw.githubusercontent.com/donnemartin/system-design-primer/master/README.md \
  && grep -o -E '[?&](aff|fpr|afftrack|ref)=[^) &"]*' readme.md | wc -l
```

Lệnh trên in `0` với README của Primer ngày thử. Đổi đường dẫn thành `https://raw.githubusercontent.com/yangshun/tech-interview-handbook/main/README.md` thì in `9`: 4 lần `afftrack=`, 4 lần `?aff=kJSIoU` và 1 lần `?fpr=techinterviewhandbook`. Tải bằng `curl -fsS` để một lần tải lỗi (không có mạng, sai đường dẫn) báo lỗi và không in số nào, nhờ đó `0` thật khác với tải hỏng; không dùng `curl -s` trần cùng một đường ống vì khi đó cả hai trường hợp đều không in gì. Nhớ rằng nội dung của các nhánh chính đổi theo thời gian, nên kết quả của bạn có thể khác.

Bài nguồn liệt kê ba mục cho mỗi mảng trong sáu mảng (tổng cộng 18 mục), gồm sách, khóa học, kênh video, nền tảng phỏng vấn thử và trang tuyển dụng. Danh sách đầy đủ nằm ở bài nguồn (liên kết ở phần cuối); bài này chỉ phân tích những mục đã nêu ở trên và không kiểm các mục còn lại.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/my-recommended-materials-for-cracking-your-next-technical-interview.md): danh sách tài nguyên theo sáu mảng.
- [Tech Interview Handbook — README](https://github.com/yangshun/tech-interview-handbook) và [trang hướng dẫn phỏng vấn hành vi](https://github.com/yangshun/tech-interview-handbook/blob/main/apps/website/contents/behavioral-interview.md): STAR, 3–5 câu chuyện, ba câu hay gặp, các liên kết khóa học. Đọc ngày 2026-10-16.
- [System Design Primer — README](https://github.com/donnemartin/system-design-primer): mục Study guide, bốn bước, không có tham số kiểu mã giới thiệu. Đọc ngày 2026-10-16.

Phần cách luyện coding và thiết kế hướng đối tượng, và cách xếp ưu tiên khi thiếu thời gian, là gợi ý chung của người biên soạn, không phải tuyên bố có nguồn. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.
