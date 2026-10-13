# Chiến lược triển khai trên Kubernetes

Khi bạn đổi image trong một Deployment, Kubernetes làm gì sẵn, và khi nào bạn phải thêm công cụ?

![Bốn thẻ: RollingUpdate mặc định, Recreate khi hai phiên bản không chạy chung được, chia traffic theo phần trăm cần Ingress hay service mesh, thử với traffic thật cần mirror.](../../diagrams/sd-13-017-main.svg)

**Đọc hình:** hai thẻ đầu là việc Kubernetes tự làm; hai thẻ sau cần cấu hình định tuyến traffic.

## Nhìn hình thử trả lời

Deployment 3 Pod, `maxSurge: 1`, `maxUnavailable: 0`. Controller nhắm tới tối đa bao nhiêu Pod đang chạy, và có lúc nào ít hơn 3 Pod sẵn sàng không?

<details>
<summary>Xem đáp án</summary>

Controller nhắm tới tối đa 4 Pod không đang tắt (3 + 1 tạm thời) và luôn giữ đủ 3 Pod sẵn sàng vì `maxUnavailable` là 0. Pod cũ đang tắt (Terminating) trong thời gian ân hạn không được tính, nên tổng Pod thực tế có thể tạm cao hơn 4.

</details>

## Giới hạn cần nhớ

"Không ngừng dịch vụ" của RollingUpdate chỉ đúng khi readiness probe chính xác và hai phiên bản tương thích khi chạy song song.

<details>
<summary>Xem sâu hơn</summary>

- **Canary đơn giản:** hai Deployment cùng sau một Service, chỉnh tỉ lệ số Pod; chia traffic theo phần trăm chính xác cần Ingress hoặc mesh.
- **Blue-Green:** hai Deployment hoặc hai môi trường, đổi selector hoặc đường vào.
- **Shadow:** bản sao traffic gửi tới phiên bản mới nhưng phản hồi bị bỏ; cẩn thận với tác dụng phụ như ghi dữ liệu.
- **A/B testing** là thí nghiệm sản phẩm, không phải cách triển khai an toàn.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/kubernetes-deployment-strategies.md).
- Kubernetes: [Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/), [canary](https://kubernetes.io/docs/concepts/workloads/management/#canary-deployments).
- [Argo Rollouts](https://argo-rollouts.readthedocs.io/), [Flagger](https://docs.flagger.app/).
