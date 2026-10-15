# JavaScript hoạt động thế nào?

**Vì sao `setTimeout(…, 0)` không chạy ngay, và vì sao một vòng lặp dài làm cả trang đứng?** Câu trả lời nằm ở cách JavaScript chia việc: một luồng, một ngăn xếp và một hàng đợi.

![Bốn khung dọc: engine đọc và biên dịch mã, còn trình duyệt hoặc Node.js cấp timer, mạng và DOM; mã chạy trên một luồng với một ngăn xếp, mỗi việc chạy trọn vẹn và một vòng lặp đồng bộ dài làm mọi thứ đứng; việc chờ như mạng hay timer do môi trường lo, khi xong thì callback xếp hàng và chỉ chạy khi ngăn xếp rỗng; hàng đợi promise chạy hết trước rồi mới tới callback timer. Bất đồng bộ không có nghĩa là song song.](../../diagrams/sd-01-014-main.svg)

## Đọc hình

**1. Engine và môi trường.** Mã chạy nhờ hai phần: *engine* (V8 trong Chrome và Node.js) đọc, phân tích và thực thi mã; *môi trường chủ* (trình duyệt, Node.js) cấp những thứ ngoài ngôn ngữ như timer, mạng, DOM. Nói "JavaScript là ngôn ngữ thông dịch" chỉ đúng một phần: thông dịch hay biên dịch là cách một engine được cài đặt, và engine hiện đại biên dịch mã ngay lúc chạy (JIT).

**2. Một luồng, một ngăn xếp.** Mã của một ngữ cảnh chạy trên một luồng, với một ngăn xếp lời gọi. Mỗi việc chạy trọn vẹn rồi mới đến việc khác, nên hàm đang chạy không bị mã khác chen ngang. Đổi lại, một vòng lặp đồng bộ dài chặn mọi thứ, kể cả thao tác của người dùng.

**3. Chờ xong thì xếp hàng.** Chờ mạng, timer hay tệp không giữ ngăn xếp: môi trường lo phần chờ, khi xong thì đặt callback vào hàng đợi. Vòng lặp sự kiện chỉ lấy việc kế tiếp khi ngăn xếp rỗng.

**4. Promise đi trước timer.** Callback của promise nằm ở hàng đợi riêng (microtask) và chạy hết trước khi vòng lặp sang việc kế của hàng đợi chính, như callback của timer.

## Giới hạn cần nhớ

Bất đồng bộ không có nghĩa là song song: callback vẫn chạy lần lượt trên cùng luồng đó, nên việc tính toán nặng phải chia nhỏ hoặc đưa sang worker. `setTimeout(fn, 0)` cũng chỉ hứa chờ tối thiểu một khoảng ngắn rồi xếp callback vào hàng đợi, không hứa chạy ngay.

## Nhìn hình thử trả lời

Đoạn mã dưới đây in ra theo thứ tự nào?

```js
console.log("A");
setTimeout(() => console.log("B"), 0);
Promise.resolve().then(() => console.log("C"));
console.log("D");
```

<details>
<summary>Xem đáp án</summary>

A, D, C, B. Hai dòng đồng bộ (A, D) chạy trước vì ngăn xếp chưa rỗng. Khi ngăn xếp rỗng, hàng đợi promise chạy hết (C), rồi mới tới callback của timer (B).

</details>

<details>
<summary>Xem sâu hơn</summary>

- **Đặc điểm của ngôn ngữ:** hàm là giá trị (gán vào biến, truyền đi, trả về); kiểu của biến quyết định lúc chạy chứ không khai báo trước; đối tượng kế thừa qua prototype, còn `class` là cú pháp viết gọn trên cùng cơ chế đó; bộ nhớ không còn tham chiếu tới được sẽ được thu gom tự động, nhưng đối tượng vẫn bị giữ (ví dụ trong bộ nhớ đệm toàn cục) thì không bị thu gom.
- **TypeScript:** tập mở rộng cú pháp của JavaScript, thêm kiểu; kiểu được kiểm lúc biên dịch rồi bị bỏ đi. Đoạn JavaScript hợp lệ vẫn có thể báo lỗi kiểu trong TypeScript, chẳng hạn gán chuỗi cho biến vừa nhận số.
- **Nhiều tầng trong V8:** gồm bộ thông dịch bytecode (Ignition) và các trình biên dịch nhanh hơn, tối ưu hơn (Sparkplug, Maglev, TurboFan); phần chạy nhiều lần được đẩy lên tầng cao hơn.
- **Node.js:** `process.nextTick` chạy trước cả hàng đợi promise. Worker (trình duyệt) và worker thread (Node.js) là ngữ cảnh riêng với ngăn xếp riêng, giao tiếp bằng tin nhắn.
- **Framework:** React, Vue hay Angular là thư viện chạy trên cùng cơ chế này; chọn framework không đổi cách engine chạy.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-javascript-work.md).
- [MDN — JavaScript execution model](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Execution_model): engine và môi trường chủ, ngăn xếp, hàng đợi, run-to-completion.
- [Node.js — Event loop, timers and nextTick](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick).
- [V8 — Launching Ignition and TurboFan](https://v8.dev/blog/launching-ignition-and-turbofan).
- [ECMAScript](https://tc39.es/ecma262/): ngôn ngữ và promise job; [HTML Standard — event loops](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops).

Đã đọc nguồn ngày 2026-10-15. Thứ tự in, độ trễ của vòng lặp đồng bộ và hành vi kiểu của TypeScript đã được chạy thử trên Node.js 22 và TypeScript 5.9; HTML Standard chưa được mở để đối chiếu trực tiếp. Bài viết và hình được thiết kế độc lập.
