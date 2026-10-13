# Terraform biến mã thành hạ tầng

Terraform quản lý hạ tầng bằng mã: bạn khai báo hạ tầng muốn có, Terraform tính chênh lệch với thực tế rồi mới thay đổi.

![Quy trình dọc: viết tệp cấu hình, init tải provider, plan xem trước thay đổi, apply gọi API nhà cung cấp, rồi state ghi lại hiện trạng.](../../diagrams/sd-13-018-main.svg)

**Đọc hình:** mũi tên là thứ tự chạy lệnh; plan không thay đổi gì trên hạ tầng thật.

## Nhìn hình thử trả lời

Có người sửa tài nguyên bằng tay trên giao diện cloud. Lần chạy `plan` kế tiếp sẽ cho thấy gì?

<details>
<summary>Xem đáp án</summary>

Sự lệch (drift): Terraform đọc hiện trạng thật, thấy khác khai báo và đề xuất đưa tài nguyên trở về như trong tệp cấu hình.

</details>

## Giới hạn cần nhớ

State có thể chứa dữ liệu nhạy cảm, nên không để trong kho mã công khai. Làm nhóm thì dùng backend từ xa có khóa để hai người không apply cùng lúc.

<details>
<summary>Xem sâu hơn</summary>

- **plan lưu được:** `terraform plan -out=tfplan` rồi `terraform apply tfplan` bảo đảm áp dụng đúng bản đã duyệt.
- **State:** ánh xạ tài nguyên khai báo với tài nguyên thật; mất state thì Terraform không biết nó đang quản lý gì.
- **Module và registry:** đóng gói phần cấu hình tái sử dụng; registry cung cấp module cộng đồng.
- **Trong CI/CD:** `plan` thường chạy tự động trong pull request, `apply` sau khi duyệt.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-terraform-turn-code-into-cloud.md).
- HashiCorp: [giới thiệu](https://developer.hashicorp.com/terraform/intro), [lệnh plan](https://developer.hashicorp.com/terraform/cli/commands/plan), [state](https://developer.hashicorp.com/terraform/language/state).
