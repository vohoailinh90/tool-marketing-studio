# Sáu mảng của hệ sinh thái Kubernetes

Kubernetes tự nó nhỏ; phần lớn việc vận hành thật dựa trên công cụ bên ngoài. Sáu mảng sau là một cách chia để tìm.

![Sáu thẻ: bảo mật, mạng, container runtime, quản lý cụm, giám sát và quan sát, điều phối hạ tầng; mỗi thẻ kèm vài ví dụ.](../../diagrams/sd-13-009-main.svg)

**Đọc hình:** mỗi mảng có nhiều lựa chọn; các tên ở đây là ví dụ để bạn có từ khóa tìm hiểu.

## Nhìn hình thử trả lời

Từ Kubernetes 1.24, cụm còn chạy được image tạo bằng Docker không?

<details>
<summary>Xem đáp án</summary>

Có. Image Docker tuân theo chuẩn OCI nên containerd hoặc CRI-O chạy được. Thứ bị gỡ là dockershim, lớp cho phép kubelet dùng Docker Engine trực tiếp.

</details>

## Giới hạn cần nhớ

Các mảng chồng lấn: service mesh vừa là mạng vừa liên quan bảo mật, Prometheus vừa giám sát vừa dùng để cảnh báo. Danh sách ví dụ không đầy đủ và không phải khuyến nghị.

<details>
<summary>Xem sâu hơn</summary>

- **CRI** (Container Runtime Interface) là giao diện kubelet dùng để nói chuyện với runtime.
- **CNI** là chuẩn cắm plugin mạng cho container.
- **Quản lý cụm vs điều phối hạ tầng:** nhóm đầu dựng và nâng cấp cụm; nhóm sau khai báo tài nguyên cloud (máy, mạng, cơ sở dữ liệu) và thường chạy ngoài cụm.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/kubernetes-tools-ecosystem.md).
- Kubernetes: [container runtime](https://kubernetes.io/docs/setup/production-environment/container-runtimes/), [Dockershim FAQ](https://kubernetes.io/blog/2022/02/17/dockershim-faq/).
- CNCF [Landscape](https://landscape.cncf.io/).
