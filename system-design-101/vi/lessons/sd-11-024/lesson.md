# Hạ tầng bằng mã: bốn lớp, và vì sao khai báo hơn từng bước

**Cấp máy, mạng, cơ sở dữ liệu bằng tay thì chậm và khó lặp lại; viết chúng thành mã thì cấp lại được, kiểm tra được, sửa được.** Có bốn lớp bổ trợ nhau, từ đóng gói ứng dụng tới quản lý hạ tầng qua Git. Chúng không phải bốn nấc phải đi lần lượt: dùng hạ tầng bằng mã không cần container, và GitOps cũng áp được cho cấu hình ứng dụng chứ không chỉ cho hạ tầng. Bài này đi qua bốn lớp, rồi thử một ý nằm sau chúng: vì sao "mô tả trạng thái mong muốn" an toàn hơn "ghi lại các bước đã làm".

![Hai khung. Khung một, bốn lớp bổ trợ nhau của việc cấp hạ tầng bằng mã: container, điều phối container, hạ tầng bằng mã, GitOps. Khung hai, thử nghiệm: chạy một kịch bản kiểu từng bước hai lần tạo 6 máy thay vì 3, còn khai báo trạng thái mong muốn chạy lần hai thay đổi 0 máy; giảm từ 3 xuống 2 chỉ xóa 1 máy.](../../diagrams/sd-11-024-main.svg)

## Từ viết tắt

- **IaC** (Infrastructure as Code) — hạ tầng bằng mã: viết cấu hình máy, mạng, dịch vụ thành tệp để lưu phiên bản, kiểm tra và dùng lại như mã nguồn.
- **GitOps** (Git Operations) — vận hành qua Git: dùng quy trình của Git làm cách duy nhất để đổi hạ tầng, kho Git là nơi nói hạ tầng nên thế nào.
- **AWS** (Amazon Web Services) — dịch vụ web của Amazon: nền tảng đám mây có công cụ CloudFormation nhắc trong bài.

## Đọc hình

**Container.** Đóng gói ứng dụng cùng phụ thuộc của nó thành một đơn vị chạy giống nhau ở mọi nơi; Docker là công cụ phổ biến nhất. Điểm của lớp này: cách triển khai ứng dụng đã thành mã (một tệp mô tả cách dựng).

**Điều phối container.** Một ứng dụng thật có nhiều container; cần công cụ quyết định chạy cái nào ở đâu, thay cái hỏng, tăng giảm số lượng. Kubernetes là công cụ phổ biến nhất của lớp này.

**IaC.** Cấp phát và cấu hình hạ tầng cũng viết thành tệp để lưu phiên bản, kiểm tra và dùng lại. Terraform và CloudFormation (của AWS) khai báo hạ tầng cần có; Ansible nghiêng về cấu hình máy hơn là cấp máy.

**GitOps.** Dùng quy trình của Git (nhánh, yêu cầu gộp, duyệt) cộng với tích hợp và triển khai tự động để thay đổi hạ tầng và cấu hình: kho Git là nơi nói hạ tầng nên thế nào, công cụ tự đưa thực tế về đúng như vậy.

## Thử: từng bước hay trạng thái mong muốn

Ngày 2026-10-19, một chương trình Python nhỏ (không cấp máy thật, chỉ đếm). Cần ba máy chủ.

| Cách làm | Lần chạy 1 | Lần chạy 2 | Sau khi đổi mục tiêu xuống 2 máy |
|---|---|---|---|
| Từng bước ("tạo một máy" ba lần) | thêm 3, có 3 máy | thêm 3 nữa, có 6 máy | cần viết một kịch bản khác để xóa |
| Khai báo ("phải có 3 máy") | thay đổi 3, có 3 máy | thay đổi 0, có 3 máy | thay đổi 1, có 2 máy |

Khác biệt nằm ở chỗ công cụ khai báo so sánh điều mong muốn với điều đang có rồi chỉ làm phần chênh lệch. Chạy lại không gây hại (tính chất gọi là lặp lại không đổi kết quả, idempotent), và đổi mục tiêu chỉ là sửa một con số.

## Giới hạn cần nhớ

Mô hình chỉ đếm máy, không có phụ thuộc giữa tài nguyên, lỗi giữa chừng hay trạng thái đã bị sửa tay. Thực tế công cụ khai báo cũng cần lưu lại nó đã tạo gì để biết phần chênh lệch, và một công cụ tên là IaC vẫn có thể viết theo từng bước. Phân chia "Ansible là cấu hình, Terraform là cấp phát" là cách nói thường gặp, không phải ranh giới cứng.

## Nhìn hình trả lời

Một đội đang mở máy bằng tay trên bảng điều khiển của nhà cung cấp đám mây, và mỗi lần dựng môi trường kiểm thử mất nửa ngày. Lớp nào trong hình giải quyết đúng nỗi đau này?

<details>
<summary>Xem đáp án</summary>

Lớp IaC: khai báo môi trường kiểm thử thành tệp, dựng lại bằng một lệnh, và xóa khi xong. Container giúp đóng gói ứng dụng nhưng không tự cấp máy; điều phối giúp chạy nhiều container nhưng cũng cần hạ tầng bên dưới; GitOps là lớp đưa thay đổi hạ tầng qua quy trình duyệt; nó đi tốt cùng IaC nhưng không bắt buộc đứng sau IaC.
Đây là suy luận của người biên soạn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn kể bốn chiến lược trong một đoạn ngắn và đặt tên các công cụ. Bài này giữ bốn lớp và tên công cụ, rồi tách ý "khai báo" ra thử riêng. Mô tả các công cụ là kiến thức chung của người biên soạn, chưa đối chiếu lại với tài liệu của từng công cụ.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/a-cheatsheet-on-infrastructure-as-code-landscape.md): bốn chiến lược và tên công cụ. Thử nghiệm và đáp án là của người biên soạn.
- [Terraform — tài liệu về cách làm việc](https://developer.hashicorp.com/terraform/intro): khai báo, kế hoạch rồi áp dụng. Kiến thức chung, chưa mở lại trong phiên viết.
- [OpenGitOps — nguyên tắc](https://opengitops.dev/): trạng thái mong muốn khai báo, có phiên bản, được kéo và đối chiếu liên tục. Kiến thức chung, chưa mở lại trong phiên viết.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.
