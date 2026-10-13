# Bốn loại Service trong Kubernetes

Service cho một nhóm Pod một địa chỉ ổn định. Trường `type` quyết định ai gọi được địa chỉ đó.

![Bốn thẻ: ClusterIP chỉ trong cụm, NodePort mở một cổng trên mọi node, LoadBalancer dùng bộ cân bằng tải của nhà cung cấp cloud, ExternalName trả tên miền thay vì IP.](../../diagrams/sd-13-006-main.svg)

**Đọc hình:** ba thẻ đầu mở rộng dần phạm vi truy cập; ExternalName khác loại: nó là bí danh DNS.

## Nhìn hình thử trả lời

Ứng dụng trong cụm gọi `db`, còn cơ sở dữ liệu thật nằm ở `db.example.com` bên ngoài. Loại nào hợp, và Service có tạo IP trong cụm không?

<details>
<summary>Xem đáp án</summary>

ExternalName. Nó chỉ làm DNS trả về CNAME tới tên ngoài, không cấp ClusterIP và không chuyển tiếp traffic.

</details>

## Giới hạn cần nhớ

Service chỉ là lớp địa chỉ và cân bằng ở tầng 4. Định tuyến HTTP theo đường dẫn hay tên miền thuộc về Ingress hoặc Gateway, không phải một loại Service.

<details>
<summary>Xem sâu hơn</summary>

- **ClusterIP** là mặc định nếu không ghi `type`.
- **NodePort:** theo mặc định cổng nằm trong dải 30000–32767.
- **LoadBalancer:** việc tạo bộ cân bằng tải do nhà cung cấp cloud hoặc một thành phần bổ sung thực hiện; thường nó dựng trên ClusterIP và NodePort.
- **ExternalName:** không dùng selector; cần chú ý giao thức dựa trên tên máy như HTTP/HTTPS vì tên đích khác tên được gọi.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-4-kubernetes-service-types-in-one-diagram.md).
- Kubernetes: [Service](https://kubernetes.io/docs/concepts/services-networking/service/).
