# Chuỗi CI/CD của Netflix: tám chặng của một thay đổi

**Theo bài nguồn, một thay đổi mã ở Netflix đi qua tám chặng, từ lập kế hoạch tới xử lý sự cố, và mỗi chặng có công cụ riêng.**
Bài này đi theo một thay đổi nhỏ qua từng chặng, hỏi ở mỗi chặng: nó nhận gì vào và giao gì cho chặng sau.

![Tám chặng nối nhau. Lập kế hoạch: Jira để lên việc, Confluence để viết tài liệu. Viết mã: Java là ngôn ngữ chính cho dịch vụ phía sau. Build: Gradle và các plugin Gradle tự viết. Đóng gói: gói và các phụ thuộc vào một AMI. Kiểm thử: văn hóa thử trên môi trường thật, dựng công cụ hỗn loạn. Triển khai: Spinnaker tự làm, phát hành canary. Giám sát: số đo dồn về Atlas, Kayenta phát hiện bất thường. Sự cố: chia theo mức ưu tiên, xử lý bằng PagerDuty. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-02-019-main.svg)

## Từ viết tắt

- **CI** (Continuous Integration) — tích hợp liên tục: mỗi thay đổi mã được tự động build và kiểm thử.
- **CD** (Continuous Delivery) — chuyển giao liên tục: bản đã kiểm thử được tự động đưa tới bước phát hành.
- **AMI** (Amazon Machine Image) — ảnh máy ảo của Amazon: bản chụp sẵn hệ điều hành, phần mềm và phụ thuộc, dùng để bật máy chủ ảo mới.

## Đọc hình

Theo nguồn, tám chặng là:

1. **Lập kế hoạch:** đội kỹ sư dùng Jira để lên việc và Confluence để viết tài liệu. Chặng này giao ra một việc cần làm.
2. **Viết mã:** Java là ngôn ngữ chính cho dịch vụ phía sau; các ngôn ngữ khác dùng cho việc khác. Chặng này giao ra mã nguồn.
3. **Build:** chủ yếu dùng Gradle, kèm các plugin Gradle Netflix tự viết cho nhiều trường hợp. Chặng này giao ra chương trình đã dịch.
4. **Đóng gói:** gói phần mềm và các phụ thuộc được đóng vào một AMI để phát hành. Chặng này giao ra một ảnh máy chạy được ngay.
5. **Kiểm thử:** nguồn nói văn hóa của Netflix nhấn vào thử trên môi trường thật, nên họ dựng các công cụ gây hỗn loạn (cố tình làm hỏng một phần hệ thống để xem phần còn lại chịu được không).
6. **Triển khai:** Netflix dùng Spinnaker, công cụ họ tự làm, để phát hành kiểu canary: bản mới chạy trên một phần nhỏ máy trước.
7. **Giám sát:** số đo dồn về Atlas; Kayenta dùng để phát hiện bất thường.
8. **Báo sự cố:** sự cố được chia theo mức ưu tiên và xử lý bằng PagerDuty.

Bài [Học từ chuỗi CI/CD của công ty lớn](../sd-13-012/lesson.md) dùng cùng bài nguồn nhưng đọc theo rủi ro; bài này đọc theo thứ tự các chặng.

## Giới hạn cần nhớ

Bài nguồn chỉ nêu tên công cụ, một câu cho mỗi chặng. Nó không nói canary chạy trên bao nhiêu máy, Kayenta so sánh gì, hay mất bao lâu đi hết tám chặng. Câu "mỗi chặng giao ra gì" và lời giải thích canary, công cụ hỗn loạn là của người biên soạn.

## Nhìn hình thử trả lời

Kayenta báo bản canary có tỉ lệ lỗi cao bất thường. Theo hình, thông tin đó nên quay lại chặng nào, và vì sao đóng gói thành AMI giúp việc quay lui dễ hơn?

<details>
<summary>Xem đáp án</summary>

Nó quay lại chặng triển khai: Spinnaker dừng đưa bản mới lên thêm máy và trả phần canary về bản cũ. Vì mỗi bản phát hành là một AMI đóng sẵn, quay lui chỉ là bật lại máy từ AMI trước đó, không phải sửa phần mềm trên từng máy đang chạy.

</details>

<details>
<summary>Xem sâu hơn: tám chặng theo kiểu vòng lặp</summary>

- Giám sát và báo sự cố tạo ra việc mới cho chặng lập kế hoạch, nên tám chặng thật ra là một vòng.
- Chặng càng về sau thì lỗi phát hiện ở đó càng tốn kém, nên các đội thường đẩy kiểm tra lên sớm nhất có thể.
- Canary là cách giới hạn thiệt hại khi một lỗi lọt qua mọi chặng trước.

Đây là nhận xét chung của người biên soạn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/netflix-tech-stack-cicd-pipeline.md): tám chặng và công cụ của từng chặng.

Đã đọc nguồn ngày 2026-10-19. Tài liệu kỹ thuật của Netflix chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.
