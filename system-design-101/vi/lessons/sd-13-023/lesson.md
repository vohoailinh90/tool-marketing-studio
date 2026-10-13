# DevOps và NoOps: ai lo phần vận hành

Câu hỏi chung là ai chịu trách nhiệm chạy phần mềm sau khi viết xong. Ba mô hình trả lời ba cách.

![Ba thẻ: mô hình truyền thống chia các chức năng riêng và bàn giao, DevOps phối hợp liên tục giữa phát triển và vận hành, NoOps dùng serverless để nhà cung cấp lo phần lớn hạ tầng.](../../diagrams/sd-13-023-main.svg)

**Đọc hình:** càng xuống dưới thì phần vận hành bạn tự làm càng ít, nhưng không về không.

## Nhìn hình thử trả lời

Chạy mã trên một dịch vụ hàm không máy chủ. Ai vá hệ điều hành bên dưới?

<details>
<summary>Xem đáp án</summary>

Nhà cung cấp cloud. Bạn vẫn chịu trách nhiệm về mã, quyền truy cập, cấu hình, giám sát và chi phí.

</details>

## Giới hạn cần nhớ

NoOps không có nghĩa là hết vận hành. Sự cố, cảnh báo, giới hạn dịch vụ, bảo mật và chi phí vẫn cần người xử lý. Nó phù hợp khi tải và yêu cầu vừa phải, và có thể không đủ khi cần tùy biến sâu hay kiểm soát thời gian phản hồi.

<details>
<summary>Xem sâu hơn</summary>

- **FaaS** (Function-as-a-Service) chạy hàm khi có sự kiện; **BaaS** (Backend-as-a-Service) cung cấp cơ sở dữ liệu, xác thực... dưới dạng dịch vụ.
- **Mô hình trách nhiệm chia sẻ:** nhà cung cấp lo "bản thân đám mây", khách hàng lo "những gì chạy trên đám mây".
- **Thực tế:** nhiều tổ chức dùng cả ba mô hình cho các hệ thống khác nhau.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/devops-vs-noops.md).
- AWS: [mô hình trách nhiệm chia sẻ](https://aws.amazon.com/compliance/shared-responsibility-model/), [Lambda](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html).
