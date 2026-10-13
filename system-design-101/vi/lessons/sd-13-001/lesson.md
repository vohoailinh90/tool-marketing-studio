# Mẫu thiết kế Kubernetes khi đưa một API lên cụm

Hãy hình dung bạn đưa một API HTTP lên Kubernetes. Mỗi mẫu thiết kế dưới đây trả lời một việc cụ thể bạn sẽ gặp, và bạn không cần học thuộc cả bộ.

![Sáu việc cần làm khi đưa một API lên cụm và mẫu giúp bạn: báo sẵn sàng bằng probe, khai báo tài nguyên (requests để đặt Pod, limits giới hạn lúc chạy), chạy migration bằng init container hoặc Job kèm migration idempotent, thêm proxy hoặc gửi nhật ký bằng sidecar, tìm nhau qua Service và DNS, và tắt êm khi bị thay Pod cùng PodDisruptionBudget khi bảo trì node.](../../diagrams/sd-13-001-main.svg)

**Đọc hình:** sáu việc độc lập, không có thứ tự bắt buộc; bài chọn các việc thường gặp, không phải danh mục đầy đủ.

## Nhìn hình thử trả lời

Migration cơ sở dữ liệu chỉ nên chạy một lần cho mỗi bản phát hành, còn nhiều Pod API chạy song song. Đặt migration trong init container của Pod API có ổn không?

<details>
<summary>Xem đáp án</summary>

Không chắc. Init container chạy ở mỗi Pod, nên nhiều Pod sẽ cùng chạy migration. Job phù hợp hơn cho việc theo bản phát hành, nhưng Job cũng không bảo đảm chạy đúng một lần: Pod lỗi hay bị thay có thể làm migration chạy lại. Vì vậy migration vẫn nên idempotent hoặc dùng công cụ có cơ chế khóa.

</details>

## Ngộ nhận dễ gặp

Bài chọn sáu việc thường gặp khi đưa một API lên cụm, tên mẫu lấy từ sách Kubernetes Patterns và tài liệu Kubernetes; không phải mẫu nào cũng cần dùng. Nhiều ứng dụng nhỏ chỉ cần probe, khai báo tài nguyên và Service.

<details>
<summary>Xem sâu hơn</summary>

- **Probe:** liveness khởi động lại container khi kẹt; readiness quyết định endpoint của Pod có nhận traffic từ Service không (Pod vẫn được liệt kê với `ready: false`); startup bảo vệ ứng dụng khởi động chậm.
- **Tài nguyên:** `requests` là thứ scheduler dùng để đặt Pod; `limits` do runtime áp dụng sau khi Pod đã được đặt để giới hạn mức dùng tối đa.
- **Init container và Job:** init container chạy lần lượt, xong hết mới tới container ứng dụng, ở mỗi Pod. Job chạy tới khi hoàn tất, có thử lại; tài liệu nêu rõ chương trình trong Job vẫn có thể chạy nhiều hơn một lần, nên cần thiết kế idempotent hoặc có khóa.
- **Sidecar:** các bản Kubernetes gần đây hỗ trợ sidecar dạng gốc, khai báo như init container có `restartPolicy: Always`.
- **Service:** Service ClusterIP thông thường (có selector) cho một địa chỉ ảo ổn định và tên DNS cho một nhóm Pod; Service headless và ExternalName không làm vậy.
- **Tắt êm:** khi Pod bị xóa, hook `preStop` (nếu có) chạy trước rồi kubelet gửi SIGTERM. `terminationGracePeriodSeconds` là tổng thời gian cho cả quá trình đó và bắt đầu đếm từ trước `preStop`, nên hook chậm làm ứng dụng còn ít thời gian dọn dẹp sau SIGTERM; hết hạn thì container bị dừng cưỡng bức.
- **PodDisruptionBudget:** chỉ giới hạn việc gỡ Pod qua Eviction API, ví dụ `kubectl drain` khi bảo trì node. Nó không ràng buộc rolling update của Deployment hay việc xóa Pod trực tiếp, nên đừng dựa vào nó để kiểm soát tính sẵn sàng khi triển khai.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-10-k8s-design-patterns.md).
- Sách [Kubernetes Patterns](https://k8spatterns.io/).
- Kubernetes: [probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/), [tài nguyên](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/), [init container](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/), [Job](https://kubernetes.io/docs/concepts/workloads/controllers/job/), [sidecar](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/), [Service](https://kubernetes.io/docs/concepts/services-networking/service/), [vòng đời Pod](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/), [disruption](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/).
