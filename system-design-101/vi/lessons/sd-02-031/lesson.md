# Lớp API của Uber qua ba thế hệ

**Theo bài nguồn, cổng API của Uber đã qua ba thế hệ: tự lớn lên từ hai dịch vụ, một cổng ôm hết mọi việc, rồi một lớp tự phục vụ, phi tập trung và chia tầng.**
Bài này đọc ba thế hệ đó theo điều đã đổi quanh cổng: số dịch vụ phía sau và số mảng kinh doanh phía trước.

![Ba bước nối nhau. Thế hệ một, tự lớn lên: năm 2014 kiến trúc Uber có hai dịch vụ chính, dịch vụ điều phối nối người đi với tài xế, và dịch vụ API giữ dữ liệu lâu dài về người dùng và chuyến đi. Thế hệ hai, một cổng ôm hết: Uber theo microservice từ rất sớm, tới năm 2019 có hơn 2.200 microservice. Thế hệ ba, tự phục vụ, phi tập trung, chia tầng: từ đầu năm 2018 có nhiều mảng kinh doanh mới như vận tải hàng hóa, ATG, Elevate và giao đồ tạp hóa. Khung cuối: ba điều cần nhớ.](../../diagrams/sd-02-031-main.svg)

## Từ viết tắt

- **API** (Application Programming Interface) — giao diện lập trình ứng dụng: cách ứng dụng của Uber gọi các dịch vụ phía sau.
- **ATG** (Advanced Technologies Group) — nhóm công nghệ tiên tiến: một mảng của Uber mà bài nguồn chỉ nêu tên, như một trong các mảng kinh doanh mới.

## Đọc hình

1. **Thế hệ một: tự lớn lên.** Năm 2014, kiến trúc Uber có hai dịch vụ chính: dịch vụ điều phối (dispatch) nối người đi với tài xế, và dịch vụ API giữ dữ liệu lâu dài về người dùng và chuyến đi.
2. **Thế hệ hai: một cổng ôm hết.** Uber theo kiến trúc microservice từ rất sớm. Theo nguồn, tới năm 2019 các sản phẩm của Uber chạy trên hơn 2.200 microservice, hệ quả của quyết định đó.
3. **Thế hệ ba: tự phục vụ, phi tập trung, chia tầng.** Từ đầu năm 2018, Uber có những mảng kinh doanh hoàn toàn mới và nhiều ứng dụng mới: vận tải hàng hóa (Freight), ATG, Elevate, giao đồ tạp hóa và hơn nữa. Mục tiêu mới dẫn tới thế hệ thứ ba.

Thứ đổi qua ba thế hệ là ai làm cổng: ban đầu cổng là một dịch vụ, rồi một cổng chung cho mọi thứ, rồi một lớp tự phục vụ và phi tập trung. Bài nguồn không nói cụ thể các đội làm gì trên lớp đó.

## Giới hạn cần nhớ

Bài nguồn chỉ nêu tên ba thế hệ và bối cảnh của mỗi thế hệ; nó không mô tả cổng thế hệ hai hay thế hệ ba làm việc thế nào. Mốc thời gian của nguồn không theo thứ tự: con số 2.200 microservice là của năm 2019, còn thế hệ ba bắt đầu "từ đầu năm 2018". Nguồn không nói vì sao cổng ôm hết không còn hợp; lời giải thích ở phần dưới là của người biên soạn.

## Nhìn hình thử trả lời

Uber mở thêm mảng giao đồ tạp hóa, cần vài API mới cho ứng dụng của mảng này. Với một cổng ôm hết (thế hệ hai), việc thêm các API đó vướng ở đâu, và thế hệ ba đổi điều gì?

<details>
<summary>Xem đáp án</summary>

Với một cổng ôm hết, mọi API mới đều phải đi qua cổng chung, nên đội làm mảng mới phải chờ hoặc phối hợp với đội giữ cổng. Theo bài nguồn, thế hệ ba theo hướng tự phục vụ và phi tập trung, nên đội làm mảng mới không còn phải xếp hàng chờ một đội giữ cổng chung. Bài nguồn không nói chi tiết đội đó làm gì trên cổng, nên đừng hiểu là mỗi đội viết mã riêng vào cổng.

</details>

<details>
<summary>Xem sâu hơn: vì sao một cổng chung khó theo kịp</summary>

- Một đội giữ cổng cho hàng nghìn dịch vụ dễ thành nút thắt: mọi thay đổi đều xếp hàng chờ đội đó.
- Một lỗi trong cổng chung có thể ảnh hưởng mọi sản phẩm cùng lúc.
- Chia tầng tách phần chung (xác thực, giới hạn lượt gọi) khỏi phần riêng của từng sản phẩm.

Đây là kiến thức chung của người biên soạn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/evolution-of-uber's-api-layer.md): ba thế hệ cổng API của Uber.

Đã đọc nguồn ngày 2026-10-19. Bài kỹ thuật gốc của Uber chưa được mở để đối chiếu.
Bài viết và hình được thiết kế độc lập.
