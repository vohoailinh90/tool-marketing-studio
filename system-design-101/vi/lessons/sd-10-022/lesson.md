# Mệnh lệnh, hàm và hướng đối tượng: ba mô hình lập trình chính

**Một bài toán nhỏ, ba cách viết: tính tổng bình phương các số chẵn trong 1 đến 6 (đáp án 56). Mỗi cách là một mô hình lập trình khác nhau.**
Bài tự viết ba đoạn mã Python cho cùng bài toán, chạy cả ba đều ra 56, rồi đọc từng cách qua hướng dẫn lập trình hàm của Python.

![Ba nhóm thẻ và một khung ghi nhớ. Mệnh lệnh: một biến total bắt đầu bằng 0; vòng lặp đi qua từng số; câu lệnh điều kiện chọn số chẵn rồi cộng bình phương vào total. Hàm: hàm is_even trả đúng hoặc sai; hàm square trả bình phương; sum, map và filter nối các hàm đó, không đổi biến nào. Hướng đối tượng: một đối tượng giữ total bên trong; phương thức add nhận từng số và tự cập nhật; mã gọi add lặp lại rồi đọc total. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-022-main.svg)

## Từ viết tắt

- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ để mô tả dữ liệu muốn lấy từ cơ sở dữ liệu; bài chỉ dùng nó làm ví dụ của lối khai báo.

## Đọc hình

**Mệnh lệnh (imperative).** Chương trình là danh sách lệnh bảo máy làm gì, theo thứ tự.

```python
total = 0
for n in numbers:
    if n % 2 == 0:
        total += n * n
```

Có một biến `total` đổi giá trị sau mỗi vòng; ta nhìn thấy từng bước (lặp, kiểm tra, cộng). Tài liệu Python gọi lối này là thủ tục (procedural) và nêu C, Pascal, thậm chí shell Unix là ví dụ; bài coi "mệnh lệnh" và "thủ tục" là cùng một họ.

**Hàm (functional).** Bài toán được chia thành các hàm nhỏ, mỗi hàm chỉ nhận đầu vào và trả đầu ra.

```python
def is_even(n):
    return n % 2 == 0
def square(n):
    return n * n
total = sum(map(square, filter(is_even, numbers)))
```

Không biến nào bị đổi: `filter` giữ số chẵn, `map` bình phương, `sum` cộng. `filter` và `map` là hàm bậc cao, vì chúng nhận một hàm làm đầu vào. Tài liệu Python nói phong cách hàm không khuyến khích hàm có tác dụng phụ (side effect), tức đổi trạng thái hay gây thay đổi không thấy qua giá trị trả về; hàm không có tác dụng phụ nào gọi là "thuần" (purely functional). Cũng theo tài liệu đó, mỗi hàm nhỏ dễ kiểm thử hơn vì chỉ cần tạo đầu vào rồi so đầu ra.

**Hướng đối tượng (object-oriented).** Chương trình thao tác trên các đối tượng, mỗi đối tượng có trạng thái bên trong và các phương thức để hỏi hoặc sửa trạng thái đó.

```python
class SquareSum:
    def __init__(self):
        self.total = 0
    def add(self, n):
        if n % 2 == 0:
            self.total += n * n

acc = SquareSum()
for n in numbers:
    acc.add(n)
```

Trạng thái `total` nằm trong đối tượng; bên ngoài chỉ gọi `add` rồi đọc `acc.total`. Với bài toán nhỏ này cách viết dài nhất, nhưng khi trạng thái và các thao tác trên nó gắn bó (một tài khoản, một phiếu mượn), gom chúng vào một đối tượng giúp mã dễ tìm.

**Chúng không loại trừ nhau.** Tài liệu Python nói Lisp, C++ và Python là ngôn ngữ đa mô hình: cùng một chương trình có thể có phần giao diện hướng đối tượng còn phần xử lý theo lối thủ tục hoặc hàm. Tài liệu còn kể một lối thứ tư, khai báo (declarative), với SQL làm ví dụ: ta mô tả dữ liệu muốn lấy, còn công cụ tự quyết cách tính.

## Giới hạn cần nhớ

Ba đoạn mã chỉ cho thấy cách viết khác nhau, không đo tốc độ hay độ rõ, và bài toán này quá nhỏ để chọn mô hình thắng; bài không nói mô hình nào tốt hơn. Cách xếp C, Pascal, Smalltalk, Java và các ngôn ngữ khác vào từng mô hình là của tài liệu Python, không phải phân loại chính thức; nhiều ngôn ngữ làm được nhiều mô hình. Bài không kiểm tra các tính năng khác thường gắn với từng mô hình (kế thừa, đa hình, đệ quy).

## Nhìn hình trả lời

Hàm `square(n)` chỉ trả `n * n` và không đụng biến nào bên ngoài. Tài liệu Python gọi hàm như vậy là gì? Còn `total += n * n` trong vòng lặp thuộc mô hình nào, và vì sao đoạn mã đó khó đưa vào một bài kiểm thử riêng hơn `square`?

<details>
<summary>Xem đáp án</summary>

`square` là hàm thuần (purely functional): không có tác dụng phụ, đầu ra chỉ phụ thuộc đầu vào.
`total += n * n` là lối mệnh lệnh (thủ tục): nó đổi một biến đang sống ngoài vòng lặp, nên kiểm thử phải dựng và đọc lại trạng thái đó. Với `square` chỉ cần đưa 3 vào rồi so với 9.

</details>

<details>
<summary>Xem sâu hơn: cùng bài toán, ba trạng thái</summary>

Trong ba đoạn mã, trạng thái có ba chỗ ở. Bản mệnh lệnh để nó ở biến `total` của chương trình. Bản hướng đối tượng để nó ở thuộc tính của một đối tượng, và chỉ phương thức `add` đổi nó. Bản hàm không giữ trạng thái chung: kết quả của mỗi hàm chảy sang hàm kế tiếp.

Tài liệu Python nói thêm rằng chương trình Python viết theo lối hàm thường không đi đến cực đoan: hàm vẫn dùng phép gán cho biến cục bộ bên trong, chỉ bên ngoài trông như hàm thuần. Vì vậy đoạn `sum(map(...))` trên đây là một cách viết, không phải luật.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/imperative-vs-functional-vs-object-oriented-programming.md): chỉ lấy tên ba mô hình; ví dụ, mã và lời giải thích trong bài là của bài này.
- [Python — hướng dẫn lập trình hàm](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/howto/functional.rst): bốn lối thủ tục, khai báo, hướng đối tượng, hàm; hàm thuần; tác dụng phụ; ngôn ngữ đa mô hình; `map` và `filter`; lợi ích kiểm thử. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-19. Ba đoạn mã được chạy ngày 2026-10-19 và cùng in 56. Câu giải nghĩa SQL trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.
