from network import app,db
from flask import render_template,redirect, url_for, flash
from network.models import Post,User,PostComentarios, UserLikes
from network.forms import PostForm, UserForm, PostComentarioForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required

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
    post = Post.query.get(post_id)
    if post:
        existing_like = UserLikes.query.filter_by(user_id=current_user.id, post_id=post_id).first()
        if not existing_like:
            new_like = UserLikes(user_id=current_user.id, post_id=post_id)
            db.session.add(new_like)
            post.likes += 1
            db.session.commit()
    return redirect(url_for('homepage'))

