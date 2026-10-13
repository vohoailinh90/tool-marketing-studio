# Chín thực hành tốt khi viết Dockerfile

Chín thói quen giúp image nhỏ hơn, build nhanh hơn và an toàn hơn. Hình dưới đặt chúng vào một Dockerfile.

![Bốn thẻ theo thứ tự Dockerfile: chọn image gốc có phiên bản cố định, sao chép tệp ít đổi trước, sao chép mã hay đổi sau, rồi chạy bằng người dùng không phải root.](../../diagrams/sd-13-011-main.svg)

- **Nền tảng:** dùng image chính thức; ghi rõ phiên bản thay vì `latest`.
- **Build:** build nhiều giai đoạn, `.dockerignore`, sắp xếp lớp theo mức độ ít đổi.
- **Chạy:** người dùng quyền thấp; cấu hình qua biến môi trường.
- **Quản lý:** gắn nhãn image và quét lỗ hổng trước khi phát hành.

## Nhìn hình thử trả lời

Bạn sửa một dòng mã nguồn nhưng không đổi danh sách phụ thuộc. Với thứ tự như hình, bước cài phụ thuộc có chạy lại không?

<details>
<summary>Xem đáp án</summary>

Không. Lớp sao chép danh sách phụ thuộc không đổi nên Docker dùng lại cache; chỉ các lớp từ bước sao chép mã nguồn trở đi chạy lại.

</details>

## Ngộ nhận dễ gặp

Thẻ phiên bản (tag) không bất biến: người duy trì có thể đẩy lại cùng tag. Cần tái lập chính xác thì ghim theo digest. Image "chính thức" cũng không có nghĩa không có lỗ hổng, nên vẫn phải quét. Đừng nhét bí mật vào biến môi trường dựng sẵn trong image.

<details>
<summary>Xem sâu hơn</summary>

```dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY --from=build /app/dist ./dist
USER node
CMD ["node", "dist/server.js"]
```

- **Nhiều giai đoạn:** công cụ build chỉ nằm ở giai đoạn đầu; image cuối nhỏ hơn.
- **`.dockerignore`:** loại `.git`, `node_modules`, tệp tạm khỏi ngữ cảnh build.
- **Nhãn:** dùng khóa chuẩn như `org.opencontainers.image.source` để biết image đến từ đâu.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/9-docker-best-practices-you-must-know.md).
- Docker: [best practices](https://docs.docker.com/build/building/best-practices/), [multi-stage](https://docs.docker.com/build/building/multi-stage/), [cache](https://docs.docker.com/build/cache/).
