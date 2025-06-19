import json
import os

all_questions = []
seen_question_contents = set()

# Giả sử bạn vẫn có các file từ quiz_data_1.json đến quiz_data_9.json
# với định dạng mới này.
for i in range(1, 145):
    file_name = f'quiz_data_{i}.json'
    
    # Kiểm tra xem file có tồn tại không
    if not os.path.exists(file_name):
        print(f"Tệp {file_name} không tồn tại, bỏ qua.")
        continue

    try:
        # Mở và đọc từng file JSON
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Lặp qua từng câu hỏi trong file
            for question_data in data:
                # Lấy nội dung câu hỏi từ khóa "question_content"
                question_content = question_data.get("question_content")
                
                # Nếu câu hỏi có nội dung và chưa từng xuất hiện,
                # thì thêm vào danh sách và đánh dấu là đã thấy
                if question_content and question_content not in seen_question_contents:
                    seen_question_contents.add(question_content)
                    all_questions.append(question_data)

    except (json.JSONDecodeError, IOError) as e:
        print(f"Lỗi khi đọc tệp {file_name}: {e}")

# Ghi danh sách câu hỏi duy nhất vào file mới
try:
    with open('quiz_data.json', 'w', encoding='utf-8') as f:
        # indent=4 để file JSON được định dạng đẹp mắt, dễ đọc
        json.dump(all_questions, f, ensure_ascii=False, indent=4)
        
    # In ra tổng số câu hỏi đã được lưu
    print(f"\nĐã xử lý xong!")
    print(f"Tổng số câu hỏi duy nhất đã được lưu vào file quiz_data.json là: {len(all_questions)}")

except IOError as e:
    print(f"Lỗi khi ghi file quiz_data.json: {e}")