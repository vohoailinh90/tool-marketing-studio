# Viết Dockerfile build nhanh, image nhỏ và không lộ bí mật

Ba nỗi đau hay gặp khi đóng gói ứng dụng: build lại quá chậm, image quá to và bí mật lọt vào image, thêm một việc phụ là làm cho lúc chạy êm và chặt. Bài chỉ chọn những kỹ thuật phục vụ các việc này.

![Ba nỗi đau chính cùng một việc phụ và kỹ thuật tương ứng: build chậm thì sắp lớp, dùng cache mount và dockerignore, image to thì build nhiều giai đoạn, bí mật lọt vào image thì dùng secret mount thay cho ARG và ENV, và việc phụ là chạy êm và chặt bằng CMD dạng exec cùng người dùng không phải root.](../../diagrams/sd-13-011-main.svg)

**Đọc hình:** bài không nhằm liệt kê mọi thực hành; mỗi thẻ là một vấn đề kèm vài kỹ thuật chọn lọc.

## Nhìn hình thử trả lời

Bạn truyền token để cài gói riêng qua ARG. Vì sao đó không phải cách an toàn?

<details>
<summary>Xem đáp án</summary>

Giá trị ARG có thể xem lại từ lịch sử build của image. Secret mount của BuildKit chỉ cho bí mật tồn tại trong lúc chạy lệnh đó và không lưu vào lớp image.

</details>

## Giới hạn cần nhớ

Chạy bằng người dùng không phải root chỉ giảm quyền của tiến trình lúc chạy, không xóa được bí mật đã nằm trong lớp image; chỉ secret mount mới tránh được việc đó. Tag có thể bị đẩy lại, nên cần tái lập chính xác thì ghim digest. Cache mount chỉ nhanh hơn khi máy build giữ lại cache. Quét lỗ hổng và theo dõi nguồn gốc image là việc riêng, bài này không đi sâu.

<details>
<summary>Xem sâu hơn</summary>

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY . .
RUN npm run build

FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm npm ci --omit=dev
COPY --from=build /app/dist ./dist
USER node
CMD ["node", "dist/server.js"]
```

Cần gói riêng thì truyền bí mật bằng secret mount, không bằng ARG:

```dockerfile
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci
```

```bash
docker build --secret id=npmrc,src=$HOME/.npmrc .
```

- **Dạng exec** `CMD ["node", ...]` chạy tiến trình trực tiếp; dạng shell bọc trong `/bin/sh -c` nên tín hiệu dừng có thể không tới ứng dụng.
- **Thứ tự lớp:** lớp nào đổi thì mọi lớp sau nó chạy lại, nên đặt phần ít đổi lên trước.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/9-docker-best-practices-you-must-know.md).
- Docker: [best practices](https://docs.docker.com/build/building/best-practices/), [multi-stage](https://docs.docker.com/build/building/multi-stage/), [tối ưu cache](https://docs.docker.com/build/cache/optimize/), [secrets](https://docs.docker.com/build/building/secrets/), [CMD](https://docs.docker.com/reference/dockerfile/#cmd).
