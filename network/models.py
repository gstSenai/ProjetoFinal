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
    last_login = db.Column(db.DateTime, nullable=True)
    imagem = db.Column(db.String, nullable=True, default='default.png')
    posts = db.relationship('Post', backref='user', lazy=True)
    post_comentarios = db.relationship('PostComentarios', backref='user', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    mensagem = db.Column(db.String, nullable=True)
    estado = db.Column(db.String, nullable=True)
    cidade = db.Column(db.String, nullable=True)
    profissao = db.Column(db.String, nullable=True)
    imagem = db.Column(db.String, nullable=True, default='default.png')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    comentarios = db.relationship('PostComentarios', backref='post', lazy=True)
    likes_count = db.Column(db.Integer, default=0)
    user_likes = db.relationship('UserLikes', backref='liked_post', lazy=True, cascade="all, delete-orphan")

    def count_likes(self):
        return UserLikes.query.filter_by(post_id=self.id).count()

    def msg_resumo(self):
        return f"{self.mensagem[:10]} ..."
    
class PostComentarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    comentario = db.Column(db.String, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)

class UserLikes(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)
    user = db.relationship('User', backref='user_likes')
    post = db.relationship('Post', backref='post_likes')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    from_user = db.relationship('User', foreign_keys=[from_user_id], backref='sent_messages')
    to_user = db.relationship('User', foreign_keys=[to_user_id], backref='received_messages')
    post = db.relationship('Post', backref='messages')