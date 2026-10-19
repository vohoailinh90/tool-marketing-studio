# Chín thuật toán dùng khắp đời sống số

**Chín cái tên, chín phép thử nhỏ. Bảy thuật toán thử được bằng vài dòng Python chạy tại chỗ; hai thuật toán học máy (Transformer, mạng nơ-ron tích chập) bài chỉ đọc tài liệu của PyTorch.**
Mỗi phép thử dưới đây là một ví dụ nhỏ do bài tự chạy; tài liệu của Python, Java, NetworkX, SymPy, PyTorch và zlib dùng để đối chiếu điều mỗi thuật toán làm.

![Ba nhóm thẻ và một khung ghi nhớ. Xếp, tìm đường và xếp hạng: sắp xếp giữ nguyên thứ tự các bản ghi cùng khóa; thuật toán Dijkstra tìm đường A tới D dài 4 thay vì 5; phân tích liên kết cho nút c điểm cao nhất, nút không ai trỏ tới điểm thấp nhất. Mật mã, số và nén: RSA mã hóa 65 thành 2790 rồi giải lại ra 65; phân tích thừa số nguyên tách 3233 thành 53 và 61; mã Huffman nén abracadabra từ 88 bit xuống 23 bit; SHA-256 của abc luôn cho một chuỗi 64 ký tự thập lục phân. Học máy: Transformer và mạng nơ-ron tích chập có lớp tương ứng trong PyTorch. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-024-main.svg)

## Từ viết tắt

- **RSA** (Rivest-Shamir-Adleman) — tên một thuật toán mã hóa khóa công khai, đặt theo chữ đầu của ba tác giả.
- **SHA** (Secure Hash Algorithm) — họ thuật toán băm: biến dữ liệu bất kỳ thành một chuỗi độ dài cố định; SHA-256 là một loại trong họ này.
- **CNN** (Convolutional Neural Network) — mạng nơ-ron tích chập: loại mạng nơ-ron dùng phép tích chập, thường dùng với ảnh.

## Đọc hình

**Xếp, tìm đường và xếp hạng.**
- Sắp xếp (sorting). Thử `sorted([("b",2),("a",1),("c",2),("d",1)], key=lambda r: r[1])` ra `a, d, b, c`: hai bản ghi cùng khóa 1 giữ thứ tự cũ (a trước d), hai bản ghi cùng khóa 2 cũng vậy (b trước c). Tài liệu Python gọi đó là sắp xếp ổn định, và nói thuật toán Timsort của nó tận dụng được thứ tự có sẵn trong dữ liệu. Mã nguồn Java của OpenJDK ghi sắp xếp mảng số dùng Dual-Pivot Quicksort, một thuật toán khác.
- Thuật toán Dijkstra. Đồ thị có bốn nút, các cạnh hai chiều A-B nặng 4, A-C nặng 1, C-B nặng 2, B-D nặng 1. Đường A tới D ngắn nhất là A, C, B, D với tổng 4, ngắn hơn A, B, D với tổng 5. Hàm `dijkstra_path` của NetworkX tính đúng đường đó (chạy ra `['A', 'C', 'B', 'D']`); tài liệu thư viện nói nó dùng phương pháp Dijkstra cho đường đi có trọng số.
- Phân tích liên kết (link analysis). Bốn trang a, b, c, d; a trỏ tới b và c, b trỏ tới c, c trỏ tới a, d trỏ tới c. Tự lặp công thức PageRank (hệ số 0,85) cho điểm c khoảng 0,39, a 0,37, b 0,20, d 0,04: trang nào được nhiều trang quan trọng trỏ tới thì điểm cao, còn d không ai trỏ tới. NetworkX mô tả PageRank là phép xếp hạng nút theo cấu trúc các liên kết đến, ban đầu thiết kế để xếp hạng trang web.

**Mật mã, số và nén.**
- RSA. Ví dụ đồ chơi: chọn hai số nguyên tố 61 và 53, nhân ra 3233; khóa công khai dùng số mũ 17, khóa riêng dùng số mũ 2753. Thông điệp 65 mã hóa bằng `pow(65, 17, 3233)` ra 2790, giải bằng `pow(2790, 2753, 3233)` ra lại 65. Với số nhỏ thế này thì không an toàn chút nào; bộ tham số sinh khóa thật của Java (`RSAKeyGenParameterSpec`) có kích thước modulus tính bằng bit và số mũ công khai.
- Phân tích thừa số nguyên (integer factorization). Hàm `factorint` của SymPy trả về các thừa số nguyên tố của một số cùng số lần lặp: `factorint(360)` ra `{2: 3, 3: 2, 5: 1}`, tức 360 = 2³ × 3² × 5, và `factorint(3233)` ra `{53: 1, 61: 1}`: lấy ngược lại hai số của ví dụ RSA.
- Mã Huffman. Đếm chữ trong `abracadabra`: a 5 lần, b 2, r 2, c 1, d 1. Thuật toán gán mã ngắn cho chữ hay gặp: a là `0`, c là `100`, d là `101`, b là `110`, r là `111`; cả chuỗi hết 23 bit thay cho 88 bit nếu mỗi chữ chiếm 8 bit. Tài liệu thuật toán của zlib nói dữ liệu nén bằng deflate dùng cây Huffman cho các byte và độ dài lặp.
- SHA. `hashlib.sha256(b"abc").hexdigest()` luôn ra một chuỗi 64 ký tự thập lục phân, bắt đầu bằng `ba7816bf`, dù dữ liệu vào dài hay ngắn. Tài liệu `hashlib` của Python nói nó có SHA-224, SHA-256, SHA-384, SHA-512 và dòng SHA-3.

**Học máy.**
- Transformer. Lớp `Transformer` của PyTorch hiện thực kiến trúc gốc trong bài báo "Attention Is All You Need", làm bản tham chiếu để hiểu nền tảng; mặc định có 8 đầu chú ý và 6 lớp mã hóa cùng 6 lớp giải mã.
- Mạng nơ-ron tích chập (CNN). Lớp `Conv2d` của PyTorch áp phép tích chập 2D lên tín hiệu đầu vào gồm nhiều mặt phẳng; việc nó là khối cơ bản của CNN là kiến thức chung của người biên soạn.

## Giới hạn cần nhớ

Các phép thử chỉ minh họa ý tưởng, không phải cách dùng thật: RSA với số nhỏ không bảo mật gì, Huffman ở đây chỉ tính độ dài mã chứ không ghi tệp, và PageRank là bản lặp tự viết cho đồ thị bốn nút. Bài không nói thuật toán nào dùng ở sản phẩm nào, không xếp hạng chín thuật toán và không đánh giá độ quan trọng của chúng. Phần học máy chỉ đọc tài liệu, chưa chạy mô hình nào.

## Nhìn hình trả lời

Bạn cần một dấu vân tay (chuỗi băm) để nhận dạng một tệp mà dù tệp dài hay ngắn cũng cho chuỗi cùng độ dài. Thuật toán nào trong chín cái làm việc đó? Và trong ví dụ Dijkstra, vì sao đường A, B, D (tổng 5) không được chọn dù ít nút hơn?

<details>
<summary>Xem đáp án</summary>

Họ băm SHA (ví dụ SHA-256): dữ liệu vào bất kỳ, chuỗi ra luôn dài 64 ký tự thập lục phân.
Dijkstra tìm đường có tổng trọng số nhỏ nhất, không phải ít nút nhất: A, C, B, D có tổng 1 + 2 + 1 = 4, nhỏ hơn 4 + 1 = 5 của A, B, D.

</details>

<details>
<summary>Xem sâu hơn: cách chạy các phép thử</summary>

Sắp xếp, RSA (`pow` với ba tham số), Huffman (tự viết bằng `heapq`) và SHA chạy bằng thư viện chuẩn của Python 3.13. Dijkstra chạy bằng NetworkX, phân tích thừa số bằng SymPy; PageRank là vòng lặp công thức với hệ số 0,85 và 100 lần lặp. Khi nhiều chữ cùng tần số (c và d, b và r), mã gán cho chúng có thể khác tùy cách chọn, nhưng tổng độ dài vẫn là 23 bit; đó là tổng nhỏ nhất của một bộ mã tiền tố cho chuỗi này (kiến thức chung của người biên soạn).

Chín thuật toán này không cùng loại: sắp xếp, Dijkstra và Huffman là thuật toán cổ điển cho một bài toán rõ ràng; RSA và SHA dựa vào toán học của số và hàm một chiều; Transformer và CNN là kiến trúc mô hình cần huấn luyện. Vì vậy "chạy một ví dụ nhỏ" chỉ làm được với nhóm đầu.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/the-9-algorithms-that-dominate-our-world.md): chỉ lấy chín tên thuật toán; ví dụ và lời giải thích trong bài là của bài này.
- [Python — HOWTO sắp xếp](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/howto/sorting.rst) và [mô-đun hashlib](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/hashlib.rst): Timsort, sắp xếp ổn định, họ băm SHA. Đọc từ kho mã.
- [OpenJDK — Arrays](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/Arrays.java) và [RSAKeyGenParameterSpec](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/security/spec/RSAKeyGenParameterSpec.java): Dual-Pivot Quicksort, tham số sinh khóa RSA. Đọc từ kho mã.
- [NetworkX — đường đi ngắn nhất](https://github.com/networkx/networkx/blob/abf2feda2252ee4e0d5a66964addf179225dfe76/networkx/algorithms/shortest_paths/weighted.py) và [PageRank](https://github.com/networkx/networkx/blob/abf2feda2252ee4e0d5a66964addf179225dfe76/networkx/algorithms/link_analysis/pagerank_alg.py): phương pháp Dijkstra, PageRank. Đọc từ kho mã.
- [SymPy — factor_](https://github.com/sympy/sympy/blob/50e68debd256f0ff52b1856bba54868e5499448e/sympy/ntheory/factor_.py): `factorint`. Đọc từ kho mã.
- [zlib — thuật toán nén](https://github.com/madler/zlib/blob/767c4c947852e143f582c85f14cf573411df1b35/doc/algorithm.txt): deflate dùng cây Huffman. Đọc từ kho mã.
- [PyTorch — Transformer](https://github.com/pytorch/pytorch/blob/a0f92a5ebaafec79f18454ffab8d8a08c6255f76/torch/nn/modules/transformer.py) và [Conv2d](https://github.com/pytorch/pytorch/blob/a0f92a5ebaafec79f18454ffab8d8a08c6255f76/torch/nn/modules/conv.py): lớp Transformer gốc, tích chập 2D. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-19. Các phép thử do người biên soạn chạy ngày 2026-10-19; các câu giải nghĩa RSA, SHA và CNN trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.
