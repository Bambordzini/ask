from flask import Flask, render_template, request, redirect, url_for
from data_manager import (
    get_all_questions, get_question, add_question,
    update_question, get_answers_for_question, add_answer, update_answer,
    get_comments_for_question, get_comments_for_answer, add_comment, update_comment,
    delete_comment, search_questions, get_tags, add_tag, delete_tag,  get_question_id_by_answer_id,
)
from dotenv import load_dotenv


from datetime import datetime

app = Flask(__name__)
load_dotenv()
@app.route("/")
def index():
    return redirect(url_for('list_questions'))



@app.route("/list")
def list_questions():
    questions = get_all_questions()
    return render_template("list.html", questions=questions)

@app.route("/question/<int:question_id>")
def show_question(question_id):
    question = get_question(question_id)
    answers = get_answers_for_question(question_id)
    comments = get_comments_for_question(question_id)
    tags = get_tags(question_id)
    return render_template("show_question.html", question=question, answers=answers, comments=comments, tags=tags)

@app.route("/question/new", methods=["GET", "POST"])
def new_question():
    if request.method == "POST":
        title = request.form["title"]
        message = request.form["message"]
        add_question(title, message)
        return redirect(url_for("list_questions"))
    return render_template("new_question.html")


@app.route("/question/<int:question_id>/edit", methods=["GET", "POST"])
def edit_question(question_id):
    question = get_question(question_id)
    if request.method == "POST":
        title = request.form["title"]
        message = request.form["message"]
        update_question(question_id, title, message)
        return redirect(url_for("show_question", question_id=question_id))
    return render_template("edit_question.html", question=question)

@app.route("/question/<int:question_id>/answer", methods=["POST"])
def new_answer(question_id):
    message = request.form["message"]
    add_answer(question_id, message)
    return redirect(url_for("show_question", question_id=question_id))

@app.route("/answer/<int:answer_id>/edit", methods=["GET", "POST"])
def edit_answer(answer_id):
    answer = get_answer(answer_id)
    if request.method == "POST":
        message = request.form["message"]
        update_answer(answer_id, message)
        return redirect(url_for("show_question", question_id=answer["question_id"]))
    return render_template("edit_answer.html", answer=answer)

@app.route("/question/<int:question_id>/new-comment", methods=["GET", "POST"])
def new_comment_to_question(question_id):
    if request.method == "POST":
        message = request.form["message"]
        add_comment(question_id=question_id, message=message)
        return redirect(url_for("show_question", question_id=question_id))
    return render_template("new_comment.html")

@app.route("/answer/<int:answer_id>/new-comment", methods=["GET", "POST"])
def new_comment_to_answer(answer_id):
    if request.method == "POST":
        message = request.form["message"]
        add_comment({"answer_id": answer_id, "message": message, "submission_time": datetime.now()})
        question_id = get_question_id_by_answer_id(answer_id)
        return redirect(url_for("show_question", question_id=question_id))
    return render_template("new_comment.html")

@app.route("/comment/<int:comment_id>/edit", methods=["GET", "POST"])
def edit_comment(comment_id):
    comment = get_comment(comment_id)
    if request.method == "POST":
        message = request.form["message"]
        update_comment(comment_id, message)
        if comment["question_id"]:
            return redirect(url_for("show_question", question_id=comment["question_id"]))
        elif comment["answer_id"]:
            question_id = get_question_id_by_answer_id(comment["answer_id"])
            return redirect(url_for("show_question", question_id=question_id))
    return render_template("edit_comment.html", comment=comment)

@app.route("/comments/<int:comment_id>/delete", methods=["POST"])
def delete_comment(comment_id):
    comment = get_comment(comment_id)
    question_id = comment["question_id"] or get_question_id_by_answer_id(comment["answer_id"])
    delete_comment(comment_id)
    return redirect(url_for("show_question", question_id=question_id))

@app.route("/search")
def search():
    search_term = request.args.get("q", "")
    questions = search_questions(search_term)
    return render_template("search_results.html", questions=questions, search_term=search_term)

@app.route("/question/<int:question_id>/new-tag", methods=["GET", "POST"])
def new_tag_to_question(question_id):
    if request.method == "POST":
        tag_name = request.form["tag_name"]
        add_tag(question_id, tag_name)
        return redirect(url_for("show_question", question_id=question_id))
    return render_template("new_tag.html")

@app.route("/question/<int:question_id>/tag/<int:tag_id>/delete", methods=["POST"])
def delete_tag_from_question(question_id, tag_id):
    delete_tag(question_id, tag_id)
    return redirect(url_for("show_question", question_id=question_id))

if __name__ == "__main__":
    app.run(debug=True)

