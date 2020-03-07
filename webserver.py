from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

NEWS_LIST_LEN = 5

def read_file_to_list(filename):
    with open(filename, 'r', encoding="utf-8") as infile:
        list_news  = infile.read().splitlines()
        for i in range(0, len(list_news)):
            list_news[i] = list_news[i].split('\t')
            while(len(list_news[i])< NEWS_LIST_LEN):
                list_news[i].append("UNKNOWN")
        return list_news

site_options = [["overall", "Overall"], ["suwon", "Suwon"], ["paths", "Paths"], ["deaths", "Deaths"], ["samsung", "Samsung"],  
["travel", "Travel"], ["india", "India"], ["gyeonggi", "Gyeonggi"], ["recovery", "Recovery"], ["seoul", "Seoul"]]
site_options_kr = [["overall", "확진자"], ["suwon", "수원"], ["paths", "동선"], ["deaths", "사망"], ["chungju", "충주"], ["seoul","서울"], ["samsung", "삼성"], 
["gyeonggi", "경기"], ["travel", "입국"], ["india", "인도"], ["recovery", "완치"]]

@app.route("/news")
def read_news():
    site = request.args.get('site')
    if site is None:
        site = "overall"
    return render_template("index.html", news=read_file_to_list(site + "-news.txt"), option_list=site_options, site=site)

@app.route("/news/kr")
def read_news_kr():
    site = request.args.get('site')
    if site is None:
        site = "overall"
    return render_template("index-kr.html", news=read_file_to_list(site + "-news.txt"), option_list=site_options_kr, site=site)
    
# app name 
@app.errorhandler(404) 
# inbuilt function which takes error as parameter 
def not_found(e): 
  
# defining function 
  return redirect(url_for('read_news'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')