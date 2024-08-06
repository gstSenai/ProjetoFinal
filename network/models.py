from network import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=True)
    sobrenome = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    senha = db.Column(db.String, nullable=True)
    posts = db.relationship('Post', backref='user', lazy=True)
    post_comentarios = db.relationship('PostComentarios', backref='user', lazy=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_criacao = db.Column(db.DateTime, default=datetime.now())
    mensagem = db.Column(db.String, nullable=True)
    cidade = db.Column(db.String, nullable=True)
    profissao = db.Column(db.String, nullable=True)
    imagem = db.Column(db.String, nullable=True, default='default.png')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    comentarios = db.relationship('PostComentarios', backref='post', lazy=True)
    likes = db.Column(db.Integer, default=0)

    def msg_resumo(self):
        return f"{self.mensagem[:10]} ..."
    
class PostComentarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_criacao = db.Column(db.DateTime,default=datetime.now())
    comentario = db.Column(db.String, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)

class UserLikes(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)
    user = db.relationship(User, backref='user_likes')
    post = db.relationship(Post, backref='post_likes')