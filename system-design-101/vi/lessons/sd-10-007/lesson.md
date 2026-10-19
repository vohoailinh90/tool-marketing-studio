# Tám lĩnh vực hay dùng C++

**C++ thường được chọn khi chương trình cần chạy nhanh và tự quản lý tài nguyên của máy; tám lĩnh vực dưới đây là những nơi người ta hay đòi hai điều đó.**
Bài nguồn chỉ nêu tên tám lĩnh vực; bài này giữ đúng tám tên đó, xếp thành ba nhóm theo điều mỗi lĩnh vực đòi hỏi, và tự giải thích từng lĩnh vực bằng lời của người biên soạn cùng vài đoạn của C++ Core Guidelines.

![Ba nhóm thẻ xếp dọc. Gần phần cứng: hệ thống nhúng là thiết bị nhỏ nên phải tính kỹ việc cấp phát bộ nhớ động; hệ điều hành nói chuyện trực tiếp với phần cứng và quản lý bộ nhớ; mạng xử lý gói tin liên tục với độ trễ thấp. Cần chạy nhanh: game có ngân sách thời gian cố định cho mỗi khung hình; cơ sở dữ liệu quản lý bộ nhớ và bộ đệm để trả lời truy vấn nhanh; tính toán khoa học lặp rất nhiều phép tính trên lượng số liệu lớn. Còn lại: trình duyệt web chạy trên máy người dùng và phải nhanh lại gọn bộ nhớ; ứng dụng tài chính gồm nhiều loại phần mềm nên bài không nói thêm. Khung cuối nhắc ba điều cần nhớ.](../../diagrams/sd-10-007-main.svg)

## Đọc hình

Hình chia tám lĩnh vực theo điều chúng đòi hỏi ở một ngôn ngữ; cả cách chia lẫn lời giải thích dưới đây là của người biên soạn, chỉ có tên tám lĩnh vực là của bài nguồn.

**Nhóm 1 · Gần phần cứng.**
- Hệ thống nhúng là phần mềm chạy trong một thiết bị nhỏ, thường ít bộ nhớ và ít sức tính. C++ Core Guidelines nói rằng lập trình viên thời gian thực cứng thường không dùng thoải mái được vùng nhớ cấp phát động (free store) và bị giới hạn trong việc chọn thư viện; chúng cũng ghi rằng các bộ chứa của thư viện chuẩn dựa vào cấp phát động nên không hợp với một số ứng dụng thời gian thực cứng và nhúng, và gợi ý dựng bộ chứa theo kiểu thư viện chuẩn trên một bộ cấp phát theo hồ (pool allocator). Tức là ở đây người viết phải tự quyết định bộ nhớ được cấp ra sao.
- Hệ điều hành quản lý phần cứng và bộ nhớ cho các chương trình khác, nên mã của nó phải nói chuyện trực tiếp với phần cứng. Guidelines nhắc tới `volatile` cho đối tượng dùng chung với mã không phải C++ hoặc với phần cứng không theo mô hình bộ nhớ của C++. Việc viết hệ điều hành đòi những thao tác mức thấp như vậy là kiến thức chung của người biên soạn.
- Mạng ở đây là phần mềm xử lý gói tin chạy liên tục, nơi độ trễ mỗi gói cộng dồn lại; đó là lý do tốc độ và quyền kiểm soát bộ nhớ quan trọng (kiến thức chung của người biên soạn).

**Nhóm 2 · Cần chạy nhanh.**
- Game phải dựng xong từng khung hình trong một khoảng thời gian rất ngắn và cố định, nên thời gian chạy cần dự đoán được (kiến thức chung của người biên soạn).
- Cơ sở dữ liệu phải giữ dữ liệu trong bộ nhớ và trên đĩa rồi trả lời truy vấn nhanh; cách bố trí dữ liệu trong bộ nhớ ảnh hưởng trực tiếp tới tốc độ (kiến thức chung của người biên soạn).
- Tính toán khoa học lặp cùng một loại phép tính rất nhiều lần trên lượng số liệu lớn, nên sức tính là tài nguyên chính (kiến thức chung của người biên soạn). Cả ba lĩnh vực hưởng lợi từ nguyên tắc "không trả giá cho thứ mình không dùng" mà Guidelines nêu: dùng một cơ chế trừu tượng đúng cách thì hiệu năng ít nhất bằng viết tay bằng cấu trúc mức thấp.

**Nhóm 3 · Hai lĩnh vực còn lại.**
- Trình duyệt web chạy trên máy của người dùng, nơi mở nhiều trang cùng lúc và phải vừa nhanh vừa không ngốn bộ nhớ (kiến thức chung của người biên soạn).
- Ứng dụng tài chính gồm rất nhiều loại phần mềm khác nhau, từ ứng dụng giao diện tới hệ thống xử lý giao dịch, nên bài này không nói thêm về lĩnh vực đó.

## Giới hạn cần nhớ

Bài nguồn chỉ nêu tên tám lĩnh vực: không so sánh C++ với ngôn ngữ khác, không nêu sản phẩm cụ thể và không đưa số liệu. Bài này cũng vậy.
Phần lớn lời giải thích ở trên là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn; chỉ các câu về cấp phát động, `volatile` và nguyên tắc không trả giá cho thứ không dùng được đối chiếu với C++ Core Guidelines. Một lĩnh vực dùng C++ không có nghĩa C++ là lựa chọn duy nhất hay tốt nhất ở đó.

## Nhìn hình trả lời

Một nhóm viết phần mềm cho một thiết bị nhỏ, ít bộ nhớ. Theo C++ Core Guidelines, điều gì trong thư viện chuẩn thường phải tính kỹ ở lĩnh vực này, và hướng gợi ý là gì?

<details>
<summary>Xem đáp án</summary>

Đó là hệ thống nhúng. Guidelines ghi rằng các bộ chứa của thư viện chuẩn dựa vào cấp phát động nên không hợp với một số ứng dụng thời gian thực cứng và nhúng, còn các thuật toán thì không bị vậy. Hướng gợi ý là dùng hoặc tự viết bộ chứa theo kiểu thư viện chuẩn trên một bộ cấp phát theo hồ.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn liệt kê tám lĩnh vực theo thứ tự hệ thống nhúng, game, hệ điều hành, cơ sở dữ liệu, ứng dụng tài chính, trình duyệt web, mạng, tính toán khoa học, mỗi mục một câu; riêng ứng dụng tài chính không có câu nào. Bài này chỉ giữ tên tám lĩnh vực; không dịch hay diễn đạt lại các câu mô tả đó mà tự giải thích từng lĩnh vực theo điều nó đòi hỏi, dựa vào C++ Core Guidelines ở ba chỗ đã nêu, còn lại là kiến thức chung của người biên soạn.
Hình gom thành ba nhóm theo điều đòi hỏi. Bài không dùng ảnh của nguồn và không thêm sản phẩm hay số liệu.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-8-c++-use-cases.md): tên tám lĩnh vực.
- [C++ Core Guidelines — tại commit cố định](https://github.com/isocpp/CppCoreGuidelines/blob/33bcd015997f0d8e0fa0202eb66254a16f59ad8f/CppCoreGuidelines.md): nguyên tắc không trả giá cho thứ không dùng, giới hạn của lập trình viên thời gian thực cứng, bộ chứa chuẩn và cấp phát động, `volatile` cho bộ nhớ dùng chung với phần cứng. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-19. Mọi câu về từng lĩnh vực không dẫn Guidelines là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.
