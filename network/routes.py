from network import app,db, bcrypt
from flask import render_template,redirect, url_for, flash, request, session, jsonify, current_app
from network.models import Post,User,PostComentarios, UserLikes, Message
from network.forms import PostForm, UserForm, PostComentarioForm, LoginForm, EditProfileForm
from flask_login import login_user, current_user, logout_user, login_required
from flask_socketio import SocketIO,join_room, leave_room, emit,send
from sqlalchemy.orm import joinedload
import requests
import os
from werkzeug.utils import secure_filename
from sqlalchemy import func
from datetime import datetime
import pytz

def get_estados():
    response = requests.get('https://servicodados.ibge.gov.br/api/v1/localidades/estados')
    return response.json()


@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('homepage'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    form = LoginForm()
    if form.validate_on_submit():
        user = form.login()
        if user:
            login_user(user, remember=True)

            br_tz = pytz.timezone('America/Sao_Paulo')
            user.last_login = datetime.now(br_tz)
            db.session.commit()

            if user.email == "admin@admin.com":
                return redirect(url_for('pagina_admin'))
            return redirect(url_for('homepage'))
        else:
            flash('E-mail ou senha inválidos', 'danger')
    return render_template('login.html', form=form)


@app.route('/home', methods=['GET'])
def homepage():
    if current_user.is_authenticated and current_user.email == "admin@admin.com":
        return redirect(url_for('pagina_admin'))

    context = {
        'dados': Post.query.all(),  
        'user_authenticated': current_user.is_authenticated
    }
    return render_template('home.html', context=context)


from flask import request

@app.route('/postagens', methods=['GET'])
@login_required
def postagens():
    nome_usuario = request.args.get('nome_usuario', '')
    estado = request.args.get('estado', '')
    cidade = request.args.get('cidade', '')

    query = Post.query

    if nome_usuario:
        query = query.filter(Post.user.has(nome=nome_usuario))

    if estado:
        query = query.filter(Post.estado == estado)

    if cidade:
        query = query.filter(Post.cidade == cidade)

    dados = query.order_by(Post.data_criacao.desc()).all()
    
    context = {'dados': dados}
    return render_template('posts.html', context=context)


@app.route('/post_novo', methods=['GET', 'POST'])
@login_required
def PostNovo():
    form = PostForm()

    if not form.estado.choices:
        form.estado.choices = [(estado['sigla'], estado['nome']) for estado in get_estados()]

    if form.estado.data:
        cidades = get_cidades_por_estado(form.estado.data)
        form.cidade.choices = [(cidade, cidade) for cidade in cidades]

    if form.validate_on_submit():
        try:
            nova_postagem = Post(
                mensagem=form.mensagem.data,
                estado=form.estado.data,
                cidade=form.cidade.data,
                profissao=form.profissao.data,
                user_id=current_user.id  
            )
            db.session.add(nova_postagem)
            db.session.commit()

            return redirect(url_for('postagens'))
        except Exception as e:
            return render_template('post_novo.html', form=form)

    dados = Post.query.order_by('cidade').all()
    context = {'dados': dados}

    return render_template('post_novo.html', form=form, context=context)


def get_cidades_por_estado(estado_sigla):
    response = requests.get(f'https://servicodados.ibge.gov.br/api/v1/localidades/estados/{estado_sigla}/municipios')
    cidades = response.json()
    return [cidade['nome'] for cidade in cidades]


@app.route('/post/lista/')
def postLista():
    dados = Post.query.order_by('cidade').all()
    context = {'dados': dados}
    return render_template('home.html', context=context)

@app.route('/cadastro/', methods=['GET', 'POST'])
def Cadastro():
    form = UserForm()
    if form.validate_on_submit():
        try:
            user = form.save()
            flash('Usuário cadastrado com sucesso!', 'success') 
            return redirect(url_for('login'))  
        except Exception as e:
            flash('Erro ao cadastrar o usuário. Tente novamente.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{form[field].label.text}: {error}', 'danger')
    return render_template('cadastro.html', form=form)



@app.route('/sair/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


from flask import jsonify

@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)  
    existing_like = UserLikes.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        post.likes_count -= 1  
        db.session.commit()
        liked = False
    else:
        new_like = UserLikes(user_id=current_user.id, post_id=post_id)
        db.session.add(new_like)
        post.likes_count += 1
        db.session.commit()
        liked = True

    return jsonify({
        'liked': liked,
        'likes_count': post.likes_count
    })


@app.route('/post/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return redirect(url_for('homepage'))
   
    if post.user_id == current_user.id:
        try:
            UserLikes.query.filter_by(post_id=post_id).delete()
            db.session.delete(post)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
    return redirect(url_for('postagens'))


@app.route('/post/<int:post_id>/add_comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    comentario_texto = request.form.get('comentario')


    if comentario_texto:
        comentario = PostComentarios(
            comentario=comentario_texto,
            user_id=current_user.id,
            post_id=post.id
        )
        db.session.add(comentario)
        db.session.commit()
    return redirect(url_for('postagens'))

@app.route('/filter/<string:profession>', methods=['GET'])
def filter_posts(profession):
    filtered_posts = Post.query.filter_by(profissao=profession).all()
    context = {
        'dados': filtered_posts
    }
    return render_template('posts.html', context=context)

socketio = SocketIO(app,cors_allowed_origins="*")

@app.route('/chat/<int:post_id>')
@login_required
def chat(post_id):
    post = Post.query.get_or_404(post_id)
    messages = Message.query.filter_by(post_id=post_id).order_by(Message.timestamp.asc()).all()
    users = User.query.all()
    dados = Post.query.order_by('cidade').all()
    context = {'dados': dados}
    return render_template('chat.html', post=post, messages=messages, users=users, context=context)


from collections import defaultdict

active_chats = defaultdict(set)  
message_notifications = defaultdict(lambda: defaultdict(int))

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    content = request.json.get('message')
    post_id = request.json.get('post_id')  
    to_user_id = request.json.get('to_user_id')

    if content and to_user_id:
        message = Message(
            from_user_id=current_user.id,
            to_user_id=to_user_id,
            post_id=post_id,  
            content=content
        )
        db.session.add(message)
        db.session.commit()

        socketio.emit('receive_message', {
            'message': content,
            'from_user_id': current_user.id,
            'from_user_nome': current_user.nome,
            'to_user_id': to_user_id,
            'post_id': post_id
        }, room=post_id or to_user_id)  

        return jsonify({'success': True}), 200

    return jsonify({'success': False, 'error': 'Dados inválidos'}), 400


@socketio.on('join')
def on_join(data):
    post_id = data['post_id']
    user_id = current_user.id
    join_room(post_id)

    active_chats[post_id].add(user_id)
    emit('status', {'msg': f'{current_user.nome} entrou no chat.'}, room=post_id)

@socketio.on('leave')
def on_leave(data):
    post_id = data['post_id']
    user_id = current_user.id
    leave_room(post_id)

    if user_id in active_chats[post_id]:
        active_chats[post_id].remove(user_id)
    emit('status', {'msg': f'{current_user.nome} saiu do chat.'}, room=post_id)

@socketio.on('load_messages')
def handle_load_messages(data):
    user_id = data.get('userId')  
    current_user_id = current_user.id

    if user_id:
        messages = Message.query.filter(
            (Message.from_user_id == current_user_id) & (Message.to_user_id == user_id) |
            (Message.from_user_id == user_id) & (Message.to_user_id == current_user_id)
        ).order_by(Message.timestamp.asc()).all()

        message_list = [{'message': msg.content, 'from_me': msg.from_user_id == current_user_id} for msg in messages]
        emit('load_messages_response', {'messages': message_list}, room=request.sid)
    else:
        emit('load_messages_response', {'messages': []}, room=request.sid)


        
@app.route('/get_notifications', methods=['GET'])
@login_required
def get_notifications():
    post_id = request.args.get('post_id')
    user_id = current_user.id

    notifications = message_notifications.get(post_id, {}).get(user_id, 0)
    return jsonify({'notifications': notifications})

app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'network/static/assets')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = EditProfileForm()

    if form.validate_on_submit():
        current_user.nome = form.nome.data
        current_user.sobrenome = form.sobrenome.data

        if form.senha.data:
            if form.senha.data == form.confirmacao_senha.data:
                current_user.senha = bcrypt.generate_password_hash(form.senha.data.encode('utf-8'))
            else:
                return redirect(url_for('profile'))

        if form.imagem.data:
            imagem = form.imagem.data
            if imagem and allowed_file(imagem.filename):
                filename = secure_filename(imagem.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                imagem.save(filepath)
                current_user.imagem = filename

        db.session.commit()
        return redirect(url_for('profile'))

    if request.method == 'GET':
        form.nome.data = current_user.nome
        form.sobrenome.data = current_user.sobrenome

    dados = Post.query.order_by('cidade').all()  
    context = {'dados': dados}  
    return render_template('profile.html', form=form, context=context) 





@app.route('/admin')
@login_required
def pagina_admin():
    usuarios = User.query.all()

    posts_por_mes = (
        db.session.query(
            func.strftime('%Y-%m', Post.data_criacao).label('mes'),
            func.count(Post.id).label('total')
        )
        .group_by('mes')
        .order_by('mes')
        .all()
    )

    labels = [mes_total.mes for mes_total in posts_por_mes]
    data = [mes_total.total for mes_total in posts_por_mes]

    return render_template('admin.html', usuarios=usuarios, labels=labels, data=data)  


@app.route('/usuario/delete/<int:user_id>', methods=['POST'])
@login_required
def excluir_usuario(user_id):
    user = User.query.get_or_404(user_id)
    
    if current_user.email == 'admin@admin.com': 
        try:
            Message.query.filter_by(from_user_id=user.id).delete()
            Message.query.filter_by(to_user_id=user.id).delete()

            UserLikes.query.filter_by(user_id=user.id).delete()

            for post in user.posts:
                PostComentarios.query.filter_by(post_id=post.id).delete()
                Post.query.filter_by(id=post.id).delete()

            db.session.delete(user)
            db.session.commit()

        except Exception as e:
            db.session.rollback() 
    return redirect(url_for('pagina_admin'))

@app.route('/historico')
@login_required
def historico():
    postagens_usuario = Post.query.filter_by(user_id=current_user.id).all()
    dados = Post.query.order_by('cidade').all()
    context = {'dados': dados}
    return render_template('historico.html', postagens=postagens_usuario, context=context)










