import streamlit as st
import funcoes as f
from time import sleep
import pandas as pd

# Conectar ao banco de dados
with open('conexao.txt', 'r') as file:
    user = file.readline().strip()
    password = file.readline().strip()
    host = file.readline().strip()
    porta = file.readline().strip()

banco_de_dados = f.database(user, password, host, porta)
conexao, cursor = banco_de_dados.conectar()


def buscar_filmes(conexao):
    cursor = conexao.cursor()
    cursor.execute("SELECT num_filme, titulo_original, titulo_brasil, ano_lancamento, poster_url, pas_origem, duracao, class_indicativo, sinopse FROM filme")
    filmes = cursor.fetchall()
    cursor.close()
    return pd.DataFrame(filmes, columns=['num_filme', 'titulo_original', 'titulo_brasil', 'ano_lancamento', 'poster_url', 'pas_origem', 'duracao', 'class_indicativo', 'sinopse'])


def atualizar_filme(conexao, num_filme, titulo_original, titulo_brasil, ano_lancamento, poster_url, pas_origem, duracao, class_indicativa, sinopse):
    try:
        cursor = conexao.cursor()
        query = """
        UPDATE filme 
        SET titulo_original = %s, titulo_brasil = %s, ano_lancamento = %s, poster_url = %s, pas_origem = %s, 
            duracao = %s, class_indicativo = %s, sinopse = %s
        WHERE num_filme = %s
        """
        
        valores = (
            titulo_original,
            titulo_brasil,
            int(ano_lancamento),  
            poster_url,
            pas_origem,
            int(duracao),        
            class_indicativa,
            sinopse,
            int(num_filme)        
        )
        cursor.execute(query, valores)
        conexao.commit()
        cursor.close()
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar filme: {e}")
        return False

def main():
    st.sidebar.title("Menu")
    option = st.sidebar.selectbox("Escolha a opção", ["Atualizar Filme",])

    if option == "Atualizar Filme":
        st.header("Atualizar Filme 🎥")
        filmes_df = buscar_filmes(conexao)

        if filmes_df.empty:
            st.warning("Nenhum filme encontrado no banco de dados.")
            return

        # Menu dropdown
        opcoes_filmes = {f"{titulo} ({ano})": num for num, titulo, ano in zip(filmes_df['num_filme'], filmes_df['titulo_brasil'], filmes_df['ano_lancamento'])}
        filme_escolhido = st.selectbox('Selecione o filme para atualizar', list(opcoes_filmes.keys()))

        
        filme_selecionado = filmes_df[filmes_df['num_filme'] == opcoes_filmes[filme_escolhido]]

        if filme_selecionado.empty:
            st.error("Erro: Filme selecionado não encontrado.")
            return
        
        filme_selecionado = filme_selecionado.iloc[0]

        with st.form(key="atualizar_filme_form"):
            titulo_original = st.text_input('Título Original', value=filme_selecionado['titulo_original'])
            titulo_brasil = st.text_input('Título no Brasil', value=filme_selecionado['titulo_brasil'])
            ano_lancamento = st.number_input('Ano de Lançamento', min_value=1800, max_value=2024, value=int(filme_selecionado['ano_lancamento']), step=1)
            poster_url = st.text_input('URL do Poster', value=filme_selecionado['poster_url'])
            pas_origem = st.text_input('País de Origem', value=filme_selecionado['pas_origem'])
            duracao = st.number_input('Duração (em minutos)', min_value=1, value=int(filme_selecionado['duracao']), step=1)
            class_indicativa = st.text_input('Classificação Indicativa', value=filme_selecionado['class_indicativo'])
            sinopse = st.text_area('Sinopse', value=filme_selecionado['sinopse'])

            submit_button = st.form_submit_button("Salvar Alterações")

        if submit_button:
            sucesso = atualizar_filme(
                conexao,
                filme_selecionado['num_filme'],
                titulo_original,
                titulo_brasil,
                ano_lancamento,
                poster_url,
                pas_origem,
                duracao,
                class_indicativa,
                sinopse
            )

            if sucesso:
                st.success("Filme atualizado com sucesso!")
                sleep(2)
                st.rerun()

    elif option == "Atualizar Exibição":
        st.header("Atualizar Exibição 🎞️")
        st.write("Essa parte ainda está em desenvolvimento...")

if __name__ == "__main__":
    main()
