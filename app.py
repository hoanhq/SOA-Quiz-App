# app.py

import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

# Khởi tạo ứng dụng Flask
app = Flask(__name__)
# Cần có một khóa bí mật để sử dụng session
app.secret_key = 'your_super_secret_key_for_quiz'

# Hàm để tải câu hỏi từ file JSON
def load_questions():
    """Tải danh sách câu hỏi từ file quiz_data.json."""
    try:
        with open('quiz_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Tải câu hỏi một lần khi ứng dụng khởi động
quiz_questions = load_questions()

@app.route('/')
def index():
    """Trang chủ, hiển thị giao diện quiz SPA."""
    # Khởi tạo điểm số trong session
    session['score'] = 0
    session['answered_questions'] = []
    return render_template('quiz.html', total_questions=len(quiz_questions))

@app.route('/api/questions')
def get_all_questions():
    """API để lấy tất cả câu hỏi cho client-side rendering."""
    return jsonify({
        'questions': quiz_questions,
        'total': len(quiz_questions)
    })

@app.route('/question')
def question():
    """Redirect cũ để tương thích."""
    return redirect(url_for('index'))

@app.route('/api/submit_answer', methods=['POST'])
def submit_answer():
    """API để submit đáp án và cập nhật điểm số."""
    data = request.json
    question_number = data.get('question_number')
    user_answer = data.get('answer')

    if not question_number or not user_answer:
        return jsonify({'error': 'Thiếu thông tin câu hỏi hoặc đáp án'}), 400

    # Tìm câu hỏi theo question_number
    current_question = None
    for q in quiz_questions:
        if q['question_number'] == question_number:
            current_question = q
            break

    if not current_question:
        return jsonify({'error': 'Không tìm thấy câu hỏi'}), 404

    correct_answer = current_question['correct_answer']
    is_correct = user_answer == correct_answer

    # Kiểm tra xem câu hỏi đã được trả lời chưa
    answered_questions = session.get('answered_questions', [])
    if question_number not in answered_questions:
        # Cập nhật điểm số nếu đúng và chưa trả lời
        if is_correct:
            session['score'] = session.get('score', 0) + 1

        # Đánh dấu câu hỏi đã được trả lời
        answered_questions.append(question_number)
        session['answered_questions'] = answered_questions

    return jsonify({
        'is_correct': is_correct,
        'correct_answer': correct_answer,
        'user_answer': user_answer,
        'current_score': session.get('score', 0)
    })

@app.route('/api/get_final_score')
def get_final_score():
    """API để lấy điểm số cuối cùng."""
    score = session.get('score', 0)
    total_questions = len(quiz_questions)
    return jsonify({
        'score': score,
        'total_questions': total_questions,
        'percentage': round((score / total_questions) * 100, 1) if total_questions > 0 else 0
    })

@app.route('/api/submit_final_score', methods=['POST'])
def submit_final_score():
    """API để lưu điểm số cuối cùng."""
    data = request.json
    score = data.get('score', 0)
    total_questions = data.get('total_questions', 0)
    percentage = data.get('percentage', 0)

    # Lưu vào session
    session['final_score'] = score
    session['final_percentage'] = percentage

    # Ở đây bạn có thể lưu vào database nếu cần
    # save_score_to_database(score, total_questions, percentage)

    return jsonify({'success': True, 'message': 'Điểm số đã được lưu'})

@app.route('/api/reset_quiz', methods=['POST'])
def reset_quiz():
    """API để reset quiz và bắt đầu lại."""
    session.clear()
    session['score'] = 0
    session['answered_questions'] = []
    return jsonify({'success': True})

@app.route('/result')
def result():
    """Trang kết quả (để tương thích với code cũ)."""
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
