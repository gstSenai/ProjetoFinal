# Projeto Final - Rede Social de Oportunidades Profissionais

## Descrição
Este repositório contém o código-fonte de uma aplicação web que simula uma rede social no estilo "LinkedIn". O objetivo deste projeto é criar uma plataforma onde os usuários podem compartilhar e descobrir oportunidades de trabalho, se conectar com outros profissionais e interagir com postagens de vagas e conteúdo relacionado ao mundo corporativo.

A aplicação permite que os usuários publiquem sobre novas vagas de emprego, conectem-se com outros profissionais da sua área e criem um perfil que destaque suas habilidades e experiências profissionais.

## Funcionalidades
**Cadastro e Login de Usuários**: Sistema de autenticação de usuários com funcionalidades de registro e login.
**Postagens de Oportunidades**: Os usuários podem criar postagens sobre vagas de emprego, incluindo título, descrição e categoria.
**Interações com Postagens**: Curtir, comentar e compartilhar postagens sobre vagas.
**Conexões Profissionais**: Usuários podem adicionar outros profissionais à sua rede de contatos, assim como no LinkedIn.
**Perfis de Usuário**: Cada usuário pode criar um perfil detalhado, exibindo suas habilidades, experiências de trabalho, educação e informações de contato.
**Feed de Atualizações**: A página principal exibe um feed com as postagens de vagas de emprego e atualizações feitas pelos usuários na rede.
**Busca e Filtro de Vagas**: Sistema de busca para filtrar as postagens de vagas com base em critérios como localidade, cargo, e setor.

## Tecnologias Utilizadas
**Flask**: Framework para desenvolvimento web em Python, utilizado para criar a API e a lógica do backend.
**SQLAlchemy**: ORM (Object Relational Mapper) utilizado para interação com o banco de dados.
**Jinja2**: Motor de templates integrado ao Flask para renderização das páginas HTML.
**HTML, CSS, JavaScript**: Linguagens e tecnologias de front-end para criação das páginas e interatividade.
**SQLite/MySQL**: Banco de dados relacional utilizado para armazenar informações dos usuários, postagens e conexões.
**Flask-Login**: Extensão do Flask para gerenciar sessões de usuários e autenticação.
**JWT (JSON Web Token)**: Sistema de autenticação para garantir que apenas usuários autenticados possam interagir com determinadas funcionalidades.
**Bootstrap**: Framework CSS para criação de uma interface de usuário responsiva e moderna.

## Pré-requisitos
Antes de rodar o projeto, certifique-se de que você tenha os seguintes itens instalados:
**Python 3.x**: Recomendado para rodar a aplicação.
**pip**: Gerenciador de pacotes do Python para instalar as dependências.
**Git**: Para clonar o repositório.

## Como Instalar

### 1. Clone o Repositório
Primeiro, clone o repositório para sua máquina local:
```bash
git clone https://github.com/gstSenai/ProjetoFinal.git
