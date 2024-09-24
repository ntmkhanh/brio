# -*- coding: utf8 -*-
from flask import Flask, flash, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
import json
import requests
from flask_mysqldb import MySQL
from flask_cors import CORS
import transformers
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

##import load_image
from load_image import *


import requests

access_token = "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"
tokenizer = AutoTokenizer.from_pretrained("ynhi/vit5-finetune-v6", use_auth_token=access_token)
model = AutoModelForSeq2SeqLM.from_pretrained("ynhi/vit5-finetune-v6", use_auth_token=access_token)
from config import DevConfig
app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app)
app.config.from_object(DevConfig)
db = SQLAlchemy(app)


mysql = MySQL(app)
#Creating a connection cursor
with app.app_context():
    cursor = mysql.connection.cursor()

def predict(text, model, tokenizer ):
    inputs = "công thức: " + text
    inputs = tokenizer(inputs, max_length=128, truncation=True, return_tensors="pt")
    output = model.generate(**inputs, num_beams=7, do_sample=False, min_length=22, max_length=1024, no_repeat_ngram_size=3)
    decoded_output = tokenizer.batch_decode(output, skip_special_tokens=False)[0]
    rs = decoded_output
    return rs

@app.route('/goi-y-mon', methods=['GET','POST'])
def generate():
    text = request.form.get("ingredients")
    if request.form.get('action_TT'):
        error = None
        list_text = []
        lt = []
        list_text = text.split(',')
        for l in list_text:
            lt.append(l.strip())
        cursor = mysql.connection.cursor()
        sql1 = 'SELECT DISTINCT RECIPE_ID from recipe_ingredient JOIN ingredients WHERE ingredients.INGREDIENT_ID=recipe_ingredient.INGREDIENT_ID AND INGREDIENT_TYPE_ID in (4,6,7,13,14) AND INGREDIENT_NAME in %s'
        cursor.execute(sql1,[lt])
        dt = cursor.fetchall()
        if len(dt)>0:
            cursor.execute('SELECT * FROM recipes WHERE RECIPE_ID in %s',[dt])
            data = cursor.fetchall()
            sql2 = 'SELECT DISTINCT RECIPE_ID from recipe_ingredient JOIN ingredients WHERE ingredients.INGREDIENT_ID=recipe_ingredient.INGREDIENT_ID AND RECIPE_ID not in %s AND INGREDIENT_NAME in %s'
            cursor.execute(sql2,[dt,lt])
            mk = cursor.fetchall()
            cursor.execute('SELECT * FROM recipes WHERE RECIPE_ID in %s',[mk])
            monkhac = cursor.fetchall()
            cursor.close()
            return render_template("mon-truyen-thong.html",list_mon = data, monkhac = monkhac)
        else:
            sql2 = 'SELECT DISTINCT RECIPE_ID from recipe_ingredient JOIN ingredients WHERE ingredients.INGREDIENT_ID=recipe_ingredient.INGREDIENT_ID AND INGREDIENT_NAME in %s'
            cursor.execute(sql2,[lt])
            mk = cursor.fetchall()
            if mk:
                cursor.execute('SELECT * FROM recipes WHERE RECIPE_ID in %s',[mk])
                monkhac = cursor.fetchall()
                cursor.close()
                return render_template("mon-truyen-thong.html", monkhac = monkhac)
            else:
                error = "Không tìm thấy món!"
                return render_template('index.html', error=error)
    else:
        if request.form.get('action_TM'):
            text.lower()
            recipe = predict(text, model, tokenizer)
            s1="<pad>"
            s2="<unk>"
            s3="</s>"
           
            title=((recipe.split(s1))[1].split(s2)[0])
            instructions=((recipe.split(s2))[1].split(s3)[0])
            img_url = get_image_url(title)
            step = []
            tmp = instructions.split('.')
            for t in tmp:
                step.append(t.strip().capitalize())
            half_len = len(step)//2
            step1,step2 = step[:half_len], step[half_len:len(step)-1]
            len_step1 = len(step1)
            return render_template('result.html',tenmon = title,step1 = step1, step2=step2,lens1=len_step1, image_url=img_url)
        else:
            error = "Không tìm thấy món!"
            return render_template('index.html', error=error)
@app.route('/', methods=['GET','POST'])
def index():
    return render_template("index.html")

@app.route('/mon-truyen-thong/<string:id>',methods=['GET'])
def detail(id):
    cursor = mysql.connection.cursor()
    cursor.execute('Select * from recipes where RECIPE_ID = %s',[id])
    recipe = cursor.fetchone()
    cursor.execute('SELECT * FROM recipe_steps WHERE RECIPE_ID = %s',[id])
    step = cursor.fetchall()
    cursor.execute('SELECT * FROM recipe_ingredient join ingredients join measurement where recipe_ingredient.INGREDIENT_ID = ingredients.INGREDIENT_ID and ingredients.MEASUREMENT_ID = measurement.MEASUREMENT_ID AND RECIPE_ID = %s',[id])
    ngl = cursor.fetchall()
    cursor.close()
    return render_template('detail.html',mon=recipe,ct=step, nguyenlieu=ngl)
if __name__ == '__main__':
    app.run(debug=True)
