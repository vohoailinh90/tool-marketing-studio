# Mười mẫu thiết kế Kubernetes

Mười mẫu chia thành bốn tầng: từ việc một container tự báo tình trạng cho tới việc đóng gói kiến thức vận hành thành phần mềm.

![Bốn thẻ xếp dọc: nền tảng (health probe, predictable demands, automated placement), cấu trúc Pod (init container, sidecar), hành vi (batch job, stateful service, service discovery) và mức cao (controller, operator).](../../diagrams/sd-13-001-main.svg)

- **Nền tảng:** ứng dụng cần cho nền tảng biết nó khỏe không, cần bao nhiêu tài nguyên để đặt đúng chỗ.
- **Cấu trúc:** chia việc trong một Pod: bước chuẩn bị riêng, phần phụ trợ riêng.
- **Hành vi:** cách chạy khác nhau cho việc một lần, dịch vụ có trạng thái và việc tìm dịch vụ.
- **Mức cao:** vòng lặp điều khiển và cách tự động hóa vận hành.

**Đọc hình:** mỗi thẻ là một tầng; mũi tên chỉ thứ tự đọc từ cơ bản đến nâng cao, không phải thứ tự chạy.

## Nhìn hình thử trả lời

Một ứng dụng phải chờ cơ sở dữ liệu sẵn sàng rồi mới nên khởi động. Bước chờ đó hợp với mẫu nào?

<details>
<summary>Xem đáp án</summary>

Init Container. Các init container chạy lần lượt và phải hoàn tất trước khi container ứng dụng bắt đầu; Sidecar thì chạy cùng ứng dụng, không dùng để chặn khởi động.

</details>

## Ngộ nhận dễ gặp

Đây là cách phân nhóm của một cuốn sách, không phải danh mục chính thức của Kubernetes, và sách còn nhiều mẫu khác (ví dụ Daemon Service). Mười mẫu không phải mười tính năng phải dùng cùng lúc: nhiều ứng dụng nhỏ chỉ cần probe, khai báo tài nguyên và Service.

<details>
<summary>Xem sâu hơn</summary>

- **Probe:** Kubernetes có ba loại: liveness (khởi động lại khi kẹt), readiness (có nhận traffic không) và startup (cho ứng dụng khởi động chậm).
- **Predictable Demands:** `requests` giúp scheduler đặt Pod; `limits` giới hạn mức dùng tối đa.
- **Sidecar:** các bản Kubernetes gần đây hỗ trợ sidecar dạng gốc, khai báo như init container có `restartPolicy: Always`, để nó khởi động trước và dừng sau container chính.
- **Controller:** vòng lặp so sánh trạng thái khai báo với trạng thái thật rồi sửa chênh lệch. **Operator** dùng cùng ý tưởng cho một ứng dụng cụ thể, thường qua CRD.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-10-k8s-design-patterns.md).
- Sách [Kubernetes Patterns](https://k8spatterns.io/).
- Kubernetes: [probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/), [tài nguyên](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/), [scheduler](https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/), [init container](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/), [sidecar](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/), [Job](https://kubernetes.io/docs/concepts/workloads/controllers/job/), [StatefulSet](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/), [Service](https://kubernetes.io/docs/concepts/services-networking/service/), [controller](https://kubernetes.io/docs/concepts/architecture/controller/), [operator](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/).
