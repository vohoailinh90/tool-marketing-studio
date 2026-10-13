# Service Kubernetes không nhận traffic: năm chỗ cần kiểm tra

Service là lớp địa chỉ ổn định trước một nhóm Pod. Khi nó không nhận traffic, hãy kiểm tra theo thứ tự từ trong ra ngoài: nhãn, cổng, trạng thái sẵn sàng, tên và đường vào từ ngoài cụm.

![Năm chỗ cần kiểm tra khi Service không nhận traffic: selector không khớp nhãn Pod, port và targetPort lệch, Pod chưa sẵn sàng nên bị loại khỏi endpoint, tên DNS sai namespace, và đường vào từ ngoài cụm như NodePort bị chặn hoặc LoadBalancer ở trạng thái pending.](../../diagrams/sd-13-006-main.svg)

**Đọc hình:** năm bước xếp theo thứ tự kiểm tra thường hiệu quả, không phải thứ tự dữ liệu chạy.

## Nhìn hình thử trả lời

`kubectl get endpointslices -l kubernetes.io/service-name=web` không trả về endpoint nào. Nghi vấn đầu tiên là gì và so sánh cái gì với cái gì?

<details>
<summary>Xem đáp án</summary>

Chủ yếu là selector của Service không khớp nhãn của Pod nào (hoặc chưa có Pod). So selector trong `kubectl get svc web -o yaml` với nhãn của Pod trong `kubectl get pods --show-labels`. Nếu EndpointSlice có endpoint nhưng điều kiện `ready` là false thì vấn đề là readiness của Pod, không phải selector.

</details>

## Giới hạn cần nhớ

Chuỗi kiểm tra trên giả định Service có selector. Service không selector (tự quản endpoint), Service headless và ExternalName hoạt động khác, nên không áp dụng nguyên văn. Định tuyến HTTP theo đường dẫn hay tên miền thuộc về Ingress hoặc Gateway, không phải Service.

<details>
<summary>Xem sâu hơn</summary>

- **Endpoint:** EndpointSlice được tạo từ các Pod khớp selector, mỗi endpoint kèm điều kiện như `ready`; chỉ endpoint ready nhận traffic bình thường, Pod chưa sẵn sàng vẫn được liệt kê với `ready: false`. Để so khớp selector, xem `kubectl get svc web -o yaml` và `kubectl get pods --show-labels`.
- **port và targetPort:** `port` là cổng của Service, `targetPort` là cổng container nhận traffic; nếu không ghi, `targetPort` bằng `port`.
- **DNS:** trong cùng namespace gọi `web`; khác namespace dùng `web.ten-namespace` hoặc tên đầy đủ `web.ten-namespace.svc.cluster.local`.
- **NodePort:** mặc định dải 30000–32767 trên mọi node; cần cho phép trong tường lửa hoặc security group.
- **LoadBalancer:** Kubernetes không tự có bộ cân bằng tải; cần nhà cung cấp cloud hoặc thành phần bổ sung (như MetalLB trên máy chủ riêng), không thì trạng thái chờ (`<pending>`) kéo dài.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-4-kubernetes-service-types-in-one-diagram.md).
- Kubernetes: [Service](https://kubernetes.io/docs/concepts/services-networking/service/), [gỡ lỗi Service](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/), [DNS cho Service và Pod](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/), [EndpointSlice](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/).
