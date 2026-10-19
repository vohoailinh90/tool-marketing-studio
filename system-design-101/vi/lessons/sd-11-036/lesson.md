# Hai thập kỷ đám mây: mỗi cột mốc nhấc phần "tự lo" lên một bậc

**Từ năm 2001 đến 2015, mỗi cột mốc của đám mây không thêm một công nghệ chồng lên nhau, mà dời đường ranh giữa phần bạn tự lo và phần nhà cung cấp lo: máy vật lý, rồi máy ảo, rồi nền tảng, rồi gói ứng dụng, rồi cả cách vận hành.**
Bài đọc bảy cột mốc ở bài nguồn theo đường ranh đó, và kiểm bốn trong bảy năm bằng kho mã và tài liệu công khai.

![Hai khung. Khung một, bốn cột mốc đầu nối nhau: năm 2001 VMware đưa ảo hóa bằng hypervisor; năm 2006 AWS cho thuê hạ tầng như một dịch vụ; năm 2009 Heroku đưa nền tảng như một dịch vụ; năm 2010 OpenStack là hạ tầng mã nguồn mở. Khung hai, ba cột mốc sau: năm 2011 Cloud Foundry là nền tảng mã nguồn mở; năm 2013 Docker đưa container; năm 2015 CNCF lập ra để giữ cloud native.](../../diagrams/sd-11-036-main.svg)

## Từ viết tắt

- **AWS** (Amazon Web Services) — dịch vụ điện toán đám mây của Amazon; bài nguồn đặt nó ở năm 2006.
- **IaaS** (Infrastructure as a Service) — hạ tầng như một dịch vụ: bạn thuê máy ảo, mạng, ổ đĩa và tự cài hệ điều hành cùng ứng dụng lên đó.
- **PaaS** (Platform as a Service) — nền tảng như một dịch vụ: nhà cung cấp lo máy chủ và hệ điều hành, bạn chỉ đưa mã ứng dụng lên.
- **CNCF** (Cloud Native Computing Foundation) — tổ chức giữ nhiều dự án mã nguồn mở của hệ sinh thái cloud native, trong đó có Kubernetes.

## Đọc hình

Bảng dưới giữ nguyên bảy cột mốc của bài nguồn. Cột "phần bạn thôi phải tự lo" là cách đọc của người biên soạn (kiến thức chung, không phải lời của nguồn).

| Năm | Cột mốc (ở nguồn) | Đường ranh dời đi đâu |
|---|---|---|
| 2001 | VMware: ảo hóa bằng hypervisor | Một máy vật lý chạy được nhiều máy ảo; phần cứng không còn gắn một hệ điều hành |
| 2006 | AWS: IaaS | Bạn không mua máy nữa, mà thuê máy ảo qua mạng và trả theo lượng dùng |
| 2009 | Heroku: PaaS | Bạn không quản máy ảo và hệ điều hành nữa, chỉ đưa mã lên |
| 2010 | OpenStack: IaaS mã nguồn mở | Cùng kiểu dịch vụ hạ tầng như 2006, nhưng tự dựng được trên máy của mình |
| 2011 | Cloud Foundry: PaaS mã nguồn mở | Cùng kiểu nền tảng như 2009, cũng tự dựng được |
| 2013 | Docker: container | Ứng dụng đóng gói cùng phần nó cần, chạy giống nhau ở máy nào |
| 2015 | CNCF: cloud native | Cách vận hành (xếp lịch, quan sát, tự phục hồi) trở thành chuẩn chung có tổ chức giữ |

Hai cặp (2006 với 2010, 2009 với 2011) cho thấy một mẫu: kiểu dịch vụ ra đời trước ở dạng thương mại, rồi có bản mã nguồn mở theo sau.

## Thử: kiểm bốn cột mốc bằng kho công khai

Ngày 2026-10-19 đối chiếu với nguồn công khai, không bằng trí nhớ:

- **2010, OpenStack.** Danh sách phiên bản trong kho `openstack/releases` ghi bản đầu tiên, Austin, phát hành ngày 2010-10-21.
- **2011, Cloud Foundry.** Kho `cloudfoundry/vcap` có commit đầu tiên ngày 2011-04-11.
- **2013, Docker.** Kho `moby/moby` có commit đầu tiên ngày 2013-01-18, và thẻ phiên bản `v0.1.0` mang ngày 2013-03-23.
- **2015, CNCF.** Điều lệ của CNCF ghi hiệu lực từ ngày 2015-11-06. Điều lệ cũng chứa định nghĩa cloud native mà tổ chức ghi là phiên bản 1.0, về sau được cập nhật.

Ba năm còn lại (2001 VMware, 2006 AWS, 2009 Heroku) là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu của các công ty đó. Phép thử chỉ xác nhận mỗi dự án có dấu vết trong năm đó; nó không chứng minh đó là "cột mốc" quan trọng nhất của năm.

## Giới hạn cần nhớ

Một dòng thời gian sắp mọi thứ vào một đường thẳng và dễ làm tưởng cái sau thay cái trước. Thực tế các tầng cùng tồn tại: nhiều hệ thống vẫn chạy trên máy ảo thuê (IaaS), và container thường chạy trên chính các máy ảo đó. Chọn cột mốc cũng mang tính chọn lọc: bảy mốc của nguồn không phải toàn bộ lịch sử. Bảng "đường ranh dời đi đâu" là cách đọc của người biên soạn.

## Nhìn hình trả lời

Một đội đưa ứng dụng lên một dịch vụ kiểu 2009 (nhận mã, tự chạy), rồi vài năm sau chuyển sang chạy container tự quản trên máy ảo thuê. Đường ranh của họ dời theo hướng nào, và họ nhận lại việc gì?

<details>
<summary>Xem đáp án</summary>

Đường ranh dời xuống: họ nhận lại việc quản máy ảo, hệ điều hành và việc xếp lịch các container, đổi lại có quyền kiểm soát môi trường chạy và chạy giống nhau ở mọi nơi. Mỗi bước trong bảng dời đường ranh lên (nhà cung cấp lo thêm) hoặc xuống (bạn nhận thêm quyền và việc); không có hướng nào luôn tốt hơn. Đây là suy luận của người biên soạn.

</details>

<details>
<summary>Xem sâu hơn: điều đã sắp xếp lại so với bài nguồn</summary>

Bài nguồn là một hình dòng thời gian và danh sách bảy cột mốc. Bài này giữ bảy cột mốc, thêm cách đọc theo đường ranh tự lo, và đối chiếu bốn năm với kho mã và điều lệ công khai.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/2-decades-of-cloud-evolution.md): bảy cột mốc và năm. Cách đọc theo đường ranh là của người biên soạn.
- [OpenStack — danh sách phiên bản](https://github.com/openstack/releases/blob/master/data/series_status.yaml): ngày bản Austin, đọc từ nhánh chính.
- [Cloud Foundry — kho vcap](https://github.com/cloudfoundry/vcap): ngày commit đầu tiên, đọc từ lịch sử git.
- [Docker — kho moby](https://github.com/moby/moby): ngày commit đầu tiên và thẻ `v0.1.0`, đọc từ lịch sử git.
- [CNCF — điều lệ](https://github.com/cncf/foundation/blob/main/charter.md): ngày hiệu lực của điều lệ.

Đã đọc nguồn ngày 2026-10-19. Các ngày kiểm là của người biên soạn.
Bài viết và hình được thiết kế độc lập.
