# Lên xu hướng, bật kiếm tiền và thu nhập trên YouTube, TikTok, Facebook

Cập nhật 18/10/2026 · báo cáo nguồn của deck `xu-huong-kiem-tien-youtube-tiktok-facebook.pptx` (cùng thư mục)

---

## Đọc trước: độ tin cậy của số liệu

Phần lớn nội dung nay đã đối chiếu với **trang của chính nền tảng**:

- **YouTube:** trang trợ giúp về YPP, "Changes to the YouTube Partner Program", chính sách kiếm tiền, chính sách Shorts, chính sách spam, khai báo AI; "How YouTube Works"; blog đề xuất; thư CEO 2026; tài liệu YouTube Data API (videos.insert, hạn mức, lịch sử sửa đổi, audit, chính sách nhà phát triển).
- **TikTok:** trang trợ giúp Creator Rewards và AIGC; Creator Academy (cả bản tiếng Anh và tiếng Việt, cập nhật 10/9/2026); newsroom (2020, 2024); Community Guidelines 2026-H2; tài liệu Content Posting API.
- **Meta:** creators.facebook.com (Content Monetization, Creator Fast Track); bài tin 24/4/2025, 14/7/2025, 13/3/2026; bài về nhãn AI (4/2024); tài liệu Reels Publishing API.

**Vẫn chưa đọc được hoặc không có nguồn chính thức:**
- Mức RPM của mọi nền tảng (không nền tảng nào công bố).
- Trung tâm trợ giúp của Meta về điều kiện Content Monetization chi tiết và quy tắc riêng về nội dung AI trên Facebook.
- Các điều kiện kiếm tiền khác của TikTok tại Việt Nam (TikTok Shop, LIVE).

Nhãn dùng trong bài:
- **[Chính thức]**: đã đọc trang của chính nền tảng.
- **[Cao]**: nhiều nguồn bên thứ ba thống nhất.
- **[Vừa]**: vài nguồn, hoặc ước tính của bên thứ ba.
- **[Thấp]**: một nguồn, hoặc các nguồn mâu thuẫn.

---

## 1. Tóm tắt (đọc trong 1 phút)

1. **Không có công thức "lên xu hướng" do nền tảng công bố.** Trang chính thức của YouTube và TikTok mà mình đọc mô tả việc chọn video cho từng người xem. Mô hình "thử với nhóm nhỏ rồi mở rộng nếu phản hồi tốt" là cách bên thứ ba và người làm nội dung mô tả, không phải điều nền tảng công bố. [Chính thức cho phần không có công thức; Cao cho mô hình nhóm nhỏ]
2. **YouTube đã gỡ trang Trending** (có hiệu lực khoảng 21/7/2025). "Lên xu hướng" nay là được đề xuất. [Chính thức, qua lịch sử sửa đổi API]
3. **YouTube bật kiếm tiền:** quảng cáo và Premium (YPP đầy đủ) hiện cần 1.000 subscriber + 4.000 giờ xem hoặc 10 triệu lượt xem Shorts/90 ngày. **Từ 1/2/2027, người mới cần 8.000 giờ hoặc 20 triệu lượt xem Shorts.** Cấp sớm (fan funding, Creator Partnerships, Shopping) cần 500 subscriber + 3 video công khai hợp lệ trong 90 ngày gần nhất + 3.000 giờ hoặc 3 triệu lượt xem Shorts/90 ngày, và không đổi sau 1/2/2027. Kênh đã trong YPP không bị ảnh hưởng tư cách, nhưng muốn nhận tiền từ Shorts phải giữ 10 triệu lượt xem Shorts/90 ngày. [Chính thức]
4. **TikTok Creator Rewards** (10.000 follower, 100.000 lượt xem/30 ngày, video gốc trên 1 phút) **hiện chỉ mở cho Mỹ, Anh, Đức, Nhật, Hàn, Pháp, Mexico, Brazil. Việt Nam không có trong danh sách.** [Chính thức]
5. **Facebook Content Monetization hiện chỉ theo lời mời**, Meta không công bố ngưỡng số liệu. [Chính thức]
6. **Tiền trên 1.000 lượt xem (RPM)** chênh nhau hàng chục lần: YouTube video dài vài USD, Shorts từ vài cent đến khoảng 0,20 USD, TikTok khoảng 0,4–1 USD (chỉ áp dụng ở 8 nước có chương trình), Facebook Reels thường 0,02–0,20 USD. Không nền tảng nào công bố RPM. [Vừa]
7. **Video tạo bằng AI không bị cấm, và không có nguồn chính thức nào nói video bị trừ điểm chỉ vì dùng AI.** TikTok nói bật nhãn AI không ảnh hưởng phân phối nếu không vi phạm quy định; YouTube nói nhãn AI không giới hạn khán giả hay quyền kiếm tiền. Rủi ro nằm ở nội dung **hàng loạt, lặp, thiếu giá trị riêng**, thiếu khai báo, và AI đóng vai chuyên gia về chủ đề nhạy cảm (không được kiếm tiền trên YouTube). [Chính thức]
8. **Đăng bằng API không phải tín hiệu xếp hạng được công bố.** Khác biệt thực tế là **cổng truy cập và hạn mức**: TikTok khóa bài ở chế độ riêng tư nếu ứng dụng chưa audit (chủ tài khoản vẫn có thể đổi từng bài sang công khai bằng tay), và **loại công cụ chỉ đăng cho tài khoản của chính bạn khỏi mục đích sử dụng được chấp nhận để audit**; YouTube mặc định 100 lượt upload/ngày/dự án. [Chính thức]
9. **Thu nhập lớn thường không đến từ tiền nền tảng trả** mà từ brand deal, affiliate, sản phẩm. [Vừa]

---

## 2. Điều kiện để bài viết "lên xu hướng"

### 2.1 Nguyên lý chung

- Mô hình phổ biến: video được đẩy tới một nhóm nhỏ trước; phản hồi tốt thì mới mở rộng. Đây là cách các nguồn bên thứ ba và người làm nội dung mô tả. Trang chính thức của YouTube và TikTok mà mình đọc không nêu cơ chế thử theo nhóm, mà mô tả việc chọn video cho từng người xem khi họ dùng ứng dụng. [Cao: bên thứ ba, không phải công bố của nền tảng]
- TikTok nói **số follower và việc video trước đó có hiệu quả không phải yếu tố trực tiếp** trong hệ thống đề xuất. [Chính thức, newsroom 2020, bài đã cũ]
- Ngưỡng cụ thể ("hoàn thành 70%", "lượt xem giờ đầu") chỉ là kinh nghiệm người làm nội dung. [Thấp]

### 2.2 YouTube

**Trang Trending đã bị gỡ** (có hiệu lực khoảng 21/7/2025), chuyển sang YouTube Charts. Creator được hướng dẫn dùng tab **Inspiration** trong YouTube Studio. [Chính thức, lịch sử sửa đổi API]

**Hệ thống đề xuất** [Chính thức]:
- Dựa trên hành vi xem, like/dislike, subscription và phản hồi, **kể cả khảo sát mức hài lòng**.
- Xét cả **uy tín và chất lượng kênh** khi quyết định hiển thị cho ai và khi nào; dùng người đánh giá bên ngoài.
- Blog nêu các tín hiệu: lượt nhấp, thời gian xem, câu trả lời khảo sát, chia sẻ/like/dislike. Nội dung "borderline" bị hạ.

**Shorts:** tín hiệu hay được nhắc là tỷ lệ xem so với vuốt bỏ, xem lại, chia sẻ. [Vừa] Từ 31/3/2025, một lượt xem Shorts được tính mỗi lần Short bắt đầu hoặc phát lại, không cần xem tối thiểu mấy giây. [Chính thức] Tiền Shorts tính theo "engaged views", không phải lượt xem thô. [Chính thức]

**Cơ hội "xu hướng" mới (từ 1/2/2027):** YouTube sẽ có chương trình khuyến khích Shorts, trong đó có **"earnings boosts for cultural trend activations"**; creator đủ điều kiện sẽ nhận thông báo trực tiếp. [Chính thức]

### 2.3 TikTok

- **Tín hiệu** [Chính thức, newsroom 2020]: tương tác (like, chia sẻ, follow, bình luận), thông tin video (chú thích, âm thanh, hashtag); cài đặt thiết bị/quốc gia có **trọng số thấp**. Ví dụ tín hiệu mạnh: xem hết một video dài từ đầu đến cuối.
- **Không đề xuất** nội dung trùng lặp, đã xem, spam; video vừa tải lên hoặc đang xét duyệt có thể chưa đủ điều kiện; không hiện hai video liên tiếp cùng âm thanh hoặc cùng creator. [Chính thức]
- **Không vào được FYF** (Community Guidelines 2026-H2) [Chính thức]: nội dung dùng lại không chỉnh sửa sáng tạo (ví dụ còn watermark người khác); nội dung chất lượng thấp hoặc chỉnh sửa tối thiểu (ví dụ clip ghép từ GIF); nội dung dụ người xem tặng quà hoặc tăng like.
- Thứ hạng "chia sẻ > lưu > bình luận > like" và các ngưỡng hoàn thành cụ thể chỉ từ blog. [Thấp]
- Creative Center có bảng hashtag/âm thanh thịnh hành; lời khuyên bắt trend sớm là của blog. [Thấp]

### 2.4 Facebook

- **Nội dung gốc được ưu tiên và nay có định nghĩa rõ** [Chính thức, Meta 13/3/2026]:
  - Nội dung do chủ Page/profile **quay hoặc tạo trực tiếp** là nội dung gốc.
  - Reels dùng một phần nội dung bên thứ ba (remix, overlay) được coi là gốc khi **creator xuất hiện trên màn hình và đưa ra điều gì thực sự mới** (thông tin mới, phân tích, cải thiện cốt truyện).
  - **Chỉ xem cùng, phản ứng bằng nét mặt, ghép nhiều clip, hoặc thuyết minh lại cảnh đang chiếu** mà không thêm gì có ý nghĩa: coi là không gốc, **sẽ bị giảm ưu tiên** trong Feed và Reels.
  - Nội dung trùng lặp hoặc chỉnh sửa nhỏ (thêm viền, phụ đề, đổi tốc độ): không gốc.
  - Tài khoản đăng chủ yếu nội dung không gốc có thể bị **"không được đề xuất" và bị tắt kiếm tiền**.
  - Meta cho biết lượt xem và thời gian xem Reels gốc **tăng khoảng gấp đôi** trong nửa cuối 2025 so với cùng kỳ 2024.
- **Spam làm giảm reach** [Chính thức, Meta 24/4/2025]: chú thích dài, nhiều hashtag, hoặc chú thích không liên quan đến nội dung (ví dụ ảnh chó kèm chú thích về máy bay): chỉ hiển thị cho follower và **không đủ điều kiện kiếm tiền**. Mạng lưới hàng trăm tài khoản đăng cùng nội dung: không đủ điều kiện kiếm tiền, có thể giảm reach.
- **Thực hành tốt** [Chính thức, Meta 14/7/2025]: nội dung gốc; cải tiến có ý nghĩa; kể chuyện; tránh watermark bên thứ ba; chú thích không chứa link, ít chữ in hoa, **không quá 5 hashtag**.
- **Công cụ chẩn đoán:** Professional Dashboard có insight cấp bài đăng giải thích vì sao bài không được phân phối; màn hình **Support** cho biết nguy cơ bị phạt đề xuất hoặc kiếm tiền. [Chính thức]
- Tín hiệu kỹ thuật như watch time và tỷ lệ xem hết chủ yếu từ blog. [Vừa]

### 2.5 So sánh nhanh

| | YouTube | TikTok | Facebook |
|---|---|---|---|
| Trang "xu hướng" | Đã gỡ (7/2025); còn Charts | Creative Center | Không có |
| Tín hiệu chính | Nhấp, thời gian xem, mức hài lòng, uy tín kênh | Hoàn thành, chia sẻ; follower không phải yếu tố trực tiếp | Nội dung gốc (chính thức); watch time (blog) |
| Bị loại/giảm đề xuất | Nội dung hàng loạt, lặp bị hạ (CEO 2026) | FYF loại nội dung dùng lại, chất lượng thấp | Nội dung không gốc bị giảm ưu tiên; có thể mất đề xuất và kiếm tiền |
| Công cụ xem lý do | Studio (Viewed vs swiped away) | Creator tools | Professional Dashboard + Support |

---

## 3. Khi nào mới bật được kiếm tiền

### 3.1 YouTube [Chính thức]

**Điều kiện cần cho YPP đầy đủ** (trang "YPP overview & eligibility"): theo chính sách kiếm tiền; ở quốc gia/vùng được hỗ trợ; không có Community Guidelines strike đang hiệu lực; bật xác minh 2 bước; có quyền "advanced features"; có một tài khoản AdSense for YouTube.

**Điều kiện cần cho cấp sớm** (trang "Overview of the expanded YouTube Partner Program"): theo chính sách kiếm tiền; kênh ở một trong các quốc gia/vùng của **danh sách riêng** của chương trình mở rộng (danh sách này **có Việt Nam**); bật xác minh 2 bước; có một tài khoản AdSense for YouTube. Trang này không nhắc điều kiện strike hay "advanced features". YouTube nói sẽ gửi email khi đã "triển khai chương trình mở rộng" cho kênh và kênh đã đạt ngưỡng (nút "Get notified" ở YouTube Studio → Earn), nên chưa chắc mọi kênh đạt ngưỡng đều nộp được ngay.

**Đến hết 31/1/2027**

| Cấp | Điều kiện | Mở khóa |
|---|---|---|
| Đầy đủ (YPP) | 1.000 subscriber + 4.000 giờ xem đủ điều kiện/12 tháng, **hoặc** 1.000 subscriber + 10 triệu lượt xem Shorts đủ điều kiện/90 ngày | Chia sẻ doanh thu quảng cáo + Premium |
| Sớm | 500 subscriber + **3 video công khai hợp lệ trong 90 ngày gần nhất** + 3.000 giờ xem/12 tháng, **hoặc** 500 subscriber + 3 video công khai hợp lệ trong 90 ngày + 3 triệu lượt xem Shorts/90 ngày | Fan funding, Creator Partnerships, Shopping |

- "Giờ xem đủ điều kiện" chỉ tính từ video dài công khai; **giờ xem từ Shorts feed không tính** vào 4.000 giờ. Video riêng tư, không công khai, đã xóa, quảng cáo trả tiền không tính.
- "Lượt xem Shorts đủ điều kiện" là lượt xem từ Shorts công khai hiển thị trong Shorts feed; bài ảnh không tính.
- Đạt ngưỡng chưa chắc được vào: kênh trải qua xét duyệt (tự động + người), **thường khoảng 1 tháng**. Bị từ chối: kháng nghị trong 21 ngày hoặc nộp lại sau 30 ngày (lần thứ hai trở đi: 90 ngày).
- Kênh không đăng video hoặc bài trong 6 tháng có thể bị tắt kiếm tiền. Vi phạm chính sách kiếm tiền thì mất kiếm tiền bất kể số liệu.

**Từ 1/2/2027** (trang "Changes to the YouTube Partner Program")

- **Người mới vào YPP:** 1.000 subscriber + **8.000 giờ xem/365 ngày** hoặc **20 triệu lượt xem Shorts/90 ngày**.
- **Kênh đã trong YPP:** tư cách **không bị ảnh hưởng**. Để nhận tiền hằng tháng từ **Shorts Creator Pool** (và phần doanh thu Premium trong Shorts feed, theo trang "YouTube Shorts monetization policies"), phải duy trì **10 triệu lượt xem Shorts đủ điều kiện trong 90 ngày gần nhất** (tính trong 90 ngày kết thúc ngày 15 của tháng trước tháng tính tiền). Nếu hụt, **không bị loại khỏi YPP**, không ảnh hưởng thu nhập khác (kể cả video dài).
- **Cấp sớm không đổi:** 500 subscriber + 3 video công khai hợp lệ trong 90 ngày + 3.000 giờ hoặc 3 triệu lượt xem Shorts.
- **"Kênh còn hoạt động"** (mới): thỏa một trong ba: 1.000 giờ xem/365 ngày; 1 triệu lượt xem Shorts/90 ngày; hoặc đăng **2 video dài hoặc 5 Shorts mỗi 90 ngày**. Kênh tụt dưới mức có thêm 90 ngày để khôi phục, và để khôi phục phải đạt 1.000 giờ xem/365 ngày hoặc 1 triệu lượt xem Shorts/90 ngày (cách đăng bài không tính để khôi phục).
- **Hạn chót chấp nhận điều khoản mới trong YouTube Studio: 31/1/2027.** Không ký thì không bị loại khỏi YPP nhưng **ngừng nhận tiền** từ module chưa ký từ 1/2/2027; ký lại sau thì nhận lại.
- **Tiền thưởng mới:** Premium Lite mở ra mọi nước có Premium, creator chia sẻ một quỹ bằng **60% doanh thu thuê bao ròng** (Premium Lite) và **30%** (Premium thường); **45%** trực tiếp cho **Targeted Shorts Ads** (quảng cáo nhắm đến 5 kênh trở xuống); chương trình thưởng Shopping, tín dụng sản xuất brand deal, tăng thu nhập khi tham gia xu hướng văn hóa.

> Hàm ý thực tế (tính tại 18/10/2026): kênh gần mốc 4.000 giờ hoặc 10 triệu lượt xem Shorts còn khoảng 3,5 tháng dưới ngưỡng cũ. Chưa thấy trang nào nói rõ đơn **nộp trước 1/2/2027 nhưng chưa duyệt xong** áp dụng mốc nào.

### 3.2 TikTok [Chính thức: trang trợ giúp, Creator Academy cập nhật 10/9/2026]

**Creator Rewards Program: điều kiện**
- **Ở một trong các nước có chương trình: Mỹ, Anh, Đức, Nhật, Hàn, Pháp, Mexico, Brazil** (tài khoản phải đăng ký tại nước đó). **Việt Nam không có trong danh sách** ở cả bản tiếng Anh và tiếng Việt của trang.
- Từ 18 tuổi (19 ở Hàn Quốc), tài khoản **cá nhân** (không phải Business), thông tin thật, trạng thái tốt.
- **10.000 follower** và **100.000 lượt xem video trong 30 ngày gần nhất**.
- Video **gốc, dài trên 1 phút**, đăng **sau khi** vào chương trình; mỗi video cần **1.000 lượt xem For You đủ điều kiện** mới bắt đầu tính tiền. Khuyến nghị 1080p trở lên.
- Đăng ký: Profile → Menu → TikTok Studio → Creator Rewards Program; phản hồi khoảng 3 ngày.

**Thế nào là "gốc" và "lượt xem đủ điều kiện"**
- Gốc = **do chính bạn thiết kế, quay và sản xuất**, thể hiện chuyên môn/sáng tạo. **Không phải gốc:** Duet/Stitch; nội dung chép nguyên, còn watermark; nội dung chỉ sửa nhẹ (tăng tốc, filter, chữ cố định, sticker); ghép video/ảnh của người khác không có ý tưởng mới; video lặp vòng, ảnh đơn/nhiều ảnh, chỉ có chữ phủ; lip sync hoặc nhạc có bản quyền phát trên 1 phút.
- Video **không đủ điều kiện** nếu: chất lượng thấp (**chia đôi màn hình, phản ứng vô nghĩa, ảnh chất lượng thấp, slide video**), clickbait, quảng cáo/nội dung tài trợ, Photo Mode, video thuộc Series.
- Lượt xem đủ điều kiện = lượt xem duy nhất từ For You, **loại** lượt xem gian lận, trả tiền, đã dislike/không quan tâm, dưới 5 giây, quảng bá, nhân tạo.
- Thưởng = **Standard Reward** (lượt xem đủ điều kiện × RPM) + **Additional Reward** (từ mùa xuân 2025, dựa trên mức độ "tinh chỉnh, hấp dẫn, chuyên sâu" của nội dung). Mức RPM **không được công bố**.
- **Vi phạm** (Creator Academy): có hai ngưỡng với hậu quả khác nhau. **5 vi phạm video trong 30 ngày gần nhất** là một lý do tài khoản không đủ điều kiện; trang không gọi đó là vĩnh viễn. **5 vi phạm tài khoản (tính tổng)** thì tài khoản **vĩnh viễn không đủ điều kiện**. Video bị báo không đạt điều kiện kháng nghị được trong **80 ngày**; tài khoản bị loại khỏi chương trình kháng nghị được trong **30 ngày**, và nếu khôi phục được tài khoản thì được đưa lại vào chương trình tự động. Tài khoản bị cấm vĩnh viễn thì mất phần thưởng chưa nhận. [Chính thức]
- **Trừ tiền khi video bị gỡ:** tiền đã nhận từ video bị gỡ **bị trừ lại** khỏi số dư. Câu này mình đọc ở một trang hỗ trợ TikTok về kháng nghị ở phiên trước; trang Creator Academy hiện tại không nêu và mình chưa mở lại được trang đó. [Vừa]
- Điều kiện duy trì có câu: **không được "tạo phần mềm độc hại hoặc sửa mã để đăng ký, đăng bài, hoặc tăng like/follow/lượt xem một cách nhân tạo"** (xem chương 5).

**Với creator ở Việt Nam:** Creator Rewards chưa dùng được. Các blog nói "có ở Việt Nam từ 2024" **không khớp** với trang chính thức; tài khoản có thể thử kiểm tra trong TikTok Studio, nhưng danh sách nước chính thức không có Việt Nam. Các nguồn thu khác của TikTok (TikTok Shop affiliate, LIVE gifts, brand deal) chưa có nguồn chính thức mình đọc được. [Thấp]

### 3.3 Facebook [Chính thức, creators.facebook.com]

- **Facebook Content Monetization hiện chỉ theo lời mời.** Meta nói đang gửi lời mời cho "hàng triệu creator" trong năm nay và "dự kiến mở đăng ký tự do trong tương lai gần". Có thể **bày tỏ quan tâm** qua biểu mẫu: dashboard → tab Monetization → Content Monetization.
- Trả tiền cho Reels, ảnh, bài chữ, stories; có "earnings insights" cho biết bài nào kiếm nhiều nhất.
- **Meta không công bố ngưỡng follower hay số phút xem.** Các mốc như "10.000 follower + 600.000 phút/60 ngày" hay "1.000 follower" trên blog **không phải điều kiện chính thức hiện hành**; nên bỏ khỏi report.
- Tiền chỉ trả sau khi liên kết tài khoản nhận tiền và hoàn tất khai thuế/xác minh (theo các nguồn thứ ba). [Vừa]

**Creator Fast Track** (chương trình riêng, 3 tháng) [Chính thức]
- Thưởng hằng tháng theo số follower trên Instagram/TikTok/YouTube: **20.000–99.999: 100–450 USD; 100.000–999.999: 1.000 USD; từ 1 triệu: 3.000 USD.**
- Điều kiện: cư trú **Mỹ, Canada, Anh hoặc Úc**; 18+; có Page; tài khoản Facebook từ 30 ngày; **chưa đăng Reel nào trong 6 tháng**; tài khoản bên ngoài có ít nhất **20.000 follower và 30.000 lượt xem video/60 ngày**; đăng **15 Reels/tháng trên 10 ngày khác nhau**; nội dung do bạn làm và **chưa từng đăng trên Facebook**.
- Vào Content Monetization ngay, không phải chờ.

### 3.4 Bảng tóm tắt

| | Mốc vào chương trình kiếm tiền chính (quảng cáo) | Độ chắc chắn | Cách xác nhận |
|---|---|---|---|
| YouTube (đến 31/1/2027) | YPP đầy đủ: 1.000 sub + 4.000 giờ hoặc 10 triệu Shorts/90 ngày. Cấp sớm (fan funding, Creator Partnerships, Shopping): 500 sub + 3 video công khai/90 ngày + 3.000 giờ hoặc 3 triệu Shorts/90 ngày | Chính thức | YouTube Studio → Earn |
| YouTube (từ 1/2/2027) | YPP đầy đủ cho người mới: 1.000 sub + 8.000 giờ hoặc 20 triệu Shorts/90 ngày. Cấp sớm không đổi (500 sub + 3 video công khai/90 ngày + 3.000 giờ hoặc 3 triệu Shorts/90 ngày) | Chính thức | Trang "Changes to the YPP" |
| TikTok | 10.000 follower + 100.000 lượt xem/30 ngày + video >1 phút; **chỉ 8 nước, không có Việt Nam** | Chính thức | TikTok Studio |
| Facebook | Chỉ theo lời mời; không có ngưỡng công khai | Chính thức | Professional Dashboard → Monetization |

---

## 4. Thu nhập đến từ đâu và bao nhiêu

### 4.1 Hai khái niệm cần phân biệt

- **CPM**: số tiền nhà quảng cáo trả cho 1.000 lượt hiển thị. Creator **không** nhận số này.
- **RPM**: số tiền creator **thực nhận** trên 1.000 lượt xem. Mẫu số là mọi lượt xem (kể cả lượt không có quảng cáo), tiền đã qua bước chia sẻ doanh thu và có thể gồm cả nguồn ngoài quảng cáo như membership hay fan funding.
- **RPM không phải một tỷ lệ cố định của CPM.** CPM tính trên 1.000 lượt hiển thị quảng cáo, trước khi chia sẻ doanh thu. Vì hai mẫu số khác nhau, không đổi CPM quảng cáo ra thu nhập bằng một hệ số chung. Ví dụ ở 4.3: khán giả Việt Nam có RPM khoảng 0,22 USD và CPM khoảng 1,14 USD (số Dynamoi đến 14/7/2026), tức RPM chỉ bằng khoảng 19% CPM. [Thấp]

### 4.2 Tiền nền tảng trả trực tiếp

**YouTube**
- Video dài: creator giữ **55%** doanh thu quảng cáo phân bổ. [Cao]
- Shorts: quảng cáo xen giữa các Short được gom vào **Creator Pool**, phân bổ theo lượt xem tương tác (engaged views) và việc dùng nhạc; creator nhận **45%** phần được phân bổ. Một phần doanh thu quảng cáo Shorts được dùng để trang trải bản quyền nhạc trước khi vào Creator Pool. [Chính thức]
- Nguồn khác: Premium, membership, Super Chat, Super Thanks, Shopping.
- Quy mô: YouTube cho biết đã trả hơn **100 tỷ USD** cho creator, nghệ sĩ và hãng truyền thông từ 2021 (công bố 9/2025). Con số gộp, không phải mức trung bình mỗi kênh. [Cao]

**TikTok**
- **Creator Rewards** (chỉ 8 nước): Standard Reward + Additional Reward. Các blog ước tính khoảng **0,40–1,00 USD / 1.000 lượt xem đủ điều kiện** (một số nguồn tới 1,20); TikTok **không công bố** bảng RPM. [Vừa]
- **LIVE gifts**: một blog nêu 50–200 USD mỗi buổi với creator tầm trung, chỉ là giai thoại. [Thấp]

**Facebook**
- **Reels**: con số được trích nhiều nhất là **0,02–0,20 USD / 1.000 lượt xem**; vài trường hợp đặc biệt 1–5 USD; một số nguồn nêu 1–3 USD. Meta không công bố mức này. [Thấp]
- **Quảng cáo xen video dài**: khoảng 3–6 USD / 1.000 lượt xem, creator nhận khoảng 55% (một nguồn). [Thấp]
- Quy mô: Meta cho biết Facebook trả khoảng **3 tỷ USD** cho creator trong 2025 (+35% so với 2024); Reels chiếm khoảng 60%. [Vừa, qua RouteNote và MediaPost]

### 4.3 Bảng RPM so sánh (trên 1.000 lượt xem)

| Nguồn thu | Khoảng giá trị | Độ tin cậy |
|---|---|---|
| YouTube video dài, giải trí | 1–8 USD | Vừa |
| YouTube video dài, công nghệ/giáo dục | 4–15 USD | Vừa |
| YouTube video dài, tài chính/B2B/pháp lý | 10–30+ USD | Vừa |
| YouTube Shorts | Khoảng dùng để tính: 0,04–0,20 USD. Nguồn: AIR (274 kênh, trung vị cả năm) nêu 0,02–1,48 USD tùy ngách, và theo bản đọc sau thì đa số ngách quanh 0,07–0,20 USD (mình chưa đọc lại được trang AIR để xác nhận); Unilink nêu 0,04–0,10 USD, Argil 0,04–0,08 USD (hai trang này xem ở Phụ lục B; mình chỉ có số liệu từ bản tóm tắt kết quả tìm kiếm, chưa mở lại được trang gốc) | Vừa |
| TikTok Creator Rewards (8 nước) | 0,40–1,00 USD (trên lượt xem đủ điều kiện) | Vừa |
| Facebook Reels | 0,02–0,20 USD (một số nguồn nêu 1–3 USD) | Thấp |
| YouTube, khán giả Việt Nam | RPM khoảng 0,18–0,22 USD, CPM khoảng 1,14 USD. Dynamoi: RPM 0,22 USD và CPM 1,14 USD ở bản dữ liệu đến 14/7/2026; bản đọc sau nêu RPM 0,18 USD đến 14/10/2026 (mình chưa đọc lại được trang để xác nhận, và chưa có CPM của bản này) | Thấp |

Ghi chú: khán giả Mỹ có giá trị gấp khoảng 3–5 lần khán giả Đông Nam Á (một nguồn). Shorts trả khoảng 3–14% so với video dài trên cùng 1.000 lượt xem (AIR). Ba hàng RPM video dài theo ngách (giải trí, công nghệ/giáo dục, tài chính/B2B/pháp lý) là ước tính của bên thứ ba mà mình chưa gắn được tên nguồn cụ thể cho từng khoảng (xem lưu ý cuối Phụ lục B); đọc chúng như thứ tự độ lớn, không phải số đo.

### 4.4 Minh họa: 1 triệu lượt xem được bao nhiêu?

*Tự tính từ các khoảng số ở trên, **không phải dữ liệu đo thực tế**.*

| Nền tảng | Cách tính | Kết quả ước tính |
|---|---|---|
| YouTube video dài (giải trí) | 1.000 × 1–8 USD | 1.000–8.000 USD |
| YouTube video dài, khán giả Việt Nam | 1.000 × 0,18–0,22 USD | khoảng 180–220 USD |
| YouTube Shorts | 1.000 × 0,04–0,20 USD | 40–200 USD |
| TikTok Creator Rewards (8 nước) | 1.000.000 lượt **đủ điều kiện** × 0,40–1,00 USD / 1.000 | 400–1.000 USD (chưa tính Additional Reward). TikTok định nghĩa lượt đủ điều kiện bằng các loại trừ, không công bố tỷ lệ so với tổng lượt xem; nếu chỉ một phần số lượt qua được thì kết quả thấp hơn |
| Facebook Reels | 1.000 × 0,02–0,20 USD | 20–200 USD (trường hợp đặc biệt 1.000–5.000 USD) |

### 4.5 Thu nhập ngoài nền tảng

- **Brand deal:** theo khảo sát Creator Signals 2026 của #paid, **81%** creator có thu nhập từ brand deal; Later nêu 82% creator coi brand partnership là nguồn thu chính. Hai con số có thể đo khác nhau. [Vừa]
- **Affiliate:** TikTok Shop thường trả hoa hồng khoảng **5–20%** tùy ngành hàng; lời mời nhắm riêng đôi khi 18–25%; trả sau khoảng 15 ngày kể từ khi giao hàng. [Thấp: blog]
- **Sản phẩm, hàng hóa, khóa học:** có trong mọi khảo sát nhưng tỷ lệ khác nhau.

### 4.6 Cơ cấu thu nhập của creator (khảo sát)

| Khảo sát | Phát hiện |
|---|---|
| Báo cáo được NetInfluencer trích | Quảng cáo 21,6%; tiền nền tảng chi trả cho creator 13,3%; brand partnership 12,7%; bán sản phẩm + affiliate cộng thêm 21,2% |
| #paid, Creator Signals 2026 | 81% creator có thu nhập từ brand deal. Các tỷ lệ khác của khảo sát này (affiliate 8%, platform payouts 3%) chưa rõ định nghĩa |
| Later | 82% creator coi brand partnership là nguồn thu chính |

Kết luận an toàn: *tiền từ nền tảng chỉ là một phần*, brand deal + affiliate + sản phẩm thường lớn hơn. Chưa có tỷ lệ theo từng nền tảng. Một báo cáo nêu khoảng 12% creator kiếm trên 100.000 USD/năm và khoảng một nửa dưới 15.000 USD/năm. [Thấp]

### 4.7 Lưu ý riêng cho Việt Nam

- RPM của khán giả Việt Nam **thấp hơn nhiều** Mỹ/Úc (xem 4.3). Bài CafeF (cũ, không rõ năm) nêu CPM Việt Nam khoảng 0,3–0,5 USD.
- **TikTok Creator Rewards chưa mở cho Việt Nam**, nên các con số RPM TikTok ở trên chưa áp dụng cho creator ở Việt Nam.
- TikTok Shop Việt Nam: hoa hồng do **nhà bán đặt**, chưa có nguồn đáng tin về thu nhập điển hình. [Thấp]
- Facebook: Content Monetization hiện theo lời mời; Creator Fast Track chỉ dành cho người cư trú ở Mỹ, Canada, Anh, Úc. [Chính thức]
- YouTube: **Việt Nam có trong danh sách nước được đăng ký YPP** (trang "YouTube Partner Program availability"), nên điều kiện YPP áp dụng chung; chỉ là RPM thấp hơn. [Chính thức]

---

## 5. Khía cạnh bổ sung: video tạo bằng AI và đăng tự động bằng API

Có hai câu hỏi khác nhau, nên tách ra:
- **(A) Nội dung do AI tạo** có bị ảnh hưởng khả năng lên xu hướng và kiếm tiền không?
- **(B) Kênh đăng tải** (đăng tay trên app, lên lịch, hay đăng tự động bằng API) có ảnh hưởng không?

### 5.1 Kết luận ngắn

1. **Mình không thấy nền tảng nào công bố "do AI tạo" hay "đăng bằng API" là tín hiệu làm giảm xếp hạng.**
   - **TikTok:** "bật cài đặt nội dung AI **không ảnh hưởng phân phối** miễn là video không vi phạm Community Guidelines". [Chính thức]
   - **YouTube:** khai báo nhãn AI "không giới hạn khán giả và không ảnh hưởng quyền kiếm tiền". [Chính thức]
   - **Meta:** nhãn "AI info" chỉ cung cấp ngữ cảnh; từ 7/2024 không gỡ nội dung chỉ vì vi phạm chính sách video bị thao túng, trừ khi vi phạm quy định khác. [Chính thức, bài 4/2024]
2. **"Không công bố" không có nghĩa là "không ảnh hưởng".** Có các đường ảnh hưởng gián tiếp, đều có căn cứ chính thức:
   - bộ lọc **nội dung gốc / chất lượng / hàng loạt** (cả ba nền tảng);
   - quy tắc về **tự động hóa hàng loạt** (hành vi, không phải đường đăng);
   - **cổng API và mục đích sử dụng** (TikTok rất nghiêm);
   - **hạn mức số bài/ngày**;
   - nhãn AI tự động gắn qua metadata C2PA, không gỡ được.
3. **Chưa có nghiên cứu đối chứng** so sánh lượt xem của video AI với video người làm. [Vừa]

### 5.2 Nội dung do AI tạo: theo từng nền tảng

| | YouTube | TikTok | Facebook |
|---|---|---|---|
| Có cấm AI không | Không. "AI là công cụ để thể hiện, không thay thế" (CEO, 1/2026) | Không; cấm AIGC giả mạo nguồn uy tín/sự kiện khủng hoảng, giả mạo người của công chúng trong một số bối cảnh, dùng hình ảnh người dưới 18 hoặc người tư nhân không có phép | Không; Meta chủ trương gắn nhãn và giữ nội dung trừ khi vi phạm chính sách khác |
| Phải khai báo | **Có**, khi nội dung **chân thực** và tạo/sửa đáng kể bằng AI (người thật nói/làm điều chưa từng; sửa cảnh quay thật; cảnh chân thực chưa từng xảy ra; nhạc do AI tạo: danh sách điều kiện của trang ghi "nhạc là trọng tâm của video", nhưng danh sách ví dụ ghi "AI generated music" không kèm điều kiện, nên khai báo cả nhạc nền) | **Có**, với mọi AIGC chứa hình ảnh, âm thanh, video **chân thực**; chưa gắn nhãn có thể bị gỡ, hạn chế hoặc TikTok tự gắn nhãn | "AI info" gắn khi phát hiện chỉ báo chuẩn ngành (C2PA/IPTC) hoặc khi người đăng tự khai |
| Không phải khai báo | Nội dung **không chân thực**, chỉnh sửa nhỏ; AI cho **dàn ý, kịch bản, thumbnail, tiêu đề, phụ đề; nhân bản giọng của chính mình để lồng tiếng** | (nhãn tập trung vào nội dung chân thực) | — |
| Tự gắn nhãn | Có: công cụ AI của YouTube, metadata C2PA, hệ thống nội bộ. Nhãn từ C2PA/công cụ YouTube/duyệt thủ công **không gỡ được** | Có: hiệu ứng AI của TikTok, **Content Credentials (C2PA)**. Đã gắn thì **không gỡ được** | Có |
| Ảnh hưởng phân phối | Nhãn **không** giới hạn khán giả; nhưng YouTube giảm lan truyền **nội dung AI chất lượng thấp, lặp** bằng hệ thống chống spam/clickbait | Nhãn **không** ảnh hưởng phân phối nếu không vi phạm. Có thanh trượt "giảm nội dung AI" trong Manage Topics (thử nghiệm cuối 2025) [Vừa]. FYF loại nội dung dùng lại/chất lượng thấp | Nội dung không gốc bị giảm ưu tiên (xem 2.4); Meta không nêu AI là yếu tố riêng |
| Ảnh hưởng kiếm tiền | Xem 5.3 | Creator Rewards yêu cầu video "do chính bạn thiết kế, quay và sản xuất"; trang mình đọc **không có điều khoản riêng về AI**, nhưng loại slide video, ảnh chất lượng thấp, nội dung chỉ sửa nhẹ. **Suy luận:** video AI kiểu slideshow nhiều khả năng không đủ điều kiện [Thấp] | Tắt kiếm tiền nếu đăng chủ yếu nội dung không gốc; không có quy tắc riêng cho AI mà mình đọc được |

**Không khai báo thì sao:**
- YouTube: người liên tục không khai báo có thể bị gắn nhãn thủ công, **gỡ nội dung hoặc đình chỉ khỏi YPP**. [Chính thức]
- TikTok: nội dung AI chân thực chưa gắn nhãn có thể bị gỡ, hạn chế hoặc bị gắn nhãn. [Chính thức]

### 5.3 YouTube: AI và quyền kiếm tiền (YPP) [Chính thức]

Chính sách kiếm tiền yêu cầu nội dung **không "hàng loạt, chung chung, lặp lại hay thao túng"**.

- **Ví dụ không được kiếm tiền:**
  - "Nội dung AI làm từ mẫu chung/không gốc, tạo cảm giác sản xuất hàng loạt mà không thêm góc nhìn, hiểu biết chân thực của creator."
  - Kênh dựa nhiều vào mẫu chung hoặc chủ đề kích động cảm xúc.
  - Video ghép các clip AI không liên quan, không có mạch kể.
- **Ví dụ được chấp nhận:**
  - AI để hình dung một nhân vật và câu chuyện bạn tự nghĩ ra.
  - AI hỗ trợ viết kịch bản hoặc tạo hình nền cho nội dung có biên tập, nghiên cứu, sáng tạo.
- **Nguyên tắc:** "Nếu dùng công cụ tự động hoặc mẫu để tạo nội dung, sản phẩm cuối vẫn phải thể hiện tầm nhìn sáng tạo và mang lại giá trị giáo dục/giải trí."
- **AI đóng vai chuyên gia thật về chủ đề nhạy cảm** (bác sĩ AI, người dẫn podcast AI tư vấn đầu tư, AI diễn giải pháp luật, chính trị): **không được kiếm tiền**.
- **Phạm vi hình phạt:** chính sách nội dung dùng lại áp dụng cho **cả kênh**; nếu không rõ ai làm ra nội dung, có thể mất kiếm tiền toàn kênh. Theo Chính sách spam: có thể **đình chỉ kiếm tiền hoặc chấm dứt kênh**; một số vi phạm bị gỡ nội dung và cảnh cáo/strike (3 strike trong 90 ngày có thể bị chấm dứt kênh).
- **Dữ liệu thực thi:** các hãng tin nêu YouTube xóa ít nhất 16 kênh "AI slop" (khoảng 4,7 tỷ lượt xem trọn đời) trong 1/2026; chỉ ở mức [Thấp].

### 5.4 Tự động hóa: quy tắc là về **hành vi**, không phải đường đăng

Không có quy định cấm "đăng bằng API" nói chung. Các quy định chính thức cấm **tự động hóa để làm hàng loạt hoặc thao túng**:

- **YouTube (Spam policy):** cấm "**Automated or synthetic mass-production**": dùng công cụ tự động hoặc AI để tạo hàng loạt nội dung giống nhau, chỉ thay đổi tối thiểu. Thử công cụ mới hoặc đăng vài biến thể của một video là được; **làm ngập nền tảng bằng nội dung lặp thì không**; bao gồm sản xuất hàng loạt có phối hợp và thao túng kỹ thuật để qua mặt bộ lọc. Ví dụ: kênh dùng cùng nhạc nền và hình ảnh AI lặp lại trên nhiều video, mỗi video đọc một kịch bản do AI viết. Cũng cấm tăng tương tác bằng bot. Hậu quả: đình chỉ kiếm tiền hoặc chấm dứt kênh.
- **YouTube (chính sách nhà phát triển API):** không được "tự động hóa hoặc kích hoạt lượt xem, upload, bình luận, like... mà không có sự đồng ý trước, cụ thể và rõ ràng của người dùng". Nghĩa là API upload là hợp lệ khi chủ kênh chủ động cấp quyền và cấu hình; cấm tạo hành động hàng loạt thay người khác mà họ không biết.
- **TikTok (Community Guidelines):** cấm dùng tự động hóa để chạy nhiều tài khoản hoặc gửi nội dung lặp; mua bán follower; dùng bot/script để tăng like/chia sẻ; **"nghiêm cấm công cụ tự động, script hoặc mẹo nhằm qua mặt hệ thống"**. Hậu quả: gỡ nội dung, cấm tài khoản; tài khoản bị hạn chế có thể mất khả năng đăng bài mới, hiện trong tìm kiếm hàng đầu hoặc FYF.
- **TikTok (Creator Rewards):** không được "tạo phần mềm độc hại hoặc sửa mã để đăng ký, đăng bài, hoặc tăng like/follow/lượt xem một cách nhân tạo".
- **Meta:** mạng lưới hàng trăm tài khoản đăng cùng nội dung: không đủ điều kiện kiếm tiền, có thể giảm reach (24/4/2025). Khoảng 500.000 tài khoản bị xử lý trong nửa đầu 2025 vì hành xử spam hoặc tương tác giả (14/7/2025).

### 5.5 Đăng bằng API: tài liệu chính thức nói gì

Đã đọc tài liệu của cả ba nền tảng (cập nhật 7–9/2026).

**YouTube Data API (`videos.insert`)**
- **Chế độ hiển thị mặc định:** nếu không chỉ định `status.privacyStatus` thì mặc định **public**; một số upload có thể mặc định private theo cài đặt tài khoản creator. [Chính thức]
- **Dự án chưa xác minh (unverified):** quy tắc hiện hành là trang tham chiếu `videos.insert`, ghi *"Videos uploaded from unverified API projects are not restricted to private viewing mode"* (video đăng từ dự án API chưa xác minh không bị giới hạn ở chế độ riêng tư). Chỉ cần coi đây là quy tắc đang áp dụng. Mục lịch sử sửa đổi ngày 28/7/2020 (dự án tạo sau 28/7/2020 bị khóa riêng tư cho tới khi audit) là bối cảnh lịch sử: mình không thấy mục nào sau đó nhắc lại quy tắc ấy, và nhiều blog vẫn lặp quy tắc cũ. [Chính thức]
- **Hạn mức:** từ 1/6/2026 hạn mức chia nhỏ; `videos.insert` có **bucket riêng**, mặc định **100 lượt gọi/ngày** mỗi dự án, mỗi lần tốn **1 đơn vị**. (Mục 4/12/2025 nói chi phí giảm từ ~1.600 xuống ~100 đơn vị, nay đã được thay thế bằng cơ chế mới.) Muốn nhiều hơn: hoàn tất **kiểm tra tuân thủ (compliance audit)** và gửi biểu mẫu Audit and Quota Extension. [Chính thức]
- **Khai báo AI qua API:** có trường `status.containsSyntheticMedia` (thêm 30/10/2024) trong `videos.insert` và `videos.update`. [Chính thức]
- **Hẹn giờ đăng (`status.publishAt`):** chỉ đặt được khi `status.privacyStatus` là `private` và video chưa từng được đăng công khai. Khi gọi `videos.update` để đặt hoặc đổi `publishAt`, phải đặt cả `privacyStatus` thành `private`, kể cả khi video đã private. Hẹn một giờ đã qua thì video được đăng ngay (giống chuyển `private` sang `public`). [Chính thức]
- **Hai trường khai báo khác trong `status` và `paidProductPlacementDetails`:** `status.selfDeclaredMadeForKids` (chủ kênh khai video hướng đến trẻ em) và `paidProductPlacementDetails.hasPaidProductPlacement` (đặt `true` nếu nội dung có quảng cáo đặt sản phẩm trả tiền; mặc định `false`). [Chính thức]

**TikTok Content Posting API**
- **Direct Post (đăng thẳng):** ứng dụng chưa audit **chỉ đăng được ở chế độ riêng tư (SELF_ONLY)**; tối đa **5 người dùng/24 giờ** và các tài khoản đó phải để riêng tư khi đăng. Lỗi `unaudited_client_can_only_post_to_private_accounts`. [Chính thức]
  - **Cách làm bài công khai sau đó (bằng tay):** Content Sharing Guidelines nêu rằng chủ tài khoản trước hết đổi chế độ tài khoản sang công khai, rồi đổi quyền riêng tư của **từng bài** từ riêng tư sang "Everyone". Cách này tốn công theo số bài, nên chỉ hợp khi đăng ít. [Chính thức]
- **Mục đích sử dụng được chấp nhận (điều kiện để audit):**
  - API phải "giúp các creator **thật** đăng **nội dung gốc**".
  - **Không chấp nhận:** ứng dụng sao chép nội dung tùy ý từ nền tảng khác sang TikTok.
  - **Không chấp nhận:** "**công cụ tiện ích giúp tải nội dung lên tài khoản mà bạn hoặc nhóm của bạn quản lý**".
  - Ứng dụng không được giới hạn ở bản thử nghiệm, phải dành cho đối tượng rộng, không phải nhóm nội bộ hay dùng riêng.
  - Do đó **một công cụ tự viết chỉ để đăng cho tài khoản của chính bạn khó vượt audit**, nên bài đăng qua API giữ ở chế độ riêng tư cho tới khi chủ tài khoản tự đổi từng bài sang công khai bằng tay (xem trên). [Chính thức]
- **Yêu cầu giao diện** (mục "Required UX Implementation in Your App" của Content Sharing Guidelines): [Chính thức]
  - Lấy thông tin creator mới nhất (`creator_info`) khi hiển thị trang đăng; hiện nickname của tài khoản sẽ nhận bài; dừng và báo thử lại sau khi API cho biết creator chưa đăng thêm được; kiểm tra độ dài video theo `max_video_post_duration_sec`.
  - Cho người dùng nhập tiêu đề; **tự chọn** quyền riêng tư từ danh sách `privacy_level_options` (không có giá trị mặc định); tự bật các tùy chọn bình luận, Duet, Stitch (không chọn sẵn; tô xám tùy chọn mà creator đã tắt trong ứng dụng; bài ảnh chỉ có "Allow Comment").
  - **Khai báo nội dung thương mại:** công tắc tắt mặc định. Khi bật, người dùng phải chọn ít nhất một trong "Your brand" (nhãn "Promotional content") và/hoặc "Branded content" (nhãn "Paid partnership"); nếu không chọn thì nút đăng bị vô hiệu. Nội dung "Branded content" không được để riêng tư: ứng dụng vô hiệu quyền "only me" hoặc tự chuyển sang công khai và báo cho người dùng.
  - Câu đồng ý trước nút đăng: "Music Usage Confirmation"; chọn "Branded content" thì thêm "Branded Content Policy".
  - Cho xem bản xem trước; chỉ gửi tệp sau khi người dùng đồng ý rõ ràng; báo rằng bài có thể mất vài phút mới hiện; theo dõi trạng thái bằng `publish/status/fetch` hoặc webhook.
  - Không được thêm watermark, logo hay link quảng bá vào nội dung; tiêu đề và hashtag soạn sẵn phải cho người dùng sửa trước khi đăng.
- **Giới hạn:** khoảng **15 bài/ngày/tài khoản creator** qua Direct Post (dùng chung mọi ứng dụng, mức thực tế khác nhau giữa creator); 6 yêu cầu/phút mỗi token; lỗi `spam_risk_too_many_posts` khi chạm trần. [Chính thức]
- **Khai báo AI qua API:** tham số `is_aigc`; nếu bật, video gắn nhãn "Creator labeled as AI-generated". [Chính thức]
- **Upload (hộp thư):** thay vì đăng thẳng, video được gửi vào hộp thư của creator; **creator phải bấm thông báo để chỉnh và hoàn tất đăng**; tối đa 5 video chờ duyệt trong 24 giờ. [Chính thức]
- **Công cụ riêng của TikTok:** Creator Academy giới thiệu **tải lên hàng loạt và hẹn giờ đăng ngay trên TikTok web**; video tối đa 60 phút. Đây là cách tự động hóa nhịp đăng mà không cần API. [Chính thức]

**Meta Graph API (Facebook Reels)**
- Chỉ đăng Reels lên **Page**, không lên trang cá nhân. [Chính thức]
- Giới hạn **30 Reels đăng qua API / 24 giờ** (cửa sổ trượt); Meta khuyên ứng dụng tự áp dụng giới hạn này, nhất là khi cho người dùng hẹn giờ. [Chính thức]
- Cần token Page cho người có quyền CREATE_CONTENT, cùng quyền `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`.
- Thông số video: dài 3–90 giây; tối thiểu 540×960 px (khuyến nghị 1080×1920); tỉ lệ 9:16 (API báo lỗi nếu ngoài khoảng từ 16:9 đến 9:16); 24–60 khung hình/giây; Reel đăng dạng story trên Page tối đa 60 giây. [Chính thức]
- **Yêu cầu giao diện** (mục "Sharing Disclosure"): ứng dụng phải cho người dùng thấy cách Reels của họ được dùng trên Facebook và cho chọn đối tượng xem. Đăng lên Page mặc định là công khai nên chỉ nên có lựa chọn "Public". [Chính thức]
- Tài liệu Reels Publishing mình đọc **không nêu tham số khai báo AI**. [Chính thức, theo những gì đọc được]

**Có nguồn chính thức nào nói đăng bằng API làm giảm reach không?** Không tìm thấy ở cả ba nền tảng. Các nhà cung cấp công cụ hẹn giờ nói không ảnh hưởng, nhưng bằng chứng yếu. [Thấp]

### 5.6 Bằng chứng thực nghiệm về hiệu quả

- **Không tìm thấy** nghiên cứu đối chứng so sánh lượt xem/tương tác giữa video AI và video người làm. [Vừa]
- **Tỷ lệ xuất hiện** (Kapwing, 6/2026, 10.742 video TikTok): khoảng **59%** nội dung hiện cho tài khoản mới là "AI slop", gấp ba lần tỷ lệ trên YouTube Shorts (khoảng 21%). Kapwing là công ty công cụ video có lợi ích riêng, phân loại thủ công. [Thấp]
- Điều này cho thấy nền tảng đang phân phối nhiều nội dung AI, nhưng **không chứng minh** nội dung AI hiệu quả hơn hay kém hơn.
- Dữ liệu duy nhất mang tính hiệu quả mà Meta công bố là về **nội dung gốc** nói chung (xem 2.4), không riêng nội dung AI.

### 5.7 Hàm ý thực tế cho một quy trình có AI và tự động hóa

*(Đây là suy luận từ các chính sách ở trên, không phải lời khuyên của nền tảng.)*

1. **Giá trị riêng trên từng video**: kịch bản, góc nhìn, dữ liệu, giọng nói mang tính cá nhân. Các ví dụ vi phạm đều là **mẫu lặp** (cùng nhạc, cùng kiểu hình ảnh, cùng khuôn kịch bản). Trên Facebook, người xuất hiện trực tiếp và đưa ra điều mới là yếu tố Meta nêu rõ.
2. **Khai báo AI đúng chỗ**: dùng `containsSyntheticMedia` (YouTube) và `is_aigc` (TikTok) khi nội dung chân thực (kể cả nhạc do AI tạo trên YouTube); không xóa metadata C2PA, vì nhãn tự động từ C2PA không gỡ được.
3. **Tránh chủ đề nhạy cảm do "chuyên gia AI" trình bày** (sức khỏe, pháp lý, tài chính, chính trị) nếu muốn kiếm tiền trên YouTube.
4. **Giữ nhịp đăng hợp lý.** YouTube cho phép "vài biến thể" nhưng cấm "làm ngập". Từ 2027, kênh chỉ cần 2 video dài hoặc 5 Shorts mỗi 90 ngày để được coi là hoạt động.
5. **Chọn đường đăng phù hợp với từng nền tảng:**
   - **YouTube:** dùng API của chính bạn được; mặc định 100 upload/ngày; dự án chưa xác minh không bị khóa riêng tư theo trang tham chiếu hiện hành; xin tăng hạn mức bằng audit nếu cần.
   - **TikTok:** nếu là công cụ cho tài khoản của chính bạn, Direct Post chưa audit sẽ đăng ở chế độ riêng tư. Tài liệu cho phép chủ tài khoản đổi tài khoản sang công khai rồi đổi từng bài sang "Everyone" bằng tay, nên chỉ hợp khi đăng ít bài. Hai cách khác: **Upload (hộp thư)** rồi bấm đăng thủ công, hoặc **hẹn giờ và tải hàng loạt trên TikTok web** của chính TikTok.
   - **Facebook:** Reels qua API chỉ đăng được lên Page, tối đa 30/24 giờ.
6. **Không nhân bản nội dung** giữa nhiều tài khoản hoặc đăng video trùng lặp: Meta giảm phân phối bản sao, TikTok không đề xuất nội dung trùng, Meta xử lý mạng lưới nhiều tài khoản.
7. **Theo dõi công cụ chẩn đoán**: Studio (Viewed vs swiped away), Professional Dashboard và màn hình Support của Facebook.

### 5.8 Những điều còn mở

- Quy tắc riêng của Meta về nội dung AI và kiếm tiền trên Facebook (trang chính thức mình đọc được không nêu).
- Chính sách Creator Rewards của TikTok đối với video hoàn toàn bằng AI: trang không có điều khoản riêng, kết luận trong 5.2 là suy luận.
- Hiệu quả thực tế của video AI so với video người làm trên cùng kênh.

---

## 6. Kết luận và gợi ý hành động

1. **Đừng chạy theo "thuật toán"**: giữ chân người xem trong vài giây đầu và tạo lý do để chia sẻ (kinh nghiệm của người làm nội dung, không phải điều nền tảng công bố). Nội dung lặp, đăng lại, sản xuất hàng loạt bị siết trên cả ba nền tảng, dù do AI hay do người làm.
2. **YouTube là con đường bật kiếm tiền dễ dự đoán nhất** và là nền tảng duy nhất trong ba nơi mà tài liệu chính thức mình đọc xác nhận là mở cho Việt Nam (danh sách nước YPP). Với Facebook, tài liệu không nêu danh sách nước, chỉ nói theo lời mời. Ngưỡng sẽ tăng gấp đôi cho người mới từ 1/2/2027.
3. **TikTok:** Creator Rewards chưa mở cho Việt Nam. Hướng kiếm tiền khác (Shop, LIVE, brand deal) cần kiểm chứng riêng.
4. **Facebook:** Content Monetization hiện theo lời mời; hãy bày tỏ quan tâm trong dashboard và theo dõi màn hình Support.
5. **AI và tự động hóa** được phép, nhưng phải có giá trị riêng ở từng video, khai báo đúng, và tôn trọng mục đích sử dụng của API (TikTok đặc biệt nghiêm).
6. **Đa dạng hóa thu nhập:** brand deal, affiliate, sản phẩm. Tiền nền tảng trả thường nhỏ, nhất là Shorts, Reels và khán giả Việt Nam.

---

## Phụ lục A. Điểm cần kiểm chứng trước khi xuất bản

**Đã xác minh từ nguồn chính thức:**
- Mốc YPP 1/2/2027 và cách áp dụng cho kênh hiện có.
- Cấp sớm 500 subscriber, kèm điều kiện 3 video công khai hợp lệ trong 90 ngày (trang "expanded YouTube Partner Program").
- Thanh toán Shorts tính theo "engaged views".
- Ngày gỡ Trending (khoảng 21/7/2025).
- **Creator Rewards không mở cho Việt Nam; YPP của YouTube có mở cho Việt Nam.**
- Điều kiện Creator Rewards và định nghĩa nội dung gốc.
- Facebook Content Monetization chỉ theo lời mời; phạm vi Creator Fast Track; định nghĩa nội dung gốc của Meta (13/3/2026).
- Hạn mức `videos.insert`: 100 lượt gọi/ngày, 1 đơn vị/lần; trường `containsSyntheticMedia` và `is_aigc`.
- Video đăng bằng `videos.insert` từ dự án API chưa xác minh không bị giới hạn ở chế độ riêng tư (trang tham chiếu hiện hành); mục 28/7/2020 là lịch sử.
- Quy tắc TikTok: ứng dụng chưa audit chỉ đăng riêng tư (chủ tài khoản có thể đổi từng bài sang công khai bằng tay), và mục đích sử dụng loại trừ công cụ chỉ cho tài khoản của chính bạn.

**Còn mở:**

| # | Điểm cần xác minh | Vì sao | Cách xác minh |
|---|---|---|---|
| 1 | Creator Rewards có loại video hoàn toàn bằng AI không | Trang không có điều khoản riêng về AI | Điều khoản chương trình trong TikTok Studio (khi có quyền truy cập) |
| 2 | Quy tắc riêng của Meta về nội dung AI và kiếm tiền trên Facebook | Chỉ có bài nhãn AI (4/2024), không có quy tắc kiếm tiền riêng cho AI | Trung tâm trợ giúp / chính sách kiếm tiền của Meta |
| 3 | Hoa hồng và điều kiện TikTok Shop, LIVE tại Việt Nam | Chỉ có blog | Seller Center TikTok Shop Việt Nam; trang LIVE của TikTok |
| 4 | RPM từng nền tảng | Không nền tảng nào công bố | Dữ liệu thực của kênh bạn |
| 5 | Facebook Reels xếp hạng bằng khảo sát từ 14/1/2026 | Chỉ một nguồn blog | Bản tin / trang minh bạch của Meta |

---

## Phụ lục B. Nguồn đã dùng

### B1. Nguồn chính thức đã đọc

**YouTube**
- YPP overview & eligibility: https://support.google.com/youtube/answer/72851
- Expanded YPP (cấp sớm 500 subscriber): https://support.google.com/youtube/answer/13429240
- Changes to the YouTube Partner Program (1/2/2027): https://support.google.com/youtube/answer/12843009
- YPP availability (danh sách nước): https://support.google.com/youtube/answer/7101720
- YouTube Shorts monetization policies: https://support.google.com/youtube/answer/12504220
- YouTube channel monetization policies: https://support.google.com/youtube/answer/1311392
- Disclosing use of GenAI content: https://support.google.com/youtube/answer/14328491
- Spam policy: https://support.google.com/youtube/answer/2801973
- How YouTube Works, Recommendations: https://www.youtube.com/howyoutubeworks/recommendations/
- On YouTube's recommendation system: https://blog.youtube/inside-youtube/on-youtubes-recommendation-system/
- Thư CEO "The future of YouTube 2026": https://blog.youtube/inside-youtube/the-future-of-youtube-2026/
- YouTube Data API, videos.insert: https://developers.google.com/youtube/v3/docs/videos/insert
- Quota cost: https://developers.google.com/youtube/v3/determine_quota_cost
- Revision history: https://developers.google.com/youtube/v3/revision_history
- Quota and compliance audits: https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits
- API developer policies: https://developers.google.com/youtube/terms/developer-policies

**TikTok**
- Creator Rewards Program (trợ giúp): https://www.tiktok.com/support/faq_detail?id=7581821550694013452
- Creator Academy, Creator Rewards (tiếng Anh): https://www.tiktok.com/creator-academy/en/article/creator-rewards-program
- Creator Academy, Creator Rewards (tiếng Việt): https://www.tiktok.com/creator-academy/vi/article/creator-rewards-program
- About AI-generated content (trợ giúp): https://www.tiktok.com/support/faq_detail?id=7636670084747893268
- Community Guidelines, Integrity & Authenticity (2026-H2): https://www.tiktok.com/safety/en/policies-and-engagement/integrity-authenticity
- How TikTok recommends videos #ForYou (2020): https://newsroom.tiktok.com/how-tiktok-recommends-videos-for-you
- AI transparency and literacy (2024): https://newsroom.tiktok.com/partnering-with-our-industry-to-advance-ai-transparency-and-literacy
- Content Sharing Guidelines (API): https://developers.tiktok.com/doc/content-sharing-guidelines
- Direct Post API: https://developers.tiktok.com/doc/content-posting-api-reference-direct-post
- Upload API (inbox): https://developers.tiktok.com/doc/content-posting-api-reference-upload-video
- Content Posting API, Get Started: https://developers.tiktok.com/doc/content-posting-api-get-started

**Meta**
- Rewarding Original Creators on Facebook (13/3/2026): https://about.fb.com/news/2026/03/rewarding-original-creators-on-facebook/
- Combating Unoriginal Content (14/7/2025): https://creators.facebook.com/blog/combating-unoriginal-content
- Cracking Down on Spammy Content on Facebook (24/4/2025): https://about.fb.com/news/2025/04/cracking-down-spammy-content-facebook/
- Our Approach to Labeling AI-Generated Content (4/2024): https://about.fb.com/news/2024/04/metas-approach-to-labeling-ai-generated-content-and-manipulated-media/
- Facebook Content Monetization: https://creators.facebook.com/tools/facebook-content-monetization
- Creator Fast Track: https://creators.facebook.com/creator-fast-track
- Policies & Guidelines: https://creators.facebook.com/stay-safe/policies-and-guidelines
- Reels Publishing API: https://developers.facebook.com/docs/video-api/guides/reels-publishing

### B2. Nguồn bên thứ ba

**YouTube: điều kiện, thay đổi 2027, thu nhập**
- AIR Media-Tech: https://air.io/en/monetization/youtube-partner-program-requirements-2026-the-complete-guide
- vidIQ: https://vidiq.com/blog/post/youtube-partner-program-changes-2027/
- RouteNote: https://routenote.com/radar/youtube-monetization-requirements-2027-new-ypp-rules-double-watch-hours-and-shorts-views/
- Search Engine Journal: https://www.searchenginejournal.com/youtube-updates-partner-program-terms-shorts-payout-rules/585331/
- ppc.land: https://ppc.land/youtube-cuts-shorts-pay-for-channels-under-10m-views-from-february-2027/
- eMarketer: https://www.emarketer.com/content/youtube-s-creator-partner-rules-favor-scale-shorts-payouts-stricter
- NewsShooter: https://www.newsshooter.com/2026/08/10/youtube-updates-its-partner-program/
- Net Influencer: https://www.netinfluencer.com/youtube-raises-bar-for-new-creators-to-join-partner-program-tightens-shorts-payout-threshold/
- AIR (RPM Shorts, 274 kênh): https://air.io/en/air-data-findings/youtube-shorts-rpm-vs-long-form-how-much-do-shorts-earn-in-2026
- vidIQ (ngách): https://www.vidiq.com/blog/post/most-profitable-youtube-niches
- Argil (RPM Shorts 0,04–0,08 USD, đọc qua bản tóm tắt tìm kiếm): https://www.argil.ai/blog/how-much-do-youtubers-make
- Unilink (RPM Shorts 0,04–0,10 USD, đọc qua bản tóm tắt tìm kiếm): https://www.unilink.us/blog/how-much-does-youtube-pay-per-1000-views
- Dynamoi (RPM Việt Nam): https://dynamoi.com/data/youtube-adsense-rpm/vn
- Exchange4media (100 tỷ USD): https://www.exchange4media.com/industry-briefing-news/mrbeast-highlights-scale-of-creator-economy-with-youtubes-100-billion-payout-figure-151292.html
- Social Samosa (gỡ Trending): https://www.socialsamosa.com/news-2/youtube-trending-page-expands-hype-launches-charts-based-discovery-9500921
- Mediaweek (inauthentic content): https://mediaweek.com.au/platforms-push-back-youtube-and-meta-crack-down-on-authentic-content
- CafeF (CPM Việt Nam, bài cũ): https://cafef.vn/hot-tiktoker-tun-pham-co-the-kiem-bao-nhieu-tien-tu-youtube-va-tiktok-188230401184920973.chn

**TikTok**
- Argil (RPM): https://argil.ai/blog/how-much-does-tiktok-pay-per-view
- Elev8or (RPM): https://www.elev8or.io/blog/tiktok-creator-rewards-rpm-2026
- Advertise Purple (hoa hồng affiliate): https://www.advertisepurple.com/?p=11584
- Outfy (affiliate): https://www.outfy.com/blog/tiktok-affiliate-marketing/
- MISA eShop (hoa hồng do nhà bán đặt): https://www.misaeshop.vn/13146/tiep-thi-lien-ket-tiktok-affiliate-marketing-tiktok/
- MagicHour (LIVE gifts): https://magichour.ai/blog/how-much-does-tiktok-pay
- Storyboard18 (thanh trượt AI): https://www.storyboard18.com/digital/tiktok-introduces-controls-to-let-users-adjust-volume-of-ai-generated-content-84502.htm

**Facebook**
- Buffer: https://www.buffer.com/resources/how-to-make-money-on-facebook/
- RouteNote (3 tỷ USD, Fast Track): https://routenote.com/blog/facebook-creator-payouts-3-billion-2025/
- MediaPost: https://www.mediapost.com/publications/article/413590/
- AdaptlyPost (Reels per 1.000 lượt xem): https://adaptlypost.com/en/blog/how-much-does-facebook-reels-pay-per-1000-views

**AI và thực thi**
- eWeek (thư CEO YouTube): https://www.eweek.com/fr/news/youtube-ai-slop-crackdown-creators/
- OutlierKit: https://outlierkit.com/resources/youtube-ai-slop-crackdown-2026/
- The Next Web (Kapwing, TikTok): https://thenextweb.com/news/tiktok-ai-slop-59-percent-new-users-kapwing-study

**Khảo sát thu nhập creator**
- NetInfluencer (#paid Creator Signals 2026): https://www.netinfluencer.com/survey-81-percent-of-creators-rely-on-brand-deals-as-primary-income-amid-life-milestones/
- NetInfluencer: https://www.netinfluencer.com/creators-favor-long-term-brand-partnerships-as-platform-diversification-becomes-the-norm-report-finds/
- Later: https://later.com/blog/2026-creator-income-diversified-monetization/

**Nguồn đã bị tài liệu chính thức thay thế (không dùng làm căn cứ):** các blog nêu "API YouTube chưa audit bị khóa riêng tư" và "chi phí upload 1.600 đơn vị" (Ayrshare, Phyllo); blog nêu Creator Rewards "có ở Việt Nam" (Rentracks Việt Nam, Toptal, ShortSync); blog nêu ngưỡng Facebook Content Monetization (10.000 follower/600.000 phút).

*Lưu ý về bốn trang RPM của bên thứ ba (AIR, Dynamoi, Unilink, Argil): máy chủ của chúng bị chặn khi mình kiểm lại, nên chưa mở lại được từ phiên viết báo cáo. Số liệu của Unilink và Argil chỉ có từ bản tóm tắt kết quả tìm kiếm. Cần mở trực tiếp các trang này trước khi xuất bản.*

*Lưu ý: hai trường hợp chưa gắn được tên nguồn: (1) nguồn RPM video dài theo ngách (giải trí 1–8 USD, công nghệ/giáo dục 4–15 USD, tài chính/B2B/pháp lý 10–30+ USD); (2) nguồn các khảo sát #paid chưa rõ định nghĩa tỷ lệ. Cần truy lại trước khi xuất bản.*

---

## Phụ lục C. Gợi ý bố cục report Moda (khoảng 12 trang)

1. Trang bìa + ghi chú độ tin cậy (Chính thức / Cao / Vừa / Thấp)
2. Tóm tắt 9 ý (mục 1)
3. "Lên xu hướng" hoạt động thế nào: nguyên lý chung + bảng so sánh (2.1, 2.5)
4. YouTube + TikTok + Facebook: tín hiệu và thứ bị loại khỏi đề xuất (2.2 đến 2.4)
5. Điều kiện bật kiếm tiền: bảng tóm tắt 3 nền tảng, nêu rõ "TikTok: 8 nước, không có Việt Nam" (3.4)
6. Mốc 1/2/2027 của YouTube: dòng thời gian (3.1)
7. Thu nhập trên 1.000 lượt xem: biểu đồ cột RPM, nên dùng thang logarit vì chênh lệch hàng chục lần (4.3)
8. 1 triệu lượt xem được bao nhiêu + thu nhập ngoài nền tảng (4.4, 4.6)
9. AI: có bị ảnh hưởng không (bảng 5.2 + 5.3)
10. Tự động hóa và API: hành vi bị cấm, cổng audit, mục đích sử dụng của TikTok (5.4, 5.5)
11. Hàm ý cho quy trình có AI và API (5.7)
12. Kết luận + việc cần kiểm chứng (mục 6, Phụ lục A)
