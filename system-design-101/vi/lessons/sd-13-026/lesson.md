# Docker chạy thế nào: client, host và registry

Lệnh `docker` chỉ là client. Việc build, kéo và chạy do daemon trên Docker host làm, còn image nằm trong registry.

![Docker client gửi lệnh tới daemon trên Docker host; daemon kéo image từ registry nếu chưa có và tạo container.](../../diagrams/sd-13-026-main.svg)

**Đọc hình:** client và daemon có thể ở cùng máy hoặc khác máy.

## Nhìn hình thử trả lời

`docker run` một image chưa có trên máy. Bước nào xảy ra trước khi container khởi động?

<details>
<summary>Xem đáp án</summary>

Daemon kéo image từ registry về máy. Sau đó nó tạo container, cấp lớp ghi, nối mạng rồi khởi động.

</details>

## Giới hạn cần nhớ

`docker run` chỉ kéo image khi nó chưa có sẵn cục bộ; nếu đã có (kể cả bản cũ cùng tag), Docker dùng bản đó. Muốn bản mới nhất của tag thì kéo lại.

<details>
<summary>Xem sâu hơn</summary>

Các bước chính của `docker run`:

1. Kéo image từ registry nếu chưa có cục bộ.
2. Tạo container mới từ image.
3. Cấp một lớp hệ thống tệp ghi được trên cùng các lớp chỉ đọc của image.
4. Tạo giao diện mạng nối container với mạng mặc định (trừ khi chọn mạng khác).
5. Khởi động container và chạy lệnh đã chỉ định.

`docker build` gửi ngữ cảnh build tới daemon để dựng image; `docker pull` chỉ tải image về.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-docker-work.md).
- Docker: [tổng quan kiến trúc](https://docs.docker.com/get-started/docker-overview/), [docker run](https://docs.docker.com/reference/cli/docker/container/run/).
