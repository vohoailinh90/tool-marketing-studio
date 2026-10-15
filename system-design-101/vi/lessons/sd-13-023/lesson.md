# NoOps và DevOps: mô hình hosting khác cách tổ chức nhóm

Hai thuật ngữ này, NoOps (No Operations — không cần nhóm vận hành riêng) và DevOps (Development và Operations — phát triển và vận hành), hay bị đặt cạnh nhau như hai lựa chọn, nhưng chúng trả lời hai câu hỏi khác nhau: ứng dụng chạy ở mô hình hosting nào, và nhóm bạn tổ chức công việc vận hành ra sao.

![Hai câu hỏi tách biệt: mô hình hosting (máy chủ tự quản, nền tảng quản lý, hàm serverless) quyết định nhà cung cấp lo những lớp nào; cách tổ chức nhóm — tách nhóm dev (developer, người phát triển) và ops (operations, vận hành), hoặc DevOps (Development và Operations, gộp hai việc) — quyết định ai trong nhóm xử lý phần còn lại. Dù chọn gì, mã, cấu hình, quyền, giám sát, sự cố và chi phí vẫn còn việc cho bạn, và serverless có ngoại lệ với container image, runtime tự dựng, chế độ cập nhật runtime không tự động hay runtime đã ngừng hỗ trợ.](../../diagrams/sd-13-023-main.svg)

**Đọc hình:** thẻ 1 và 2 là hai trục độc lập, chọn một ô ở mỗi thẻ; hai thẻ sau là phần còn lại bất kể bạn chọn gì.

## Nhìn hình thử trả lời

Một nhóm theo DevOps chạy hàm serverless đóng gói bằng container image. Khi có bản vá cho ảnh cơ sở, ai chịu trách nhiệm cập nhật?

<details>
<summary>Xem đáp án</summary>

Nhóm bạn. Theo tài liệu Lambda, với hàm dùng container image hoặc runtime tự dựng, việc cập nhật runtime và ảnh cơ sở thuộc về khách hàng; nhà cung cấp vẫn lo hạ tầng bên dưới. Với runtime do Lambda quản lý, chế độ mặc định (Auto) để Lambda tự áp dụng bản cập nhật, còn ở chế độ Function update hoặc Manual thì bạn phải cập nhật hàm hoặc chọn phiên bản. Với runtime đã ngừng hỗ trợ, Lambda có thể không còn áp bản vá bảo mật hay bản cập nhật và hàm dùng nó không còn được hỗ trợ kỹ thuật, nên đừng trông chờ bản vá mà hãy chuyển sang runtime còn được hỗ trợ.

</details>

## Giới hạn cần nhớ

Hosting không xóa vận hành: sự cố, cảnh báo, giới hạn dịch vụ, bảo mật, quyền truy cập và chi phí vẫn cần người xử lý, dù nhà cung cấp lo nhiều lớp hơn. Ranh giới trách nhiệm đổi theo dịch vụ bạn chọn, nên hãy đọc phần chia việc của đúng dịch vụ đó. Mức tải không tự nó loại bỏ serverless vì nhiều dịch vụ tự mở rộng; điều cần cân nhắc là hình dạng công việc (theo sự kiện, biến động hay chạy liên tục), hạn mức của nhà cung cấp, yêu cầu độ trễ và mức kiểm soát hạ tầng bạn cần.

<details>
<summary>Xem sâu hơn</summary>

- **Mô hình hosting:** máy chủ hay máy ảo tự quản thì bạn lo hệ điều hành, bản vá và runtime; nền tảng quản lý (PaaS, tức Platform as a Service — nền tảng như một dịch vụ; container không cần quản lý node) giảm phần máy chủ; hàm serverless (Function as a Service, FaaS — hàm như một dịch vụ) để nhà cung cấp lo máy chủ, hệ điều hành và, với runtime được quản lý ở chế độ cập nhật tự động (Auto, mặc định), cả runtime. BaaS (Backend as a Service — phần máy chủ phía sau như một dịch vụ) cung cấp cơ sở dữ liệu, xác thực... dưới dạng dịch vụ.
- **Mô hình trách nhiệm chia sẻ:** nhà cung cấp lo "bản thân đám mây", khách hàng lo "những gì chạy trên đám mây"; ranh giới đổi theo dịch vụ được chọn.
- **DevOps là cách tổ chức công việc:** AWS (Amazon Web Services — dịch vụ điện toán đám mây của Amazon) mô tả nó là tập hợp văn hóa, thực hành và công cụ. Có nơi gộp dev (developer — người phát triển phần mềm) và ops (operations — vận hành) thành một nhóm, có nơi giữ hai nhóm cộng tác; điểm chung là trách nhiệm được chia sẻ. Cách này áp dụng được dù hosting là máy chủ hay serverless.
- **NoOps** thường chỉ trạng thái việc hạ tầng gần như dồn hết cho nhà cung cấp, ví dụ với serverless. Nó mô tả hệ quả của lựa chọn hosting, không phải một cách tổ chức khác thay cho DevOps.
- Nhiều tổ chức dùng nhiều mô hình hosting cho các hệ thống khác nhau.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/devops-vs-noops.md).
- AWS: [DevOps là gì](https://aws.amazon.com/devops/what-is-devops/), [mô hình trách nhiệm chia sẻ](https://aws.amazon.com/compliance/shared-responsibility-model/), [runtime của Lambda](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html), [trách nhiệm cập nhật runtime](https://docs.aws.amazon.com/lambda/latest/dg/runtime-management-shared.html).
