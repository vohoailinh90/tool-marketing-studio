# SSH hoạt động thế nào? Ba lớp của giao thức

**SSH gồm ba giai đoạn chạy chồng lên nhau trên một kết nối TCP: lớp truyền tải dựng đường mã hóa và cho máy khách nhận ra khóa của máy chủ, lớp xác thực cho máy chủ biết ai đang đăng nhập, lớp kết nối chia đường đó thành nhiều kênh. Nhiều kênh vẫn chỉ cần một kết nối TCP và một lần xác thực.**
Bài dựng một máy chủ và một máy khách SSH bằng thư viện Python `asyncssh` trên `127.0.0.1` để xem từng lớp xảy ra, rồi đối chiếu với tài liệu của OpenSSH. Bài không nhắc lại chuyện khóa SSH ([bài sd-14-014](../sd-14-014/lesson.md)) hay chữ ký số ([bài sd-14-015](../sd-14-015/lesson.md)), và không dùng nội dung các RFC vì không đọc được chúng.

![Bốn thẻ xếp dọc, nối bằng mũi tên. Kết nối TCP: một ổ cắm mạng giữa hai máy. Một, lớp truyền tải: trao khóa, mã hóa, kiểm khóa máy chủ. Hai, lớp xác thực: máy chủ kiểm người dùng, trong đường đã mã hóa. Ba, lớp kết nối: chia thành nhiều kênh: lệnh, chuyển tiếp cổng. Khung cuối ghi bốn điều quan sát khi chạy thử: trên dây chỉ thấy phiên bản và tên thuật toán; khóa máy chủ lạ làm máy khách ngắt trước khi xác thực; khóa lạ hoặc mật khẩu khi máy chủ không bật bị từ chối ở lớp xác thực; ba kênh cùng lúc vẫn là một kết nối TCP và một lần xác thực.](../../diagrams/sd-14-024-main.svg)

## Từ viết tắt

- **SSH** (Secure SHell) — vỏ lệnh an toàn: giao thức đăng nhập và chạy lệnh trên máy khác qua mạng không đáng tin; OpenSSH là một bộ phần mềm cài đặt nó.
- **TCP** (Transmission Control Protocol) — giao thức điều khiển truyền tải: giao thức tạo một kết nối hai chiều giữa hai máy; SSH chạy bên trên một kết nối như vậy.
- **MAC** (Message Authentication Code) — mã xác thực thông điệp: đoạn dữ liệu đi kèm gói tin để bên nhận phát hiện gói bị sửa; không phải địa chỉ phần cứng.
- **SHA** (Secure Hash Algorithm) — họ thuật toán băm: biến dữ liệu thành một chuỗi cố định; SHA-256 dùng để tính dấu vân tay của khóa máy chủ.
- **RFC** (Request for Comments) — "đề nghị bình luận": loạt tài liệu kỹ thuật đánh số của cộng đồng Internet; nhiều RFC là tiêu chuẩn.
- **IETF** (Internet Engineering Task Force) — nhóm đặc nhiệm kỹ thuật Internet: cộng đồng soạn các tiêu chuẩn Internet và công bố chúng dưới dạng RFC.

## Đọc hình

Các lần thử dùng `asyncssh` 2.24.1 (Python 3.13) cho cả máy chủ lẫn máy khách, khóa tạm, cổng ngẫu nhiên. Mọi con số là một lần đo trên máy biên soạn.

**Kết nối TCP.** SSH chạy trên một kết nối TCP thường. Hai bên mở nó rồi gửi nhau một dòng chữ trơn, `SSH-2.0-AsyncSSH_2.24.1`. Tôi đặt giữa hai bên một bộ chuyển tiếp tự viết (đếm kết nối, ghi byte) và thấy dòng đó mở đầu luồng byte của cả hai chiều.

**1 · Truyền tải.** Thương lượng, trao khóa, rồi mọi thứ sau đó được mã hóa.

- *Thương lượng.* Mỗi bên đưa danh sách thuật toán và chọn cái cả hai có. Mặc định thư viện chọn `mlkem768x25519-sha256` để trao khóa và `chacha20-poly1305@openssh.com` để mã hóa; ở cột MAC nó báo lại chính tên thuật toán mã hóa, còn khi ép dùng `aes256-ctr` thì có MAC riêng `hmac-sha2-256`. Khi máy khách chỉ đưa `aes256-ctr` mà máy chủ chỉ có `aes128-gcm@openssh.com`, thư viện báo `KeyExchangeFailed` và máy chủ chưa kịp bắt đầu xác thực.
- *Danh tính máy chủ.* Máy chủ trình khóa máy chủ (`ssh-ed25519`), máy khách so với khóa đã biết. Dấu vân tay có dạng `SHA256:` cộng 43 ký tự; tôi tính lại từ khóa công khai bằng SHA-256 rồi base64 thì ra đúng chuỗi thư viện in. Khi máy khách mong một khóa khác, nó báo `HostKeyNotVerifiable`; máy chủ thấy một kết nối TCP đến nhưng không có yêu cầu xác thực nào.
- *Mã hóa và toàn vẹn.* Chuỗi `secret-line-93` mang trong một lệnh không xuất hiện ở luồng byte nào qua bộ chuyển tiếp; cùng phép thử trên TCP trơn thì thấy ngay. Tên thuật toán thấy được (thương lượng xảy ra trước khi mã hóa), tên người dùng `alice` thì không. Khi bộ chuyển tiếp lật một bit dữ liệu máy chủ gửi, máy khách báo `MACError: MAC verification failed` rồi đóng kết nối.

**2 · Xác thực.** Chạy sau truyền tải, trong đường đã mã hóa, nên tên người dùng không lộ trên dây. Máy chủ thử cho biết nó nhận một phương thức: `publickey`.

- Khóa đúng: vào được. Máy chủ bị hỏi hai lần về cùng một khóa: nhật ký ghi lần đầu là thử khóa (`Trying public key auth`), lần sau là kiểm yêu cầu có kèm chữ ký (`Verifying request`; về chữ ký xem [bài sd-14-015](../sd-14-015/lesson.md)).
- Khóa hợp lệ nhưng không có trong danh sách: `PermissionDenied` ngay ở lần hỏi đầu.
- Mật khẩu khi máy chủ không bật: `PermissionDenied`, và hàm kiểm mật khẩu của máy chủ không được gọi lần nào. Đối chứng: máy chủ thứ hai bật mật khẩu nhận đúng mật khẩu đó và từ chối mật khẩu sai.

**3 · Kết nối.** Trên một kết nối đã xác thực, tôi mở ba kênh cùng lúc: A chạy một lệnh và giữ mở, B chạy lệnh thứ hai, C chuyển tiếp một cổng TCP tới một máy echo cục bộ. Cả ba trả lời đúng, và A vẫn mở khi B và C đã xong. Bộ chuyển tiếp đếm 1 kết nối TCP, máy chủ nhận 1, bảng kết nối của hệ điều hành cũng chỉ có 1. Nhật ký thư viện có một lần trao khóa, một lần xác thực thành công và ba kênh mang số 0, 1, 2. Đối chứng: gọi `connect()` ba lần cho ba việc thì ra 3 kết nối TCP. Kênh C khiến máy chủ SSH tự mở một kết nối TCP khác tới đích; đó không phải kết nối giữa máy khách và máy chủ SSH.

## Giới hạn cần nhớ

Mã hóa không cho biết bạn đang nói chuyện với ai. Khi tắt việc kiểm khóa máy chủ (`known_hosts=None`), kết nối vẫn thành công và vẫn dùng `chacha20-poly1305@openssh.com`; tài liệu của `asyncssh` nói không nên làm vậy vì dễ bị tấn công xen giữa. Danh tính chỉ có khi khóa nhận được khớp khóa bạn đã biết từ nguồn đáng tin. Theo `ssh.1` của OpenSSH, lần đầu nối tới một máy, ssh đưa dấu vân tay khóa để người dùng đối chiếu; khi khóa của một máy đã biết đổi đi, ssh cảnh báo và tắt xác thực bằng mật khẩu.

## Nhìn hình trả lời

Máy khách nhận được khóa máy chủ khác khóa nó đã biết. Vì sao nó nên dừng ngay ở lớp truyền tải thay vì cứ đi tiếp sang xác thực, rồi tính sau?

<details>
<summary>Xem đáp án</summary>

Vì xác thực là lúc máy khách đưa thông tin cho đầu bên kia. `ssh.1` nói mật khẩu được gửi tới máy chủ để máy chủ kiểm, và mã hóa chỉ che nó khỏi người nghe trên đường chứ không che khỏi chính đầu bên kia. Nếu đầu bên kia là máy lạ, nó nhận được mật khẩu. Vì vậy lớp truyền tải phải xong và khóa máy chủ phải được chấp nhận trước. Trong lần thử, máy chủ thấy kết nối đến nhưng 0 lần bắt đầu xác thực: máy khách đã bỏ đi trước đó.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn và giới hạn của lần thử</summary>

**Giới hạn của lần thử.** `ssh`, `sshd` và `ssh-keygen` không có trên máy biên soạn (kiểm bằng `which`), nên hai đầu đều là `asyncssh`: thuật toán mặc định ở trên là của thư viện này, không nói gì về OpenSSH. Tài liệu OpenSSH chỉ được đọc, chưa chạy. Chưa kiểm: nội dung RFC 4251 đến 4254, forward secrecy, nén dữ liệu, và các phương thức xác thực khác ngoài khóa công khai và mật khẩu.

**Tên các lớp.** Bài nguồn gọi là Transport Layer, Authentication Layer và Connection Layer. Danh sách tiêu chuẩn trong `ssh.1` ghi RFC 4251 đến 4254 với tên: kiến trúc giao thức, giao thức truyền tải (Transport Layer Protocol), giao thức xác thực (Authentication Protocol) và giao thức kết nối (Connection Protocol). Chỉ tên đầu mang chữ "Layer". Tôi chỉ đọc danh sách tên ấy, không đọc nội dung RFC.

**Phần nguồn bỏ sót.** Bài nguồn nói lớp truyền tải mã hóa và bảo vệ dữ liệu, lớp xác thực kiểm máy khách; nó không nói máy chủ cũng phải được nhận ra, mà việc đó nằm ở lớp truyền tải: `sshd.8` nói mỗi máy có khóa riêng để định danh và máy khách so khóa máy chủ với cơ sở dữ liệu của mình. Cũng theo `sshd.8` (về OpenSSH, chưa thử ở đây), khóa phiên có được nhờ trao khóa Diffie-Hellman nên có forward secrecy.

**Phiên bản.** Bài nguồn nói SSH có hai phiên bản, SSH-1 và SSH-2, và SSH-2 do IETF chuẩn hóa. Tôi chỉ nói được điều đã đọc: `ssh.1` nói ứng dụng khách OpenSSH hỗ trợ giao thức 2, `sshd.8` nói máy chủ OpenSSH chỉ hỗ trợ giao thức 2, và `asyncssh` tự mô tả là bản cài đặt SSHv2. Mục tác giả trong các man page nhắc việc hỗ trợ giao thức 1.5 và 2.0 như lịch sử đóng góp; không tài liệu nào tôi đọc nói SSH-1 đã lỗi thời, nên bài không nói thế. Câu "do IETF chuẩn hóa" là hiểu biết chung của người biên soạn, vì `ssh.1` chỉ liệt kê số và tên RFC.

**Lớp kết nối.** Câu của bài nguồn (chia đường đã mã hóa và xác thực thành nhiều kênh) khớp với quan sát. Sách OpenSSH thêm hai chi tiết: `MaxSessions` trong `sshd_config.5` giới hạn số phiên (shell, lệnh, hệ con) trên mỗi kết nối mạng, mặc định 10 theo bản đã ghim, và đặt 0 thì không còn phiên nhưng vẫn cho chuyển tiếp; `ControlMaster` trong `ssh_config.5` cho nhiều lệnh `ssh` dùng chung một kết nối mạng. Bài không dùng ảnh của bài nguồn.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-ssh-work.md): ba lớp truyền tải, xác thực, kết nối.
- OpenSSH: [ssh.1](https://github.com/openssh/openssh-portable/blob/26b1363c7cbf5d01c730f45fc0b4abc5686beaf7/ssh.1), [sshd.8](https://github.com/openssh/openssh-portable/blob/26b1363c7cbf5d01c730f45fc0b4abc5686beaf7/sshd.8), [sshd_config.5](https://github.com/openssh/openssh-portable/blob/26b1363c7cbf5d01c730f45fc0b4abc5686beaf7/sshd_config.5), [ssh_config.5](https://github.com/openssh/openssh-portable/blob/26b1363c7cbf5d01c730f45fc0b4abc5686beaf7/ssh_config.5), [PROTOCOL](https://github.com/openssh/openssh-portable/blob/26b1363c7cbf5d01c730f45fc0b4abc5686beaf7/PROTOCOL): phiên bản giao thức, khóa máy chủ, phương thức xác thực, `MaxSessions`, `ControlMaster`, danh sách RFC. Đọc ở commit cố định.
- AsyncSSH 2.24.1: [README](https://github.com/ronf/asyncssh/blob/5dbdf18494589a6de7065f9fb89bd5d716f36a35/README.rst), [hướng dẫn](https://github.com/ronf/asyncssh/blob/5dbdf18494589a6de7065f9fb89bd5d716f36a35/docs/index.rst), [tài liệu API](https://github.com/ronf/asyncssh/blob/5dbdf18494589a6de7065f9fb89bd5d716f36a35/docs/api.rst), mã nguồn [connection.py](https://github.com/ronf/asyncssh/blob/5dbdf18494589a6de7065f9fb89bd5d716f36a35/asyncssh/connection.py), [server.py](https://github.com/ronf/asyncssh/blob/5dbdf18494589a6de7065f9fb89bd5d716f36a35/asyncssh/server.py), [auth.py](https://github.com/ronf/asyncssh/blob/5dbdf18494589a6de7065f9fb89bd5d716f36a35/asyncssh/auth.py): các lần chạy thử dùng đúng bản này.

Đã đọc nguồn ngày 2026-10-18. Cách chia theo ba lớp để quan sát, các phép thử và phần chỉnh nguồn là của người biên soạn. Bài viết và hình được thiết kế độc lập.
