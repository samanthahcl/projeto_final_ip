from app import db

class Termo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    termo = db.Column(db.String(255), nullable=False)
    definicao = db.Column(db.Text, nullable=False)




