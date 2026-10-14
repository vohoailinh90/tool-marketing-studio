# Container Docker thoát ngay hoặc khởi động lại mãi: bốn manh mối

Bạn chạy `docker run -d` và vài giây sau container đã biến mất khỏi `docker ps`, hoặc cứ ở trạng thái Restarting. Docker giữ lại trạng thái thoát của container cho đến khi bạn xóa nó, và bốn chỗ dưới đây cho biết vì sao nó dừng.

![Bốn manh mối khi container Docker thoát ngay hoặc khởi động lại liên tục: trạng thái và mã thoát trong docker ps -a, nhật ký bằng docker logs, trạng thái chi tiết trong docker inspect như ExitCode và OOMKilled (Out Of Memory Killed — bị dừng vì hết bộ nhớ), và chính sách khởi động lại quyết định container có chạy lại sau khi thoát hay không.](../../diagrams/sd-13-026-main.svg)

**Đọc hình:** bốn thẻ là bốn chỗ để hỏi một container đã thoát; làm theo thứ tự hoặc chỉ đọc chỗ cần.

## Từ viết tắt

- **SIGKILL** (SIGnal KILL) — tín hiệu số 9, buộc dừng tiến trình ngay và tiến trình không kịp dọn dẹp; mã thoát 137 thường là dấu hiệu của nó.
- **PID** (Process IDentifier) — mã số tiến trình: số hệ điều hành gán cho mỗi tiến trình; trong container, tiến trình chính có PID 1 và container chạy đến khi nó thoát.
- **OOM** (Out Of Memory) — hết bộ nhớ: tình trạng một tiến trình cần nhiều bộ nhớ hơn mức được cấp nên bị hệ điều hành dừng; OOMKilled là trạng thái ghi lại việc đó.

## Nhìn hình thử trả lời

Container thoát với mã 137 ngay sau khi nhận nhiều request, và `docker logs` không có dòng lỗi nào. Bước kiểm tra tiếp theo là gì?

<details>
<summary>Xem đáp án</summary>

Mã thoát lớn hơn 128 thường là 128 cộng số hiệu tín hiệu, nên 137 thường báo hiệu SIGKILL (signal kill — tín hiệu số 9, buộc dừng tiến trình ngay); đây chỉ là manh mối, vì ứng dụng cũng có thể tự thoát với mã 137. Với container, nguyên nhân hay gặp là hết bộ nhớ, hoặc có người dùng `docker kill` hay dừng quá hạn. Chạy `docker inspect --format '{{.State.OOMKilled}}' tên-container`: true nghĩa là container bị dừng vì hết bộ nhớ, khi đó tăng giới hạn `--memory` hay giảm mức dùng của ứng dụng. Nếu là false, xem `docker events` và nhật ký kernel của máy chủ để tìm ai đã gửi SIGKILL.

</details>

## Giới hạn cần nhớ

Trạng thái thoát chỉ còn khi container chưa bị xóa: chạy với `--rm` thì Docker xóa container ngay khi nó thoát, nên bỏ cờ này khi đang tìm lỗi. Bài chỉ nói về container đã chạy rồi dừng, không bàn lỗi kéo image, mạng hay build. Mã thoát do chính ứng dụng quy định, nên cùng một mã có thể mang nghĩa khác nhau giữa các ứng dụng.

<details>
<summary>Xem sâu hơn</summary>

```bash
docker ps -a --format 'table {{.Names}}\t{{.Status}}'                          # mọi container: Exited kèm mã thoát, Restarting khi đang tự khởi động lại
docker logs --tail 50 tên-container                                              # 50 dòng cuối
docker inspect --format 'code={{.State.ExitCode}} oom={{.State.OOMKilled}} err={{.State.Error}}' tên-container
docker events --since 10m --filter container=tên-container                      # die, oom, kill, restart
```

- **Tiến trình chính quyết định đời container:** container chạy đến khi tiến trình chính (PID — process identifier, mã số tiến trình — bằng 1) thoát. Lệnh tự chạy nền rồi trả về (kiểu daemonize), hay một shell không có gì để chờ (như `docker run ubuntu bash` không có `-it`), làm container thoát ngay; hãy chạy ứng dụng ở foreground.
- **Mã đặc biệt của docker run:** 125 là lỗi của chính Docker (như cờ sai), 126 là lệnh trong container không thực thi được, 127 là không tìm thấy lệnh; mã khác là mã thoát của lệnh trong container, nên một ứng dụng tự thoát với mã 137 cũng cho đúng mã mà một tiến trình bị SIGKILL cho.
- **OOMKilled (Out Of Memory Killed — bị dừng vì hết bộ nhớ):** `true` cho biết kernel đã dừng container vì hết bộ nhớ. `false` chưa bảo đảm mã 137 không đến từ bộ nhớ, nên đối chiếu thêm với nhật ký kernel của máy chủ.
- **Chính sách khởi động lại:** `no` (mặc định), `on-failure[:số lần]` (chỉ chạy lại khi mã thoát khác 0), `always`, `unless-stopped`. Container ở vòng Restarting thì sửa nguyên nhân thoát; gỡ chính sách bằng `docker update --restart=no` chỉ che triệu chứng. Docker coi Restarting và Exited là hai trạng thái riêng, nên lọc `--filter status=exited` sẽ bỏ sót container đang ở vòng khởi động lại.

</details>

## Nguồn đối chiếu

- [ByteByteGo tại snapshot cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/how-does-docker-work.md).
- Docker: [docker run và mã thoát](https://docs.docker.com/reference/cli/docker/container/run/), [chính sách khởi động lại](https://docs.docker.com/engine/containers/start-containers-automatically/), [docker container inspect](https://docs.docker.com/reference/cli/docker/container/inspect/), [docker events](https://docs.docker.com/reference/cli/docker/system/events/), [docker container logs](https://docs.docker.com/reference/cli/docker/container/logs/), [docker container ls và bộ lọc status](https://docs.docker.com/reference/cli/docker/container/ls/#status).
- Bash: [trạng thái thoát](https://www.gnu.org/software/bash/manual/html_node/Exit-Status.html).
