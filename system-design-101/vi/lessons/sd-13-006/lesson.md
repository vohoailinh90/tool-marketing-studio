# Service Kubernetes không nhận traffic: năm chỗ cần kiểm tra

Service là lớp địa chỉ ổn định trước một nhóm Pod. Khi nó không nhận traffic, hãy kiểm tra theo thứ tự từ trong ra ngoài: nhãn, cổng, trạng thái sẵn sàng, tên và đường vào từ ngoài cụm.

![Năm chỗ cần kiểm tra khi Service không nhận traffic: selector không khớp nhãn Pod nên EndpointSlice trống, port và targetPort lệch, với Service ở cấu hình mặc định endpoint có ready là false thì không nhận traffic, và cần xem serving và terminating để biết Pod chưa qua readiness hay đang bị xóa (Service đặt publishNotReadyAddresses: true là ngoại lệ), tên DNS (Domain Name System — hệ thống phân giải tên miền) sai namespace, và đường vào từ ngoài cụm như NodePort bị chặn hoặc LoadBalancer ở trạng thái pending.](../../diagrams/sd-13-006-main.svg)

**Đọc hình:** năm bước xếp theo thứ tự kiểm tra thường hiệu quả, không phải thứ tự dữ liệu chạy.

## Từ viết tắt

- **DNS** (Domain Name System) — hệ thống tên miền: "danh bạ" của Internet, đổi tên như example.com thành địa chỉ để các máy tìm thấy nhau.
- **HTTP** (HyperText Transfer Protocol) — giao thức truyền siêu văn bản: quy ước để trình duyệt gửi yêu cầu và máy chủ gửi trả lời.
- **LB** (Load Balancer) — bộ cân bằng tải: thành phần chia các yêu cầu tới nhiều bản sao của một dịch vụ; Service kiểu LoadBalancer cần có thành phần tạo ra LB, thiếu nó thì Service đứng ở trạng thái pending.

## Nhìn hình thử trả lời

`kubectl get endpointslices -l kubernetes.io/service-name=web` không trả về endpoint nào. Nghi vấn đầu tiên là gì và so sánh cái gì với cái gì?

<details>
<summary>Xem đáp án</summary>

Chủ yếu là selector của Service không khớp nhãn của Pod nào (hoặc chưa có Pod). So selector trong `kubectl get svc web -o yaml` với nhãn của Pod trong `kubectl get pods --show-labels`. Nếu EndpointSlice có endpoint nhưng điều kiện `ready` là false thì selector không phải nguyên nhân, vì endpoint đã được tạo từ Pod khớp. Hãy xem tiếp `serving` và `terminating`, vì `ready` về cơ bản là `serving` và không `terminating`: `serving: false` nghĩa là Pod chưa Ready, nên xem readiness probe; `terminating: true` nghĩa là Pod đang bị xóa (đã có deletion timestamp, thường gặp khi cập nhật cuốn chiếu), và `ready` là false dù Pod có thể vẫn Ready. Riêng Service đặt `publishNotReadyAddresses: true` báo mọi endpoint là ready bất kể Pod, nên với loại Service đó hãy xem `serving` hoặc `kubectl get pods`.

</details>

## Giới hạn cần nhớ

Chuỗi kiểm tra trên giả định Service có selector. Service không selector (tự quản endpoint), Service headless, ExternalName và Service đặt `publishNotReadyAddresses: true` (báo mọi endpoint là ready) hoạt động khác, nên không áp dụng nguyên văn. Định tuyến HTTP (HyperText Transfer Protocol — giao thức truyền siêu văn bản) theo đường dẫn hay tên miền thuộc về Ingress hoặc Gateway, không phải Service.

<details>
<summary>Xem sâu hơn</summary>

- **Endpoint:** EndpointSlice được tạo từ các Pod khớp selector, mỗi endpoint kèm điều kiện như `ready`; với Service ở cấu hình mặc định, chỉ endpoint ready nhận traffic bình thường. `ready` về cơ bản là `serving` và không `terminating`: Pod chưa sẵn sàng vẫn được liệt kê với `serving: false` và `ready: false`, còn Pod đang bị xóa có `terminating: true` và `ready: false` dù `serving` vẫn có thể là true. Ngoại lệ: Service đặt `spec.publishNotReadyAddresses: true` (thường để các Pod của StatefulSet tìm thấy nhau) báo mọi endpoint là `ready: true` bất kể Pod có sẵn sàng hay không, còn `serving` vẫn theo readiness của Pod. Để so khớp selector, xem `kubectl get svc web -o yaml` và `kubectl get pods --show-labels`.
- **port và targetPort:** `port` là cổng của Service, `targetPort` là cổng container nhận traffic; nếu không ghi, `targetPort` bằng `port`.
- **DNS (Domain Name System — hệ thống phân giải tên miền):** trong cùng namespace gọi `web`; khác namespace dùng `web.ten-namespace` hoặc tên đầy đủ `web.ten-namespace.svc.<miền-cụm>`, trong đó `<miền-cụm>` là miền DNS đã cấu hình của cụm (thường là `cluster.local`).
- **NodePort:** mặc định dải 30000–32767 trên mọi node; cần cho phép trong tường lửa hoặc security group.
- **LoadBalancer:** Kubernetes không tự có bộ cân bằng tải; cần nhà cung cấp cloud hoặc thành phần bổ sung (như MetalLB trên máy chủ riêng), không thì trạng thái chờ (`<pending>`) kéo dài.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-4-kubernetes-service-types-in-one-diagram.md).
- Kubernetes: [Service](https://kubernetes.io/docs/concepts/services-networking/service/), [gỡ lỗi Service](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/), [DNS cho Service và Pod](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/), [EndpointSlice](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/).
