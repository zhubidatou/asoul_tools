from flask import Flask,request,render_template
import replace
import med
import similarity_cal
import predict
import transformer_predict
app = Flask(__name__,template_folder='templates',static_url_path='/', static_folder='static')

@app.route('/replacement',methods=['GET','POST'])
def replaced():
    if request.method == "GET":
        return render_template("word_replacement.html",medic=med.medic())
    if request.method == 'POST':
        comment = request.form.get("comment")
        if comment == "":
            return render_template("word_replacement.html", result='请输入需要降重的评论')
        else:
            return render_template("word_replacement.html", result=replace.synonym_change(comment))

@app.route('/med_creator',methods=['GET','POST'])
def med_creator():
    return render_template("med.html",result=med.medic())

@app.route('/')
def danmu_monitor():
    return render_template("monitor.html")

@app.route('/sim',methods=['GET','POST'])
def similarity():
    if request.method == "GET":
        return render_template("similarity.html",medic=med.medic())
    if request.method == 'POST':
        comment = request.form.get("comment")
        if comment == "":
            return render_template("similarity.html", result='请输入需要降重的评论')
        else:
            return render_template("similarity.html", result=similarity_cal.str_cal(comment))

@app.route('/pre',methods=['GET','POST'])
def prediction():
    if request.method == "GET":
        return render_template("prediction.html")
    if request.method == 'POST':
        comment = request.form.get("comment")
        if comment == "":
            return render_template("prediction.html", result='请输入需要预测的评论')
        else:
            return render_template("prediction.html", result=predict.predict(comment))

@app.route('/transformer',methods=['GET','POST'])
def transformer_prediction():
    if request.method == "GET":
        return render_template("prediction.html")
    if request.method == 'POST':
        comment = request.form.get("comment")
        if comment == "":
            return render_template("prediction.html", result='请输入需要预测的评论')
        else:
            return render_template("prediction.html", result=transformer_predict.transformer_predict(comment))
if __name__ == '__main__':
        app.run(debug=True,host='0.0.0.0',port=80)
