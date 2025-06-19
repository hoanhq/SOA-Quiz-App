import requests
from bs4 import BeautifulSoup
import json
import time
import csv
import os
from datetime import datetime
import random

# --- CẤU HÌNH ---
BASE_URL = 'http://203.162.10.109/Webcms'
LOGIN_URL = f'{BASE_URL}/Login/Check'
QUIZ_URL = f'{BASE_URL}/QuizExam/Index'

# File chứa danh sách username và password
DATA_FILE = 'cnpm05.csv'

# Tổng số câu hỏi cần lấy
TOTAL_QUESTIONS = 40

# Thời gian timeout giữa các lần đăng nhập (10 phút = 600 giây)
TIMEOUT_BETWEEN_ACCOUNTS = 600

# Số file bắt đầu
STARTING_FILE_NUMBER = 82

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
]

# --- FUNCTIONS ---

def read_accounts_from_csv(filename):
    """Đọc danh sách tài khoản từ file CSV và random thứ tự"""
    accounts = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'].strip() and row['password'].strip():
                    accounts.append({
                        'username': row['username'].strip(),
                        'password': row['password'].strip()
                    })
        random.shuffle(accounts)  # Random thứ tự tài khoản
        print(f"Đã đọc {len(accounts)} tài khoản từ file {filename}")
        return accounts
    except FileNotFoundError:
        print(f"Không tìm thấy file {filename}")
        return []
    except Exception as e:
        print(f"Lỗi khi đọc file {filename}: {e}")
        return []

def get_next_output_filename():
    """Tìm tên file output tiếp theo"""
    file_number = STARTING_FILE_NUMBER
    while True:
        filename = f'quiz_data_{file_number}.json'
        if not os.path.exists(filename):
            return filename, file_number
        file_number += 1

def random_headers(session):
    """Sinh headers HTTP ngẫu nhiên cho mỗi request"""
    headers = {
        'Referer': BASE_URL,
        'User-Agent': session.headers.get('User-Agent', random.choice(USER_AGENTS)),
        'Accept-Language': random.choice([
            'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'en-US,en;q=0.9,vi;q=0.8',
            'vi,en-US;q=0.9,en;q=0.8',
        ]),
        'Accept-Encoding': random.choice(['gzip, deflate', 'gzip, deflate, br']),
        'Accept': random.choice([
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'text/html,application/xml;q=0.9,*/*;q=0.8',
        ]),
        'Connection': 'keep-alive',
        'DNT': random.choice(['1', '0']),
        'Cache-Control': random.choice(['no-cache', 'max-age=0', 'no-store']),
        'Pragma': random.choice(['no-cache', '']),
    }
    return headers

def visit_extra_pages(session):
    """Truy cập một số trang phụ để giả lập hành vi người dùng"""
    extra_pages = [
        f"{BASE_URL}/Home",
        f"{BASE_URL}/User/Password",
    ]
    for url in random.sample(extra_pages, k=random.randint(1, len(extra_pages))):
        try:
            session.get(url, headers=random_headers(session), timeout=10)
            time.sleep(random.uniform(0.3, 1.2))
        except Exception:
            pass

def login_account(session, username, password):
    """Đăng nhập với một tài khoản"""
    print(f"Đang đăng nhập với tài khoản {username}...")

    # Dữ liệu form đăng nhập
    login_data = {
        'txtUser': username,
        'txtPassword': password
    }

    headers = random_headers(session)

    try:
        # Gửi yêu cầu POST để đăng nhập
        response_login = session.post(LOGIN_URL, data=login_data, headers=headers)
        response_login.raise_for_status()

        # Kiểm tra xem đăng nhập có thành công không
        if username not in response_login.text:
            print(f"Đăng nhập thất bại với tài khoản {username}!")
            return False

        print(f"Đăng nhập thành công với tài khoản {username}!")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Lỗi trong quá trình đăng nhập tài khoản {username}: {e}")
        return False

def crawl_quiz_data(session, username):
    """Crawl dữ liệu quiz cho một tài khoản với random thứ tự câu hỏi và có thể bỏ qua một số câu"""
    all_questions_data = []
    print(f"\nBắt đầu lấy dữ liệu của {TOTAL_QUESTIONS} câu hỏi cho tài khoản {username}...")

    # Random thứ tự câu hỏi và có thể bỏ qua 1-3 câu (giả lập người dùng không làm hết)
    question_indices = list(range(1, TOTAL_QUESTIONS + 1))
    random.shuffle(question_indices)
    num_skip = random.randint(1, 3)
    skip_indices = set(random.sample(question_indices, k=num_skip))
    for i in question_indices:
        if i in skip_indices:
            print(f"Bỏ qua câu hỏi số {i} (giả lập người dùng không làm hết)")
            continue
        question_url = f"{QUIZ_URL}?qIndex={i}"
        print(f"Đang lấy dữ liệu câu hỏi số {i}...")

        try:
            headers = random_headers(session)
            response_quiz = session.get(question_url, headers=headers)
            response_quiz.raise_for_status()

            soup = BeautifulSoup(response_quiz.text, 'html.parser')

            # Trích xuất dữ liệu câu hỏi và đáp án
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
            correct_answer = correct_answer_text.split(':')[-1].strip()

            question_data = {
                "question_number": i,
                "question_content": question,
                "options": answers,
                "correct_answer": correct_answer,
                "crawled_by": username,
                "crawled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            all_questions_data.append(question_data)

            print(f"  -> Thành công: {question[:60]}...")

            time.sleep(random.uniform(0.7, 2.5))

            # Thỉnh thoảng truy cập trang phụ giữa các câu hỏi
            if random.random() < 0.18:
                visit_extra_pages(session)

        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi lấy câu hỏi số {i}: {e}")
        except Exception as e:
            print(f"Lỗi khi xử lý dữ liệu câu hỏi số {i}: {e}")

    return all_questions_data

def save_quiz_data(data, filename, username):
    """Lưu dữ liệu quiz vào file JSON"""
    if data:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"\nHoàn tất! Dữ liệu từ tài khoản {username} đã được lưu vào file {filename}")
            return True
        except Exception as e:
            print(f"Lỗi khi lưu file {filename}: {e}")
            return False
    else:
        print(f"\nKhông có dữ liệu nào được lấy từ tài khoản {username}. File không được tạo.")
        return False

# --- BẮT ĐẦU SCRIPT CHÍNH ---

def main():
    """Hàm chính để chạy toàn bộ quá trình crawl"""
    print("=" * 60)
    print("BẮT ĐẦU QUẤY TRÌNH CRAWL DỮ LIỆU QUIZ")
    print("=" * 60)

    # Đọc danh sách tài khoản từ file CSV
    accounts = read_accounts_from_csv(DATA_FILE)
    if not accounts:
        print("Không có tài khoản nào để xử lý. Thoát chương trình.")
        return

    print(f"Sẽ xử lý {len(accounts)} tài khoản")
    print(f"Thời gian chờ giữa các tài khoản: {TIMEOUT_BETWEEN_ACCOUNTS} giây ({TIMEOUT_BETWEEN_ACCOUNTS//60} phút)")

    successful_crawls = 0
    failed_crawls = 0

    for index, account in enumerate(accounts, 1):
        username = account['username']
        password = account['password']

        print(f"\n{'='*60}")
        print(f"XỬ LÝ TÀI KHOẢN {index}/{len(accounts)}: {username}")
        print(f"{'='*60}")

        # Khởi tạo session mới cho mỗi tài khoản
        session = requests.Session()
        session.headers.update({
            'User-Agent': random.choice(USER_AGENTS)
        })

        # Truy cập trang phụ trước khi login (giả lập người dùng)
        if random.random() < 0.5:
            visit_extra_pages(session)

        # Thử đăng nhập
        if login_account(session, username, password):
            # Lấy tên file output
            output_filename, file_number = get_next_output_filename()

            # Crawl dữ liệu
            quiz_data = crawl_quiz_data(session, username)

            # Lưu dữ liệu
            if save_quiz_data(quiz_data, output_filename, username):
                successful_crawls += 1
                print(f"✅ Thành công crawl tài khoản {username} -> {output_filename}")
            else:
                failed_crawls += 1
                print(f"❌ Thất bại khi lưu dữ liệu cho tài khoản {username}")
        else:
            failed_crawls += 1
            print(f"❌ Thất bại đăng nhập tài khoản {username}")

        # Đóng session
        session.close()

        # Random delay sau mỗi tài khoản (ngoài TIMEOUT_BETWEEN_ACCOUNTS)
        if index < len(accounts):
            extra_delay = random.uniform(2, 8)
            print(f"\n⏰ Chờ {TIMEOUT_BETWEEN_ACCOUNTS} giây + {extra_delay:.1f} giây random trước khi xử lý tài khoản tiếp theo...")
            time.sleep(TIMEOUT_BETWEEN_ACCOUNTS + extra_delay)

    # Tổng kết
    print(f"\n{'='*60}")
    print("TỔNG KẾT")
    print(f"{'='*60}")
    print(f"Tổng số tài khoản xử lý: {len(accounts)}")
    print(f"Thành công: {successful_crawls}")
    print(f"Thất bại: {failed_crawls}")
    print(f"Tỷ lệ thành công: {(successful_crawls/len(accounts)*100):.1f}%")
    print("Hoàn tất toàn bộ quá trình!")

if __name__ == "__main__":
    main()