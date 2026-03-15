# Quy chuẩn làm việc và Workflow GitHub

Tài liệu này quy định **quy chuẩn làm việc và quy trình phát triển code của nhóm**.
Tất cả thành viên tham gia project cần tuân thủ để đảm bảo code ổn định, dễ quản lý và tránh xung đột khi làm việc nhóm.

---

# 1. Cấu trúc nhánh (Branch Structure)

Repository sử dụng cấu trúc nhánh như sau:

* **main**

  * Nhánh chính của project
  * Luôn ở trạng thái ổn định
  * Chỉ nhận code đã hoàn thiện từ `dev`

* **dev**

  * Nhánh phát triển chính
  * Tất cả các chức năng mới sẽ được merge vào đây trước

* **feature/<tên-tính-năng>**

  * Nhánh dùng để phát triển một tính năng mới

* **fix/<tên-lỗi>**

  * Nhánh dùng để sửa lỗi

* **docs/<nội-dung>**

  * Nhánh dùng để cập nhật tài liệu

Ví dụ:

```
main
dev
feature/a-star
feature/dijkstra
feature/map-visualization
fix/map-loading
docs/update-readme
```

---

# 2. Quy tắc làm việc chung

Tất cả thành viên cần tuân thủ các quy tắc sau:

1. **Không commit trực tiếp vào `main`**
2. **Không commit trực tiếp vào `dev`**
3. Mỗi tính năng phải được phát triển trên **một branch riêng**
4. Mọi code phải được merge thông qua **Pull Request**
5. Trước khi bắt đầu làm việc phải **pull code mới nhất**
6. Không commit các file không cần thiết (log, build, dữ liệu lớn, v.v.)

---

# 3. Quy trình làm việc tổng thể (Full Development Workflow)

Luồng làm việc chuẩn của project:

```
Clone repository
      ↓
Checkout sang nhánh dev
      ↓
Pull code mới nhất
      ↓
Tạo branch feature mới
      ↓
Code và commit
      ↓
Push branch lên GitHub
      ↓
Tạo Pull Request
      ↓
Review code
      ↓
Merge vào dev
```

Sau khi `dev` ổn định:

```
dev → merge → main
```

---

# 4. Quy trình làm việc chi tiết

## Bước 1: Clone repository

Clone project từ GitHub về máy:

```
git clone <repo-url>
cd <repo-name>
```

Ví dụ:

```
git clone https://github.com/team/project-ai.git
cd project-ai
```

Lệnh `clone` sẽ tải toàn bộ source code và lịch sử commit về máy.

---

# Bước 2: Checkout sang nhánh dev

Sau khi clone, chuyển sang nhánh `dev`:

```
git checkout dev
git pull origin dev
```

Ý nghĩa:

* `checkout dev`: chuyển sang nhánh phát triển
* `pull origin dev`: cập nhật code mới nhất từ repository

Việc này giúp đảm bảo bạn luôn làm việc với **version mới nhất của project**.

---

# Bước 3: Tạo nhánh mới để phát triển tính năng

Không làm việc trực tiếp trên `dev`.
Mỗi tính năng phải được phát triển trên một branch riêng.

```
git checkout -b feature/<ten-tinh-nang>
```

Ví dụ:

```
git checkout -b feature/a-star-algorithm
```

Branch này sẽ chứa toàn bộ code liên quan tới tính năng đó.

---

# Bước 4: Code và Commit

Sau khi viết code xong một phần chức năng:

```
git add .
git commit -m "feat: implement A* pathfinding"
```

Ý nghĩa:

* `git add` đưa file vào vùng chuẩn bị commit
* `git commit` tạo một bản ghi thay đổi của code

Commit message phải rõ ràng.

Ví dụ commit tốt:

```
feat: implement A* algorithm
fix: correct heuristic calculation
refactor: optimize graph structure
docs: update project README
```

---

# Bước 5: Push code lên GitHub

Sau khi commit, code vẫn chỉ nằm trên máy local.
Cần push lên GitHub:

```
git push origin feature/a-star-algorithm
```

Lệnh này sẽ:

* upload code lên repository
* tạo branch đó trên GitHub

Sau khi push xong, các thành viên khác có thể xem và review code.

---

# Bước 6: Tạo Pull Request

Trên GitHub, tạo **Pull Request** để yêu cầu merge code:

```
feature/a-star-algorithm → dev
```

Pull Request cho phép:

* review code
* thảo luận thay đổi
* phát hiện bug trước khi merge

---

# 5. Quy chuẩn Pull Request

Một Pull Request cần có:

### Tiêu đề rõ ràng

```
[Feature] Implement A* pathfinding
```

### Mô tả thay đổi

Ví dụ:

```
- Implement A* search algorithm
- Add heuristic function
- Add path reconstruction
- Test with sample map
```

---

# 6. Điều kiện trước khi Merge

Pull Request chỉ được merge khi:

* Code compile được
* Không có lỗi runtime
* Không phá vỡ chức năng cũ
* Đã được ít nhất một người review

---

# 7. Quy tắc Commit Message

Format commit message:

```
<type>: <description>
```

Các loại commit phổ biến:

| Type     | Ý nghĩa           |
| -------- | ----------------- |
| feat     | thêm chức năng    |
| fix      | sửa bug           |
| docs     | cập nhật tài liệu |
| refactor | cải thiện code    |
| style    | chỉnh format code |
| test     | thêm test         |
| chore    | thay đổi cấu hình |

---

# 8. File cần bỏ qua (.gitignore)

Không commit các file sau:

```
node_modules/
build/
dist/
.env
*.log
.DS_Store
```

---

# 9. Ví dụ Workflow hoàn chỉnh

Ví dụ khi phát triển thuật toán A*:

```
git checkout dev
git pull origin dev

git checkout -b feature/a-star

(code...)

git add .
git commit -m "feat: implement A* algorithm"

git push origin feature/a-star
```

Sau đó:

1. Tạo Pull Request
2. Review code
3. Merge vào `dev`

---

# 10. Lưu ý khi làm việc nhóm

* Luôn pull code trước khi bắt đầu làm việc
* Không sửa code của người khác khi chưa thảo luận
* Commit thường xuyên với message rõ ràng
* Không push code chưa chạy được
* Luôn sử dụng Pull Request khi merge

---

# Kết luận

Tuân thủ quy chuẩn này giúp:

* Giảm conflict khi làm việc nhóm
* Quản lý code rõ ràng
* Dễ review và kiểm soát chất lượng code
* Giữ repository luôn ổn định
