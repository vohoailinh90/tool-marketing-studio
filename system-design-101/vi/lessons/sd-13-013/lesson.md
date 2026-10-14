# Docker khi chạy web kèm cơ sở dữ liệu: bốn chỗ hay hỏng

Hãy hình dung một ứng dụng web kèm cơ sở dữ liệu chạy bằng Docker trên một máy chủ. Có bốn chỗ người mới hay vấp, và mỗi chỗ chỉ ra một khái niệm Docker cần hiểu.

![Bốn sự cố và cách xử lý: xóa container làm mất dữ liệu thì dùng volume, web không gọi được cơ sở dữ liệu thì dùng network do người dùng tạo và gọi bằng tên dịch vụ, từ ngoài không vào được web thì với network bridge phải publish cổng (EXPOSE không tự publish, chỉ cờ -P dùng nó; network host bỏ qua publish), container chết không tự chạy lại thì đặt restart policy.](../../diagrams/sd-13-013-main.svg)

**Đọc hình:** bốn sự cố độc lập; cuối bài có một tệp Compose ghép cả bốn.

## Từ viết tắt

- **URI** (Uniform Resource Identifier) — định danh tài nguyên thống nhất: chuỗi viết ra một tài nguyên theo quy tắc chung; trong bài là chuỗi kết nối cơ sở dữ liệu, nơi ký tự đặc biệt trong mật khẩu phải được mã hóa phần trăm.
- **TCP** (Transmission Control Protocol) — giao thức điều khiển truyền: tạo kết nối đáng tin cậy, dữ liệu đến đủ và đúng thứ tự.
- **DNS** (Domain Name System) — hệ thống tên miền: "danh bạ" của Internet, đổi tên như example.com thành địa chỉ để các máy tìm thấy nhau.

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
    environment:
      DB_HOST: db
      DB_PORT: "5432"
      DB_NAME: app
      DB_USER: app
      DB_PASSWORD: ${DB_PASSWORD}
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: app
      POSTGRES_DB: app
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes: ["dbdata:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -h 127.0.0.1 -U app -d app"]
      interval: 5s
      timeout: 3s
      retries: 10
    restart: unless-stopped
volumes:
  dbdata:
```

Đặt `DB_PASSWORD` trong biến môi trường hoặc trong tệp `.env` không đưa vào Git. Image PostgreSQL chính thức cần một mật khẩu không rỗng khi khởi tạo dữ liệu lần đầu, đưa vào qua `POSTGRES_PASSWORD` hoặc qua `POSTGRES_PASSWORD_FILE` trỏ tới một tệp (cách dùng với Docker secrets, để mật khẩu không nằm trong biến môi trường), trừ khi cố ý đặt `POSTGRES_HOST_AUTH_METHOD=trust` để bỏ qua xác thực bằng mật khẩu; tài liệu của image cảnh báo cấu hình đó không an toàn. Ví dụ truyền các tham số kết nối riêng thay vì nhúng mật khẩu vào một URI (Uniform Resource Identifier — định danh tài nguyên thống nhất), vì mật khẩu có ký tự đặc biệt (`@`, `:`, `/`, `%`, `#`) trong URI phải được mã hóa phần trăm. Healthcheck gọi `pg_isready` với `-h 127.0.0.1` để kiểm tra qua TCP (Transmission Control Protocol — giao thức điều khiển truyền tải) ngay trong container `db`: nếu bỏ `-h`, lệnh kiểm tra socket Unix và có thể báo sẵn sàng khi máy chủ tạm của image PostgreSQL (chỉ nghe trên socket lúc khởi tạo dữ liệu lần đầu) chưa mở cổng mạng. Kiểm tra này hẹp hơn đường `web` dùng: nó chỉ cho biết máy chủ nhận kết nối TCP từ chính container `db`, không thử phân giải tên `db` hay đường mạng Compose từ `web`, và `pg_isready` không cần tên người dùng, mật khẩu hay cơ sở dữ liệu đúng để trả lời, nên kết nối thật của `web` vẫn có thể lỗi dù healthcheck đạt.

- **Image và container:** image chỉ đọc; container thêm một lớp ghi, mất khi container bị xóa, nên dữ liệu cần ở volume.
- **Network:** trong Compose, các dịch vụ dùng chung một network mặc định và gọi nhau bằng tên dịch vụ; network bridge do người dùng tạo có DNS (Domain Name System — hệ thống phân giải tên miền) theo tên, bridge mặc định thì không.
- **Publish cổng:** với network bridge như ví dụ này, chỉ cổng được publish mới truy cập được từ ngoài máy chủ. `EXPOSE` trong Dockerfile không publish cổng; cờ `-P` của `docker run` publish các cổng đã `EXPOSE` (hoặc `--expose`) ra cổng ngẫu nhiên của máy chủ, còn `-p` ánh xạ cổng cụ thể. Network host dùng thẳng mạng của máy chủ và bỏ qua publish, còn chế độ định tuyến trực tiếp của bridge (ví dụ `nat-unprotected`) có thể để lộ cả cổng chưa publish.
- **Restart policy:** `no`, `on-failure`, `always`, `unless-stopped`.
- **Thứ tự khởi động:** `depends_on` đơn giản chỉ xếp thứ tự khởi động, không đợi cơ sở dữ liệu sẵn sàng; điều kiện `service_healthy` cùng `healthcheck` mới đợi đến khi lệnh kiểm tra thành công, trong phạm vi mà lệnh đó kiểm tra.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-8-must-know-docker-concepts.md).
- Docker: [volume](https://docs.docker.com/engine/storage/volumes/), [network bridge](https://docs.docker.com/engine/network/drivers/bridge/), [publish cổng](https://docs.docker.com/engine/network/port-publishing/), [EXPOSE](https://docs.docker.com/reference/dockerfile/#expose), [docker run -P](https://docs.docker.com/reference/cli/docker/container/run/#publish-all), [network host](https://docs.docker.com/engine/network/drivers/host/), [restart policy](https://docs.docker.com/engine/containers/start-containers-automatically/), [Compose networking](https://docs.docker.com/compose/how-tos/networking/). PostgreSQL: [pg_isready](https://www.postgresql.org/docs/current/app-pg-isready.html), [entrypoint của image chính thức](https://github.com/docker-library/postgres/blob/master/docker-entrypoint.sh).
