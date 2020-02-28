from flask import Flask, render_template

app = Flask(__name__)

def read_file_to_list(filename):
    with open(filename, 'r', encoding="utf-8") as infile:
        list_news  = infile.read().splitlines()
        for i in range(0, len(list_news)):
            list_news[i] = list_news[i].split('\t')
        return list_news

@app.route("/news/overall")
def read_overall_news():
    return render_template("index.html", news=read_file_to_list("overall-news.txt"))

@app.route("/news/suwon")
def read_suwon_news():
    return render_template("index.html", news=read_file_to_list("suwon-news.txt"))

@app.route("/news/travel")
def read_travel_news():
    return render_template("index.html", news=read_file_to_list("travel-news.txt"))

@app.route("/news/gyeonggi")
def read_gyeonggi_news():
    return render_template("index.html", news=read_file_to_list("gyeonggi-news.txt"))

@app.route("/news/chungju")
def read_chungju_news():
    return render_template("index.html", news=read_file_to_list("chungju-news.txt"))

@app.route("/news/samsung")
def read_samsung_news():
    return render_template("index.html", news=read_file_to_list("samsung-news.txt"))

@app.route("/news/india")
def read_india_news():
    return render_template("index.html", news=read_file_to_list("india-news.txt"))

@app.route("/news/overall/kr")
def read_overall_news_kr():
    return render_template("index-kr.html", news=read_file_to_list("overall-news.txt"))

@app.route("/news/suwon/kr")
def read_suwon_news_kr():
    return render_template("index-kr.html", news=read_file_to_list("suwon-news.txt"))

@app.route("/news/travel/kr")
def read_travel_news_kr():
    return render_template("index-kr.html", news=read_file_to_list("travel-news.txt"))

@app.route("/news/gyeonggi/kr")
def read_gyeonggi_news_kr():
    return render_template("index-kr.html", news=read_file_to_list("gyeonggi-news.txt"))

@app.route("/news/chungju/kr")
def read_chungju_news_kr():
    return render_template("index-kr.html", news=read_file_to_list("chungju-news.txt"))

@app.route("/news/samsung/kr")
def read_samsung_news_kr():
    return render_template("index-kr.html", news=read_file_to_list("samsung-news.txt"))

@app.route("/news/india/kr")
def read_india_news_kr():
    return render_template("index-kr.html", news=read_file_to_list("india-news.txt"))
    
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')