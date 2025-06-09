from flask import Flask, render_template, request
import pickle
import pandas as pd
import numpy as np
with open("Top_Book_Details.pkl", "rb") as file:
    filtered = pickle.load(file)
with open("pivot.pkl", "rb") as file:
    pivot = pickle.load(file)
with open("book.pkl", "rb") as file:
    book = pickle.load(file)
with open("SmilarityScore.pkl", "rb") as file:
    similarity = pickle.load(file)
app = Flask(__name__)
@app.route("/")
def index():
    # Example validation for filtered
    if not isinstance(filtered, pd.DataFrame):
        return render_template("error.html", message="'filtered' must be a pandas DataFrame.")
    if not isinstance(pivot, pd.DataFrame):
        raise ValueError("Error: 'pivot' must be a pandas DataFrame.")
    if not isinstance(book, pd.DataFrame):
        raise ValueError("Error: 'book' must be a pandas DataFrame.")
    if not isinstance(similarity, np.ndarray):
        raise ValueError("Error: 'similarity' must be a numpy array.")
    required_columns = ["Book-Title", "Book-Author", "Image-URL-M"]
    missing_columns = [col for col in required_columns if col not in filtered.columns]
    if missing_columns:
        raise ValueError(f"Error: Missing required columns: {', '.join(missing_columns)} in 'filtered'.")
    return render_template(
        "index.html",
        book_name=filtered["Book-Title"].dropna().to_list(),
        author=filtered["Book-Author"].dropna().to_list(),
        image=filtered["Image-URL-M"].dropna().to_list()
    )
@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')
@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get("user_input", "").strip()
    if not user_input:
        return render_template("recommend.html", data=[], error="Input cannot be empty. Please enter a book title.")

    indices = np.where(pivot.index.str.lower() == user_input.lower())[0]
    if len(indices) == 0:
        return render_template("recommend.html", data=[], error="Book not found.")

    index = indices[0]
    suggestions = sorted(list(enumerate(similarity[index])), key=lambda x: x[1], reverse=True)[1:7]

    df = []
    for i in suggestions:
        item = []
        temp_df = book[book["Book-Title"] == pivot.index[i[0]]]

        title = temp_df.drop_duplicates(subset=["Book-Title"])["Book-Title"].values
        author = temp_df.drop_duplicates(subset=["Book-Title"])["Book-Author"].values
        image = temp_df.drop_duplicates(subset=["Book-Title"])["Image-URL-M"].values

        item.append(title[0] if len(title) > 0 else "Unknown Title")
        item.append(author[0] if len(author) > 0 else "Unknown Author")
        item.append(image[0] if len(image) > 0 else "No Image Available")

        df.append(item)

    print("Debug: Data being sent to template ->", df)
    return render_template("recommend.html", data=df)
@app.route('/recommend_books', methods=['POST'])
@app.errorhandler(Exception)
def handle_exception(e):
    return f"An unexpected error occurred: {str(e)}", 500
if __name__ == "__main__":
    app.run(debug=True)


