# Pod không chạy: chẩn đoán theo từng chặng

Khi một Pod không chạy, trạng thái hiển thị cho biết nó dừng ở chặng nào: chưa có node, node chưa khởi động xong container, container chết, hay chạy mà chưa sẵn sàng. Mỗi chặng có vài nguyên nhân quen thuộc và một chỗ để xem.

![Bốn chặng khi Pod không chạy: Pending khi chưa có node thường do thiếu tài nguyên theo requests, taint, nodeSelector hay PVC chưa gắn; ContainerCreating khi kéo image hoặc gắn volume lỗi; chạy rồi thoát như CrashLoopBackOff hay OOMKilled do vượt limits bộ nhớ hoặc do node hết bộ nhớ; chạy nhưng chưa Ready do readiness probe thất bại.](../../diagrams/sd-13-025-main.svg)

**Đọc hình:** bốn chặng theo thứ tự Pod đi qua khi khởi động; lỗi ở chặng nào thì dừng ở đó.

## Nhìn hình thử trả lời

Pod ở Pending, `kubectl describe pod` báo `0/3 nodes are available: 3 Insufficient memory`. Điều gì đang xảy ra và nên làm gì?

<details>
<summary>Xem đáp án</summary>

Scheduler không tìm được node nào còn đủ bộ nhớ cho `requests` của Pod. Giảm `requests` nếu khai quá tay, hoặc thêm tài nguyên cho node hay thêm node. `limits` không quyết định việc đặt Pod, `requests` mới quyết định.

</details>

## Giới hạn cần nhớ

Tên trong cột STATUS của kubectl là cách hiển thị tóm tắt, không phải giai đoạn (phase) chính thức. Một Pod có thể kẹt vì nhiều lý do cùng lúc, nên đọc sự kiện thay vì đoán từ tên. Bài không đi vào lỗi mạng hay bảo mật.

<details>
<summary>Xem sâu hơn</summary>

```bash
kubectl describe pod ten-pod             # phần Events cho biết lý do ở chặng nào
kubectl logs ten-pod --previous          # nhật ký của lần chạy trước khi chết
kubectl get events --sort-by=.lastTimestamp
```

- **Pending:** scheduler chọn node dựa trên `requests` của Pod, cùng taint, toleration, nodeSelector và affinity. Sự kiện `FailedScheduling` liệt kê lý do loại từng node. PVC chưa gắn được cũng giữ Pod ở Pending.
- **ContainerCreating:** kubelet nhờ container runtime kéo image và chuẩn bị volume. Tên image sai, thiếu quyền kéo (cần `imagePullSecrets`) hay registry không với tới cho `ErrImagePull` rồi `ImagePullBackOff`.
- **CrashLoopBackOff:** kubelet khởi động lại container và tăng dần thời gian chờ giữa các lần (tối đa vài phút); tìm nguyên nhân trong `logs --previous`.
- **OOMKilled:** `describe pod` ghi lý do ở trạng thái lần trước của container (`Reason: OOMKilled`, thường kèm mã thoát 137, tức bị dừng cưỡng bức). Hết bộ nhớ có thể do container vượt `limits` bộ nhớ của chính nó, hoặc do node hết bộ nhớ (khi đó kernel có thể dừng cả container chưa vượt limit hay không đặt limit). Hãy kiểm tra `limits` của container và sự kiện của node (`kubectl describe node`).
- **Chưa Ready:** container chạy nhưng readiness probe thất bại, nên Pod không được tính là sẵn sàng.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-is-k8s-kubernetes.md).
- Kubernetes: [gỡ lỗi Pod](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/), [vòng đời Pod](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/), [tài nguyên container](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/), [kube-scheduler](https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/), [áp lực node và OOM](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/).
