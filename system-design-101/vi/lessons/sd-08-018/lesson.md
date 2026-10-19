# Phát hành ứng dụng di động: bảy bước của nguồn, điều tài liệu của hai cửa hàng xác nhận, và một mô hình phát hành theo pha

**Bài nguồn tóm tắt hành trình đưa một ứng dụng lên iOS và Android thành bảy bước, mỗi bước vài gạch đầu dòng. Bài này giữ đủ bảy bước, đối chiếu những điểm kiểm được với tài liệu của Apple và của Android, nói rõ bước nào chưa đối chiếu được, và thêm một mô hình tính xem phát hành theo pha của Apple giới hạn được bao nhiêu thiệt hại khi bản mới có lỗi.**

![Ba khung. Khung một, bảy bước phát hành ứng dụng di động của nguồn: đăng ký và phát triển, build và thử, QA, duyệt nội bộ, tối ưu trang cửa hàng, nộp lên cửa hàng, phát hành. Khung hai, điều tài liệu độc lập xác nhận: TestFlight cho tối đa 100 người thử nội bộ và 10.000 người thử ngoài, mỗi build thử được 90 ngày; Android khuyên thử bản phát hành trên ít nhất một điện thoại và một máy tính bảng; Apple cho phát hành theo pha trong 7 ngày, từ 1% đến 100%. Khung ba, mô hình phát hành theo pha với số báo cáo kỳ vọng: lỗi chạm 10% người dùng dừng được ở ngày 1 với 1% đã nhận; chạm 1% dừng ngày 2 với 2%; chạm 0,1% dừng ngày 5 với 20%; chạm 0,01% không dừng kịp, cả 100% nhận bản lỗi.](../../diagrams/sd-08-018-main.svg)

## Từ viết tắt

- **QA** (Quality Assurance) — đảm bảo chất lượng: khâu kiểm tra sản phẩm trước khi tới người dùng, gồm thử nội bộ, thử với người ngoài và thử lại các tính năng cũ.
- **ASO** (App Store Optimization) — tối ưu trang trên cửa hàng ứng dụng: chỉnh tiêu đề, mô tả, từ khoá, ảnh chụp màn hình để dễ được tìm thấy; ở bài này chỉ nhắc, không đo.
- **OS** (Operating System) — hệ điều hành: phần mềm nền của điện thoại; iOS là hệ điều hành của Apple, còn Android là hệ điều hành của Google.

## Đọc hình

| Bước của nguồn | Nguồn nói | Điều tài liệu độc lập nói |
|---|---|---|
| 1. Đăng ký và phát triển | Đăng ký với Apple và Google; Swift hoặc Objective-C cho iOS, Java hoặc Kotlin cho Android | Apple: Chương trình nhà phát triển có phí 99 đô la Mỹ mỗi năm và bao gồm TestFlight. Ngôn ngữ và phí của Google: chưa đối chiếu |
| 2. Build và thử | Biên dịch, thử trên cả hai nền tảng, tạo bản ứng viên phát hành | Android: đặt `debuggable` thành sai, tắt nhật ký, ký bản phát hành, và thử bản phát hành trên ít nhất một điện thoại và một máy tính bảng; ứng dụng mới trên Google Play phải nộp ở dạng Android App Bundle từ tháng 8 năm 2021 |
| 3. QA | Thử nội bộ, thử với người ngoài, thử lại các tính năng cũ | Apple TestFlight: tối đa 100 người thử nội bộ và 10.000 người thử ngoài; build đầu tiên cho nhóm ngoài phải qua App Review; mỗi build thử được 90 ngày; có số phiên và số lần sập |
| 4. Duyệt nội bộ | Các bên liên quan, quy định của cửa hàng, bảo mật | Là quy trình của từng công ty: chưa có tài liệu độc lập để đối chiếu |
| 5. ASO | Tiêu đề, từ khoá, ảnh, ghi chú bản phát hành | Chưa đối chiếu |
| 6. Nộp lên cửa hàng | Qua App Store Connect và Google Play Console; cửa hàng có thể yêu cầu sửa | Apple: duyệt mọi ứng dụng và mọi bản cập nhật; Android: sau khi qua duyệt của Google Play thì ứng dụng mới lên |
| 7. Phát hành | Đặt ngày phát hành để ra mắt đồng bộ | Apple: có thể phát hành theo pha trong 7 ngày (bảng bên dưới), dừng tối đa 30 ngày, hoặc bấm phát hành cho mọi người bất cứ lúc nào. Phía Android: chưa đối chiếu |

## Thử: phát hành theo pha giới hạn được bao nhiêu thiệt hại?

Theo trang Apple về phát hành bản cập nhật theo pha, một phần ngẫu nhiên người dùng có bật tự cập nhật nhận bản mới theo lịch cố định:

| Ngày | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| Tỷ lệ người dùng | 1% | 2% | 5% | 10% | 20% | 50% | 100% |

Đây là **mô hình tính**, không phải phép đo trên cửa hàng thật. Giả sử 1.000.000 người dùng đủ điều kiện, mọi người được chọn đều cập nhật và dùng ứng dụng trong ngày; một lỗi làm sập ứng dụng của một tỷ lệ r người dùng; mỗi người bị sập được báo cáo với xác suất 0,5, tính theo giá trị kỳ vọng (số người bị sập nhân 0,5, không mô phỏng ngẫu nhiên); và nhóm dừng phát hành vào ngày số báo cáo kỳ vọng cộng dồn đạt 100. Ngày 2026-10-19, một đoạn chương trình Python ngắn tính ra:

| Lỗi làm sập tỷ lệ r người dùng | Phát hành theo pha: ngày dừng và số người đã nhận bản lỗi | Phát hành một lần cho mọi người |
|---|---|---|
| 10% | ngày 1, 10.000 người (1%) | 1.000.000 |
| 1% | ngày 2, 20.000 người (2%) | 1.000.000 |
| 0,1% | ngày 5, 200.000 người (20%) | 1.000.000 |
| 0,01% | không bao giờ đạt 100 báo cáo trong 7 ngày: cả 1.000.000 người | 1.000.000 |

Vì số báo cáo thật là ngẫu nhiên, mỗi ngày dừng ở bảng là ngày theo giá trị kỳ vọng. Ở hàng 1% và hàng 0,1%, kỳ vọng đúng bằng ngưỡng 100 (ngày 2 và ngày 5), nên trong thực tế ngày dừng có thể sớm hoặc muộn hơn một ngày; hàng 10% vượt ngưỡng rất xa nên chắc chắn dừng ngày 1.

Hai điều đọc được. Một, với lỗi phổ biến, phát hành theo pha giảm thiệt hại từ 100 đến 50 lần: bạn dừng khi mới 1% hay 2% người dùng đã nhận. Hai, với lỗi hiếm, lịch cố định 7 ngày không kịp bắt: lỗi chạm một người trong mười nghìn sinh ra quá ít báo cáo để đạt ngưỡng, và đến ngày 7 mọi người đều có bản lỗi. Trang Apple nói cũng rõ rằng người dùng vẫn có thể tải bản mới thủ công bất cứ lúc nào trong lúc phát hành theo pha, nên con số "người đã nhận" là cận dưới.

## Giới hạn cần nhớ

Bài nguồn là một hình và vài gạch đầu dòng cho cả hai nền tảng; đối chiếu ở đây dựa vào các trang tài liệu Apple đọc ngày 2026-10-19 và trang Android Studio về xuất bản ứng dụng, không phải toàn bộ quy định của cửa hàng. Trang của Google Play về phát hành theo pha và về phí đăng ký không truy cập được từ máy viết bài, nên phía Android chưa được đối chiếu ở các điểm đó. Thời gian chờ duyệt của cả hai cửa hàng không được nêu trong tài liệu đã đọc và không được ước lượng ở đây. Mô hình phát hành theo pha dùng các giả định ở trên (ngưỡng 100 báo cáo, xác suất báo cáo 0,5, mọi người được chọn đều cập nhật); đổi giả định thì ngày dừng đổi theo, và chỉ hướng của kết quả là đáng đọc.

## Nhìn hình trả lời

Bản cập nhật mới của ứng dụng có một lỗi làm sập ứng dụng với khoảng 1 trong 1.000 người dùng. Bạn bật phát hành theo pha 7 ngày của Apple và đặt ngưỡng dừng là 100 báo cáo sập. Bạn kỳ vọng bao nhiêu người đã nhận bản lỗi lúc dừng, và điều gì sẽ đổi nếu lỗi chỉ chạm 1 trong 10.000 người?

<details>
<summary>Xem đáp án</summary>

Với 1 trong 1.000 và giả định của bài (một nửa số người bị sập báo cáo, 1.000.000 người đủ điều kiện), số báo cáo đạt 100 vào ngày 5, khi 20% người dùng, tức 200.000 người, đã nhận bản mới; tức là phát hành theo pha đã tránh cho 80% còn lại. Nếu lỗi chỉ chạm 1 trong 10.000, đến ngày 7 vẫn chưa đủ 100 báo cáo, lịch hết và mọi người đều nhận bản lỗi: phát hành theo pha không thay được việc theo dõi tốc độ sập thật và một ngưỡng dừng thấp hơn, hoặc dừng theo tỷ lệ chứ không theo số tuyệt đối.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một hình và bảy bước, mỗi bước vài gạch đầu dòng. Bài này giữ bảy bước theo đúng thứ tự, thêm cột đối chiếu (có chỗ chưa đối chiếu được) và một mô hình tính cho bước cuối, thay cho câu "đặt ngày phát hành" chung chung.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-to-release-a-mobile-app.md): bảy bước.
- [Apple — Release a version update in phases](https://developer.apple.com/help/app-store-connect/update-your-app/release-a-version-update-in-phases/): lịch 7 ngày 1%, 2%, 5%, 10%, 20%, 50%, 100%, dừng tối đa 30 ngày. Đọc ngày 2026-10-19.
- [Apple — TestFlight overview](https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview/): 100 người thử nội bộ, 10.000 người thử ngoài, 90 ngày, App Review cho build đầu của nhóm ngoài. Đọc ngày 2026-10-19.
- [Apple — Apple Developer Program](https://developer.apple.com/programs/): phí 99 đô la Mỹ mỗi năm. Đọc ngày 2026-10-19.
- [Apple — App Review](https://developer.apple.com/distribute/app-review/): duyệt ứng dụng, bản cập nhật gửi lên App Store Connect. Đọc ngày 2026-10-19.
- [Android — Publish your app](https://developer.android.com/studio/publish): chuẩn bị bản phát hành, thử trên điện thoại và máy tính bảng, Android App Bundle, duyệt của Google Play. Đọc ngày 2026-10-19.

Đã đọc nguồn ngày 2026-10-19. Mô hình tính là của người biên soạn.
Bài viết và hình được thiết kế độc lập.
