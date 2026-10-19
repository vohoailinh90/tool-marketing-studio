# Mười nguyên tắc viết mã tốt để nâng chất lượng mã

**Một hàm tính phí trả muộn viết cẩu thả, rồi viết lại; mười nguyên tắc hiện ra từng cái ở những chỗ cụ thể được sửa.**
Bài tự viết cả hai bản bằng Python, chạy ba ca kiểm thử trên bản mới, rồi đối chiếu vài nguyên tắc với PEP 8, hướng dẫn Java của Google, tài liệu `unittest`, hướng dẫn lập trình hàm của Python và bảng kiểm tra kiểm soát đầu vào của OWASP.

![Ba nhóm thẻ và một khung ghi nhớ, theo mười nguyên tắc đánh số. Đọc được và bền: một theo quy ước, tên gọi rõ và hằng số viết hoa; hai chú thích nói vì sao; ba báo lỗi thay vì nuốt lỗi; bốn mỗi hàm một việc, thêm loại thành viên bằng cách thêm dữ liệu. Dễ kiểm thử và dễ đổi: năm hàm gọn với ba ca kiểm thử; sáu một hàm che giấu bảng giảm giá; bảy hai loại thành viên chỉ cần một bảng, không cần lớp; tám bỏ biến toàn cục. Giữ lâu dài: chín viết kiểm thử rồi đổi từng bước nhỏ; mười kiểm đầu vào ở biên. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-028-main.svg)

## Từ viết tắt

- **PEP** (Python Enhancement Proposal) — đề xuất cải tiến Python: văn bản đề xuất một thay đổi hay quy ước cho Python; PEP 8 là văn bản quy ước viết mã Python.
- **SOLID** (Single, Open, Liskov, Interface, Dependency) — năm nguyên tắc thiết kế mã hướng đối tượng, mỗi chữ cái là chữ đầu của một nguyên tắc: trách nhiệm đơn (Single responsibility), mở/đóng (Open/closed), thay thế Liskov (Liskov substitution), tách giao diện (Interface segregation), đảo ngược phụ thuộc (Dependency inversion).
- **OWASP** (Open Worldwide Application Security Project) — dự án mở về an toàn ứng dụng: tổ chức phát hành các bảng kiểm tra bảo mật cho lập trình viên.
- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; bài chỉ nhắc nó khi nói về kiểm đầu vào.

## Đọc hình

Bản cẩu thả của hàm tính phí trả muộn (mỗi ngày muộn 5000 đồng, hội viên "vip" giảm một nửa):

```python
fee = 0
def calc(d, m):
    global fee
    # nhân d với 5000
    try:
        fee = d * 5000
        if m == "vip":
            fee = fee / 2
    except:
        fee = 0
    return fee
```

Bản viết lại:

```python
LATE_FEE_PER_DAY = 5000  # đồng mỗi ngày, theo quy định của thư viện
MEMBER_DISCOUNT = {"vip": 0.5}

def late_fee(days_late, member_type="standard"):
    """Phí trả muộn của một phiếu mượn, tính bằng đồng."""
    if days_late < 0:
        raise ValueError("days_late must not be negative")
    discount = MEMBER_DISCOUNT.get(member_type, 1.0)
    return days_late * LATE_FEE_PER_DAY * discount
```

**Đọc được và bền.**
1. Theo quy ước viết mã. PEP 8 mở đầu bằng ý: mã được đọc nhiều hơn được viết, và hướng dẫn nhằm làm mã dễ đọc, nhất quán. Nó cũng nói hằng số thường định nghĩa ở mức mô-đun và viết toàn chữ hoa nối bằng dấu gạch dưới, nên `5000` chôn trong phép nhân thành `LATE_FEE_PER_DAY`, và `calc`, `d`, `m` thành `late_fee`, `days_late`, `member_type`. Với Java, hướng dẫn của Google tự giới thiệu là định nghĩa đầy đủ chuẩn viết mã Java của hãng, và chỉ mã theo đúng các quy tắc trong đó mới được gọi là "theo Google Style".
2. Tài liệu và chú thích. Chú thích `# nhân d với 5000` chỉ lặp điều mã đã nói; PEP 8 gọi chú thích nêu điều hiển nhiên là gây xao nhãng. Bản mới nói vì sao: mức 5000 là quy định của thư viện, kèm một dòng mô tả hàm. PEP 8 cũng dặn: chú thích mâu thuẫn với mã còn tệ hơn không có chú thích, nên khi mã đổi phải sửa chú thích.
3. Vững vàng. `except:` trống nuốt mọi lỗi: `calc("2", "vip")` trả về 0 như thể không phải trả đồng nào, trong khi đầu vào sai. PEP 8 nói `except:` trống bắt cả `SystemExit` và `KeyboardInterrupt` và có thể che giấu vấn đề khác. Bản mới từ chối số ngày âm bằng `ValueError`; với `"2"` phép so sánh `"2" < 0` tự ném `TypeError`, nên lỗi hiện ra thay vì bị nuốt.
4. Theo nguyên tắc SOLID. Hàm mới chỉ làm một việc (tính phí), gần ý trách nhiệm đơn; muốn thêm loại hội viên thì thêm một dòng vào `MEMBER_DISCOUNT` mà không sửa thân hàm, gần ý mở cho mở rộng, đóng cho sửa đổi. Cách đọc SOLID này là của người biên soạn, và bài không kiểm tra cả năm nguyên tắc.

**Dễ kiểm thử và dễ đổi.**
5. Dễ kiểm thử. Hàm mới chỉ phụ thuộc đầu vào và bảng `MEMBER_DISCOUNT` mà ta coi là hằng (không sửa khi chạy; muốn chắc hơn thì truyền bảng vào làm tham số), nên dễ viết vài ca kiểm thử ngắn; ba ca minh họa (chưa phải bộ kiểm thử đầy đủ, còn thiếu số 0, số lẻ, loại hội viên lạ): khách thường 2 ngày trả 10000, hội viên "vip" 2 ngày trả 5000, và `late_fee(-1)` phải ném `ValueError`. Tài liệu `unittest` nói một test case kiểm tra phản hồi cụ thể cho một bộ đầu vào, và `assertRaises` kiểm tra có ngoại lệ. Bản cũ khó kiểm thử hơn vì kết quả còn nằm lại ở biến toàn cục `fee`.
6. Trừu tượng. Bên gọi chỉ cần biết `late_fee(số_ngày, loại)`; bảng giảm giá nằm sau hàm và đổi được mà bên gọi không biết. Mức vừa phải ở đây là một hàm cộng một bảng, chưa cần gì lớn hơn.
7. Dùng mẫu thiết kế nhưng đừng thiết kế quá tay. Hai loại hội viên chỉ cần một từ điển. Dựng một lớp chính sách phí cho mỗi loại cùng một lớp cha (mẫu chiến lược) sẽ thêm khoảng bốn lớp mà chưa mua được gì. Khi số quy tắc và chỗ khác nhau đủ lớn thì mẫu đó mới đáng; đây là nhận định của người biên soạn.
8. Bớt phụ thuộc toàn cục. Bản cũ ghi kết quả vào `fee` toàn cục sau mỗi lần gọi; gọi hai nơi cùng lúc là dẫm lên nhau. Bản mới chỉ đọc hằng số và trả kết quả. Hướng dẫn lập trình hàm của Python nói phong cách hàm không khuyến khích hàm có tác dụng phụ, tức làm đổi trạng thái nội bộ hoặc có tác động không thấy qua giá trị trả về.

**Giữ lâu dài.**
9. Tái cấu trúc liên tục. Từ bản cũ sang bản mới nên đi bằng bước nhỏ: viết trước vài ca kiểm thử cho điều cần giữ, đổi tên, bỏ biến toàn cục, bỏ `except:` trống, chạy lại kiểm thử sau mỗi bước. Cách làm này là của người biên soạn; bài không đo nợ kỹ thuật.
10. Bảo mật là ưu tiên hàng đầu. Bảng kiểm tra kiểm soát đầu vào của OWASP nói hãy kiểm cả cú pháp (kiểu, định dạng) lẫn ngữ nghĩa (giá trị có hợp lý cho thao tác không), và với số thì kiểm kiểu, định dạng, giá trị nhỏ nhất và lớn nhất. Từ chối ngày âm là một nửa của quy tắc đó; hàm thật còn nên chặn cả cận trên. Bảng kiểm tra cũng dặn kiểm đầu vào không thay cho các biện pháp khác, như dùng truy vấn tham số hóa với SQL.

## Giới hạn cần nhớ

Hàm này đủ nhỏ để làm ví dụ, và vì nhỏ nên không đo được chuyện mở rộng hay bảo trì lâu dài: các nhận định về SOLID, mẫu thiết kế và tái cấu trúc là của người biên soạn. Bài không nói nguyên tắc nào quan trọng nhất, không nói theo mức nào là đủ, và không kiểm tra ngôn ngữ khác ngoài Python và phần giới thiệu của chuẩn Java của Google. Ba ca kiểm thử chỉ chứng minh ba trường hợp đó.

## Nhìn hình trả lời

Một đồng nghiệp thêm loại hội viên "gold" giảm 30%. Với bản mới cần sửa chỗ nào, và vì sao không cần chạm vào thân hàm? Và `late_fee("2")` làm gì, so với `calc("2", "vip")` của bản cũ?

<details>
<summary>Xem đáp án</summary>

Thêm một dòng `"gold": 0.7` vào `MEMBER_DISCOUNT` (và một ca kiểm thử mới); thân hàm chỉ tra bảng nên không đổi.
`late_fee("2")` ném `TypeError` ngay khi so `"2" < 0`, nên lỗi hiện ra. `calc("2", "vip")` bắt lỗi bằng `except:` trống và trả về 0, che đi đầu vào sai.

</details>

<details>
<summary>Xem sâu hơn: ba ca kiểm thử chạy được</summary>

```python
import unittest

class LateFeeTest(unittest.TestCase):
    def test_standard_member_pays_full_rate(self):
        self.assertEqual(late_fee(2), 10000)
    def test_vip_pays_half(self):
        self.assertEqual(late_fee(2, "vip"), 5000)
    def test_negative_days_are_rejected(self):
        with self.assertRaises(ValueError):
            late_fee(-1)
```

Chạy ngày 2026-10-19 với Python 3.13.16: ba ca đều qua. `calc(2, "vip")` ra 5000.0, còn `calc("2", "vip")` và `calc(None, "vip")` đều ra 0. Mười nguyên tắc không độc lập: tên rõ, hàm gọn và kiểm thử nâng đỡ nhau, nên hình chỉ nêu chỗ nổi bật nhất của từng nguyên tắc trong ví dụ này.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/10-good-coding-principles-to-improve-code-quality.md): chỉ lấy tên mười nguyên tắc và thứ tự; ví dụ, mã và lời giải thích trong bài là của bài này.
- [Python — PEP 8](https://github.com/python/peps/blob/6068058b896441388bbf22f2607ab681193f6a3d/peps/pep-0008.rst): mã được đọc nhiều hơn được viết, hằng số viết hoa, chú thích hiển nhiên và chú thích lỗi thời, `except:` trống. Đọc từ kho mã.
- [Google — Java Style Guide](https://github.com/google/styleguide/blob/f43b95b083a5e52c85fcbb9e7e76cbd5e1c2b3f8/javaguide.html): định nghĩa chuẩn viết mã Java của Google. Đọc từ kho mã.
- [Python — unittest](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/unittest.rst) và [hướng dẫn lập trình hàm](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/howto/functional.rst): test case, `assertRaises`; hàm không tác dụng phụ. Đọc từ kho mã.
- [OWASP — Input Validation Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/d89285c7bfc3f24fa79881407c89a85bf6d17272/cheatsheets/Input_Validation_Cheat_Sheet.md): kiểm cú pháp và ngữ nghĩa, giới hạn của số, kiểm đầu vào không thay truy vấn tham số hóa. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-19. Mã được chạy ngày 2026-10-19; các câu giải nghĩa PEP, SOLID, OWASP và SQL trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.
