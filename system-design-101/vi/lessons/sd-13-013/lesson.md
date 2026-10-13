# Docker khi chạy web kèm cơ sở dữ liệu: bốn chỗ hay hỏng

Hãy hình dung một ứng dụng web kèm cơ sở dữ liệu chạy bằng Docker trên một máy chủ. Có bốn chỗ người mới hay vấp, và mỗi chỗ chỉ ra một khái niệm Docker cần hiểu.

![Bốn sự cố và cách xử lý: xóa container làm mất dữ liệu thì dùng volume, web không gọi được cơ sở dữ liệu thì dùng network do người dùng tạo và gọi bằng tên dịch vụ, từ ngoài không vào được web thì publish cổng, container chết không tự chạy lại thì đặt restart policy.](../../diagrams/sd-13-013-main.svg)

**Đọc hình:** bốn sự cố độc lập; cuối bài có một tệp Compose ghép cả bốn.

## Nhìn hình thử trả lời

Trong container web, địa chỉ `localhost:5432` trỏ tới đâu?

<details>
<summary>Xem đáp án</summary>

Tới chính container web, vì mỗi container có không gian mạng riêng, không phải container cơ sở dữ liệu. Hãy đặt hai container trên cùng một network và gọi bằng tên dịch vụ.

</details>

## Giới hạn cần nhớ

Volume không thay cho sao lưu, và cô lập của container phụ thuộc cấu hình nên không coi là hàng rào bảo mật tuyệt đối. Bài này chỉ chọn bốn chỗ hỏng hay gặp, không phải mọi khái niệm Docker.

<details>
<summary>Xem sâu hơn</summary>

```yaml
services:
  web:
    image: example/web:1.0
    ports: ["8080:80"]
    depends_on: [db]
    restart: unless-stopped
  db:
    image: postgres:16
    volumes: ["dbdata:/var/lib/postgresql/data"]
    restart: unless-stopped
volumes:
  dbdata:
```

- **Image và container:** image chỉ đọc; container thêm một lớp ghi, mất khi container bị xóa, nên dữ liệu cần ở volume.
- **Network:** trong Compose, các dịch vụ dùng chung một network mặc định và gọi nhau bằng tên dịch vụ; network bridge do người dùng tạo có DNS theo tên, bridge mặc định thì không.
- **Publish cổng:** chỉ cổng được publish mới truy cập được từ ngoài máy chủ.
- **Restart policy:** `no`, `on-failure`, `always`, `unless-stopped`.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-8-must-know-docker-concepts.md).
- Docker: [volume](https://docs.docker.com/engine/storage/volumes/), [network bridge](https://docs.docker.com/engine/network/drivers/bridge/), [publish cổng](https://docs.docker.com/engine/network/port-publishing/), [restart policy](https://docs.docker.com/engine/containers/start-containers-automatically/), [Compose networking](https://docs.docker.com/compose/how-tos/networking/).
