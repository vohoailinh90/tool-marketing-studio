# Docker chạy thế nào: client, host và registry

Lệnh `docker` chỉ là client. Việc build, kéo và chạy do daemon trên Docker host làm, còn image nằm trong registry.

![Docker client gửi lệnh tới daemon trên Docker host; daemon kéo image từ registry nếu chưa có và tạo container.](../../diagrams/sd-13-026-main.svg)

**Đọc hình:** client và daemon có thể ở cùng máy hoặc khác máy.

## Nhìn hình thử trả lời

`docker run` một image chưa có trên máy. Bước nào xảy ra trước khi container khởi động?

<details>
<summary>Xem đáp án</summary>

Daemon kéo image từ registry về kho cục bộ trước, rồi mới tạo và khởi động container.

</details>

## Giới hạn cần nhớ

`docker run` chỉ kéo image khi nó chưa có sẵn cục bộ; nếu đã có (kể cả bản cũ cùng tag), Docker dùng bản đó. Muốn bản mới nhất của tag thì kéo lại.

<details>
<summary>Xem sâu hơn</summary>

- **build:** client gửi ngữ cảnh build (Dockerfile và các tệp liên quan) cho daemon; kết quả là một image trong kho cục bộ.
- **pull:** chép image từ registry vào kho cục bộ, không tạo container nào.
- **run:** gộp `docker create` (dựng container từ image cùng cấu hình như mạng, volume, biến môi trường) và `docker start`. Image chưa có cục bộ thì daemon kéo trước.
- Cả ba đều là yêu cầu API gửi tới daemon, nên client và daemon có thể ở hai máy khác nhau.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-docker-work.md).
- Docker: [tổng quan kiến trúc](https://docs.docker.com/get-started/docker-overview/), [docker run](https://docs.docker.com/reference/cli/docker/container/run/).
