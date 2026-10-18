# Từ hàng đợi tới nhật ký: IBM MQ, RabbitMQ, Kafka, Pulsar khác nhau ở chỗ tin có còn sau khi đọc

**Bước ngoặt lớn nhất trong lịch sử hàng đợi tin nhắn là tin không còn bị xóa khi đã đọc.** Nguồn kể bốn chặng: IBM MQ, RabbitMQ, Kafka, Pulsar. Với hàng đợi kiểu cũ, một tin được giao cho một người nhận rồi biến mất. Với nhật ký sự kiện kiểu Kafka, tin nằm lại tới khi hết hạn, và mỗi nhóm người nhận tự giữ vị trí đọc của mình, nên nhóm mới có thể đọc lại từ đầu. Bài này thử cả hai cách bằng Redis, vì Redis có sẵn cả hàng đợi (danh sách) lẫn nhật ký (stream).

![Ba khung dọc. Khung một, bốn chặng: IBM MQ, hàng đợi tin nhắn ra đời năm 1993 theo nguồn; RabbitMQ, người gửi đưa tin vào một exchange và exchange chuyển tin tới hàng đợi theo kiểu direct, topic hay fanout; Kafka, nhật ký sự kiện, tin không bị xóa khi đọc mà được giữ theo thời hạn; Pulsar, có cả kiểu chủ đề lẫn kiểu hàng đợi và nhớ vị trí đọc của từng người nhận. Khung hai, thử hàng đợi bằng danh sách của Redis 7.0: sáu tin, hai người nhận chia nhau ba và ba; người nhận đến sau không còn tin nào. Khung ba, thử nhật ký bằng stream của Redis: hai người trong nhóm kho chia nhau ba và ba; nhóm thống kê đọc đủ sáu tin; một nhóm tạo sau vẫn đọc được cả sáu tin cũ.](../../diagrams/sd-04-037-main.svg)

## Từ viết tắt

- **IBM** (International Business Machines) — tập đoàn công nghệ của Mỹ, làm ra sản phẩm IBM MQ.
- **MQ** (Message Queue) — hàng đợi tin nhắn: nơi chương trình gửi để tin lại cho chương trình khác lấy sau, hai bên không cần chạy cùng lúc.

## Đọc hình

1. **IBM MQ.** Nguồn ghi sản phẩm ra đời năm 1993 (tên đầu là MQSeries) và được dùng nhiều trong ngành tài chính. Đây là hàng đợi tin nhắn đúng nghĩa: gửi vào, lấy ra.
2. **RabbitMQ.** Người gửi không gửi thẳng vào hàng đợi mà vào một exchange; exchange chuyển tin tới các hàng đợi theo kiểu của nó: `direct` (khớp đúng khóa định tuyến), `topic` (khớp theo mẫu), `fanout` (gửi bản sao cho mọi hàng đợi). Tài liệu RabbitMQ nói mọi loại hàng đợi của nó đều "tiêu thụ có xóa": tin bị xóa khỏi hàng đợi khi người nhận xử lý xong.
3. **Kafka.** Tài liệu Kafka viết: khác với hệ nhắn tin truyền thống, sự kiện không bị xóa sau khi đọc; mỗi chủ đề đặt thời hạn giữ, quá hạn mới bỏ. Một sự kiện đọc được bao nhiêu lần cũng được.
4. **Pulsar.** README của Pulsar nêu có cả kiểu chủ đề lẫn kiểu hàng đợi, và hệ thống nhớ vị trí đọc của từng người nhận. Nguồn thêm rằng Pulsar chia hai tầng (phục vụ và lưu trữ) và có lưu trữ phân tầng sang kho rẻ hơn.

**Thử ngày 2026-10-18 với Redis 7.0.15.** Danh sách làm hàng đợi: đẩy 6 tin, người nhận A lấy 3, B lấy 3; người nhận C đến sau lấy được `None`. Stream làm nhật ký: ghi 6 tin; nhóm `kho` có hai người nhận chia nhau 3 và 3; nhóm `thống_kê` đọc đủ 6; một nhóm tạo sau cả hai vẫn đọc được 6 tin cũ, và stream vẫn giữ 6 tin. Tài liệu Redis tự mô tả stream là cấu trúc giống nhật ký chỉ ghi nối, và nói nhóm người nhận của nó về cơ bản là điều Kafka làm.

## Giới hạn cần nhớ

Lịch sử không đi một đường thẳng: RabbitMQ ngày nay cũng có stream, mô hình nhật ký chỉ ghi nối đọc lại được tới khi hết hạn; Redis có cả hai. Câu hỏi đúng không phải "dùng sản phẩm đời mới nhất" mà "tin có cần đọc lại không". Nếu chỉ cần giao mỗi việc cho đúng một người làm, hàng đợi là đủ và đơn giản hơn; nếu nhiều hệ cần cùng một chuỗi sự kiện, hoặc cần đọc lại sau sự cố, thì cần nhật ký. Phép thử dùng Redis làm mô hình, không chạy Kafka, RabbitMQ hay Pulsar thật. Bài không giữ con số doanh thu của IBM MQ mà nguồn nêu, vì chưa đối chiếu được.

## Nhìn hình thử trả lời

Một hệ đặt hàng gửi sự kiện "đơn mới" cho dịch vụ kho. Tháng sau, nhóm phân tích muốn dựng một dịch vụ thống kê cần mọi đơn của ba tháng qua. Với hàng đợi kiểu cũ và với nhật ký kiểu Kafka, chuyện gì xảy ra?

<details>
<summary>Xem đáp án</summary>

Với hàng đợi kiểu cũ, mỗi tin đã bị xóa khi kho xử lý xong, như người nhận C trong phép thử: dịch vụ thống kê mới không có gì để đọc, phải xin dữ liệu từ cơ sở dữ liệu đơn hàng. Muốn có từ đầu thì lẽ ra phải tạo thêm một hàng đợi riêng cho thống kê (chẳng hạn bằng exchange `fanout`) trước khi các đơn được gửi.
Với nhật ký, dịch vụ thống kê là một nhóm người nhận mới, đọc từ đầu, như nhóm tạo sau trong phép thử, miễn là thời hạn giữ của chủ đề còn dài hơn ba tháng.

</details>

<details>
<summary>Xem sâu hơn: mã phép thử</summary>

```python
import redis                                         # pip install redis; cần một Redis đang chạy
r = redis.Redis(port=6393, decode_responses=True)
r.delete("orders_queue", "orders_log")

# 1. Hàng đợi kiểu cũ: tin đã lấy là mất; hai người nhận chia nhau các tin
for i in range(1, 7):
    r.lpush("orders_queue", f"đơn {i}")
a = [r.rpop("orders_queue") for _ in range(3)]       # người nhận A lấy 3 tin
b = [r.rpop("orders_queue") for _ in range(3)]       # người nhận B lấy 3 tin còn lại
print("hàng đợi: A nhận", a, "| B nhận", b, "| còn lại", r.llen("orders_queue"))
print("người nhận C đến sau:", r.rpop("orders_queue"))

# 2. Nhật ký kiểu Kafka (Redis Streams): tin được giữ lại; mỗi nhóm nhận có vị trí đọc riêng
for i in range(1, 7):
    r.xadd("orders_log", {"đơn": i})
r.xgroup_create("orders_log", "kho", id="0")
r.xgroup_create("orders_log", "thống_kê", id="0")
read = lambda group, who, n: [f["đơn"] for _, msgs in r.xreadgroup(group, who, {"orders_log": ">"}, count=n) for _, f in msgs]
print("nhật ký: nhóm kho, hai người nhận:", read("kho", "k1", 3), read("kho", "k2", 3))
print("nhật ký: nhóm thống_kê đọc lại từ đầu:", read("thống_kê", "t1", 6))
r.xgroup_create("orders_log", "kiểm_toán_mới", id="0")        # một nhóm sinh sau vẫn đọc được lịch sử
print("nhóm sinh sau:", read("kiểm_toán_mới", "x1", 6), "| số tin vẫn còn trong nhật ký:", r.xlen("orders_log"))
```

Kết quả: A nhận đơn 1 đến 3, B nhận đơn 4 đến 6, còn lại 0; C nhận `None`. Nhóm `kho`: `['1', '2', '3']` và `['4', '5', '6']`; nhóm `thống_kê` và nhóm sinh sau: cả sáu tin; stream còn 6 tin.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-do-message-queue-architectures-evolve.md): bốn chặng IBM MQ, RabbitMQ, Kafka, Pulsar.
- Tài liệu, mỗi tệp tại commit đầu nhánh chính ngày 2026-10-18, đọc từ bản clone nông: [RabbitMQ — Exchanges](https://github.com/rabbitmq/rabbitmq-website/blob/7c2c1490f144bc62be5e3c8c0306d9742882196c/docs/exchanges.md) (các kiểu exchange) và [Streams](https://github.com/rabbitmq/rabbitmq-website/blob/7c2c1490f144bc62be5e3c8c0306d9742882196c/docs/streams.md) (hàng đợi tiêu thụ có xóa, stream thì không); [Kafka — Introduction](https://github.com/apache/kafka/blob/cc8baadc9f0363f2bdfe68a2f1cd8dbe4372d282/docs/getting-started/introduction.md) (sự kiện không bị xóa sau khi đọc, giữ theo thời hạn); [Pulsar — README](https://github.com/apache/pulsar/blob/c9a95df05883e112151bda20c70b2b33d9067454/README.md) (kiểu chủ đề và hàng đợi, nhớ vị trí đọc); [Redis — Streams](https://github.com/redis/docs/blob/3b030c7ef066c0bb7f88ddec02c784e49783b0f8/content/develop/data-types/streams/_index.md) (nhật ký chỉ ghi nối, nhóm người nhận).

Phép thử chạy trên Redis 7.0.15 với thư viện redis-py 8.1.0 ngày 2026-10-18 trên máy biên soạn. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.
