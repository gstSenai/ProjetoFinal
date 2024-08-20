from network import app,db
from flask import render_template,redirect, url_for, flash, request, session, jsonify
from network.models import Post,User,PostComentarios, UserLikes, Message
from network.forms import PostForm, UserForm, PostComentarioForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required
from flask_socketio import SocketIO,join_room, leave_room, emit,send


@app.route('/', methods=['GET', 'POST'])
def homepage():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.login()
        if user:
            login_user(user, remember=True)
            return redirect(url_for('homepage'))
        else:
            flash('E-mail ou senha inválidos', 'danger')


    context = {
        'dados': Post.query.all()
    }


    return render_template('index.html', form=form, context=context)
   
@app.route('/post/novo',methods=['GET', 'POST'])
@login_required
def PostNovo():
    form = PostForm()
    if form.validate_on_submit():
        form.save()
        return redirect(url_for('homepage'))
    return render_template('post_novo.html', form=form)


@app.route('/post/lista/')
def postLista():
    dados = Post.query.order_by('cidade').all()
    context = {'dados': dados}
    return render_template('index.html', context=context)

@app.route('/cadastro/', methods=['GET', 'POST'])
def Cadastro():
    form = UserForm()
    if form.validate_on_submit():
        user = form.save()
        if user:
            flash('Cadastro realizado com sucesso! Você está agora logado.', 'success')
            return redirect(url_for('homepage'))
        else:
            flash('Erro ao cadastrar o usuário. Tente novamente.', 'danger')
    return render_template('cadastro.html', form=form)


@app.route('/sair/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))


@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)  
   
    existing_like = UserLikes.query.filter_by(user_id=current_user.id, post_id=post_id).first()
   
    if existing_like:
        db.session.delete(existing_like)
        post.likes_count -= 1  
        flash('Você removeu seu like.', 'info')
    else:
        new_like = UserLikes(user_id=current_user.id, post_id=post_id)
        db.session.add(new_like)
        post.likes_count += 1
        flash('Post curtido com sucesso!', 'success')
    db.session.commit()
    return redirect(url_for('homepage'))


@app.route('/post/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        flash('Post não encontrado.', 'error')
        return redirect(url_for('homepage'))
   
    if post.user_id == current_user.id:
        try:
            UserLikes.query.filter_by(post_id=post_id).delete()
            db.session.delete(post)
            db.session.commit()
            flash('Post excluído com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao excluir o post: {str(e)}', 'danger')
    else:
        flash('Você não tem permissão para excluir este post.', 'danger')


    return redirect(url_for('homepage'))


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
        flash('Comentário adicionado com sucesso!', 'success')
    else:
        flash('Não é possível adicionar um comentário vazio.', 'danger')


    return redirect(url_for('homepage'))

@app.route('/filter/<string:profession>', methods=['GET'])
def filter_posts(profession):
    filtered_posts = Post.query.filter_by(profissao=profession).all()
    context = {
        'dados': filtered_posts
    }


    return render_template('index.html', context=context)

@app.route('/chat/<int:post_id>')
@login_required
def chat(post_id):
    post = Post.query.get_or_404(post_id)
    messages = Message.query.filter_by(post_id=post_id).order_by(Message.timestamp.asc()).all()
    
    return render_template('chat.html', post=post, messages=messages)

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    content = request.form.get('message')
    post_id = request.form.get('post_id')
    post = Post.query.get_or_404(post_id)
    
    if content:
        message = Message(
            from_user_id=current_user.id,
            to_user_id=post.user_id,
            content=content
        )
        db.session.add(message)
        db.session.commit()
        socketio.emit('receive_message', {'message': content, 'from_user_id': current_user.id}, room=post_id)
    
    return jsonify({'success': True})


socketio = SocketIO(app,cors_allowed_origins="*")

@socketio.on('connect')
def on_connect():
    print('Client connected')

@socketio.on('disconnect')
def on_disconnect():
    print('Client disconnected')

@socketio.on('join')
def on_join(data):
    post_id = data['post_id']
    join_room(post_id)
    emit('status', {'msg': f'{current_user.nome} entrou no chat.'}, room=post_id)

@socketio.on('leave')
def on_leave(data):
    post_id = data['post_id']
    leave_room(post_id)
    emit('status', {'msg': f'{current_user.nome} saiu do chat.'}, room=post_id)

@socketio.on('send_message')
def handle_send_message_event(data):
    post_id = data['post_id']
    content = data['message']
    
    message = Message(
        from_user_id=current_user.id,
        to_user_id=data['to_user_id'],
        post_id=post_id,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    
    emit('receive_message', {'message': content, 'from_user_id': current_user.id}, room=post_id)





