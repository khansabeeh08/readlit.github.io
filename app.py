from flask import Flask, render_template, request
import pandas as pd
import numpy as np

def load_csv(file_path, index_col=None):
    return pd.read_csv(file_path, index_col=index_col)

def load_numpy(file_path):
    return np.load(file_path, allow_pickle=True)

# Load data
try:
    popular_df = load_csv('popular.csv')
    pt = load_csv('pt.csv', index_col=0)  # Assuming the index is important
    books = load_csv('bookss.csv')
    similarity_scores = load_numpy('similarity_scores.npy')
except (FileNotFoundError, pd.errors.EmptyDataError, ValueError) as e:
    print(f"Error loading data files: {e}")
    popular_df = pd.DataFrame()
    pt = pd.DataFrame()
    books = pd.DataFrame()
    similarity_scores = np.array([])

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['post'])
def recommend():
    user_input = request.form.get('user_input')
    try:
        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

            data.append(item)

        return render_template('recommend.html', data=data)
    except Exception as e:
        print(f"Error during recommendation: {e}")
        return render_template('recommend.html', data=[])

if __name__ == '__main__':
    app.run(debug=True)