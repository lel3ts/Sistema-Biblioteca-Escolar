import os
import sqlite3
from functools import wraps
from datetime import date, timedelta
from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave-de-desenvolvimento-troque-antes-de-publicar")
DB_PATH = os.path.join(os.path.dirname(__file__), "biblioteca.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student'
    );
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        category TEXT,
        isbn TEXT,
        quantity INTEGER NOT NULL DEFAULT 1 CHECK(quantity >= 0)
    );
    CREATE TABLE IF NOT EXISTS loans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        loan_date TEXT NOT NULL,
        due_date TEXT NOT NULL,
        return_date TEXT,
        status TEXT NOT NULL DEFAULT 'Em andamento',
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(book_id) REFERENCES books(id)
    );
    """)
    admin = conn.execute("SELECT id FROM users WHERE email = ?", ("admin@biblioteca.com",)).fetchone()
    if not admin:
        conn.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
            ("Administrador", "admin@biblioteca.com", generate_password_hash("admin123"), "admin")
        )
    conn.commit()
    conn.close()

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Faça login para continuar.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Essa área é exclusiva da administração.", "warning")
            return redirect(url_for("dashboard"))
        return view(*args, **kwargs)
    return wrapped

@app.context_processor
def inject_globals():
    return {"today": date.today().isoformat()}

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            session.clear()
            session.update(user_id=user["id"], name=user["name"], role=user["role"])
            flash(f"Bem-vindo(a), {user['name']}!", "success")
            return redirect(url_for("dashboard"))
        flash("E-mail ou senha incorretos.", "danger")
    return render_template("login.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 4:
            flash("Preencha todos os campos. A senha deve ter pelo menos 4 caracteres.", "warning")
            return render_template("cadastro.html")
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, 'student')",
                (name, email, generate_password_hash(password))
            )
            conn.commit()
            flash("Cadastro realizado! Agora você já pode entrar.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Já existe uma conta cadastrada com esse e-mail.", "danger")
        finally:
            conn.close()
    return render_template("cadastro.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    stats = {
        "books": conn.execute("SELECT COUNT(*) FROM books").fetchone()[0],
        "copies": conn.execute("SELECT COALESCE(SUM(quantity), 0) FROM books").fetchone()[0],
        "loans": conn.execute("SELECT COUNT(*) FROM loans WHERE status = 'Em andamento'").fetchone()[0],
        "users": conn.execute("SELECT COUNT(*) FROM users WHERE role = 'student'").fetchone()[0]
    }
    recent = conn.execute("""
        SELECT loans.*, books.title AS book_title, users.name AS user_name
        FROM loans JOIN books ON books.id = loans.book_id
        JOIN users ON users.id = loans.user_id
        ORDER BY loans.id DESC LIMIT 5
    """).fetchall()
    conn.close()
    return render_template("dashboard.html", stats=stats, recent=recent)

@app.route("/livros", methods=["GET", "POST"])
@login_required
def livros():
    conn = get_db()
    if request.method == "POST":
        if session.get("role") != "admin":
            conn.close()
            flash("Somente a administração pode cadastrar livros.", "warning")
            return redirect(url_for("livros"))
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        category = request.form.get("category", "").strip()
        isbn = request.form.get("isbn", "").strip()
        try:
            quantity = max(0, int(request.form.get("quantity", "1")))
        except ValueError:
            quantity = 1
        if title and author:
            conn.execute("INSERT INTO books (title, author, category, isbn, quantity) VALUES (?, ?, ?, ?, ?)",
                         (title, author, category, isbn, quantity))
            conn.commit()
            flash("Livro cadastrado com sucesso.", "success")
        else:
            flash("Título e autor são obrigatórios.", "warning")
        conn.close()
        return redirect(url_for("livros"))
    search = request.args.get("q", "").strip()
    if search:
        rows = conn.execute("""
            SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR category LIKE ?
            ORDER BY title
        """, (f"%{search}%", f"%{search}%", f"%{search}%")).fetchall()
    else:
        rows = conn.execute("SELECT * FROM books ORDER BY title").fetchall()
    conn.close()
    return render_template("livros.html", books=rows, search=search)

@app.route("/livros/<int:book_id>/editar", methods=["POST"])
@admin_required
def editar_livro(book_id):
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    category = request.form.get("category", "").strip()
    isbn = request.form.get("isbn", "").strip()
    try:
        quantity = max(0, int(request.form.get("quantity", "0")))
    except ValueError:
        quantity = 0
    conn = get_db()
    conn.execute("UPDATE books SET title=?, author=?, category=?, isbn=?, quantity=? WHERE id=?",
                 (title, author, category, isbn, quantity, book_id))
    conn.commit()
    conn.close()
    flash("Dados do livro atualizados.", "success")
    return redirect(url_for("livros"))

@app.route("/livros/<int:book_id>/excluir", methods=["POST"])
@admin_required
def excluir_livro(book_id):
    conn = get_db()
    has_loans = conn.execute("SELECT COUNT(*) FROM loans WHERE book_id=?", (book_id,)).fetchone()[0]
    if has_loans:
        flash("Este livro possui histórico de empréstimos e não pode ser excluído.", "warning")
    else:
        conn.execute("DELETE FROM books WHERE id=?", (book_id,))
        conn.commit()
        flash("Livro removido do catálogo.", "success")
    conn.close()
    return redirect(url_for("livros"))

@app.route("/emprestimos", methods=["GET", "POST"])
@login_required
def emprestimos():
    conn = get_db()
    if request.method == "POST":
        if session.get("role") != "admin":
            conn.close()
            flash("Somente a administração pode registrar empréstimos.", "warning")
            return redirect(url_for("emprestimos"))
        try:
            user_id = int(request.form.get("user_id"))
            book_id = int(request.form.get("book_id"))
        except (TypeError, ValueError):
            conn.close()
            flash("Selecione um usuário e um livro válidos.", "warning")
            return redirect(url_for("emprestimos"))
        book = conn.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
        user = conn.execute("SELECT * FROM users WHERE id=? AND role='student'", (user_id,)).fetchone()
        if not book or not user:
            flash("Usuário ou livro não encontrado.", "danger")
        elif book["quantity"] < 1:
            flash("Não há exemplares disponíveis desse livro.", "warning")
        else:
            loan_date = date.today()
            due_date = loan_date + timedelta(days=7)
            conn.execute("INSERT INTO loans (user_id, book_id, loan_date, due_date) VALUES (?, ?, ?, ?)",
                         (user_id, book_id, loan_date.isoformat(), due_date.isoformat()))
            conn.execute("UPDATE books SET quantity = quantity - 1 WHERE id=?", (book_id,))
            conn.commit()
            flash("Empréstimo registrado! Prazo padrão: 7 dias.", "success")
        conn.close()
        return redirect(url_for("emprestimos"))
    if session.get("role") == "admin":
        rows = conn.execute("""
            SELECT loans.*, books.title AS book_title, users.name AS user_name
            FROM loans JOIN books ON books.id=loans.book_id JOIN users ON users.id=loans.user_id
            ORDER BY CASE WHEN loans.status='Em andamento' THEN 0 ELSE 1 END, loans.id DESC
        """).fetchall()
        students = conn.execute("SELECT id, name FROM users WHERE role='student' ORDER BY name").fetchall()
    else:
        rows = conn.execute("""
            SELECT loans.*, books.title AS book_title, users.name AS user_name
            FROM loans JOIN books ON books.id=loans.book_id JOIN users ON users.id=loans.user_id
            WHERE loans.user_id=? ORDER BY loans.id DESC
        """, (session["user_id"],)).fetchall()
        students = []
    available_books = conn.execute("SELECT id, title, quantity FROM books WHERE quantity > 0 ORDER BY title").fetchall()
    conn.close()
    return render_template("emprestimos.html", loans=rows, students=students, books=available_books)

@app.route("/emprestimos/<int:loan_id>/devolver", methods=["POST"])
@admin_required
def devolver(loan_id):
    conn = get_db()
    loan = conn.execute("SELECT * FROM loans WHERE id=? AND status='Em andamento'", (loan_id,)).fetchone()
    if loan:
        conn.execute("UPDATE loans SET status='Devolvido', return_date=? WHERE id=?",
                     (date.today().isoformat(), loan_id))
        conn.execute("UPDATE books SET quantity=quantity+1 WHERE id=?", (loan["book_id"],))
        conn.commit()
        flash("Devolução registrada.", "success")
    else:
        flash("Empréstimo não encontrado ou já devolvido.", "warning")
    conn.close()
    return redirect(url_for("emprestimos"))

@app.route("/usuarios")
@admin_required
def usuarios():
    conn = get_db()
    rows = conn.execute("""
        SELECT users.id, users.name, users.email,
        COUNT(loans.id) AS total_loans
        FROM users LEFT JOIN loans ON loans.user_id=users.id
        WHERE users.role='student'
        GROUP BY users.id ORDER BY users.name
    """).fetchall()
    conn.close()
    return render_template("usuarios.html", users=rows)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
