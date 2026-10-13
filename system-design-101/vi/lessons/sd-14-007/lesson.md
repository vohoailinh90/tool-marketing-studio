# Tường lửa hoạt động thế nào?

**Tường lửa là điểm kiểm soát giữa hai mạng: nó nhìn từng gói tin hoặc cả kết nối và quyết định cho qua hay chặn theo luật.**
Các loại tường lửa khác nhau ở chỗ chúng nhìn vào cái gì: một gói riêng lẻ, một phiên, trạng thái của cả kết nối, hay nội dung của ứng dụng.

![Bảy thẻ xếp dọc. Thẻ đầu là câu hỏi chung: gói tin đi tới tường lửa thì cho qua hay chặn. Năm thẻ tiếp theo là năm loại, mỗi loại nhìn vào một thứ khác. Lọc gói tin: nhìn địa chỉ nguồn, đích, giao thức và cổng của từng gói, không nhớ gói trước. Cổng mức mạch: theo dõi bắt tay TCP để xem phiên có hợp lệ không. Cổng ứng dụng, hay proxy: nhận kết nối thay cho máy bên trong và đọc nội dung ở tầng ứng dụng. Theo dõi trạng thái: nhớ các kết nối đang mở, nên nhận ra gói trả lời. Tường lửa thế hệ mới: gộp các cách trên với các tính năng như ngăn chặn xâm nhập và nhận diện ứng dụng. Thẻ cuối là lời nhắc: tường lửa chỉ áp luật tại điểm nó đứng, luật sai hoặc lưu lượng đi đường khác thì không được bảo vệ.](../../diagrams/sd-14-007-main.svg)

## Đọc hình

**Lọc gói tin.** Mỗi gói được xét riêng theo địa chỉ nguồn, địa chỉ đích, giao thức và cổng. Không nhớ gói trước đó.

**Cổng mức mạch (circuit-level).** Theo dõi bắt tay TCP để xem một phiên có hợp lệ không, mà không đọc nội dung ứng dụng.

**Cổng ứng dụng (proxy).** Máy bên ngoài nói chuyện với proxy, proxy mới nói chuyện với máy bên trong. Vì proxy đứng ở tầng ứng dụng nên đọc được nội dung, ví dụ một yêu cầu HTTP, chứ không chỉ phần đầu gói.

**Theo dõi trạng thái.** Tường lửa giữ một bảng các kết nối đang mở, nên nhận ra một gói là trả lời của kết nối do máy bên trong đã mở. Chạy thử trên Linux với nftables: với luật theo cổng cho gói đi tới cổng 18081 nhưng chặn mọi gói xuất phát từ cổng đó (một cách dựng thử nghiệm), bắt tay TCP không hoàn tất vì gói trả lời bị chặn (kết nối quá hạn);
thêm luật `ct state established,related accept` thì cùng kết nối chạy bình thường, còn kết nối mới tới cổng bị cấm vẫn bị chặn.

**Tường lửa thế hệ mới (NGFW).** Gộp các cách trên với các tính năng như ngăn chặn xâm nhập, kiểm tra sâu gói tin và nhận diện ứng dụng. Đây là tên gọi cho một nhóm tính năng, mỗi sản phẩm làm khác nhau.

## Giới hạn cần nhớ

Nhìn nhiều hơn thì thường tốn nhiều tài nguyên hơn và cần cấu hình đúng hơn (suy luận của người biên soạn). Tường lửa chỉ áp luật ở điểm nó đứng: lưu lượng đi đường khác, hoặc luật viết sai, thì không được bảo vệ.
Cuộc chạy thử không thử trường hợp bộ lọc theo gói mở thêm luật cho gói trả lời theo cổng nguồn. Lọc theo gói muốn cho gói trả lời đi qua thì phải mở thêm luật theo cổng nguồn, và luật đó cũng cho qua các gói khác tự mang cổng nguồn ấy, kể cả gói không thuộc kết nối nào (suy luận của người biên soạn, chưa chạy thử).

## Nhìn hình trả lời

Máy trong mạng nội bộ mở một kết nối ra ngoài, và tường lửa chỉ có luật “cho gói đi ra, chặn gói đi vào”. Vì sao gói trả lời vẫn vào được nếu tường lửa theo dõi trạng thái, còn tường lửa lọc gói thuần túy thì sao?

<details>
<summary>Xem đáp án</summary>

Tường lửa theo dõi trạng thái ghi lại kết nối đi ra, nên gói đi vào khớp với kết nối đó được coi là gói trả lời và cho qua. Lọc gói thuần túy không có ghi nhớ này: gói trả lời trông như một gói đi vào bất kỳ nên bị chặn, trừ khi người quản trị mở thêm luật theo cổng.
Khi chạy thử trên Linux, chỉ có luật theo cổng thì kết nối quá hạn, còn khi thêm luật theo trạng thái thì kết nối thành công.

</details>

<details>
<summary>Xem sâu hơn: điều đã chỉnh so với bài nguồn</summary>

Bài nguồn liệt kê năm loại theo một dòng mỗi loại, kèm hai nhóm phần mềm và phần cứng. Bài này giữ thứ tự của bài nguồn, ghi rõ mỗi loại nhìn vào gì (không xếp hạng các loại theo độ sâu), và chạy thử riêng sự khác biệt giữa lọc theo cổng và theo trạng thái.
Bài nguồn tả cổng ứng dụng là “lọc lưu lượng giữa mạng và nguồn”; bài này nêu cụ thể hơn là proxy nhận kết nối thay cho máy bên trong. Chưa đối chiếu với một tài liệu chuẩn, nên các mô tả của cổng mức mạch, cổng ứng dụng và NGFW lấy từ bài nguồn và hiểu biết chung của người biên soạn.

Ví dụ chạy thử là một bảng nftables dựng riêng cho một cổng trên giao diện loopback rồi xóa; luật “chặn mọi gói từ cổng nguồn đó” là cách dựng thử nghiệm, không phải cấu hình nên dùng thật.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/firewall-explained-to-kids-and-adults.md): các loại tường lửa và hai nhóm phần mềm, phần cứng.
- [Linux kernel — Netfilter Conntrack sysctl](https://github.com/torvalds/linux/blob/master/Documentation/networking/nf_conntrack-sysctl.rst): Linux theo dõi kết nối và giữ số mục luồng đang theo dõi. Đọc qua nguồn trên GitHub.

Đã đọc nguồn ngày 2026-10-13. Ví dụ chạy thử bằng nftables trên Linux; không có tài liệu chuẩn nào được mở để đối chiếu các mô tả loại tường lửa, và bài nói rõ điều đó. Bài viết và hình được thiết kế độc lập.
