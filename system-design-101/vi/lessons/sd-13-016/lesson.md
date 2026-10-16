# Tìm đúng Pod trong cụm lớn: selector và cách in kết quả của kubectl

Sau một lần triển khai, cụm có vài trăm Pod mà chỉ vài Pod của dịch vụ `web` đáng ngờ. `kubectl get pods` in ra cả danh sách, trong khi bạn cần đúng những Pod đó cùng vài thông tin như node, image hay số lần khởi động lại. Bài nêu năm cách thu hẹp danh sách và chọn thông tin in ra.

![Năm cách thu hẹp danh sách Pod khi cụm có hàng trăm Pod: chọn phạm vi bằng -n cho một namespace hoặc -A cho mọi namespace, chọn theo nhãn bằng -l, chọn theo trường bằng --field-selector với các trường mà loại tài nguyên hỗ trợ, chọn thông tin in ra bằng -o wide, custom-columns hoặc jsonpath, và sắp thứ tự bằng --sort-by.](../../diagrams/sd-13-016-main.svg)

**Đọc hình:** ba thẻ đầu thu hẹp tập Pod, hai thẻ sau chọn cách hiện kết quả; có thể dùng riêng hoặc kết hợp.

## Từ viết tắt

- **IP** (Internet Protocol) — giao thức Internet: quy ước đánh địa chỉ và chuyển gói tin giữa các máy; địa chỉ IP là địa chỉ của một máy hay một Pod trên mạng.

## Nhìn hình thử trả lời

Bạn chạy `kubectl get pods -A --field-selector status.phase!=Running` để tìm Pod hỏng sau khi triển khai, nhưng Pod đang `CrashLoopBackOff` không xuất hiện. Vì sao, và nên nhìn vào đâu?

<details>
<summary>Xem đáp án</summary>

`status.phase` chỉ nhận Pending, Running, Succeeded, Failed hoặc Unknown. Pod có container chết rồi được khởi động lại vẫn có thể ở phase `Running` (với `restartPolicy` mặc định là `Always`), còn `CrashLoopBackOff` là lý do chờ của container và hiện ở cột STATUS do kubectl tính, không phải một phase. Hãy nhìn các cột READY và RESTARTS, hoặc thêm `--sort-by` theo số lần khởi động lại để Pod khởi động lại nhiều nhất nằm cuối danh sách.

</details>

## Giới hạn cần nhớ

Selector chỉ thu hẹp danh sách, không giải thích vì sao một Pod lỗi; khi đã chọn được Pod, bước tiếp theo là chẩn đoán nó. `--field-selector` chỉ nhận các trường mà loại tài nguyên hỗ trợ, chọn trường khác thì kubectl báo lỗi. Các lệnh trong bài chỉ đọc: trước khi dùng cùng selector cho lệnh xóa hay sửa hàng loạt, hãy chạy `get` với đúng selector đó để xem nó chọn những Pod nào.

<details>
<summary>Xem sâu hơn</summary>

```bash
kubectl get pods -n shop --show-labels                      # xem Pod có những nhãn nào trước khi chọn
kubectl get pods -n shop -l app=web                         # một nhãn
kubectl get pods -n shop -l 'app in (web,api),tier!=batch'  # nhiều giá trị, phủ định
kubectl get pods -A --field-selector status.phase=Pending   # theo trường
kubectl get pods -A --field-selector spec.nodeName=node-1   # Pod trên một node
kubectl get pods -n shop -l app=web -o wide                 # thêm cột node và IP
kubectl get pods -n shop -l app=web \
  -o custom-columns='NAME:.metadata.name,IMAGE:.spec.containers[*].image'
kubectl get pods -n shop -l app=web \
  -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].image}{"\n"}{end}'
kubectl get pods -n shop --sort-by='.status.containerStatuses[0].restartCount'
```

- **Nhãn và trường khác nhau:** nhãn do người dùng gắn và chọn được trên mọi loại tài nguyên. `--field-selector` đọc các trường có sẵn của đối tượng: mọi loại hỗ trợ `metadata.name` và `metadata.namespace`, các trường còn lại tùy loại (với Pod có `status.phase`). Với cả hai, dấu phẩy nối nhiều điều kiện thành "và".
- **`!=` rộng hơn vẻ ngoài:** `tier!=batch` chọn cả Pod không có nhãn `tier`. Muốn chỉ lấy Pod có nhãn `tier` mà khác `batch`, nối thêm điều kiện tồn tại: `-l 'tier,tier!=batch'`.
- **STATUS không phải phase:** cột STATUS do kubectl tính từ nhiều trường. `CrashLoopBackOff` và `Terminating` không phải giá trị phase, và Pod đang hiện chúng có thể vẫn ở phase `Running`. Ngược lại, `status.phase!=Running` chọn cả Pod `Succeeded` của các Job đã xong, vốn không hỏng.
- **Bắt đầu đường dẫn jsonpath:** `kubectl get pods` trả về một danh sách nên đường dẫn bắt đầu bằng `.items[*]`; `kubectl get pod ten-pod` trả về một đối tượng nên đường dẫn bắt đầu thẳng bằng `.metadata.name`.
- **Sắp thứ tự:** `--sort-by` sắp tăng dần theo đường dẫn trường; ví dụ trên chỉ xét container đầu tiên của mỗi Pod.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/the-ultimate-kubernetes-command-cheatsheet.md).
- Kubernetes: [nhãn và selector](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/#label-selectors), [field selector](https://kubernetes.io/docs/concepts/overview/working-with-objects/field-selectors/), [phase của Pod](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-phase), [kubectl quick reference](https://kubernetes.io/docs/reference/kubectl/quick-reference/), [JSONPath với kubectl](https://kubernetes.io/docs/reference/kubectl/jsonpath/).
