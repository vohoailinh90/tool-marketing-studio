# Gỡ lỗi Docker: bốn sự cố hay gặp

Khi Docker báo lỗi, câu hỏi hữu ích là lỗi nằm ở đâu: giữa lệnh và daemon, giữa máy và registry, trong ổ đĩa, hay giữa kiến trúc CPU. Bốn sự cố dưới đây đại diện cho bốn chỗ đó.

![Bốn sự cố và chỗ cần kiểm tra: không kết nối được daemon thì xem socket, quyền và context, kéo image bị từ chối thì xem tên registry và đăng nhập, ổ đĩa đầy thì xem dung lượng bằng docker system df, và image chạy sai kiến trúc thì xem nền tảng.](../../diagrams/sd-13-026-main.svg)

**Đọc hình:** mỗi sự cố chỉ ra một thành phần: daemon, registry, kho lưu trữ cục bộ, nền tảng chạy.

## Nhìn hình thử trả lời

`docker system prune` có xóa volume chứa dữ liệu của bạn không?

<details>
<summary>Xem đáp án</summary>

Mặc định thì không: với các bản Docker Engine hiện nay volume chỉ bị xóa khi thêm `--volumes`. Dù vậy, nên xem `docker system df` và biết lệnh sẽ xóa gì trước khi chạy.

</details>

## Giới hạn cần nhớ

Lệnh dọn dẹp xóa thật; chạy nhầm trên máy chủ dùng chung có thể mất container đã dừng hay cache build của người khác. Đọc kỹ cảnh báo và thêm cờ chỉ khi hiểu hậu quả.

<details>
<summary>Xem sâu hơn</summary>

- **Daemon và client:** lệnh `docker` chỉ là client gọi daemon qua REST API, trên Linux mặc định bằng socket Unix. Daemon dừng cho lỗi "Cannot connect to the Docker daemon"; thiếu quyền với socket cho lỗi "permission denied" khi kết nối. `DOCKER_HOST` hoặc `docker context` có thể đổi daemon bị gọi.
- **Registry:** tên image có thể kèm máy chủ registry (`registry.example.com/nhom/ung-dung:1.0`); không có thì mặc định là Docker Hub. Từ chối thường do chưa đăng nhập, sai quyền hoặc tag không tồn tại.
- **Dung lượng:** `docker system df` cho thấy image, container, volume và cache build dùng bao nhiêu.
- **Kiến trúc:** image gắn với kiến trúc CPU; chạy image của kiến trúc khác có thể báo lỗi `exec format error` hoặc chạy chậm nếu có giả lập. Image đa nền tảng có nhiều biến thể, chọn bằng `--platform`.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-docker-work.md).
- Docker: [tổng quan](https://docs.docker.com/get-started/docker-overview/), [docker system prune](https://docs.docker.com/reference/cli/docker/system/prune/), [docker system df](https://docs.docker.com/reference/cli/docker/system/df/), [image đa nền tảng](https://docs.docker.com/build/building/multi-platform/).
