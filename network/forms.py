from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from network import db, app, bcrypt
from network.models import PostComentarios, User, Post
from flask_login import current_user
from wtforms.validators import Length

import os
from werkzeug.utils import secure_filename

class UserForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    sobrenome = StringField('Sobrenome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirmacao_senha = PasswordField('Confirmar senha', validators=[DataRequired(), EqualTo('senha')])
    btnSubmit = SubmitField('Cadastrar')

    def validade_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Usuário já cadastrado com esse E-mail!!!')

    def save(self):
        senha = bcrypt.generate_password_hash(self.senha.data.encode('utf-8'))
        user = User(
            nome=self.nome.data,
            sobrenome=self.sobrenome.data,
            email=self.email.data,
            senha=senha
        )
        db.session.add(user)
        db.session.commit()
        return user

class LoginForm(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    btnSubmit = SubmitField('Login')

    def login(self):
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.senha, self.senha.data.encode('utf-8')):
                    return user
            else:
                    raise Exception('Senha Incorreta!!!')
        else:
            raise Exception('Usuario nao encontrado')

class PostForm(FlaskForm):
    mensagem = StringField('Mensagem:', validators=[DataRequired()])
    cidade = StringField('Cidade:', validators=[DataRequired()])
    profissao = StringField('Profissão:', validators=[DataRequired()])
    btnSubmit = SubmitField('Enviar')

    def save(self):
        post = Post(
            mensagem = self.mensagem.data,
            cidade = self.cidade.data,
            profissao = self.profissao.data,
            user_id=current_user.id
        )

        db.session.add(post)
        db.session.commit()

class PostComentarioForm(FlaskForm):
     comentario = StringField('Comentario', validators=[DataRequired()])
     btnSubmit = SubmitField('Enviar')

     def save(self, user_id, post_id):
        comentario = PostComentarios (
             comentario=self.comentario.data,
             user_id= user_id,
             post_id = post_id
        )

        db.session.add(comentario)
        db.session.commit()