# Hệ sinh thái Kubernetes theo nhu cầu vận hành

Một cụm Kubernetes chạy thật sớm muộn cũng phát sinh vài nhu cầu vận hành quen thuộc. Mỗi nhu cầu có cơ chế sẵn có của Kubernetes hoặc một dự án quen thuộc trong hệ sinh thái; tên công cụ chỉ là ví dụ.

![Năm nhu cầu vận hành và công cụ ví dụ: triển khai lặp lại được bằng Git và Argo CD hoặc Flux, chia cụm cho nhiều nhóm bằng namespace, quota, RBAC và NetworkPolicy, co giãn theo tải bằng HPA và Cluster Autoscaler hay Karpenter, biết sự cố trước người dùng bằng cảnh báo từ số đo, và giữ bí mật ngoài Git bằng kho bí mật bên ngoài.](../../diagrams/sd-13-009-main.svg)

**Đọc hình:** năm nhu cầu độc lập, không theo thứ tự; bài chọn các nhu cầu thường gặp, không phải bản đồ đầy đủ của hệ sinh thái.

## Nhìn hình thử trả lời

Tải tăng đột ngột. HPA và Cluster Autoscaler mỗi cái làm gì, và cái nào chạy trước?

<details>
<summary>Xem đáp án</summary>

HPA chạy trước: nó tăng số Pod dựa trên số đo như CPU. Nếu không còn node đủ chỗ, Pod mới nằm ở Pending và Cluster Autoscaler (hoặc Karpenter) thêm node để Pod được đặt.

</details>

## Giới hạn cần nhớ

Mỗi công cụ thêm vào là một thứ cần nâng cấp, vá lỗi và dạy người mới. NetworkPolicy chỉ có tác dụng khi plugin mạng của cụm thực thi nó. Danh sách ví dụ không đầy đủ và không phải khuyến nghị; hãy bắt đầu từ nhu cầu thực của bạn.

<details>
<summary>Xem sâu hơn</summary>

- **GitOps:** Argo CD và Flux đưa trạng thái cụm về đúng thứ khai báo trong Git; Helm đóng gói có tham số, Kustomize chồng lớp cấu hình và tích hợp sẵn trong kubectl.
- **Nhiều nhóm một cụm:** namespace tách tên, `ResourceQuota` giới hạn tài nguyên mỗi namespace, RBAC giới hạn quyền, NetworkPolicy giới hạn luồng mạng.
- **Co giãn:** HPA đổi số Pod theo số đo; Cluster Autoscaler và Karpenter đổi số node theo Pod chưa đặt được.
- **Cảnh báo:** nên đặt từ mục tiêu mức dịch vụ để cảnh báo phản ánh tác động tới người dùng.
- **Bí mật:** đừng lưu bí mật dạng rõ trong Git; công cụ như External Secrets Operator hay Secrets Store CSI Driver lấy chúng từ kho bí mật bên ngoài.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/kubernetes-tools-ecosystem.md).
- Kubernetes: [HPA](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/), [ResourceQuota](https://kubernetes.io/docs/concepts/policy/resource-quotas/), [NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/).
- [Argo CD](https://argo-cd.readthedocs.io/), [Flux](https://fluxcd.io/), [Cluster Autoscaler](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler), [External Secrets](https://external-secrets.io/). CNCF [Landscape](https://landscape.cncf.io/).
