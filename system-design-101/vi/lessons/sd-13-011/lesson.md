# Vì sao Docker build chạy lại bước nặng: năm nguyên nhân mất cache

Sửa một dòng mã mà docker build lại cài lại toàn bộ phụ thuộc là chuyện quen thuộc. Cache của Docker hoạt động theo quy tắc cụ thể, nên mỗi lần mất cache đều truy ra được nguyên nhân. Bài nêu năm nguyên nhân hay gặp và cách chữa từng cái.

![Năm nguyên nhân Docker build mất cache và cách chữa: đổi một lớp thì các lớp sau phải build lại nên đặt phần ít đổi lên trên, COPY quá rộng và quá sớm nên copy tệp khóa trước rồi cài phụ thuộc, ngữ cảnh build lẫn tệp hay đổi nên loại chúng khỏi ngữ cảnh, cache dùng được nhưng đã cũ nên build sạch định kỳ, và máy mới không có cache nên xuất nhập cache hoặc dùng cache mount.](../../diagrams/sd-13-011-main.svg)

**Đọc hình:** năm thẻ là năm nguyên nhân độc lập; thẻ nào cũng kèm cách chữa.

## Nhìn hình thử trả lời

Dockerfile có `COPY . .` rồi `RUN npm ci`. Bạn sửa một dòng trong tệp README. Lần build sau có phải cài lại phụ thuộc không, và chữa thế nào?

<details>
<summary>Xem đáp án</summary>

Có. `COPY . .` so checksum nội dung các tệp, nên chỉ cần một tệp đổi là lớp đó mất cache và `RUN npm ci` sau nó phải chạy lại. Hãy `COPY package.json package-lock.json ./`, chạy `npm ci`, rồi mới `COPY . .`; khi chỉ mã đổi, hai lớp đầu vẫn dùng lại được.

</details>

## Giới hạn cần nhớ

Cache giúp nhanh nhưng không bảo đảm đúng: lớp cũ có thể giữ phụ thuộc hay danh sách gói đã lỗi thời, nên cần build sạch định kỳ. Cache từ xa tốn dung lượng và băng thông, và cache mount cần BuildKit. Bài không bàn kích thước image, người dùng không đặc quyền hay quét lỗ hổng.

<details>
<summary>Xem sâu hơn</summary>

```dockerfile
FROM node:22-slim
WORKDIR /app
# lớp ít đổi trước: chỉ tệp khóa
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
# lớp hay đổi sau cùng
COPY . .
CMD ["node", "server.js"]
```

- **Quy tắc vô hiệu hóa:** khi một lớp bị vô hiệu hóa, mọi lớp sau nó phải build lại. Với `COPY` và `ADD`, Docker so checksum nội dung tệp; với `RUN`, chỉ so chuỗi lệnh.
- **Cache cũ:** vì `RUN` chỉ so chuỗi lệnh, `apt-get update` có thể được dùng lại với danh sách gói cũ; gộp `apt-get update` và `apt-get install` trong cùng một `RUN` để chúng cùng mất cache. `--no-cache` bỏ qua cache và `--pull` luôn kéo image cơ sở mới.
- **Cache từ xa:** `--cache-to` và `--cache-from` xuất và nhập cache qua các backend như registry hay thư mục cục bộ, để máy CI mới không bắt đầu từ rỗng.
- **Cache mount:** `RUN --mount=type=cache` giữ thư mục cache của trình quản lý gói giữa các lần build mà không đưa vào image, nên cài lại nhanh dù lớp bị mất cache.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/9-docker-best-practices-you-must-know.md).
- Docker: [vô hiệu hóa cache build](https://docs.docker.com/build/cache/invalidation/), [tối ưu cache](https://docs.docker.com/build/cache/optimize/), [backend cache từ xa](https://docs.docker.com/build/cache/backends/), [docker buildx build](https://docs.docker.com/reference/cli/docker/buildx/build/).
