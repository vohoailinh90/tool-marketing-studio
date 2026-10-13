# Kubernetes: mặt phẳng điều khiển và các node

Một cụm Kubernetes có hai phần: mặt phẳng điều khiển quyết định, các node chạy ứng dụng.

![Mặt phẳng điều khiển gồm API server, scheduler, controller manager và etcd; mỗi node chạy kubelet, kube-proxy, container runtime và các Pod.](../../diagrams/sd-13-025-main.svg)

**Đọc hình:** mọi thành phần nói chuyện với nhau qua API server.

## Nhìn hình thử trả lời

Hai container trong cùng một Pod gọi nhau bằng địa chỉ nào?

<details>
<summary>Xem đáp án</summary>

`localhost`. Các container trong một Pod dùng chung không gian mạng nên cùng một IP và gọi nhau qua `localhost` bằng cổng khác nhau.

</details>

## Giới hạn cần nhớ

Chạy một cụm một mặt phẳng điều khiển trên một máy thì không chịu được lỗi. Môi trường production thường chạy nhiều bản của mặt phẳng điều khiển và nhiều node.

<details>
<summary>Xem sâu hơn</summary>

- **API server** là thành phần duy nhất đọc ghi etcd; kubectl, scheduler và kubelet đều đi qua nó.
- **etcd** lưu toàn bộ trạng thái cụm, nên cần sao lưu.
- **Scheduler** xem các Pod chưa có node và chọn node phù hợp.
- **Controller manager** gồm nhiều controller (node, job, endpoint...) mỗi cái là một vòng lặp so trạng thái mong muốn với hiện tại.
- **kubelet** nhận mô tả Pod và bảo đảm container đang chạy; **kube-proxy** lập luật để Service đến đúng Pod.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/what-is-k8s-kubernetes.md).
- Kubernetes: [thành phần của cụm](https://kubernetes.io/docs/concepts/overview/components/), [Pod](https://kubernetes.io/docs/concepts/workloads/pods/).
