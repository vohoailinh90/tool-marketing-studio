# Bản đồ kỹ năng của lập trình viên full-stack

**Full-stack nghĩa là làm được việc ở nhiều vùng của một ứng dụng, từ màn hình người dùng tới hạ tầng chạy ứng dụng; bảy vùng dưới đây là tấm bản đồ.**
Bài nguồn là một lộ trình; bài này giữ đúng bảy vùng nguồn nêu và xếp chúng thành ba nhóm theo vị trí trong một ứng dụng.

![Ba nhóm thẻ xếp dọc. Phía người dùng gồm giao diện web (frontend), ứng dụng di động và thiết kế giao diện, trải nghiệm. Phía máy chủ gồm backend với logic phía máy chủ và tích hợp dịch vụ, và cơ sở dữ liệu với lưu trữ, truy xuất, xử lý dữ liệu. Phía vận hành gồm điện toán đám mây và hạ tầng cùng DevOps, gồm triển khai và CI/CD. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-003-main.svg)

## Từ viết tắt

- **DevOps** (Development and Operations) — phát triển và vận hành: cách làm gắn việc viết phần mềm với việc đưa nó lên chạy và giữ nó chạy.
- **CI** (Continuous Integration) — tích hợp liên tục: tự động gộp và kiểm tra mã mỗi khi có thay đổi.
- **CD** (Continuous Delivery) — chuyển giao liên tục: tự động đưa bản đã kiểm tra tới bước phát hành; CI/CD là đường ống gồm cả hai.

## Đọc hình

Mô tả từng vùng theo bài nguồn; cách chia ba nhóm là của người biên soạn.

**Phía người dùng.**
Frontend là việc tạo giao diện và trải nghiệm người dùng của ứng dụng web. Phát triển di động là tạo ứng dụng cho thiết bị di động. Thiết kế giao diện và trải nghiệm là việc thiết kế cách ứng dụng trông thế nào và dùng ra sao.

**Phía máy chủ.**
Backend lo logic phía máy chủ, cơ sở dữ liệu và việc tích hợp nhiều dịch vụ. Phát triển cơ sở dữ liệu lo việc lưu trữ, truy xuất và xử lý dữ liệu.

**Phía vận hành.**
Điện toán đám mây là triển khai và quản lý ứng dụng trên các nền tảng đám mây. Hạ tầng và DevOps là quản lý hạ tầng, việc triển khai và CI/CD của ứng dụng.

## Giới hạn cần nhớ

Bài nguồn nêu **vùng**, không nêu công nghệ cụ thể, mức thành thạo hay thứ tự học. Thứ tự trong hình chỉ để đọc, không phải thứ tự phải học.
Bảy vùng cũng không có nghĩa một người phải sâu ở cả bảy; nguồn chỉ nói người làm full-stack cần thành thạo một dải rộng công nghệ và công cụ.

## Nhìn hình trả lời

Một nhóm nhỏ làm chức năng đặt lịch hẹn: người dùng chọn giờ trên màn hình, lịch được ghi lại, và bản mới phải được đưa lên chạy. Mỗi việc thuộc vùng nào trong hình?

<details>
<summary>Xem đáp án</summary>

Màn hình chọn giờ là frontend (và mobile nếu làm ứng dụng điện thoại); cách bố trí và độ dễ dùng thuộc thiết kế giao diện và trải nghiệm.
Nhận yêu cầu và kiểm tra giờ trống là logic backend, còn ghi lại lịch là việc của cơ sở dữ liệu.
Đưa bản mới lên chạy thuộc điện toán đám mây, hạ tầng và DevOps, qua đường ống CI/CD.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn liệt kê bảy vùng theo thứ tự frontend, backend, cơ sở dữ liệu, di động, đám mây, thiết kế giao diện và trải nghiệm, hạ tầng và DevOps, mỗi vùng một câu. Hình đổi thứ tự để các vùng gần nhau trong một ứng dụng đứng cạnh nhau.
Bài không dùng ảnh lộ trình của nguồn nên không nêu tên công nghệ nào.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/a-roadmap-for-full-stack-development.md): bảy vùng kỹ thuật của người làm full-stack.

Đã đọc nguồn ngày 2026-10-18. Các câu giải nghĩa DevOps, CI và CD trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.
