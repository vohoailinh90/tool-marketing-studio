# Các loại bản ghi DNS cần biết

**Một tên miền không chỉ có một địa chỉ.** Dữ liệu DNS là các *bản ghi* có loại; mỗi loại trả lời một kiểu câu hỏi — địa chỉ ở đâu, thư gửi về đâu, ai quản lý vùng này.

![Ba khung dọc: A, AAAA và CNAME trỏ tên tới địa chỉ hoặc tên khác; MX và NS chỉ máy chủ nhận thư và máy chủ tên của vùng; TXT, PTR và SRV chứa văn bản, tra ngược địa chỉ ra tên, và chỉ máy chủ cùng cổng của một dịch vụ.](../../diagrams/sd-15-005-main.svg)

## Đọc hình

- **A / AAAA:** tên → địa chỉ IPv4 / IPv6.
- **CNAME:** đặt tên này là *bí danh* của tên khác; resolver tra tiếp tên đích. Tên có CNAME không được có bản ghi loại khác cùng tên (trừ bản ghi của DNSSEC).
- **MX:** miền nhận thư ở máy chủ nào; có thứ tự ưu tiên.
- **NS:** máy chủ tên chịu trách nhiệm cho vùng, dùng để ủy quyền xuống cấp dưới.
- **TXT:** văn bản tự do; thường chứa xác minh quyền sở hữu miền và chính sách thư như SPF.
- **PTR:** tra *ngược* từ địa chỉ IP ra tên, nằm trong vùng đặc biệt của dải địa chỉ.
- **SRV:** máy chủ và cổng cho một dịch vụ cụ thể; tên máy chủ đó lại cần bản ghi A hoặc AAAA.

## Giới hạn cần nhớ

Bản ghi không tự bảo đảm đáng tin: TXT chứa gì cũng được, PTR do chủ dải địa chỉ đặt chứ không do chủ tên miền xác nhận. Mỗi bản ghi có TTL riêng nên thay đổi lan chậm. CNAME ở *gốc* của miền (apex) thường không được phép, vì gốc đã phải có SOA và NS.

## Nhìn hình thử trả lời

Bạn muốn `www.example.com` luôn đi theo địa chỉ của `app.example.net`, dù địa chỉ đó đổi. Dùng bản ghi nào?

<details>
<summary>Xem đáp án</summary>

CNAME trên `www.example.com` trỏ tới `app.example.net`. Khi `app.example.net` đổi địa chỉ, tên `www` tự theo.

</details>

<details>
<summary>Xem sâu hơn</summary>

```
example.com.      3600  IN  MX   10 mail.example.com.
www.example.com.  3600  IN  CNAME app.example.net.
mail.example.com. 3600  IN  A    192.0.2.25
```

- **MX** trỏ tới *tên* máy chủ, không trỏ thẳng IP; tên đó cần có A/AAAA.
- **Chưa kể:** SOA (thông tin vùng), CAA (giới hạn CA được cấp chứng chỉ), DS/DNSKEY (DNSSEC) và nhiều loại khác.
- **SPF** từng có loại bản ghi riêng; hiện nay dùng TXT.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/dns-record-types-you-should-know.md).
- [RFC 1035](https://www.rfc-editor.org/rfc/rfc1035): A, NS, CNAME, PTR, MX, TXT. [RFC 3596](https://www.rfc-editor.org/rfc/rfc3596): AAAA. [RFC 2782](https://www.rfc-editor.org/rfc/rfc2782): SRV.
- [RFC 2181 §10.1](https://www.rfc-editor.org/rfc/rfc2181) và [RFC 4034](https://www.rfc-editor.org/rfc/rfc4034): CNAME đứng một mình, trừ bản ghi DNSSEC.
- [RFC 7208](https://www.rfc-editor.org/rfc/rfc7208): SPF dùng TXT.

Đã đọc nguồn ngày 2026-10-13; các tài liệu chuẩn nêu trên chưa được mở để đối chiếu trực tiếp trong lượt biên soạn này. Bài viết và hình được thiết kế độc lập.
