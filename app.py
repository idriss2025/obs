from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'gizli_anahtar'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class Puan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(100))
    ders = db.Column(db.String(100))
    not_ = db.Column(db.Integer)
    tarih = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    if 'kullanici' not in session:
        return redirect(url_for('login'))
    puanlar = Puan.query.all()
    toplam = len(puanlar)
    ortalama = sum([p.not_ for p in puanlar]) / toplam if toplam > 0 else 0
    son_not = puanlar[-1].tarih.strftime('%Y-%m-%d %H:%M') if puanlar else "Yok"
    return render_template('index.html', toplam=toplam, ortalama=ortalama, son_not=son_not)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        kullanici = request.form['kullanici']
        sifre = request.form['sifre']
        if kullanici and sifre:
            session['kullanici'] = kullanici
            return redirect(url_for('index'))
        else:
            return render_template('login.html', hata="اسم المستخدم أو كلمة المرور غير صحيحة")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('kullanici', None)
    return redirect(url_for('login'))

@app.route('/puan-ekle', methods=['GET', 'POST'])
def puan_ekle():
    if 'kullanici' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        isim = request.form['isim']
        ders = request.form['ders']
        not_ = int(request.form['not'])
        yeni_puan = Puan(isim=isim, ders=ders, not_=not_)
        db.session.add(yeni_puan)
        db.session.commit()
        return redirect(url_for('puanlar'))
    return render_template('puan_ekle.html')

@app.route('/puanlar')
def puanlar():
    if 'kullanici' not in session:
        return redirect(url_for('login'))
    puanlar = Puan.query.all()
    return render_template('puanlar.html', puanlar=puanlar)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        ad_soyad = request.form['ad_soyad']
        email = request.form['email']
        sifre = request.form['sifre']
        sifre_tekrar = request.form['sifre_tekrar']

        if sifre != sifre_tekrar:
            return render_template('register.html', hata="Şifreler eşleşmiyor!")

        # هنا يمكنك حفظ المستخدم في قاعدة بيانات لاحقًا
        return redirect(url_for('login'))

    return render_template('register.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
