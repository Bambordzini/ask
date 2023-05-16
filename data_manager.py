import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    connection = psycopg2.connect(
        dbname=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        host=os.environ.get('DB_HOST'),
        port=os.environ.get('DB_PORT'),
        cursor_factory=psycopg2.extras.RealDictCursor 
    )

    return connection


def get_question(question_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM questions WHERE id = %s", (question_id,))
    question = cursor.fetchone()

    connection.close()
    return question

def add_question(title, message):
    with get_connection() as connection:
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            INSERT INTO questions (title, message, submission_time)
            VALUES (%s, %s, NOW());
        """, (title, message))
        connection.commit()


def get_question_id_by_answer_id(answer_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT question_id FROM answers WHERE id = %s", (answer_id,))
    result = cursor.fetchone()

    connection.close()

    if result:
        return result['question_id']
    return None


def update_question(question_id, question_data):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE questions
        SET title = %s, message = %s
        WHERE id = %s
    """, (question_data['title'], question_data['message'], question_id))

    connection.commit()
    connection.close()

# Kod do obsługi odpowiedzi
def get_answers_for_question(question_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM answers
        WHERE question_id = %s
    """, (question_id,))

    answers = cursor.fetchall()
    connection.close()
    return answers

def add_answer(answer_data):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO answers (question_id, message, submission_time)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (answer_data['question_id'], answer_data['message'], answer_data['submission_time']))

    answer_id = cursor.fetchone()['id']
    connection.commit()
    connection.close()

    return answer_id

def update_answer(answer_id, answer_data):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE answers
        SET message = %s
        WHERE id = %s
    """, (answer_data['message'], answer_id))

    connection.commit()
    connection.close()

# Kod do obsługi komentarzy
def get_comments_for_question(question_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM comments
        WHERE question_id = %s
    """, (question_id,))

    comments = cursor.fetchall()
    connection.close()
    return comments

def get_comments_for_answer(answer_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM comments
        WHERE answer_id = %s
    """, (answer_id,))

    comments = cursor.fetchall()
    connection.close()
    return comments

def add_comment(comment_data):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO comments (question_id, answer_id, message, submission_time)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (comment_data.get('question_id'), comment_data.get('answer_id'), comment_data['message'], comment_data['submission_time']))

    comment_id = cursor.fetchone()['id']
    connection.commit()
    connection.close()

    return comment_id

def get_comment(comment_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM comments
        WHERE id = %s
    """, (comment_id,))

    comment = cursor.fetchone()
    connection.close()
    return comment

def update_comment(comment_id, comment_data):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE comments
        SET message = %s
        WHERE id = %s
    """, (comment_data['message'], comment_id))

    connection.commit()
    connection.close()

def delete_comment(comment_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM comments
        WHERE id = %s
    """, (comment_id,))

    connection.commit()
    connection.close()

def get_tags_for_question(question_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT tag.id, tag.name
    FROM tag
    JOIN question_tag ON tag.id = question_tag.tag_id
    WHERE question_tag.question_id = %s
""", (question_id,))


    tags = cursor.fetchall()
    connection.close()
    return tags

def add_tag_to_question(question_id, tag_name):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO tag (name)
    VALUES (%s)
    ON CONFLICT (name)
    DO NOTHING
    RETURNING id
""", (tag_name,))

    tag_id = cursor.fetchone()
    if tag_id is None:
        cursor.execute("""
            SELECT id FROM tag
            WHERE name = %s
    """, (tag_name,))
    tag_id = cursor.fetchone()

    cursor.execute("""
    INSERT INTO question_tag (question_id, tag_id)
    VALUES (%s, %s)
""", (question_id, tag_id['id']))


    connection.commit()
    connection.close()

def remove_tag_from_question(question_id, tag_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    DELETE FROM question_tag
    WHERE question_id = %s AND tag_id = %s
""", (question_id, tag_id))


    connection.commit()
    connection.close()

def get_all_questions():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM question
        ORDER BY submission_time DESC
    """)

    questions = cursor.fetchall()
    connection.close()

    return questions

def search_questions(search_query):
    connection = get_connection()
    cursor = connection.cursor()

    search_query = f"%{search_query}%"
    cursor.execute("""
        SELECT * FROM question
        WHERE title LIKE %s OR message LIKE %s
        ORDER BY submission_time DESC
    """, (search_query, search_query))

    questions = cursor.fetchall()
    connection.close()

    return questions

def get_tags():
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM tag")
    
    tags = cursor.fetchall()
    connection.close()
    
    return tags


def add_tag(tag_name):
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("INSERT INTO tag (name) VALUES (%s)", (tag_name,))
    
    connection.commit()
    connection.close()


def delete_tag(tag_id):
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("DELETE FROM tag WHERE id = %s", (tag_id,))
    
    connection.commit()
    connection.close()
