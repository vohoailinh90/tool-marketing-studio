# Pipeline CI/CD: cổng nhanh trước, cổng đắt sau

Một pipeline tốt xếp kiểm tra theo chi phí: cổng rẻ và nhanh đứng trước, cổng chậm và đắt đứng sau, để lỗi bị chặn càng sớm càng tốt.

![Bốn nhóm cổng theo thời gian phản hồi tăng dần: kiểm tra tĩnh và kiểm thử đơn vị trong vài giây đến vài phút, kiểm thử tích hợp, kiểm thử toàn diện trên môi trường thử, rồi duyệt và theo dõi trên production.](../../diagrams/sd-13-027-main.svg)

**Đọc hình:** thứ tự là về chi phí phản hồi; tên giai đoạn cụ thể khác nhau tùy dự án.

## Nhìn hình thử trả lời

Kiểm thử đơn vị thất bại. Có nên vẫn chạy kiểm thử toàn diện để "xem thêm"?

<details>
<summary>Xem đáp án</summary>

Thường không. Cổng đắt chạy khi cổng rẻ đã qua giúp tiết kiệm thời gian và không đưa bản đã biết lỗi đi tiếp. Dừng sớm (fail fast) là mục đích của việc xếp cổng.

</details>

## Giới hạn cần nhớ

Pipeline xanh chỉ chứng minh các kiểm tra đã viết đều qua, không bảo đảm không có lỗi. Kiểm thử chập chờn (khi qua khi trượt) làm mọi người mất tin và bỏ qua kết quả đỏ.

<details>
<summary>Xem sâu hơn</summary>

- **Phản hồi nhanh:** kết quả phải về trong thời gian đủ ngắn để người viết mã còn nhớ thay đổi.
- **Build một lần:** dùng cùng sản phẩm build cho mọi môi trường, để thứ được kiểm thử là thứ được phát hành.
- **Cổng duyệt cuối:** có thể là người (Continuous Delivery) hoặc quy tắc tự động (Continuous Deployment).
- **Chạy song song:** các kiểm tra độc lập chạy song song để rút ngắn thời gian của một cổng.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/cicd-pipeline-explained-in-simple-terms.md).
- Martin Fowler: [DeploymentPipeline](https://martinfowler.com/bliki/DeploymentPipeline.html), [Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html).
