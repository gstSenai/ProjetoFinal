from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FileField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Optional
from network import db, app, bcrypt
from network.models import PostComentarios, User, Post
from flask_login import current_user
from flask import flash
from flask_wtf.file import FileAllowed


import os
from werkzeug.utils import secure_filename

class UserForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    sobrenome = StringField('Sobrenome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6, message="A senha deve ter pelo menos 6 caracteres.")])
    confirmacao_senha = PasswordField('Confirmar senha', validators=[DataRequired(), EqualTo('senha', message="As senhas devem ser iguais.")])
    btnSubmit = SubmitField('Cadastrar')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Usuário já cadastrado com esse E-mail!!!')

    def save(self):
        senha = bcrypt.generate_password_hash(self.senha.data).decode('utf-8')
        user = User(
            nome=self.nome.data,
            sobrenome=self.sobrenome.data,
            email=self.email.data,
            senha=senha,
        )
        db.session.add(user)
        db.session.commit()
        return user
    
class EditProfileForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    sobrenome = StringField('Sobrenome', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[Optional(), Length(min=6, message="A senha deve ter pelo menos 6 caracteres.")])
    confirmacao_senha = PasswordField('Confirmar senha', validators=[Optional(), EqualTo('senha', message="As senhas devem ser iguais.")])
    imagem = FileField('Imagem de Perfil', validators=[Optional()])
    btnSubmit = SubmitField('Salvar')



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
    estado = SelectField('Estado:', choices=[], validators=[DataRequired()])
    cidade = SelectField('Cidade:', choices=[], validators=[DataRequired()])
    profissao = StringField('Profissão:', validators=[DataRequired()])
    btnSubmit = SubmitField('Enviar')

    def save(self):
        try:
            post = Post(
                mensagem=self.mensagem.data,
                estado=self.estado.data,
                cidade=self.cidade.data,
                profissao=self.profissao.data,
                user_id=current_user.id  
            )
            
            db.session.add(post)
            db.session.commit()
            print(f"Post {post.id} salvo com sucesso!")  
            return post
        
        except Exception as e:
            db.session.rollback() 
            print(f"Erro ao salvar o post: {e}")
            raise

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