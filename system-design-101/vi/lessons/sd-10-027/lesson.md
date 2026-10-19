# Mười một bước từ lập trình viên mới vào nghề tới cấp cao

**Một dịch vụ mượn sách của thư viện nhỏ đi qua mười một bước của lộ trình: mỗi bước là một việc cụ thể bạn làm với dịch vụ đó.**
Tên mười một bước lấy từ bài nguồn (và thứ tự theo nguồn); việc làm ở mỗi bước, ví dụ và số đo là của bài này, đối chiếu với tài liệu của gRPC, Kubernetes, OWASP, Python, GitHub và Redis.

![Bốn chuỗi bước, mười một bước, minh họa bằng dịch vụ mượn sách. Cách làm việc: một phiếu việc cho mỗi thay đổi; viết hàm tính phí trả muộn bằng một ngôn ngữ; đặt tên và giao diện cho thao tác mượn sách. Vận hành và dữ liệu: chạy dịch vụ trên máy chủ và đám mây; đăng nhập an toàn và kiểm thử; lưu phiếu mượn trong cơ sở dữ liệu. Tự động hóa và nền tảng: mỗi thay đổi tự chạy kiểm thử; tìm sách trong một triệu mã bằng 20 phép so sánh thay vì một triệu. Tầm nhìn: bộ nhớ đệm và cân bằng tải cho ngày đông người; truyền bảng giảm giá vào hàm thay vì cố định trong mã; xem gợi ý của công cụ AI như mã của người lạ. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-027-main.svg)

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: tập quy ước để một chương trình dùng chức năng của chương trình khác; ở đây là cách ứng dụng mượn sách mở các thao tác của nó ra ngoài.
- **REST** (REpresentational State Transfer) — kiểu thiết kế dịch vụ qua giao thức web: mỗi tài nguyên (như một phiếu mượn) có một địa chỉ riêng; bài chỉ nhắc tên.
- **gRPC** (gRPC Remote Procedure Calls) — khung gọi thủ tục từ xa mã nguồn mở: bên gọi gọi một phương thức của dịch vụ ở máy khác như gọi hàm tại chỗ.
- **QL** (Query Language) — ngôn ngữ truy vấn: chữ QL trong tên GraphQL, một cách làm API mà bài chỉ nhắc tên.
- **OAuth** (Open AUTHorization) — chuẩn ủy quyền mở; thực ra OAuth là tên giao thức, không phải chữ viết tắt chính thức, và cách đọc "Open AUTHorization" chỉ để dễ nhớ: cho một ứng dụng được làm một số việc thay bạn mà không biết mật khẩu của bạn.
- **OpenID** (Open IDentity) — danh tính mở: tên một họ chuẩn về danh tính; bài chỉ dùng nó trong tên OpenID Connect.
- **OIDC** (OpenID Connect) — kết nối OpenID: lớp xác thực đặt trên OAuth2 để biết người đăng nhập là ai (không phải giao thức OpenID Authentication 2.0 cũ); bài chỉ nhắc tên.
- **PKCE** (Proof Key for Code Exchange) — cơ chế chứng minh khóa khi đổi mã: cách chống việc kẻ xấu chặn mã ủy quyền rồi đem đổi lấy quyền truy cập.
- **JWT** (JSON Web Token) — token web: định dạng mang các thông tin xác nhận (claim), thường được ký để kiểm tra; ứng dụng phải yêu cầu và kiểm tra đúng lớp bảo vệ mong đợi trước khi tin token; bài chỉ nhắc tên.
- **JSON** (JavaScript Object Notation) — ký hiệu đối tượng JavaScript: định dạng văn bản mô tả dữ liệu bằng các cặp tên và giá trị.
- **TDD** (Test-Driven Development) — phát triển hướng kiểm thử: viết kiểm thử trước rồi viết mã làm kiểm thử đó qua.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ.
- **CI** (Continuous Integration) — tích hợp liên tục: tự động xây dựng và kiểm thử mỗi thay đổi mã.
- **CD** (Continuous Delivery) — phân phối liên tục: tự động đưa bản đã kiểm thử tới nơi sẵn sàng phát hành.
- **AI** (Artificial Intelligence) — trí tuệ nhân tạo: ở đây là công cụ gợi ý mã.
- **OWASP** (Open Worldwide Application Security Project) — dự án mở về an toàn ứng dụng: tổ chức phát hành các bảng kiểm tra bảo mật cho lập trình viên.

## Đọc hình

**Cách làm việc.**
1. Công cụ cộng tác. Mỗi thay đổi của dịch vụ có một phiếu việc, một người nhận và một nơi thảo luận chung, để quyết định không nằm trong tin nhắn riêng. Đây là cách làm của người biên soạn, không phải điều tài liệu nào đã nêu.
2. Ngôn ngữ lập trình. Chọn một ngôn ngữ và viết cho thành thạo; ở đây là hàm tính phí trả muộn bằng Python, viết lại từng bước trong [bài về mười nguyên tắc viết mã tốt](../sd-10-028/lesson.md).
3. Phát triển API. Việc mượn sách cần một giao diện mà nơi khác gọi được. Trong gRPC, theo tài liệu của nó, ta định nghĩa một dịch vụ cùng các phương thức gọi từ xa với tham số và kiểu trả về; bên gọi có một stub (đại diện) có cùng phương thức, nên gọi `Borrow(...)` ở máy khác như gọi hàm tại chỗ. Với REST, mỗi phiếu mượn có một địa chỉ riêng. Còn GraphQL cho bên gọi tự nêu dữ liệu muốn lấy. Hai ý sau là kiến thức chung của người biên soạn.

**Vận hành và dữ liệu.**
4. Máy chủ web và lưu trữ. Dịch vụ phải chạy ở đâu đó liên tục. Tài liệu Kubernetes nói nó là nền tảng quản lý các khối công việc đóng gói trong container; nếu một container hỏng thì container khác phải chạy lên, và Kubernetes lo việc mở rộng và chuyển khi lỗi.
5. Xác thực và kiểm thử. Người mượn phải đăng nhập; OAuth2 chỉ lo ủy quyền, còn việc xác định danh tính cần lớp xác thực như OpenID Connect (OIDC) chạy trên nó. Bảng kiểm tra OAuth2 của OWASP nói PKCE là kỹ thuật chống tấn công chặn mã ủy quyền ở các ứng dụng công khai. Phần kiểm thử: viết kiểm thử trước khi viết mã (TDD) hoặc ngay sau; tài liệu `unittest` nói nó hỗ trợ kiểm thử tự động. JWT thường là dạng token mà các luồng đó trao đi, kiến thức chung của người biên soạn.
6. Cơ sở dữ liệu. Phiếu mượn phải sống lâu hơn chương trình. Tài liệu Python nói SQLite là thư viện cơ sở dữ liệu nhẹ lưu trên đĩa, không cần tiến trình máy chủ riêng, và có thể dùng để làm thử rồi chuyển sang hệ lớn hơn như PostgreSQL. Tài liệu Redis nói Redis dùng được như cơ sở dữ liệu, bộ nhớ đệm, bộ phát luồng sự kiện hay bộ môi giới thông điệp.

**Tự động hóa và nền tảng.**
7. CI/CD. Tài liệu GitHub Actions nói bạn có thể tạo workflow xây dựng và kiểm thử mỗi pull request, hoặc đưa các pull request đã gộp lên môi trường chạy thật. Với dịch vụ này: mỗi thay đổi tự chạy ba ca kiểm thử của hàm tính phí.
8. Cấu trúc dữ liệu và thuật toán. Tìm một mã sách trong danh sách một triệu mã đã sắp xếp. Quét tuần tự mất tới 1.000.000 phép so sánh (khi mã ở cuối); `bisect.bisect_left` chỉ mất 20 (đo bằng cách đếm lời gọi so sánh). Tài liệu `bisect` nói mô-đun này giúp giữ danh sách theo thứ tự mà không phải sắp xếp lại sau mỗi lần chèn, và có thể tốt hơn tìm tuần tự với danh sách dài.

**Tầm nhìn.**
9. Thiết kế hệ thống. Ngày hội mượn sách, nhiều người xem cùng một danh sách. Thêm bộ nhớ đệm: tài liệu `functools` nói `lru_cache` lưu tối đa `maxsize` lời gọi gần nhất và tiết kiệm thời gian khi một hàm tốn kém được gọi lặp lại với cùng đối số. Thêm cân bằng tải: tài liệu Kubernetes nói nó có thể phân phối lưu lượng mạng cho các bản chạy của dịch vụ để hệ thống ổn định.
10. Mẫu thiết kế. Hàm tính phí đang cố định bảng giảm giá. Truyền bảng vào làm tham số (một dạng "dependency injection") để thử với bảng giả mà không đụng vào bảng thật. Cần đổi cả chữ ký lẫn thân hàm: chữ ký thành `late_fee(days_late, member_type="standard", discounts=MEMBER_DISCOUNT)` và dòng tra bảng thành `discounts.get(member_type, 1.0)` thay cho `MEMBER_DISCOUNT.get(member_type, 1.0)`; chỉ thêm tham số mà vẫn tra bảng toàn cục thì giá trị truyền vào bị bỏ qua. Đây là cách làm của người biên soạn.
11. Công cụ AI. Một công cụ gợi ý mã cho ra đoạn mã nhìn hợp lý. Tài liệu hướng dẫn cách dùng Copilot của GitHub nói nó không thay chuyên môn của bạn, và nên luôn kiểm tra mã nó gợi ý, dùng kiểm thử tự động và công cụ để kiểm lại. Vậy hãy đọc gợi ý như mã của người lạ: hiểu nó, rồi chạy ba ca kiểm thử của bước 5.

## Giới hạn cần nhớ

Đây là một dự án nhỏ để minh họa, không phải lộ trình bắt buộc: bài không nói thứ tự nào đúng, mỗi bước mất bao lâu hay mức nào được gọi là senior. Các công cụ nhắc tới là ví dụ đã đối chiếu tài liệu, không phải danh sách đầy đủ hay khuyến nghị chọn; phần nói về REST, GraphQL, JWT, dependency injection và cách dùng phiếu việc là kiến thức chung của người biên soạn. Số đo 1.000.000 và 20 là của một danh sách số nguyên liên tiếp trong Python 3.13.16 và chỉ đếm số phép so sánh.

## Nhìn hình trả lời

Bạn vừa chuyển bản chạy thử của dịch vụ từ SQLite sang một cơ sở dữ liệu lớn hơn và muốn mỗi thay đổi tự chạy kiểm thử trước khi gộp. Hai bước nào của lộ trình nói về hai việc đó? Và nếu một container của dịch vụ hỏng giữa ngày hội, bước nào lo việc chạy container khác lên?

<details>
<summary>Xem đáp án</summary>

Bước 6, cơ sở dữ liệu: tài liệu Python nói có thể làm thử với SQLite rồi chuyển sang hệ lớn hơn như PostgreSQL.
Bước 7, CI/CD: tự xây dựng và kiểm thử mỗi thay đổi, như workflow của GitHub Actions.
Bước 4, máy chủ web và lưu trữ: Kubernetes quản lý container và chạy container khác lên khi một cái hỏng.

</details>

<details>
<summary>Xem sâu hơn: cách đo ở bước 8</summary>

Tạo danh sách một triệu đối tượng có phương thức `__lt__` đếm số lần nó được gọi. `bisect.bisect_left(danh_sách, mã_cần_tìm)` với mã ở cuối danh sách gọi `__lt__` 20 lần; một vòng lặp so từng phần tử với mã đó đi qua 1.000.000 phần tử. Tài liệu `bisect` nói các hàm của nó chỉ gọi `__lt__` và không bao giờ gọi `__eq__`, nên đếm `__lt__` là đếm số phép so sánh của nó. Hai con số khớp với ý của ký hiệu Big O: tuần tự tăng theo số phần tử, còn tìm đôi tăng rất chậm.

Mười một bước gộp nhiều việc: bước 5 gộp xác thực và kiểm thử, bước 9 gộp rất nhiều chủ đề. Đó là cách chia của nguồn mà bài giữ lại cho ví dụ này.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/11-steps-to-go-from-junior-to-senior-developer.md): chỉ lấy tên mười một bước và thứ tự; ví dụ, việc làm và số đo trong bài là của bài này.
- [gRPC — giới thiệu](https://github.com/grpc/grpc.io/blob/aeb4fafc3a135208450c066cafcc6fa522471ca1/content/en/docs/what-is-grpc/introduction.md): dịch vụ, phương thức gọi từ xa, stub. Đọc từ kho mã.
- [Kubernetes — tổng quan](https://github.com/kubernetes/website/blob/0b9277aa15af13c16f79d9c1d58acaf7c2d10298/content/en/docs/concepts/overview/_index.md): quản lý container, chạy lại khi hỏng, cân bằng tải. Đọc từ kho mã.
- [OWASP — OAuth2 Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/d89285c7bfc3f24fa79881407c89a85bf6d17272/cheatsheets/OAuth2_Cheat_Sheet.md): PKCE. Đọc từ kho mã.
- [Python — unittest](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/unittest.rst), [sqlite3](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/sqlite3.rst), [bisect](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/bisect.rst) và [functools](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/functools.rst): kiểm thử tự động, SQLite, tìm đôi, `lru_cache`. Đọc từ kho mã.
- [Redis — bắt đầu nhanh](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/develop/get-started/_index.md): các vai trò của Redis. Đọc từ kho mã.
- [GitHub — Understanding GitHub Actions](https://github.com/github/docs/blob/dae83f7d28f3b8e10015bd6b6d8b72267cedceca/content/actions/get-started/understand-github-actions.md) và [Best practices for using GitHub Copilot](https://github.com/github/docs/blob/dae83f7d28f3b8e10015bd6b6d8b72267cedceca/content/copilot/get-started/best-practices.md): workflow, kiểm tra gợi ý của công cụ AI. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-19. Số đo ở bước 8 do người biên soạn chạy ngày 2026-10-19; các câu giải nghĩa viết tắt trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.
