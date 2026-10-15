# Cụm Kubernetes cần thêm công cụ nào trước: đi từ triệu chứng

Hệ sinh thái Kubernetes có rất nhiều công cụ, và một nhóm nhỏ mới vận hành cụm không cần cài tất cả ngay từ đầu. Cách chọn thực dụng là đi từ triệu chứng đang gặp: mỗi triệu chứng gợi ra một nhu cầu, và mỗi nhu cầu có vài công cụ quen thuộc để làm ví dụ.

![Ba triệu chứng và công cụ ví dụ: không rõ cụm đang chạy bản nào thì để cấu hình trong Git và để Argo CD (CD là Continuous Delivery — chuyển giao liên tục) hoặc Flux đồng bộ cụm theo Git; người dùng biết lỗi trước nhóm thì đặt cảnh báo từ số đo bằng Prometheus với Alertmanager; bí mật nằm trong Git thì giữ chúng ở kho bí mật bên ngoài và đồng bộ vào cụm bằng External Secrets Operator hoặc Secrets Store CSI (Container Storage Interface — giao diện lưu trữ cho container) Driver.](../../diagrams/sd-13-009-main.svg)

**Đọc hình:** ba triệu chứng độc lập, không theo thứ tự; bài chỉ chọn ba nhu cầu nên giải quyết sớm, không phải bản đồ của cả hệ sinh thái.

## Từ viết tắt

- **CD** (Continuous Delivery) — chuyển giao liên tục: tự động đưa bản đã kiểm tra tới bước phát hành; Argo CD là công cụ đồng bộ cụm với cấu hình đặt trong Git.
- **CSI** (Container Storage Interface) — giao diện lưu trữ cho container: chuẩn để Kubernetes gắn các loại kho lưu trữ khác nhau; Secrets Store CSI Driver dùng nó để gắn bí mật từ kho bên ngoài vào Pod.

## Nhìn hình thử trả lời

Ai đó sửa tay một Deployment bằng `kubectl` trên cụm, còn Git vẫn giữ bản cũ. Argo CD (CD là Continuous Delivery — chuyển giao liên tục) sẽ làm gì?

<details>
<summary>Xem đáp án</summary>

Mặc định Argo CD chỉ báo ứng dụng lệch khỏi Git (OutOfSync) và không tự sửa, vì thay đổi làm trực tiếp trên cụm không kích hoạt đồng bộ tự động. Bật `selfHeal` trong chính sách đồng bộ tự động thì nó đưa cụm về đúng bản trong Git. Muốn thay đổi bền vững, hãy sửa trong Git.

</details>

## Giới hạn cần nhớ

Mỗi công cụ thêm vào là một thứ cần nâng cấp, vá lỗi và dạy người mới, nên hãy xem nhà cung cấp cụm đã có chức năng tương ứng chưa trước khi tự cài. Ba nhu cầu trên chỉ là điểm bắt đầu cho nhóm nhỏ; cụm lớn hơn sẽ gặp nhiều nhu cầu khác mà bài không bàn. Tên công cụ chỉ là ví dụ, không phải khuyến nghị.

<details>
<summary>Xem sâu hơn</summary>

- **Đồng bộ theo Git:** Argo CD và Flux đều giữ cụm đồng bộ với cấu hình trong Git. Ở Argo CD, bật đồng bộ tự động cùng `selfHeal: true` thì thay đổi làm tay trên cụm bị đưa về đúng bản trong Git; mặc định thì không.
- **Cảnh báo:** Prometheus gửi cảnh báo tới Alertmanager, nơi gom nhóm, loại trùng và định tuyến chúng tới nơi nhận như email hay PagerDuty. Tài liệu Prometheus khuyên cảnh báo theo triệu chứng gắn với trải nghiệm người dùng thay vì theo từng nguyên nhân, và giữ số cảnh báo ít.
- **Bí mật:** Secret của Kubernetes mặc định được lưu không mã hóa trong etcd, và giá trị trong trường `data` chỉ là chuỗi base64, đọc lại được dễ dàng, nên đừng đưa chúng vào Git dạng rõ. External Secrets Operator đọc bí mật từ hệ thống bên ngoài rồi tạo Secret trong cụm; Secrets Store CSI Driver (CSI là Container Storage Interface — giao diện lưu trữ cho container) gắn bí mật từ kho bên ngoài vào Pod như một volume.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/kubernetes-tools-ecosystem.md).
- Argo CD: [đồng bộ tự động và tự chữa](https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/). [Flux](https://fluxcd.io/flux/).
- Prometheus: [Alertmanager](https://prometheus.io/docs/alerting/latest/alertmanager/), [thực hành cảnh báo](https://prometheus.io/docs/practices/alerting/).
- Kubernetes: [Secret](https://kubernetes.io/docs/concepts/configuration/secret/). [External Secrets](https://external-secrets.io/), [Secrets Store CSI Driver](https://secrets-store-csi-driver.sigs.k8s.io/). CNCF (Cloud Native Computing Foundation — quỹ bảo trợ các dự án điện toán đám mây nguyên bản như Kubernetes) [Landscape](https://landscape.cncf.io/).
