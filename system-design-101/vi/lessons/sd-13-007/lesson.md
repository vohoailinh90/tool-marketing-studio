# Lỗi thường gặp khi đưa ứng dụng lên cloud-native

Một ứng dụng cloud-native phải chịu được việc bị thay thế, phát hành lặp lại và phụ thuộc bị lỗi. Bốn câu hỏi tự kiểm tra dưới đây lộ ra những lỗi hay gặp.

![Bốn câu hỏi tự kiểm tra: một bản sao biến mất thì sao, cấu hình đổi thì sao, phụ thuộc chậm hoặc lỗi thì sao, và phát hành cùng chi phí có kiểm soát không; mỗi câu kèm lỗi thường gặp.](../../diagrams/sd-13-007-main.svg)

**Đọc hình:** bốn câu hỏi để tự kiểm tra, không phải danh mục đầy đủ; mỗi câu có thể lộ nhiều lỗi.

## Nhìn hình thử trả lời

Một dịch vụ tự động gọi lại ngay 5 lần mỗi khi một phụ thuộc chậm. Điều gì có thể xảy ra khi phụ thuộc đó đang quá tải?

<details>
<summary>Xem đáp án</summary>

Lượng yêu cầu bội lên và làm phụ thuộc quá tải nặng hơn, lỗi lan ra (retry storm). Nên đặt timeout, giới hạn số lần thử và giãn cách tăng dần có yếu tố ngẫu nhiên (backoff with jitter).

</details>

## Giới hạn cần nhớ

Không có danh mục lỗi nào đúng cho mọi bối cảnh. Monolith chia module rõ ràng vẫn hợp lý cho nhiều nhóm, và dùng nhiều dịch vụ cloud không phải lỗi nếu có chiến lược. Bốn câu hỏi giúp phát hiện chỗ cần xem lại, không phải bảng chấm điểm.

<details>
<summary>Xem sâu hơn</summary>

- **Tiến trình có thể bị thay:** không giữ trạng thái bền trong tiến trình; khởi động nhanh và tắt êm khi nhận tín hiệu tắt, theo nguyên tắc Twelve-Factor về tính dùng-và-bỏ.
- **Cấu hình ngoài mã:** đọc cấu hình và bí mật từ môi trường chạy, để cùng một bản build chạy được ở mọi môi trường.
- **Chịu lỗi của phụ thuộc:** timeout, giới hạn thử lại và backoff có jitter; tránh để một cơ sở dữ liệu chung thành điểm nghẽn.
- **Hạ tầng bất biến:** tạo bản mới từ định nghĩa rồi thay thế, thay vì sửa tại chỗ.
- **Chi phí:** gắn nhãn tài nguyên và theo dõi theo dịch vụ giúp thấy ngay khoản tăng bất thường.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/cloud-native-anti-patterns.md).
- [The Twelve-Factor App](https://12factor.net/): [config](https://12factor.net/config), [disposability](https://12factor.net/disposability), [processes](https://12factor.net/processes).
- AWS Builders Library: [timeouts, retries và backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/).
- Martin Fowler: [ImmutableServer](https://martinfowler.com/bliki/ImmutableServer.html). AWS: [trụ cột tối ưu chi phí](https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/welcome.html).
