# Tắt êm một API trên Kubernetes: năm chỗ làm rớt request

Mỗi lần triển khai bản mới hoặc dồn node, Kubernetes xóa Pod cũ. Nếu API (Application Programming Interface — giao diện lập trình ứng dụng) rớt vài request đúng lúc đó, nguyên nhân thường nằm ở trình tự tắt Pod chứ không ở mã xử lý. Bài đi theo trình tự ấy để chỉ ra năm chỗ cần để mắt tới.

![Năm chặng khi một Pod của API (Application Programming Interface — giao diện lập trình ứng dụng) bị xóa: Pod chuyển sang Terminating và endpoint của nó được đánh dấu terminating, thường không sẵn sàng và chưa bị xóa ngay, song song với việc tắt, traffic vẫn có thể đến thêm một lúc (do cập nhật chậm, hoặc do proxy cố ý chuyển tới endpoint còn phục vụ khi mọi endpoint đều đang tắt) nên cần chờ ngắn trong preStop, tiến trình chính nhận SIGTERM (signal terminate — tín hiệu yêu cầu tiến trình tự kết thúc) phải ngừng nhận kết nối mới và làm xong việc đang chạy, hết thời gian ân hạn thì bị dừng cưỡng bức (hook preStop chạy quá hạn được gia hạn một lần thêm 2 giây; với ân hạn bằng 0 thì hook preStop không chạy, còn xóa cưỡng bức chỉ có một khoảng ân hạn rất nhỏ), và khi dồn node thì PodDisruptionBudget giữ số Pod tối thiểu.](../../diagrams/sd-13-001-main.svg)

**Đọc hình:** bốn thẻ đầu là trình tự thời gian của một Pod bị xóa; thẻ cuối nói về lúc nhiều Pod bị gỡ có chủ đích cùng một thời điểm.

## Nhìn hình thử trả lời

Pod đã chuyển sang Terminating thì còn nhận được request nào nữa không?

<details>
<summary>Xem đáp án</summary>

Có thể còn trong một khoảng ngắn. Khi Pod bắt đầu tắt, endpoint của nó trong EndpointSlice được đánh dấu terminating và (với Service ở cấu hình mặc định) `ready` thành false, nên bộ cân bằng tải sẽ không dùng nó cho traffic thường; nhưng endpoint chưa bị xóa ngay, và thay đổi lan tới kube-proxy, ingress controller hay bộ cân bằng tải ngoài không tức thì. Vì vậy vài request có thể vẫn tới Pod sau khi nó đã bắt đầu tắt. Ngoài độ trễ lan truyền còn một trường hợp có chủ đích: nếu mọi endpoint của Service đều đang tắt, proxy có thể vẫn chuyển traffic tới endpoint vừa `serving` vừa `terminating` để khỏi mất traffic khi cập nhật cuốn chiếu. Hãy cho ứng dụng thời gian chờ (hook preStop) và để nó làm nốt các request đang chạy.

</details>

## Giới hạn cần nhớ

Bài chỉ nói về tắt êm và giữ số Pod tối thiểu, không bàn cách tạo Pod, probe, tài nguyên hay migration. Phần về endpoint áp dụng cho Service ở cấu hình mặc định; Service đặt `publishNotReadyAddresses: true` hoạt động khác (xem phần sâu). Trình tự `preStop` rồi SIGTERM (signal terminate — tín hiệu yêu cầu tiến trình tự kết thúc) chỉ áp dụng khi thời gian ân hạn khác 0: với `terminationGracePeriodSeconds: 0` hook `preStop` không chạy, còn xóa cưỡng bức chỉ cho một khoảng ân hạn rất nhỏ (xem phần sâu). Độ trễ cập nhật endpoint phụ thuộc cách traffic đi vào cụm (Service, ingress, bộ cân bằng tải của nhà cung cấp), nên con số chờ phải đo trên hệ thống của bạn chứ không lấy từ bài.

<details>
<summary>Xem sâu hơn</summary>

- **Trình tự của kubelet:** hook `preStop` (nếu có) chạy trước, rồi container nhận SIGTERM; `terminationGracePeriodSeconds` (mặc định 30 giây) là thời gian cho cả quá trình và bắt đầu đếm từ trước `preStop`, nên hook chậm làm ứng dụng còn ít thời gian sau SIGTERM. Ngoại lệ nhỏ: nếu `preStop` vẫn đang chạy khi hết hạn, kubelet xin gia hạn một lần thêm 2 giây, nên mốc dừng cưỡng bức có thể muộn hơn giá trị đã đặt; đừng dựa vào 2 giây đó. Hết hạn thì container bị dừng cưỡng bức. Trình tự này chỉ áp dụng khi thời gian ân hạn khác 0. Với `terminationGracePeriodSeconds: 0`, hook `preStop` không chạy và container bị dừng gần như ngay. Xóa cưỡng bức (`kubectl delete --grace-period=0 --force`) gỡ Pod khỏi API ngay và kubelet dọn ngay, chỉ cho container một khoảng ân hạn rất nhỏ trước khi dừng cưỡng bức. Cả hai cách đều không đảm bảo việc tắt êm, nên đừng dùng khi cần xả request.
- **Endpoint không biến mất ngay:** cùng lúc kubelet bắt đầu tắt Pod, control plane đánh giá việc loại Pod đang tắt khỏi EndpointSlice của Service có selector. Endpoint của Pod đang tắt chưa bị xóa ngay: nó được đánh dấu `terminating`, và với Service ở cấu hình mặc định `ready` luôn là false nên bộ cân bằng tải không dùng nó cho traffic thường; điều kiện `serving` cho biết Pod có thật sự còn phục vụ được, dùng để xả dần kết nối. Nếu mọi endpoint của Service đều đang tắt, proxy có thể có chủ đích vẫn chuyển traffic tới endpoint vừa `serving` vừa `terminating` để khỏi mất traffic lúc cập nhật cuốn chiếu, nên đừng giả định Pod đang tắt không nhận thêm request nào. Service đặt `spec.publishNotReadyAddresses: true` là ngoại lệ: endpoint được báo là ready kể cả khi Pod đang tắt, nên việc ngừng nhận traffic ở loại Service đó phải do cơ chế khác đảm nhiệm (ví dụ chính ứng dụng). Các thành phần dẫn traffic nhận thay đổi sau đó vài giây tùy cấu hình, nên một khoảng chờ ngắn trong `preStop` cho chúng thời gian bắt kịp.
- **SIGTERM và tiến trình chính:** dạng exec của `CMD` hoặc `ENTRYPOINT` chạy tiến trình trực tiếp; dạng shell chạy qua một shell nên tín hiệu có thể không tới ứng dụng. Ứng dụng cần xử lý SIGTERM: ngừng nhận kết nối mới và chờ request đang chạy xong.
- **Kết nối dài:** HTTP (HyperText Transfer Protocol — giao thức truyền siêu văn bản) keep-alive, gRPC (giao thức gọi hàm từ xa, RPC là Remote Procedure Call), WebSocket giữ kết nối qua thời điểm tắt; máy chủ nên báo cho client mở kết nối mới (ví dụ đóng kết nối sau request cuối, hay gửi khung GOAWAY của HTTP/2, là tin báo sắp đóng kết nối) thay vì để chúng bị cắt.
- **Đặt thời gian ân hạn:** nên không nhỏ hơn thời gian chờ ở `preStop` cộng với thời gian xử lý của request lâu nhất (không tính vào khoản gia hạn 2 giây dành cho hook chạy quá hạn); đặt quá lớn làm việc thay Pod chậm.
- **PodDisruptionBudget:** `minAvailable` hoặc `maxUnavailable` giới hạn số Pod bị gỡ qua Eviction API (ví dụ `kubectl drain`); không chặn sự cố bất ngờ, và rolling update của Deployment dùng tham số riêng của nó.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-10-k8s-design-patterns.md).
- Kubernetes: [vòng đời Pod và cách Pod bị chấm dứt](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination), [lifecycle hook](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/), [PodDisruptionBudget và disruption](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/), [EndpointSlice](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/).
- Docker: [CMD và ENTRYPOINT, dạng exec và dạng shell](https://docs.docker.com/reference/dockerfile/#entrypoint).
