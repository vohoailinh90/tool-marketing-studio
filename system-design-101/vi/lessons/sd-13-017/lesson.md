# Deployment của Kubernetes thay Pod như thế nào

Khi bạn đổi image trong một Deployment, controller làm theo một nhịp có thể chỉnh được. Hiểu nhịp này giúp bạn đọc đúng vì sao một lần cập nhật trôi chảy, chậm hoặc kẹt.

![Năm chặng: đổi image thì Deployment tạo ReplicaSet mới, maxSurge và maxUnavailable điều chỉnh nhịp, readiness probe và minReadySeconds quyết định khi nào đi tiếp, kubectl rollout undo hoặc pause khi cần, và Recreate cùng chia traffic theo phần trăm nằm ngoài nhịp mặc định.](../../diagrams/sd-13-017-main.svg)

**Đọc hình:** bốn thẻ đầu là nhịp của RollingUpdate, mặc định của Deployment; thẻ cuối là những gì Deployment không tự làm.

## Nhìn hình thử trả lời

Deployment 3 Pod, `maxSurge: 1`, `maxUnavailable: 0`. Controller nhắm tới tối đa bao nhiêu Pod đang chạy, và có lúc nào ít hơn 3 Pod sẵn sàng không?

<details>
<summary>Xem đáp án</summary>

Controller nhắm tới tối đa 4 Pod không đang tắt (3 + 1 tạm thời) và luôn giữ đủ 3 Pod sẵn sàng vì `maxUnavailable` là 0. Pod cũ đang tắt (Terminating) trong thời gian ân hạn không được tính, nên tổng Pod thực tế có thể tạm cao hơn 4.

</details>

## Giới hạn cần nhớ

"Không ngừng dịch vụ" của RollingUpdate chỉ đúng khi readiness probe chính xác và hai phiên bản tương thích khi chạy song song. Probe sai thì Pod mới nhận traffic quá sớm.

<details>
<summary>Xem sâu hơn</summary>

- **Mặc định:** `strategy.type` là `RollingUpdate`, với `maxSurge` và `maxUnavailable` mặc định 25%.
- **minReadySeconds:** Pod mới phải sẵn sàng liên tục chừng đó giây mới được tính là có sẵn.
- **progressDeadlineSeconds:** quá hạn mà chưa tiến triển thì Deployment bị đánh dấu không tiến triển; controller không tự quay lui.
- **Quay lui:** `kubectl rollout undo` về bản trước; `kubectl rollout history` xem các bản đã lưu.
- **Recreate:** hợp khi hai phiên bản không thể chạy cùng lúc (ví dụ khóa dữ liệu độc quyền).
- **Chia traffic theo phần trăm:** Deployment chỉ đổi số Pod; muốn chia theo phần trăm chính xác cần lớp định tuyến như Ingress hoặc service mesh, hay công cụ như Argo Rollouts, Flagger.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/kubernetes-deployment-strategies.md).
- Kubernetes: [Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/).
- [Argo Rollouts](https://argo-rollouts.readthedocs.io/), [Flagger](https://docs.flagger.app/).
