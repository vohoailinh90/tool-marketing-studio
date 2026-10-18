# Chín thuật toán dùng khắp đời sống số

**Bài nguồn nêu chín thuật toán dùng trong đời sống hằng ngày, từ công cụ tìm kiếm tới vệ tinh: sắp xếp, Dijkstra, Transformer, phân tích liên kết, RSA, phân tích thừa số nguyên, mạng nơ-ron tích chập, mã Huffman và SHA.**
Phần chữ của nguồn chỉ có tên chín thuật toán và một câu mở đầu; mô tả từng cái nằm trong ảnh mà bài này không dùng. Vì thế mỗi mô tả ngắn dưới đây lấy từ tài liệu của một thư viện phần mềm tại commit cố định.

![Ba nhóm thẻ và một khung ghi nhớ. Xếp, tìm đường và xếp hạng: sắp xếp, thuật toán Dijkstra, phân tích liên kết. Mật mã, số và nén: RSA, phân tích thừa số nguyên, mã Huffman, họ băm SHA. Học máy: Transformer, mạng nơ-ron tích chập. Khung cuối nêu ba điều cần nhớ.](../../diagrams/sd-10-024-main.svg)

## Từ viết tắt

- **RSA** (Rivest-Shamir-Adleman) — tên một thuật toán mã hóa khóa công khai, đặt theo ba tác giả.
- **SHA** (Secure Hash Algorithm) — họ thuật toán băm: biến dữ liệu bất kỳ thành một chuỗi cố định; SHA-256 là một loại trong họ này.
- **CNN** (Convolutional Neural Network) — mạng nơ-ron tích chập: loại mạng nơ-ron đặc biệt mạnh với ảnh.
- **JDK** (Java Development Kit) — bộ công cụ phát triển Java: gói gồm thư viện chuẩn và công cụ để viết, chạy chương trình Java; bài trích mã nguồn của nó để đối chiếu.

## Đọc hình

**Điều nguồn nói.** Các thuật toán trong hình là những thuật toán dùng nhiều nhất trong đời sống hằng ngày: trong công cụ tìm kiếm trên Internet, mạng xã hội, WiFi, điện thoại di động và cả vệ tinh. Nguồn liệt kê chín thuật toán theo thứ tự: sắp xếp, thuật toán Dijkstra, Transformer, phân tích liên kết, RSA, phân tích thừa số nguyên, CNN, mã Huffman, SHA.

**Xếp, tìm đường và xếp hạng.**
- Sắp xếp (sorting): xếp các phần tử theo thứ tự. Tài liệu Python nói thuật toán Timsort mà Python dùng tận dụng được thứ tự có sẵn trong dữ liệu, và phép sắp xếp của Python là ổn định (các bản ghi cùng khóa giữ nguyên thứ tự ban đầu). Mã JDK ghi sắp xếp mảng số dùng Dual-Pivot Quicksort.
- Thuật toán Dijkstra: thư viện NetworkX dùng phương pháp Dijkstra để tính đường đi có trọng số ngắn nhất giữa hai nút của một đồ thị.
- Phân tích liên kết (link analysis): NetworkX đặt PageRank trong nhóm này. PageRank xếp hạng các nút của đồ thị theo cấu trúc các liên kết đến; ban đầu nó được thiết kế để xếp hạng trang web.

**Mật mã, số và nén.**
- RSA: mã JDK có `RSAKeyGenParameterSpec`, tập tham số dùng để sinh một cặp khóa RSA.
- Phân tích thừa số nguyên (integer factorization): hàm `factorint(n)` của SymPy trả về từ điển các thừa số nguyên tố của số nguyên dương n cùng số lần lặp của từng thừa số.
- Mã Huffman: nguồn chỉ nêu tên; bài không có tài liệu để đối chiếu.
- SHA: mô-đun `hashlib` của Python nói nó có giao diện chung cho nhiều thuật toán băm, gồm các thuật toán băm an toàn SHA-224, SHA-256, SHA-384, SHA-512 và dòng SHA-3.

**Học máy.**
- Transformer: lớp Transformer của PyTorch hiện thực kiến trúc Transformer gốc trong bài báo "Attention Is All You Need", làm bản tham chiếu để hiểu nền tảng.
- Mạng nơ-ron tích chập (CNN): PyTorch có lớp `Conv2d`, áp phép tích chập 2D lên tín hiệu đầu vào gồm nhiều mặt phẳng; việc lớp này là một khối cơ bản của CNN là kiến thức chung của người biên soạn.

## Giới hạn cần nhớ

Nguồn không nói thuật toán nào dùng ở đâu: danh sách nơi dùng (tìm kiếm, mạng xã hội, WiFi, điện thoại, vệ tinh) chỉ là câu chung cho cả chín. Bài không gán từng thuật toán vào từng nơi, và không xếp hạng chúng. Chữ "chi phối thế giới" là lời của nguồn, bài không kiểm tra.
Các mô tả ngắn lấy từ tài liệu của thư viện (Python, JDK, NetworkX, SymPy, PyTorch), chỉ nói thư viện đó làm gì, không phải định nghĩa toán học đầy đủ. Tên "thuật toán Dijkstra" và "phân tích liên kết" ở nguồn là tên mục; bài chỉ đối chiếu một ví dụ cho mỗi tên.

## Nhìn hình trả lời

Bạn cần tìm đường đi có trọng số ngắn nhất giữa hai nút của một đồ thị. Trong chín thuật toán, cái nào lo việc đó? Cái nào xếp hạng trang web theo các liên kết đến? Và thuật toán nào nguồn nêu tên nhưng bài không có tài liệu để đối chiếu?

<details>
<summary>Xem đáp án</summary>

Thuật toán Dijkstra: tìm đường đi có trọng số ngắn nhất giữa hai nút.
Phân tích liên kết, với PageRank là ví dụ trong NetworkX: xếp hạng nút theo cấu trúc liên kết đến, ban đầu để xếp hạng trang web.
Mã Huffman: nguồn chỉ nêu tên.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có một ảnh, một đoạn mở đầu và chín tiêu đề được đánh số mà không có chữ giải thích bên dưới. Hình ở đây giữ cả chín tên và chia chúng thành ba nhóm theo họ hàng; cách chia nhóm là của bài, không phải của nguồn. Bài không dùng ảnh nguồn.
Các mô tả ngắn lấy từ tài liệu của Python, JDK, NetworkX, SymPy và PyTorch tại các commit cố định ở mục nguồn, không phải từ bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/the-9-algorithms-that-dominate-our-world.md): chín tên thuật toán và câu mở đầu.
- [Python — HOWTO sắp xếp](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/howto/sorting.rst) và [mô-đun hashlib](https://github.com/python/cpython/blob/b00a14018172652226bd6efb517af021bd03aa88/Doc/library/hashlib.rst): Timsort, sắp xếp ổn định, họ băm SHA. Đọc từ kho mã.
- [OpenJDK — Arrays](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/util/Arrays.java) và [RSAKeyGenParameterSpec](https://github.com/openjdk/jdk/blob/3104115c2a0587895997965c9e88a1181f52ee47/src/java.base/share/classes/java/security/spec/RSAKeyGenParameterSpec.java): Dual-Pivot Quicksort, tham số sinh khóa RSA. Đọc từ kho mã.
- [NetworkX — đường đi ngắn nhất](https://github.com/networkx/networkx/blob/abf2feda2252ee4e0d5a66964addf179225dfe76/networkx/algorithms/shortest_paths/weighted.py) và [PageRank](https://github.com/networkx/networkx/blob/abf2feda2252ee4e0d5a66964addf179225dfe76/networkx/algorithms/link_analysis/pagerank_alg.py): phương pháp Dijkstra, PageRank. Đọc từ kho mã.
- [SymPy — factor_](https://github.com/sympy/sympy/blob/50e68debd256f0ff52b1856bba54868e5499448e/sympy/ntheory/factor_.py): `factorint`. Đọc từ kho mã.
- [PyTorch — Transformer](https://github.com/pytorch/pytorch/blob/a0f92a5ebaafec79f18454ffab8d8a08c6255f76/torch/nn/modules/transformer.py) và [Conv2d](https://github.com/pytorch/pytorch/blob/a0f92a5ebaafec79f18454ffab8d8a08c6255f76/torch/nn/modules/conv.py): lớp Transformer gốc, tích chập 2D. Đọc từ kho mã.

Đã đọc nguồn ngày 2026-10-18. Các câu giải nghĩa RSA, SHA, CNN và JDK trong mục từ viết tắt là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu chuẩn.
Bài viết và hình được thiết kế độc lập.
