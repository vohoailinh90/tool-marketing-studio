# JavaScript hoạt động thế nào?

**JavaScript chạy từng việc một, nhưng vẫn lo được nhiều việc đang chờ.** Hiểu engine, call stack, hàng đợi và event loop giải thích vì sao trang không đứng khi chờ mạng, và vì sao một vòng lặp dài lại làm trang đứng.

![Năm khung dọc: engine đọc mã thành bytecode và JIT tối ưu đoạn hay chạy; call stack chạy mã từng việc một nên việc dài làm trang đứng; môi trường như trình duyệt hoặc Node lo timer, mạng và sự kiện; hai hàng đợi gồm microtask cho promise chạy trước và task cho setTimeout và sự kiện; event loop lấy việc kế tiếp khi stack rỗng và chạy hết microtask trước. Ví dụ trong bài in A, D, C, B.](../../diagrams/sd-01-014-main.svg)

## Đọc hình

**1. Engine.** Trình duyệt hoặc Node có một engine JavaScript (như V8). Nó đọc mã thành dạng trung gian (bytecode) rồi chạy; đoạn chạy nhiều có thể được biên dịch tối ưu ngay lúc đang chạy (JIT). Nên nói "JavaScript là ngôn ngữ thông dịch" chỉ đúng một phần.

**2. Call stack.** Mã của bạn chạy trên một luồng: mỗi lời gọi hàm được đẩy lên stack, xong thì bỏ ra. Một việc chạy lâu giữ stack, nên trang không phản hồi.

**3. Môi trường làm hộ.** Chờ timer, mạng hay sự kiện không phải việc của engine mà của môi trường (trình duyệt, Node). Khi xong, môi trường đưa hàm gọi lại vào một hàng đợi.

**4. Hai hàng đợi.** Hàng *microtask* chứa phần việc tiếp theo của promise (`.then`, sau `await`). Hàng *task* chứa `setTimeout` và các sự kiện.

**5. Event loop.** Khi stack rỗng, nó lấy việc kế tiếp: chạy hết microtask trước, rồi mới lấy một task.

## Giới hạn cần nhớ

"Bất đồng bộ" không có nghĩa là "song song". Mã JavaScript của bạn vẫn chạy từng việc một; chỉ việc *chờ* được giao cho môi trường. Việc nặng về tính toán nên đưa ra khỏi luồng chính, ví dụ bằng Web Worker hoặc worker thread của Node. Thứ tự hàng đợi do chuẩn quy định, còn cách tối ưu thì tùy engine.

## Nhìn hình thử trả lời

```js
console.log('A');
setTimeout(() => console.log('B'), 0);
Promise.resolve().then(() => console.log('C'));
console.log('D');
```

Chương trình in ra thứ tự nào?

<details>
<summary>Xem đáp án</summary>

A, D, C, B. Hai lệnh `console.log` đồng bộ chạy trước (A, D). Khi stack rỗng, microtask của promise (C) chạy trước task của `setTimeout` (B), dù độ trễ là 0.

</details>

<details>
<summary>Xem sâu hơn</summary>

- **Kiểu động:** biến không khai báo kiểu trước, giá trị mới mang kiểu; kiểu có thể đổi khi chạy. TypeScript thêm kiểu tĩnh và bị biên dịch về JavaScript.
- **Hàm là giá trị:** có thể gán cho biến, truyền vào hàm khác, trả về từ hàm; đó là nền của hàm gọi lại.
- **Kế thừa bằng prototype:** đối tượng kế thừa từ đối tượng khác; `class` là cú pháp viết gọn trên cơ chế đó.
- **Thu gom rác:** bộ nhớ của đối tượng không còn được tham chiếu sẽ được tự thu hồi, nhưng tham chiếu bị giữ nhầm vẫn gây rò rỉ.
- **`setTimeout(..., 0)`:** không chạy ngay; nó chỉ xếp một task sau khi hết thời gian chờ và stack rỗng.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-javascript-work.md).
- [HTML Standard — Event loops](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) và [ECMAScript](https://tc39.es/ecma262/): hàng đợi và microtask.
- [MDN — Event loop](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Event_loop), [Node.js — Event loop](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick) và [Web Workers](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API).
- [V8 — Ignition và TurboFan](https://v8.dev/blog/launching-ignition-and-turbofan).
- [MDN — Kế thừa và chuỗi prototype](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Inheritance_and_the_prototype_chain), [Quản lý bộ nhớ](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Memory_management) và [TypeScript](https://www.typescriptlang.org/docs/handbook/intro.html).

Đã đọc bản nguồn ByteByteGo ngày 2026-10-13; các tài liệu nêu trên chưa được mở để đối chiếu trực tiếp trong lượt biên soạn này. Bài viết và hình được thiết kế độc lập.
