# Chuyển hệ thống sang cloud native: sáu mảng việc cần phủ

**Cloud native là một cách vận hành chứ không phải một sản phẩm để cài; khi chuyển một hệ thống sang đó, công việc chia thành sáu mảng: định nghĩa ứng dụng, điều phối, môi trường chạy, cấp phát, quan sát và serverless.**
Bài này đọc sáu mảng như sáu câu hỏi, và dùng sổ đăng ký của CNCF để thấy mỗi mảng gồm những loại công cụ nào.

![Hai khung. Khung một, ba mảng nền nối nhau: cấp phát tạo hạ tầng, cấu hình và kho ảnh; môi trường chạy giữ container, mạng và lưu trữ; điều phối xếp lịch, tìm dịch vụ và lưới dịch vụ. Khung hai, ba mảng phía trên: định nghĩa ứng dụng dựng ảnh và phân phối liên tục; quan sát cho thấy hệ thống đang làm gì; serverless chạy mã mà không quản máy chủ.](../../diagrams/sd-11-034-main.svg)

## Từ viết tắt

- **CNCF** (Cloud Native Computing Foundation) — tổ chức giữ nhiều dự án mã nguồn mở của hệ sinh thái này, trong đó có Kubernetes; bài dùng định nghĩa và sổ đăng ký công cụ của họ.
- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách một phần mềm cho phần mềm khác gọi vào; cổng API là điểm vào chung cho các lời gọi tới nhiều dịch vụ.
- **CI** (Continuous Integration) — tích hợp liên tục: mỗi thay đổi mã được ghép vào nhánh chung và kiểm tra tự động ngay.
- **CD** (Continuous Delivery) — phân phối liên tục: bản đã qua kiểm tra được đưa lên môi trường chạy bằng một quy trình lặp lại được.

## Đọc hình

CNCF định nghĩa cloud native là những thực hành giúp tổ chức phát triển, dựng và triển khai khối lượng công việc trên môi trường điện toán (công cộng, riêng hay lai) ở quy mô lớn, theo cách lập trình được và lặp lại được. Hệ thống đặc trưng bởi các phần ghép lỏng, nói chuyện được với nhau, và an toàn, bền bỉ, dễ quản lý, bền vững, quan sát được. Định nghĩa không nhắc một công cụ nào, nên sáu mảng dưới đây là cách chia việc, không phải danh sách thứ phải mua.

Mũi tên ở khung một là cách đọc của người biên soạn: mảng sau dựa vào mảng trước (cần hạ tầng được tạo ra thì mới có chỗ chạy container, cần container thì mới có gì để xếp lịch). Nguồn không vẽ thứ tự này.

| Mảng (tên ở nguồn) | Câu hỏi nó trả lời | Loại công cụ ở lớp tương ứng của Landscape |
|---|---|---|
| Cấp phát (Provisioning) | Hạ tầng và cấu hình được tạo ra thế nào, ảnh container nằm ở đâu, khóa và việc tuân thủ được giữ ra sao? | Tự động hóa và cấu hình; kho ảnh container; bảo mật và tuân thủ; quản lý khóa |
| Môi trường chạy (Runtime) | Mã chạy ở đâu, dữ liệu và mạng của nó nằm ở đâu? | Lưu trữ; môi trường chạy container; mạng |
| Điều phối và quản lý (Orchestration and management) | Nhiều bản chạy được xếp lịch, tìm thấy nhau và nói chuyện với nhau thế nào? | Xếp lịch và điều phối; phối hợp và tìm dịch vụ; gọi thủ tục từ xa; proxy dịch vụ; cổng API; lưới dịch vụ |
| Định nghĩa và phát triển ứng dụng (Application definition development) | Ứng dụng được mô tả, dựng thành ảnh và đưa lên bằng cách nào? | Cơ sở dữ liệu; luồng dữ liệu và nhắn tin; định nghĩa ứng dụng và dựng ảnh; CI và CD |
| Quan sát (Observability) | Hệ thống đang làm gì, và lúc hỏng thì thấy ở đâu? | Quan sát; cờ tính năng; kỹ thuật hỗn loạn; tối ưu liên tục |
| Serverless | Có thể bỏ hẳn việc quản máy chủ cho một phần hệ thống không? | Bảo mật; công cụ; khung làm việc; nền tảng có người lưu trữ; nền tảng tự cài |

## Thử: đếm sổ đăng ký của CNCF

Ngày 2026-10-19, đọc tệp `landscape.yml` của kho CNCF Landscape (nhánh chính) và đếm các mục con của từng lớp. Sáu lớp có tên gần như trùng sáu mảng của nguồn: Provisioning 4 mục con, Runtime 3, Orchestration & Management 6, App Definition and Development 4, Observability and Analysis 4, Serverless 5. Việc coi hai bộ tên là một là suy luận của người biên soạn: nguồn không nói nó lấy tên từ đâu. Tệp còn có các lớp khác, như Platform (bản phân phối Kubernetes, dịch vụ container) và một nhóm lớp về trí tuệ nhân tạo; những lớp đó nằm ngoài sáu mảng của nguồn.

Một điều đáng chú ý: lớp quan sát của Landscape chứa cả cờ tính năng và kỹ thuật hỗn loạn, những thứ vượt ra ngoài "xem hệ thống đang làm gì". Ranh giới giữa các mảng không sắc nét, và công cụ nào thuộc mảng nào do người lập sổ quyết định.

## Giới hạn cần nhớ

Sáu mảng là bản đồ của loại việc, không phải lộ trình: nguồn nói có một "lộ trình áp dụng" trong hình của nó, nhưng bài này không dùng hình đó và không khẳng định thứ tự nào nên làm trước. Landscape là danh mục công cụ chứ không phải lời khuyên chọn công cụ, và số mục con có thể đổi theo thời gian. Một hệ thống nhỏ có thể không cần phủ cả sáu mảng bằng công cụ chuyên dụng; đó là nhận xét của người biên soạn, không từ nguồn.

## Nhìn hình trả lời

Đội của bạn muốn mỗi lần gộp mã vào nhánh chính thì bản mới tự lên môi trường thử. Việc đó thuộc mảng nào trong sáu mảng?

<details>
<summary>Xem đáp án</summary>

Phần dựng ảnh và chạy kiểm tra thuộc mảng định nghĩa và phát triển ứng dụng (có mục con CI và CD trong Landscape). Phần đưa bản mới lên và thay các bản cũ lại nằm ở mảng điều phối, vì chính bộ xếp lịch quyết định chạy bản nào ở đâu. Một việc chạm hai mảng là bình thường, và đó là lý do ranh giới giữa các mảng chỉ là cách chia việc.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn gồm một hình lộ trình và danh sách sáu mảng, không giải thích từng mảng. Bài này viết lại sáu mảng như sáu câu hỏi, gắn mỗi mảng vào lớp tương ứng của sổ đăng ký CNCF để thấy các loại công cụ bên trong, và nói rõ chỗ ghép tên là suy luận. Định nghĩa của CNCF được đọc từ văn bản của chính họ.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-we-transform-a-system-to-be-cloud-native.md): tên sáu mảng. Cách đọc từng mảng, bảng loại công cụ và nhận xét về ranh giới là của người biên soạn.
- [CNCF — định nghĩa cloud native (kho cncf/toc)](https://github.com/cncf/toc/blob/main/DEFINITION.md): định nghĩa, đọc từ nhánh chính.
- [CNCF Landscape — landscape.yml](https://github.com/cncf/landscape/blob/master/landscape.yml): tên lớp và mục con, đếm từ nhánh chính; số mục con có thể đổi theo thời gian.

Đã đọc nguồn ngày 2026-10-19. Phép đếm là của người biên soạn.
Bài viết và hình được thiết kế độc lập.
