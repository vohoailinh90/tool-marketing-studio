# 04 · Kiểm chứng nhu cầu

## Thang tín hiệu (yếu → mạnh)

like < comment "hay quá" < comment kể chuyện của họ < bấm link < trả lời khảo sát < để lại liên hệ dùng thử
< đồng ý phỏng vấn < **trả tiền / đặt trước**

Chỉ hai bậc cuối là bằng chứng thật về nhu cầu. Like nhiều mà không ai để lại liên hệ = chưa có nhu cầu.

## Ngưỡng kết luận (trong `campaign.yaml`)

```yaml
validation:
  min_counts: {reach: 1000, link_clicks: 30, survey_responses: 15}   # dưới mức này: CHƯA ĐỦ DỮ LIỆU
  go_if: {survey_responses: 30, signups: 10, click_rate: 0.01}        # đạt hết: NÊN LÀM TIẾP
```

App/CLI tính riêng **từng ngôn ngữ** và luôn ghi kèm cỡ mẫu (n). 2/10 lượt bấm không phải tín hiệu — đó là nhiễu.

## Khảo sát

Mẫu đầy đủ 3 ngôn ngữ: `research/survey-template.md`. Nguyên tắc:
- Hỏi **hành vi đã xảy ra** ("lần gần nhất bạn tổ chức…"), không hỏi "bạn có muốn…".
- Một câu về **giá** (4 câu Van Westendorp) để biết khoảng giá chấp nhận được.
- Câu cuối: email để dùng thử / phỏng vấn (không bắt buộc).
- File CSV xuất ra để trong `research/raw/` (không lên git); `python studio.py survey research/raw/x.csv` để đếm.

## Phỏng vấn (5–10 người là đủ để thấy mẫu)

Kịch bản: `research/interview-script.md`. Theo tinh thần *The Mom Test*: hỏi về quá khứ cụ thể, không giới thiệu
tool trước khi họ kể xong, không hỏi "bạn có mua không".

## Ra quyết định

| Kết quả | Hành động |
|---|---|
| NÊN LÀM TIẾP ở ≥ 1 ngôn ngữ | Làm bộ cài, tìm 5–10 người dùng thử thật, đo thời gian thật → playbook 05 |
| CHƯA ĐẠT nhưng comment nói rõ nhu cầu khác | Đổi góc định vị / đổi tính năng chính, chạy lại 2–3 bài |
| CHƯA ĐỦ DỮ LIỆU | Tăng reach: thêm group, thêm ngôn ngữ, chạy quảng cáo nhỏ |
| Nhiều reach, không ai đăng ký | Dừng hoặc xoay — nỗi đau chưa đủ lớn |

Trang **Phân tích nhu cầu** để AI đọc số liệu + comment và đề xuất bước tiếp theo — nhưng quyết định là của bạn.
