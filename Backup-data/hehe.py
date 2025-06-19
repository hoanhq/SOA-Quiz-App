import requests
from bs4 import BeautifulSoup
import json

# --- CẤU HÌNH ---
# 1. Mở trình duyệt, đăng nhập vào trang web.
# 2. Mở Developer Tools (nhấn F12).
# 3. Đi tới tab "Network", tải lại trang câu hỏi.
# 4. Tìm yêu cầu tới "Index?qIndex=...", nhấn vào nó.
# 5. Trong phần "Request Headers", tìm dòng "Cookie" và sao chép toàn bộ giá trị của nó vào đây.
SESSION_COOKIE = 'ASP.NET_SessionId=btxt5v1goshc0nyotxkm1nu1' # Ví dụ: 'ASP.NET_SessionId=abcdef123456; .ASPXAUTH=...'

BASE_URL = 'http://203.162.10.109/Webcms/QuizExam/Index'
TOTAL_QUESTIONS = 40 # Lấy từ HTML

# Chuẩn bị header để gửi kèm cookie
headers = {
    'Cookie': SESSION_COOKIE,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

all_questions_data = []

# Vòng lặp để lấy từng câu hỏi
for i in range(1, TOTAL_QUESTIONS + 1):
    url = f"{BASE_URL}?qIndex={i}"
    print(f"Đang lấy dữ liệu câu hỏi số {i}...")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Báo lỗi nếu request không thành công (vd: 404, 500)

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Trích xuất dữ liệu
        question_text_area = soup.select_one('#txtqContent')
        question = question_text_area.get_text(strip=True) if question_text_area else "Không tìm thấy câu hỏi"
        
        answers = {
            'A': soup.select_one('#txtAnswerOne').get_text(strip=True) if soup.select_one('#txtAnswerOne') else '',
            'B': soup.select_one('#txtAnswerTwo').get_text(strip=True) if soup.select_one('#txtAnswerTwo') else '',
            'C': soup.select_one('#txtAnswerThree').get_text(strip=True) if soup.select_one('#txtAnswerThree') else '',
            'D': soup.select_one('#txtAnswerFour').get_text(strip=True) if soup.select_one('#txtAnswerFour') else '',
        }
        
        correct_answer_tag = soup.select_one('#solutionDiv h2')
        correct_answer_text = correct_answer_tag.get_text(strip=True) if correct_answer_tag else ''
        # Trích xuất chữ cái đáp án (vd: từ "ĐÁP ÁN: D" -> "D")
        correct_answer = correct_answer_text.split(':')[-1].strip()

        question_data = {
            "question_number": i,
            "question_content": question,
            "options": answers,
            "correct_answer": correct_answer
        }
        all_questions_data.append(question_data)
        
        # In ra màn hình để theo dõi
        print(f"  -> Thành công: {question[:50]}...")


    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi lấy câu hỏi số {i}: {e}")
    except Exception as e:
        print(f"Lỗi khi xử lý dữ liệu câu hỏi số {i}: {e}")

# Lưu kết quả ra file JSON để dễ sử dụng
with open('quiz_data_9.json', 'w', encoding='utf-8') as f:
    json.dump(all_questions_data, f, ensure_ascii=False, indent=4)

print("\nHoàn tất! Dữ liệu đã được lưu vào file quiz_data.json")