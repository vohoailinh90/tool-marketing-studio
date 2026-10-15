# Terraform plan báo thay đổi bạn không định làm: năm nguyên nhân

Bạn không sửa dòng mã nào mà `terraform plan` vẫn báo sẽ thêm, sửa hay thay thế tài nguyên. Plan so sánh mã, state và hạ tầng thật, nên mỗi thay đổi bất ngờ đều lần được về một chỗ lệch. Bài nêu năm nguồn lệch hay gặp và cách xác nhận từng cái.

![Năm nguyên nhân Terraform plan báo thay đổi ngoài ý muốn: hạ tầng bị sửa ngoài Terraform nên có drift, phiên bản provider hoặc module đổi, sai workspace hoặc đầu vào, giá trị do hệ thống ngoài tự điền hoặc thứ tự phần tử, và state không dùng chung hoặc bị người khác cập nhật.](../../diagrams/sd-13-018-main.svg)

**Đọc hình:** năm thẻ là năm nguồn lệch độc lập; thẻ nào cũng kèm cách xác nhận hoặc ngăn.

## Từ viết tắt

- **CI** (Continuous Integration) — tích hợp liên tục: tự động xây dựng và kiểm tra mã mỗi khi có thay đổi.

## Nhìn hình thử trả lời

Sáng nay bạn chạy `terraform plan` mà không đổi mã, và plan báo sẽ sửa kích thước một máy ảo về giá trị cũ trong mã. Đêm qua đồng nghiệp đã tăng kích thước máy đó trên giao diện cloud để xử lý sự cố. Có nên `apply` ngay không?

<details>
<summary>Xem đáp án</summary>

Chưa. Apply sẽ đưa kích thước về giá trị trong mã, tức hoàn tác bản vá của đồng nghiệp. Plan đã làm mới trạng thái trong bộ nhớ theo hạ tầng thật, chưa ghi vào state đã lưu, và thấy chỗ lệch (drift). Hãy hỏi người đã sửa, rồi chọn một trong hai: cập nhật mã cho khớp giá trị mới nếu đó là quyết định đúng, hoặc apply để về lại mã nếu thay đổi tay chỉ là biện pháp tạm. `terraform plan -refresh-only` cho xem riêng phần lệch mà không đề xuất thay đổi hạ tầng.

</details>

## Giới hạn cần nhớ

Plan chỉ biết những gì provider báo về, nên thay đổi ở thuộc tính mà provider không đọc được sẽ không hiện, và plan không thay cho review mã. State và tệp plan đã lưu có thể chứa dữ liệu nhạy cảm dạng rõ, nên không để trong kho mã công khai. Bài không dạy viết cấu hình hay chia module.

<details>
<summary>Xem sâu hơn</summary>

```bash
terraform workspace show                  # đang ở workspace nào
terraform plan -refresh-only              # chỉ xem phần lệch giữa state và hạ tầng thật, chưa ghi gì
terraform apply -refresh-only             # ghi phần lệch đó vào state, không đổi hạ tầng
terraform plan -out=plan.tfplan           # lưu plan để apply đúng bản đã xem
terraform apply plan.tfplan
```

- **Đọc ký hiệu:** `+` tạo mới, `-` xóa, `~` sửa tại chỗ, `-/+` xóa rồi tạo lại; dòng `# forces replacement` chỉ thuộc tính buộc phải thay thế tài nguyên. Dòng `-/+` ngoài ý muốn cần dừng lại kiểm tra trước, vì tài nguyên bị xóa rồi tạo lại.
- **Drift:** plan và apply mặc định làm mới state trong bộ nhớ theo hạ tầng thật trước khi so với mã (`-refresh=false` tắt bước này); plan không ghi phần làm mới đó vào state đã lưu, chỉ apply mới ghi. Chế độ `-refresh-only` lập plan chỉ để cập nhật state cho khớp hạ tầng thật, không đề xuất thay đổi hạ tầng: `terraform plan -refresh-only` chỉ cho xem những thay đổi sẽ được ghi vào state, còn state chỉ được cập nhật khi chạy `terraform apply -refresh-only` (hoặc apply một plan refresh-only đã lưu). Tài nguyên có sẵn mà chưa nằm trong state thì đưa vào bằng khối `import` (Terraform 1.5 trở lên) hoặc lệnh `terraform import`.
- **Phiên bản:** `terraform init` giữ đúng phiên bản provider đã ghi trong `.terraform.lock.hcl`; `terraform init -upgrade` mới chọn bản mới trong khoảng ràng buộc và cập nhật tệp khóa. Đưa tệp khóa vào kho mã để mọi người và CI (Continuous Integration — tích hợp liên tục) dùng cùng bản. Module từ registry cần ràng buộc `version` riêng.
- **Workspace và đầu vào:** mỗi workspace có state riêng; biến lấy từ `-var-file`, `terraform.tfvars` và biến môi trường `TF_VAR_tên`, nên cùng một mã với đầu vào khác cho plan khác.
- **Giá trị tự điền và thứ tự:** thuộc tính do hệ thống ngoài tự gắn (ví dụ tag do chính sách tổ chức thêm) tạo thay đổi ở mỗi lần plan; `lifecycle { ignore_changes = [tags] }` bỏ qua thuộc tính được liệt kê, nên dùng hẹp nhất có thể. Với danh sách mà provider trả về theo thứ tự khác mã, đưa các phần tử trong mã về đúng thứ tự đó.
- **State dùng chung:** nhiều backend từ xa hỗ trợ khóa state để hai thao tác không ghi cùng lúc; `-lock=false` bỏ khóa, chỉ dùng khi chắc không có thao tác nào khác.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-terraform-turn-code-into-cloud.md).
- HashiCorp: [lệnh plan](https://developer.hashicorp.com/terraform/cli/commands/plan), [refresh-only](https://developer.hashicorp.com/terraform/tutorials/cli/refresh), [tệp khóa phụ thuộc](https://developer.hashicorp.com/terraform/language/files/dependency-lock), [lifecycle](https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle), [khóa state](https://developer.hashicorp.com/terraform/language/state/locking), [import](https://developer.hashicorp.com/terraform/language/import).
