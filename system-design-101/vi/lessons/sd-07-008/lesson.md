# Đối soát thanh toán: ba nỗi đau và cách gỡ

**Đối soát là so sánh các bản ghi ở nhiều hệ thống khác nhau để chắc chắn số tiền khớp nhau. Nguồn gọi đây có thể là quy trình đau đầu nhất của một hệ thống thanh toán.**
Ba nỗi đau chính là khác định dạng, dữ liệu quá lớn, và lệch giờ chốt sổ.

![Hai khung. Khung một, ba bản ghi của một khoản 200 đô la mua đồng hồ: đơn hàng trên website thương mại điện tử, giao dịch ở PayPal, sổ cái ghi nợ người mua 200 và ghi có người bán 200. Khung hai, ba nỗi đau và cách gỡ: định dạng dữ liệu khác nhau thì thêm một lớp chuyển về cùng định dạng; dữ liệu rất lớn thì dùng xử lý dữ liệu lớn, luồng nếu cần gần thời gian thực, lô cuối ngày nếu không; lệch giờ chốt thì xếp vào lệch tạm thời rồi so lại với bản ghi ngày sau.](../../diagrams/sd-07-008-main.svg)

## Đọc hình

**Ba bản ghi của một khoản tiền.** Bạn trả 200 đô la mua một chiếc đồng hồ qua PayPal. Trang thương mại điện tử phải có một bản ghi đơn mua 200 đô la. PayPal phải có một bản ghi giao dịch 200 đô la. Và sổ cái phải ghi nợ 200 đô la cho người mua, ghi có 200 đô la cho người bán: đó là ghi sổ kép (double-entry bookkeeping). Đối soát là kiểm ba bản ghi này khớp nhau.

**Nỗi đau 1: khác định dạng.** Mỗi hệ thống ghi dữ liệu một kiểu; chẳng hạn ngày có thể là "2022/01/01" ở nơi này và "Jan 1, 2022" ở nơi khác. Cách gỡ: thêm một lớp chuyển các định dạng khác nhau về cùng một định dạng rồi mới so.

**Nỗi đau 2: dữ liệu rất lớn.** Cách gỡ: dùng kỹ thuật xử lý dữ liệu lớn để so nhanh hơn. Nếu cần đối soát gần thời gian thực, dùng nền tảng xử lý luồng như Flink; nếu không, xử lý theo lô vào cuối ngày, chẳng hạn bằng Hadoop, là đủ.

**Nỗi đau 3: lệch giờ chốt.** Chọn 00:00:00 làm giờ chốt mỗi ngày. Một bản ghi trong hệ thống nội bộ đóng dấu 23:59:55, nhưng bên PayPal lại đóng dấu 00:00:30, tức là ngày hôm sau. Hôm nay tìm không thấy bản ghi đó ở PayPal nên hai bên lệch nhau. Cách gỡ: xếp chỗ lệch này vào loại "lệch tạm thời" và so lại với bản ghi PayPal của ngày hôm sau; nếu khớp thì chỗ lệch được xóa và không cần làm gì thêm.

**Vì sao vẫn cần đối soát?** Có người cho rằng nếu hệ thống xử lý "đúng một lần" (exactly-once) thì đâu ra lệch. Nguồn đáp: có quá nhiều chỗ có thể sai, nên hệ thống đối soát luôn cần thiết, như tấm lưới an toàn giúp ngủ yên.

## Giới hạn cần nhớ

Nguồn dùng ví dụ PayPal và hai công cụ Flink, Hadoop như minh họa; bài không so sánh các công cụ và không nói một công ty thật đối soát thế nào.
Nguồn cũng không nói chỗ lệch nào là tạm thời và chỗ nào là lỗi thật, hay quá bao lâu mà chưa khớp thì phải xử lý tay: đó là chuyện của từng hệ thống.

## Nhìn hình trả lời

Một giao dịch có dấu 23:59:58 trong hệ thống nội bộ nhưng PayPal ghi 00:00:10 ngày hôm sau. Hôm nay đối soát báo lệch. Đây có phải lỗi thật không, và bước tiếp theo là gì?

<details>
<summary>Xem đáp án</summary>

Chưa chắc là lỗi: đây đúng là kiểu "lệch tạm thời" do giờ chốt. Nên đánh dấu là lệch tạm thời, rồi so lại với bản ghi PayPal của ngày hôm sau. Nếu thấy bản ghi 200 đô la khớp, chỗ lệch được xóa; nếu hôm sau vẫn không thấy thì mới là chỗ cần điều tra.
Phần "nếu vẫn không thấy thì điều tra" là suy luận của người biên soạn; nguồn chỉ nói chỗ lệch được xóa khi tìm thấy bản ghi khớp.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn có ba nỗi đau, mỗi nỗi đau một cách gỡ, kèm sơ đồ. Bài này giữ cả ba theo đúng thứ tự, và đặt ba bản ghi của ví dụ 200 đô la thành một khung riêng để thấy đối soát so cái gì với cái gì.
Bài chưa đối chiếu với tài liệu của một công ty thanh toán cụ thể.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/reconciliation-in-payment.md): định nghĩa đối soát, ví dụ 200 đô la, ba nỗi đau và cách gỡ. Phần giới hạn và đáp án là suy luận của người biên soạn.

Đã đọc nguồn ngày 2026-10-19. Bài viết và hình được thiết kế độc lập.
