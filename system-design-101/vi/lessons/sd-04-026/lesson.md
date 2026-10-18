# Sáu mô hình dữ liệu: một cửa hàng nhỏ, sáu cách xếp

**Sáu cái tên này không cùng một tầng.** Bảng phẳng, phân cấp, mạng và quan hệ là cách một hệ quản trị nhìn dữ liệu. Sao và bông tuyết là cách xếp các bảng quan hệ cho việc phân tích. Để so, bài dựng cùng một cửa hàng nhỏ (hai khách, ba sản phẩm, bốn món hàng) theo từng cách, rồi hỏi hai câu: một sự việc bị lưu mấy lần, và đi từ một sản phẩm tới người mua có dễ không.

![Ba khung dọc. Khung một, bốn cách hệ quản trị nhìn dữ liệu: bảng phẳng, một bảng duy nhất; phân cấp, khách dẫn tới đơn dẫn tới món, mỗi bản ghi một cha; mạng, một món có hai cha là đơn và sản phẩm; quan hệ, mỗi sự việc lưu một lần nối bằng khóa. Khung hai, hai cách xếp bảng quan hệ để phân tích: sao, bảng bán hàng ở giữa và mỗi chiều một bảng; bông tuyết, chiều sản phẩm tách thành sản phẩm, danh mục, ngành. Khung ba, kết quả đo trên bốn món hàng: bảng phẳng sửa sót một dòng làm khách An ở hai thành phố; phân cấp phải đọc cả 4 món để biết ai mua ấm trà; mạng theo con trỏ chỉ đọc 2 món; hỏi theo ngành, sao cần 1 phép nối và lưu chữ Gia dụng 3 lần, bông tuyết cần 3 phép nối và lưu 1 lần.](../../diagrams/sd-04-026-main.svg)

## Từ viết tắt

- **SQL** (Structured Query Language) — ngôn ngữ truy vấn có cấu trúc: ngôn ngữ chuẩn để hỏi và ghi dữ liệu trong cơ sở dữ liệu quan hệ; SQLite là hệ cơ sở dữ liệu nhỏ dùng nó, chạy ngay trong Python.
- **OLAP** (OnLine Analytical Processing) — xử lý phân tích trực tuyến: kiểu công việc tổng hợp nhiều dữ liệu để báo cáo, như doanh thu theo ngành hàng từng tháng.

## Đọc hình

Phép thử chạy bằng SQLite trong Python 3.13 ngày 2026-10-18; mã ở phần "Xem sâu hơn".

1. **Bảng phẳng.** Mỗi dòng là một món trong một đơn, kèm tên và thành phố của khách. Chữ "Huế" bị ghi ở 3 dòng. Sửa thành phố của An mà sót một dòng thì bảng nói An ở cả Huế lẫn Đà Nẵng: không có chỗ nào giữ sự thật duy nhất.
2. **Phân cấp.** Dữ liệu là một cây: khách chứa đơn, đơn chứa món, mỗi bản ghi có đúng một cha. Hỏi theo chiều cây (đơn của An) thì nhanh. Hỏi ngược chiều ("ai mua ấm trà?") thì phải đọc cả 4 món, và tên sản phẩm bị chép vào mỗi đơn có nó.
3. **Mạng.** Cho phép một bản ghi có nhiều cha: mỗi món vừa thuộc một đơn vừa thuộc một sản phẩm. Từ "ấm trà" đi theo con trỏ chỉ đọc 2 món. Cái giá là chương trình phải biết sẵn đường đi giữa các bản ghi.
4. **Quan hệ.** Khách, sản phẩm, đơn và món là bốn bảng, nối với nhau bằng khóa. Thành phố của An nằm ở đúng một dòng, sửa một lần là xong. Câu hỏi nào cũng viết được bằng SQL mà không cần biết trước đường đi; ở đây "ai mua ấm trà" cần ba phép nối.
5. **Sao và bông tuyết.** Đều là bảng quan hệ, xếp cho công việc OLAP: một bảng sự kiện bán hàng ở giữa, các bảng chiều (sản phẩm, thời gian…) quanh nó. Bảng chiều kiểu sao gộp sản phẩm, danh mục và ngành vào một bảng: hỏi theo ngành cần 1 phép nối, nhưng chữ "Gia dụng" lặp ở 3 dòng. Kiểu bông tuyết tách ra ba bảng: lưu "Gia dụng" 1 lần, đổi lại phải nối 3 lần. Hai cách cho cùng đáp án (8 món).

## Giới hạn cần nhớ

Bốn món hàng chỉ đủ để thấy dữ liệu bị lặp ở đâu và đường đi dài hay ngắn, không nói gì về tốc độ trên dữ liệu thật. Phân cấp và mạng ở đây được giả lập bằng cấu trúc của Python, không phải hệ quản trị thật dùng các mô hình đó. Lặp dữ liệu không phải lúc nào cũng xấu: kiểu sao chấp nhận lặp để câu hỏi phân tích ngắn và ít phép nối.

## Nhìn hình thử trả lời

Bảng chiều sản phẩm của bạn có 50.000 dòng, và tên các ngành hàng đổi vài tháng một lần. Bạn nghiêng về kiểu sao hay bông tuyết, và cái giá của lựa chọn đó là gì?

<details>
<summary>Xem đáp án</summary>

Kiểu sao giữ câu hỏi ngắn (ít phép nối), nhưng mỗi lần đổi tên một ngành phải sửa mọi dòng sản phẩm thuộc ngành đó, và sửa sót là ra hai tên cho cùng một ngành, đúng lỗi của bảng phẳng. Kiểu bông tuyết chỉ sửa một dòng ở bảng ngành, đổi lại mọi câu hỏi theo ngành phải nối thêm bảng.
Không có đáp án duy nhất: cân xem việc sửa hay việc hỏi xảy ra nhiều hơn.

</details>

<details>
<summary>Xem sâu hơn: mã phép thử</summary>

```python
import sqlite3
db = sqlite3.connect(":memory:")
q = lambda sql: db.execute(sql).fetchall()

# Bảng phẳng
db.executescript("""
create table flat(order_id, customer, city, product, category, qty);
insert into flat values (1,'An','Huế','Ấm trà','Bếp',1),(1,'An','Huế','Chén','Bếp',4),
 (2,'An','Huế','Đèn bàn','Nhà',1),(3,'Bình','Vinh','Ấm trà','Bếp',2);
""")
print(q("select count(*) from flat where city='Huế'"))                     # [(3,)]
db.execute("update flat set city='Đà Nẵng' where customer='An' and order_id=1")  # sót đơn 2
print(q("select distinct city from flat where customer='An'"))             # Đà Nẵng và Huế

# Phân cấp: khách -> đơn -> món; mạng: món có hai cha
tree = {"An": {1: ["Ấm trà", "Chén"], 2: ["Đèn bàn"]}, "Bình": {3: ["Ấm trà"]}}
print([c for c, orders in tree.items() for items in orders.values() if "Ấm trà" in items])  # đọc cả 4 món
items = [{"order": 1, "product": "Ấm trà"}, {"order": 1, "product": "Chén"},
         {"order": 2, "product": "Đèn bàn"}, {"order": 3, "product": "Ấm trà"}]
owner, by_product = {1: "An", 2: "An", 3: "Bình"}, {}
for i, it in enumerate(items): by_product.setdefault(it["product"], []).append(i)
print(sorted({owner[items[i]["order"]] for i in by_product["Ấm trà"]}), len(by_product["Ấm trà"]))  # 2 món

# Quan hệ
db.executescript("""
create table customers(id integer primary key, name, city);
create table products(id integer primary key, name, category);
create table orders(id integer primary key, customer_id);
create table order_items(order_id, product_id, qty);
insert into customers values (1,'An','Huế'),(2,'Bình','Vinh');
insert into products values (1,'Ấm trà','Bếp'),(2,'Chén','Bếp'),(3,'Đèn bàn','Nhà');
insert into orders values (1,1),(2,1),(3,2);
insert into order_items values (1,1,1),(1,2,4),(2,3,1),(3,1,2);
""")
print(q("""select distinct c.name from customers c join orders o on o.customer_id=c.id
 join order_items i on i.order_id=o.id join products p on p.id=i.product_id where p.name='Ấm trà'"""))

# Sao và bông tuyết
db.executescript("""
create table dim_product_star(id integer primary key, name, category, department);
insert into dim_product_star values (1,'Ấm trà','Bếp','Gia dụng'),(2,'Chén','Bếp','Gia dụng'),(3,'Đèn bàn','Nhà','Gia dụng');
create table dim_department(id integer primary key, name);
create table dim_category(id integer primary key, name, department_id);
create table dim_product_snow(id integer primary key, name, category_id);
insert into dim_department values (1,'Gia dụng');
insert into dim_category values (1,'Bếp',1),(2,'Nhà',1);
insert into dim_product_snow values (1,'Ấm trà',1),(2,'Chén',1),(3,'Đèn bàn',2);
create table fact_sales(product_id, qty);
insert into fact_sales select product_id, qty from order_items;
""")
print(q("select d.department, sum(f.qty) from fact_sales f join dim_product_star d on d.id=f.product_id group by 1"))
print(q("""select dep.name, sum(f.qty) from fact_sales f join dim_product_snow p on p.id=f.product_id
 join dim_category c on c.id=p.category_id join dim_department dep on dep.id=c.department_id group by 1"""))
```

Hai câu hỏi cuối cùng in `[('Gia dụng', 8)]`. Câu hỏi "ai mua ấm trà" in An và Bình ở cả ba mô hình phân cấp, mạng và quan hệ; chỉ số bản ghi phải đọc và số chỗ lưu một sự việc là khác.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/top-6-database-models.md): sáu mô hình phẳng, phân cấp, quan hệ, sao, bông tuyết và mạng; nguồn ghi mô hình quan hệ do E. F. Codd đưa ra năm 1970.

Phép thử chạy bằng SQLite 3.45.1 trong Python 3.13.16 ngày 2026-10-18 trên máy biên soạn. Cách chia sáu tên thành hai tầng là cách trình bày của người biên soạn. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.
