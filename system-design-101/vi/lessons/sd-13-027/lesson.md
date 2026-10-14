# Thiết kế pipeline CI/CD cho một repo: năm quyết định

Thay vì kể pipeline CI/CD (Continuous Integration/Continuous Delivery hoặc Deployment — tích hợp liên tục/chuyển giao hoặc triển khai liên tục) có những giai đoạn nào, hãy nhìn các quyết định bạn phải đưa ra khi dựng pipeline cho một repo (viết tắt của repository — kho mã nguồn): khi nào chạy, chạy nhanh bằng cách nào, cấp quyền gì, ai được đưa lên môi trường nào và khi nào được merge.

![Năm quyết định khi dựng pipeline cho một repo (viết tắt của repository — kho mã nguồn): khi nào chạy, làm sao chạy nhanh, cấp quyền gì, ai được đưa lên môi trường nào, và điều kiện để merge.](../../diagrams/sd-13-027-main.svg)

**Đọc hình:** năm quyết định độc lập; tên cơ chế là của GitHub Actions nhưng nền tảng khác có khái niệm tương tự.

## Từ viết tắt

- **CI** (Continuous Integration) — tích hợp liên tục: tự động xây dựng và kiểm tra mã mỗi khi có thay đổi.
- **CD** (Continuous Delivery) — chuyển giao liên tục: tự động đưa bản đã kiểm tra tới bước phát hành hoặc triển khai.
- **PR** (Pull Request) — yêu cầu gộp mã: đề nghị đưa thay đổi từ một nhánh vào nhánh chính để người khác xem xét.
- **OIDC** (OpenID Connect) — chuẩn xác thực dựa trên token định danh: workflow nhận một token từ GitHub rồi đổi lấy thông tin xác thực ngắn hạn từ nhà cung cấp cloud, thay vì lưu khóa dài hạn trong bí mật.
- **OpenID** (Open IDentity) — tên một chuẩn xác thực mở, phần cuối của tên là identity (danh tính); bài dùng OpenID Connect để workflow đổi token của GitHub lấy thông tin xác thực ngắn hạn.

## Nhìn hình thử trả lời

Một pull request từ fork của người lạ có được dùng bí mật của repo gốc trong workflow không?

<details>
<summary>Xem đáp án</summary>

Mặc định không: với sự kiện `pull_request` từ fork, bí mật (trừ GITHUB_TOKEN quyền thấp) không được chuyển cho runner, để người lạ không đọc được. Sự kiện `pull_request_target` chạy với ngữ cảnh repo gốc nên phải rất thận trọng khi chạy mã từ PR (pull request — yêu cầu gộp mã). Kho riêng tư có thể đổi mặc định này trong cài đặt Actions.

</details>

## Giới hạn cần nhớ

Pipeline xanh chỉ chứng minh các kiểm tra đã viết đều qua, không bảo đảm không có lỗi. Mỗi quyết định có giá: cổng chặn nhiều làm chậm phản hồi, người duyệt thủ công làm chậm phát hành, và quyền quá chặt có thể làm pipeline hỏng khi cần việc mới. Kiểm thử chập chờn làm mọi người mất tin vào kết quả đỏ.

<details>
<summary>Xem sâu hơn</summary>

```yaml
name: ci
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm test
```

- **Hủy lượt cũ:** chỉ hủy với PR; không nên hủy lượt đang chạy trên nhánh chính hay phát hành.
- **Quyền tối thiểu:** khai `permissions` ở mức workflow hoặc job, chỉ mở thêm khi cần.
- **OIDC (OpenID Connect — chuẩn xác thực dựa trên token định danh):** workflow nhận một token OIDC từ GitHub rồi đổi lấy thông tin xác thực ngắn hạn từ nhà cung cấp cloud, thay vì lưu khóa dài hạn trong bí mật.
- **Environment:** gắn bí mật riêng cho từng môi trường và có thể đặt người duyệt bắt buộc. Người duyệt bắt buộc phụ thuộc gói: trên gói Free, Pro và Team nó chỉ dùng được ở kho công khai, còn kho riêng tư hoặc nội bộ cần gói cao hơn như GitHub Enterprise. Environment và bí mật của environment ở kho riêng tư cần gói Pro, Team hoặc Enterprise. Nếu không có người duyệt bắt buộc, cần một cơ chế duyệt khác.
- **Branch protection:** đặt các kiểm tra bắt buộc phải qua trước khi merge vào nhánh chính.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/cicd-pipeline-explained-in-simple-terms.md).
- GitHub Docs: [workflow syntax](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions), [bảo mật workflow](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions), [cài đặt Actions của kho](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository), [environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments), [protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
- Martin Fowler: [DeploymentPipeline](https://martinfowler.com/bliki/DeploymentPipeline.html).
