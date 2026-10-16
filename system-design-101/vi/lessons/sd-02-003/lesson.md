# Pinterest cắt thời gian clone bằng một dòng refspec

**Một bước checkout trong pipeline build có thể chậm chỉ vì nó lấy nhiều hơn mức cần.** Theo nguồn, đội Engineering Productivity của Pinterest thêm một dòng refspec để chỉ lấy một nhánh, và thời gian clone monorepo Pinboard giảm từ 40 phút xuống 30 giây.

![Năm khung dọc: trước đây bước checkout không đặt refspec nên mỗi lần build lấy hơn 2500 nhánh dù đã clone nông; sau khi thêm refspec chỉ trỏ vào nhánh master thì chỉ nhánh đó được tải; ba núm riêng biệt là depth chọn sâu bao nhiêu, no-tags chọn có lấy tag không và refspec chọn lấy những nhánh nào; theo nguồn thứ cấp thời gian clone giảm từ 40 phút xuống 30 giây, chưa được kiểm chứng độc lập; cái giá là các nhánh khác không có sẵn trong bản clone. Kết luận: giảm bề sâu chưa đủ, phải giảm cả bề rộng.](../../diagrams/sd-02-003-main.svg)

## Đọc hình

1. **Trước: lấy mọi nhánh.** *Refspec* của Git là quy tắc nói "lấy những tham chiếu nào từ kho ở xa và đặt vào đâu". Quy tắc mặc định của một remote thông thường, `+refs/heads/*:refs/remotes/origin/*`, nghĩa là mọi nhánh. Theo nguồn, bước Checkout trong pipeline build của Pinboard đã chọn clone nông, chỉ 50 commit cuối và bỏ tag, nhưng không đặt refspec, nên mỗi lần build Git lấy hơn 2500 nhánh. Một lệnh `git clone --depth` thuần thì chỉ lấy một nhánh (xem mục cuối), nên theo suy luận của bài, công cụ checkout ở đây phải chạy `git fetch` với refspec đã cấu hình; bài chưa tái hiện pipeline đó.
2. **Sau: một nhánh.** Đội thêm refspec chỉ nêu nhánh cần, ở đây là master. Git chỉ tải nhánh đó (tag đã bị bỏ sẵn).
3. **Ba núm riêng biệt.** `depth` giới hạn lịch sử *của mỗi nhánh được lấy*, `no-tags` bỏ các tag, refspec chọn *những nhánh nào*. Chỉnh một núm không thay cho hai núm kia: khi `git fetch` dùng refspec mặc định, giới hạn độ sâu không làm số nhánh được lấy ít đi (`git clone --depth` thì ngầm chỉ lấy một nhánh, xem mục cuối).
4. **Kết quả theo nguồn.** Từ 40 phút còn 30 giây, tức giảm khoảng 99% (2.400 giây còn 30 giây là giảm 98,75%). Nguồn nêu thêm vài số của Pinboard: 350 nghìn commit, 20 gigabyte khi clone đầy đủ, 60 nghìn lệnh pull mỗi ngày làm việc.
5. **Cái giá.** Khung này do bài bổ sung, không có trong nguồn: bản clone chỉ có nhánh đã chọn, nên build nào cần nhánh khác (so với nhánh gốc, hoặc chạy trên nhánh tính năng) phải khai thêm refspec hay tải thêm.

## Giới hạn cần nhớ

Các con số của Pinterest và của Pinboard là theo nguồn ByteByteGo; bài gốc của Pinterest chưa được mở để đối chiếu. Mức giảm phụ thuộc kho có bao nhiêu nhánh và mỗi nhánh khác nhánh chính bao nhiêu, nên đừng áp nguyên 40 phút → 30 giây cho kho khác. Cũng đừng suy ra "refspec luôn là thủ phạm": nếu kho chỉ có vài nhánh thì dòng này gần như không đổi gì, và thời gian clone còn phụ thuộc mạng, kích thước tệp, máy chủ. Cơ chế "bề sâu khác bề rộng" thì kiểm tra được; phần "Xem sâu hơn" có một thử nghiệm cục bộ.

## Nhìn hình thử trả lời

Công cụ build của bạn chạy `git fetch --depth=50` với refspec mặc định trên một kho có 800 nhánh cũ. Bước build chỉ cần nhánh chính, nhưng việc tải vẫn chậm. Vì sao, và bạn sửa gì?

<details>
<summary>Xem đáp án</summary>

Khi `git fetch` dùng refspec mặc định, `--depth` chỉ giới hạn bề sâu: mỗi nhánh được lấy vẫn kéo theo tới 50 commit gần nhất của nó, và cả 800 nhánh đều được lấy. Nếu công cụ chạy đúng `git clone --depth=50` thì Git đã ngầm chỉ lấy một nhánh (xem mục cuối), và nguyên nhân phải tìm ở chỗ khác. Với `git fetch` như trên, sửa bằng cách đặt refspec chỉ nêu nhánh chính (kèm `--no-tags` nếu không cần tag), và khai thêm đúng những nhánh mà build thật sự dùng. Đừng vội xóa nhánh cũ trên máy chủ: với client dùng refspec hẹp trên giao thức v2, Git thường chỉ xin liệt kê nhánh cần nên các nhánh đó thường không ảnh hưởng gì (xem mục dưới; đây là một tối ưu hóa chứ không phải bảo đảm của giao thức), còn xóa nhánh là việc khó hoàn lại và thuộc quyền chủ kho. Dọn nhánh chỉ đáng cân nhắc khi vẫn còn client lấy mọi nhánh mà chưa sửa được.

</details>

<details>
<summary>Xem sâu hơn</summary>

Thử nghiệm cục bộ của người biên soạn ngày 2026-10-16, Git 2.43.0, tải qua `file://` từ một kho tự dựng: nhánh master có 120 commit, thêm 300 nhánh, mỗi nhánh có 5 commit riêng toàn dữ liệu ngẫu nhiên. Số đo là tương đối trên một đĩa cục bộ, không phải thời gian qua mạng, và không tái hiện số của Pinterest.

- **`git fetch --depth=50 --no-tags` với refspec mặc định (mọi nhánh):** 301 tham chiếu, 4.720 object, khoảng 14 megabyte, 1,49 giây.
- **Cùng lệnh nhưng refspec chỉ nêu master:** 1 tham chiếu, 220 object, khoảng 0,56 megabyte, 0,07 giây. Giảm khoảng 95% trở lên so với dòng trên, ở cả ba số đo.
- **Mọi nhánh, không `--depth`:** 4.860 object, gần bằng dòng đầu. Mỗi nhánh thử chỉ có 5 commit riêng, ít hơn 50, nên trong kho thử này giới hạn độ sâu gần như không cắt được gì. Nhánh dài hơn thì nó cắt được nhiều hơn, nhưng số nhánh được lấy vẫn không đổi.
- **Mọi nhánh, `--depth=1`:** 2.222 object, vẫn khoảng 13,5 megabyte vì commit mới nhất của mỗi nhánh vẫn có 5 tệp riêng.
- **Giao thức v2 cho client xin liệt kê theo tiền tố:** client gửi lệnh `ls-refs` kèm `ref-prefix`, và server thường chỉ trả những tham chiếu khớp. Bắt gói tin với Git 2.43.0 ở cả hai đầu thấy refspec chỉ master gửi `ref-prefix refs/heads/master` và server trả về 1 tham chiếu; refspec mọi nhánh gửi `ref-prefix refs/heads/` và nhận 301. Đây chỉ là hành vi của cài đặt đã thử: tài liệu giao thức coi `ref-prefix` là tối ưu hóa, nên một server khác vẫn có thể trả thêm tham chiếu không khớp. Điều chắc chắn hơn là client không yêu cầu tải đối tượng của những nhánh nằm ngoài refspec. Vì vậy, ở cài đặt đã thử, cái giá liệt kê các nhánh cũ rơi vào client lấy mọi nhánh; client có refspec hẹp không phải tải đối tượng của chúng, còn việc server có liệt kê thừa hay không là tùy cài đặt.
- **Mặc định và `git clone --depth=50`:** một lần `git clone` thường để lại refspec `+refs/heads/*:refs/remotes/origin/*` và lấy cả 301 nhánh (kèm HEAD). Còn `git clone --depth=50` cho ra bản chỉ có một nhánh: tài liệu Git ghi `--depth` ngầm kèm `--single-branch`, và thử cho thấy cấu hình sinh ra là `+refs/heads/master:refs/remotes/origin/master`. Vì vậy cùng một ý "clone nông" có thể cho kết quả rất khác nhau tùy công cụ gọi `git clone` hay gọi `git fetch` với refspec đã cấu hình; muốn chắc thì đặt refspec rõ ràng.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/the-one-line-change-that-reduced-clone-times-by-a-whopping-99-says-pinterest.md): Pinboard, clone nông, refspec và con số 40 phút → 30 giây.
- [git-fetch](https://git-scm.com/docs/git-fetch) và [git-clone](https://git-scm.com/docs/git-clone): `--depth`, `--no-tags`, `--single-branch`, refspec.
- [Pro Git: The Refspec](https://git-scm.com/book/en/v2/Git-Internals-The-Refspec): cú pháp refspec.
- [Jenkins Git plugin](https://plugins.jenkins.io/git/): cấu hình checkout của pipeline.

Đã đọc body nguồn ByteByteGo ghim ngày 2026-10-16; hành vi của Git nêu ở mục "Xem sâu hơn" được chạy thử cục bộ cùng ngày. Bài gốc của Pinterest, tài liệu Git và Jenkins chưa được mở để đối chiếu (máy biên soạn không truy cập được các trang đó), và pipeline Jenkins của Pinterest chưa được tái hiện. Bài viết và hình được thiết kế độc lập; chưa thử với người học.
