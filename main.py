__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import os
import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import io

# Configuração da página
st.set_page_config(
    page_title="Gerador de Briefing para Sites",
    page_icon="📝",
    layout="wide"
)

# Configuração do Gemini
gemini_api_key = os.getenv("GEM_API_KEY")
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Título da aplicação
st.title("📋 Gerador de Briefing para Desenvolvimento de Site")
st.markdown("""
Preencha o formulário abaixo ou faça upload de um arquivo CSV com as respostas para gerar automaticamente um briefing completo.
""")

# Função para mapear colunas do CSV para o formato interno
def mapear_csv_para_respostas(df):
    # Pega a primeira linha (assumindo que há apenas um registro no CSV)
    row = df.iloc[0]
    
    respostas = {
        "nome_empresa": row.get("Nome da sua empresa/Instituição", ""),
        "nome_responsavel": row.get("Nome:", ""),
        "cargo_responsavel": row.get("Cargo:", ""),
        "email_responsavel": row.get("E-mail:", ""),
        "telefone_responsavel": row.get("Telefone:", ""),
        "descricao_site": row.get("Por favor, descreva o site que deseja.", ""),
        "objetivos_principais": row.get("Quais são os principais objetivos que você deseja alcançar com o site?", ""),
        "objetivos_secundarios": row.get("Há objetivos secundários que o site deve atingir?", ""),
        "publico_alvo": row.get("Quem é o público-alvo do seu site?", ""),
        "segmentos_especificos": row.get("Há algum segmento específico que precisa ser destacado no site?", ""),
        "concorrentes": row.get("Quem são os seus principais concorrentes?", ""),
        "gosta_concorrentes": row.get("O que você gosta nos sites dos seus concorrentes?", ""),
        "nao_gosta_concorrentes": row.get("O que você não gosta nos sites dos seus concorrentes?", ""),
        "diferenciais": row.get("O que você espera que seu site ofereça de diferente em relação aos concorrentes?", ""),
        "funcionalidades": row.get("Quais funcionalidades específicas você gostaria de incluir no site?", ""),
        "conteudo_pronto": "Sim" if str(row.get("Você já possui todo o conteúdo pronto (textos, imagens, vídeos)?", "")).lower().startswith(('sim', 's', 'yes', 'y')) else "Não",
        "numero_paginas": row.get("Quantas páginas aproximadamente o site terá?", ""),
        "paginas_desejadas": row.get("Quais páginas você gostaria de incluir no novo site?", ""),
        "percepcao_visual": row.get("Como você gostaria que o site fosse visualmente percebido?", ""),
        "referencias_gosta": row.get("Há algum site ou referência visual que você gosta?", ""),
        "referencias_nao_gosta": row.get("Há alguma referência visual que você não gosta?", ""),
        "seo": "Sim" if str(row.get("O site precisa ser otimizado para SEO?", "")).lower().startswith(('sim', 's', 'yes', 'y')) else "Não",
        "otimizacoes_seo": row.get("Se sim, gostaria de incluir algum tipo de otimização específica?", ""),
        "mobile_prioritario": "Sim" if str(row.get("A versão mobile do site é uma prioridade?", "")).lower().startswith(('sim', 's', 'yes', 'y')) else "Não",
        "ssl": "Sim" if str(row.get("Você precisa de algum certificado de segurança SSL para o site?", "")).lower().startswith(('sim', 's', 'yes', 'y')) else "Não",
        "plataforma": row.get("Você tem alguma preferência de plataforma para o desenvolvimento do site?", ""),
        "hospedagem": "Sim" if str(row.get("Você já possui um serviço de hospedagem para o site?", "")).lower().startswith(('sim', 's', 'yes', 'y')) else "Não",
        "uso_dados": "Sim" if str(row.get("Você deseja utilizar dados de usuários no seu site (exemplo: cookies, analytics)?", "")).lower().startswith(('sim', 's', 'yes', 'y')) else "Não",
        "banner_cookies": "Sim" if str(row.get("Será necessário implementar alguma solução de governança digital, como banner de consentimento para cookies?", "")).lower().startswith(('sim', 's', 'yes', 'y')) else "Não",
        "tagueamento": "Sim" if str(row.get("Você precisará de tagueamento de dados para monitoramento de ações no site?", "")).lower().startswith(('sim', 's', 'yes', 'y')) else "Não",
        "tags_especificas": row.get("Quais tags de conversão ou tracking você precisará integrar?", ""),
        "integracoes": "Sim" if str(row.get("Você irá integrar o site com plataformas externas ou APIs?", "")).lower().startswith(('sim', 's', 'yes', 'y')) else "Não",
        "detalhes_integracoes": row.get("Quais integrações específicas?", ""),
        "prazo": row.get("Qual a sua expectativa de prazo para o lançamento do novo site?", ""),
        "tem_orcamento": "Sim" if str(row.get("Você já tem um orçamento estimado para esse projeto?", "")).lower().startswith(('sim', 's', 'yes', 'y')) else "Não",
        "orcamento": row.get("Orçamento estimado", ""),
        "manutencao": "Sim" if str(row.get("Após o lançamento, você precisará de serviços de manutenção contínuos?", "")).lower().startswith(('sim', 's', 'yes', 'y')) else "Não",
        "consideracoes_finais": f"{row.get('Há alguma outra necessidade ou exigência que não foi mencionada?', '')}\n\n{row.get('Alguma consideração adicional sobre o projeto que gostaria de compartilhar conosco?', '')}"
    }
    
    return respostas

# Função para gerar o briefing com a LLM
def gerar_briefing(respostas):
    prompt = f"""
    Com base nas seguintes respostas do cliente, gere um briefing profissional e detalhado 
    para desenvolvimento de um site institucional/empresarial. Organize em seções claras 
    com títulos destacados e mantenha um tom profissional:

    # Briefing para Desenvolvimento de Site - {respostas['nome_empresa']}

    ## 1. Informações Básicas
    - Empresa: {respostas['nome_empresa']}
    - Responsável: {respostas['nome_responsavel']} ({respostas['cargo_responsavel']})
    - Contato: {respostas['email_responsavel']} | {respostas['telefone_responsavel']}

    ## 2. Descrição do Projeto
    O cliente deseja: {respostas['descricao_site']}

    ## 3. Objetivos
    Principais objetivos:
    - {respostas['objetivos_principais']}

    Objetivos secundários:
    - {respostas['objetivos_secundarios'] if respostas['objetivos_secundarios'] else 'Não especificado'}

    ## 4. Público-Alvo
    {respostas['publico_alvo']}

    Segmentos específicos:
    - {respostas['segmentos_especificos'] if respostas['segmentos_especificos'] else 'Não aplicável'}

    ## 5. Análise Competitiva
    Concorrentes mencionados: {respostas['concorrentes']}

    Pontos positivos observados nos concorrentes:
    - {respostas['gosta_concorrentes']}

    Pontos negativos observados nos concorrentes:
    - {respostas['nao_gosta_concorrentes']}

    Diferenciais desejados:
    - {respostas['diferenciais']}

    ## 6. Requisitos Técnicos e Funcionalidades
    Funcionalidades solicitadas:
    - {respostas['funcionalidades']}

    Conteúdo disponível:
    - {'Sim, o cliente já possui todo o conteúdo' if respostas['conteudo_pronto'] == 'Sim' else 'Não, será necessário criar conteúdo'}

    Número estimado de páginas: {respostas['numero_paginas']}

    Páginas solicitadas:
    - {respostas['paginas_desejadas']}

    ## 7. Design e Identidade Visual
    Percepção visual desejada: {respostas['percepcao_visual']}

    Referências de design:
    - O que gosta: {respostas['referencias_gosta']}
    - O que não gosta: {respostas['referencias_nao_gosta']}

    ## 8. SEO e Performance
    Necessidade de SEO: {'Sim' if respostas['seo'] == 'Sim' else 'Não'}
    {'Otimizações específicas solicitadas: ' + respostas['otimizacoes_seo'] if respostas['seo'] == 'Sim' else ''}

    Prioridade mobile: {'Alta' if respostas['mobile_prioritario'] == 'Sim' else 'Não especificada'}
    Certificado SSL: {'Necessário' if respostas['ssl'] == 'Sim' else 'Não solicitado'}

    ## 9. Plataforma e Hospedagem
    Plataforma preferida: {respostas['plataforma'] if respostas['plataforma'] else 'Não especificada'}
    Hospedagem: {'Já possui' if respostas['hospedagem'] == 'Sim' else 'Necessária'}

    ## 10. Governança Digital
    Uso de dados: {'Sim' if respostas['uso_dados'] == 'Sim' else 'Não'}
    Banner de consentimento: {'Necessário' if respostas['banner_cookies'] == 'Sim' else 'Não necessário'}
    Tagueamento: {'Sim' if respostas['tagueamento'] == 'Sim' else 'Não'}
    {'Tags específicas: ' + respostas['tags_especificas'] if respostas['tagueamento'] == 'Sim' else ''}

    ## 11. Integrações
    Integrações necessárias: {'Sim' if respostas['integracoes'] == 'Sim' else 'Não'}
    {'Detalhes das integrações: ' + respostas['detalhes_integracoes'] if respostas['integracoes'] == 'Sim' else ''}

    ## 12. Cronograma e Orçamento
    Prazo desejado: {respostas['prazo']}
    {'Orçamento estimado: ' + respostas['orcamento'] if respostas['tem_orcamento'] == 'Sim' else 'Orçamento não informado'}
    Manutenção pós-lançamento: {'Necessária' if respostas['manutencao'] == 'Sim' else 'Não solicitada'}

    ## 13. Considerações Adicionais
    {respostas['consideracoes_finais'] if respostas['consideracoes_finais'] else 'Nenhuma consideração adicional'}

    ---

    Por favor, formate este briefing em um documento profissional com:
    1. Seções claramente destacadas
    2. Listas com marcadores para facilitar a leitura
    3. Destaque para informações críticas
    4. Linguagem técnica apropriada para desenvolvimento web
    5. Resumo executivo no início destacando os pontos mais importantes
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Erro ao gerar o briefing: {str(e)}")
        return None

# Opção de upload de CSV
st.sidebar.header("Opção de Upload")
uploaded_file = st.sidebar.file_uploader("Faça upload de um arquivo CSV com as respostas", type=["csv"])

if uploaded_file is not None:
    try:
        # Lê o arquivo CSV
        df = pd.read_csv(uploaded_file)
        
        # Mostra pré-visualização
        st.sidebar.subheader("Pré-visualização do CSV")
        st.sidebar.write(df.head())
        
        # Mapeia para o formato interno
        respostas = mapear_csv_para_respostas(df)
        
        # Gera o briefing
        with st.spinner("Gerando briefing a partir do CSV..."):
            briefing = gerar_briefing(respostas)
            
            if briefing:
                st.success("Briefing gerado com sucesso a partir do CSV!")
                st.subheader("📄 Briefing Completo para Desenvolvimento de Site")
                st.markdown(briefing)
                
                # Opção para download
                st.download_button(
                    label="Baixar Briefing",
                    data=briefing,
                    file_name=f"briefing_site_{respostas['nome_empresa']}_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown"
                )
    except Exception as e:
        st.error(f"Erro ao processar o arquivo CSV: {str(e)}")

# Formulário manual
st.header("Ou preencha o formulário manualmente")
with st.form("formulario_briefing"):
    st.subheader("Informações Básicas")
    col1, col2 = st.columns(2)
    with col1:
        nome_empresa = st.text_input("Nome da empresa/instituição*", key="nome_empresa")
        nome_responsavel = st.text_input("Nome do responsável*", key="nome_responsavel")
    with col2:
        cargo_responsavel = st.text_input("Cargo do responsável*", key="cargo_responsavel")
        email_responsavel = st.text_input("E-mail*", key="email_responsavel")
        telefone_responsavel = st.text_input("Telefone*", key="telefone_responsavel")

    st.subheader("Descrição do Site")
    descricao_site = st.text_area("Descreva o site que deseja*", 
                                 placeholder="Ex: Um site institucional que apresenta a empresa e seus serviços...",
                                 key="descricao_site")

    st.subheader("Objetivos do Site")
    objetivos_principais = st.text_area("Principais objetivos*",
                                      placeholder="Ex: Melhorar a imagem institucional, facilitar a navegação...",
                                      key="objetivos_principais")
    objetivos_secundarios = st.text_area("Objetivos secundários",
                                       placeholder="Ex: Aumentar o tráfego orgânico, coletar dados de leads...",
                                       key="objetivos_secundarios")

    st.subheader("Público-Alvo")
    publico_alvo = st.text_area("Quem é o público-alvo do seu site?*",
                              placeholder="Descreva faixa etária, interesses, localização geográfica...",
                              key="publico_alvo")
    segmentos_especificos = st.text_input("Há algum segmento específico que precisa ser destacado?",
                                        placeholder="Ex: Clientes de uma região específica, público jovem...",
                                        key="segmentos_especificos")

    st.subheader("Concorrência e Diferenciação")
    concorrentes = st.text_input("Quem são seus principais concorrentes?",
                               placeholder="Liste os principais concorrentes",
                               key="concorrentes")
    col1, col2 = st.columns(2)
    with col1:
        gosta_concorrentes = st.text_area("O que você gosta nos sites dos concorrentes?",
                                        placeholder="Pontos positivos observados",
                                        key="gosta_concorrentes")
    with col2:
        nao_gosta_concorrentes = st.text_area("O que você não gosta nos sites dos concorrentes?",
                                            placeholder="Pontos negativos observados",
                                            key="nao_gosta_concorrentes")
    diferenciais = st.text_area("O que você espera que seu site ofereça de diferente?*",
                              placeholder="Funcionalidades exclusivas, diferenciação no atendimento...",
                              key="diferenciais")

    st.subheader("Características e Funcionalidades do Site")
    funcionalidades = st.text_area("Quais funcionalidades específicas você gostaria de incluir?*",
                                 placeholder="Formulários de contato, área de login, blog...",
                                 key="funcionalidades")
    col1, col2 = st.columns(2)
    with col1:
        conteudo_pronto = st.radio("Você já possui todo o conteúdo pronto (textos, imagens, vídeos)?*",
                                 ("Sim", "Não"), key="conteudo_pronto")
    with col2:
        numero_paginas = st.text_input("Quantas páginas aproximadamente o site terá?*",
                                     placeholder="Ex: 5-10 páginas",
                                     key="numero_paginas")
    paginas_desejadas = st.text_area("Quais páginas você gostaria de incluir no novo site?*",
                                   placeholder="Home, Sobre, Produtos, Contato, Blog...",
                                   key="paginas_desejadas")

    st.subheader("Estilo e Design")
    percepcao_visual = st.text_input("Como você gostaria que o site fosse visualmente percebido?*",
                                   placeholder="Ex: Como uma marca confiável, moderna, especializada...",
                                   key="percepcao_visual")
    col1, col2 = st.columns(2)
    with col1:
        referencias_gosta = st.text_area("Há algum site ou referência visual que você gosta?",
                                       placeholder="Links ou descrição dos pontos positivos",
                                       key="referencias_gosta")
    with col2:
        referencias_nao_gosta = st.text_area("Há alguma referência visual que você não gosta?",
                                           placeholder="Links ou descrição dos pontos negativos",
                                           key="referencias_nao_gosta")

    st.subheader("SEO, Performance e Segurança")
    col1, col2, col3 = st.columns(3)
    with col1:
        seo = st.radio("O site precisa ser otimizado para SEO?", ("Sim", "Não"), key="seo")
    with col2:
        mobile_prioritario = st.radio("A versão mobile é uma prioridade?", ("Sim", "Não"), key="mobile_prioritario")
    with col3:
        ssl = st.radio("Você precisa de certificado SSL?", ("Sim", "Não"), key="ssl")
    if seo == "Sim":
        otimizacoes_seo = st.text_input("Que tipo de otimização específica você deseja?",
                                      placeholder="SEO local, SEO para produtos/serviços...",
                                      key="otimizacoes_seo")

    st.subheader("Aspectos Técnicos e Hospedagem")
    col1, col2 = st.columns(2)
    with col1:
        plataforma = st.text_input("Preferência de plataforma para desenvolvimento",
                                 placeholder="WordPress, customizado, etc.",
                                 key="plataforma")
    with col2:
        hospedagem = st.radio("Você já possui hospedagem?", ("Sim", "Não"), key="hospedagem")

    st.subheader("Governança Digital e Tagueamento")
    col1, col2, col3 = st.columns(3)
    with col1:
        uso_dados = st.radio("Deseja usar dados de usuários (cookies, analytics)?", ("Sim", "Não"), key="uso_dados")
    with col2:
        banner_cookies = st.radio("Precisa de banner de consentimento para cookies?", ("Sim", "Não"), key="banner_cookies")
    with col3:
        tagueamento = st.radio("Precisa de tagueamento para monitoramento?", ("Sim", "Não"), key="tagueamento")
    
    if tagueamento == "Sim":
        tags_especificas = st.text_input("Quais tags de conversão/tracking precisará?",
                                       placeholder="Pixel do Facebook, Google Analytics...",
                                       key="tags_especificas")

    st.subheader("Integrações")
    integracoes = st.radio("Precisará integrar com plataformas externas ou APIs?", ("Sim", "Não"), key="integracoes")
    if integracoes == "Sim":
        detalhes_integracoes = st.text_input("Quais integrações específicas?",
                                           placeholder="APIs para conversão do Meta, CRM...",
                                           key="detalhes_integracoes")

    st.subheader("Cronograma e Orçamento")
    col1, col2 = st.columns(2)
    with col1:
        prazo = st.text_input("Expectativa de prazo para lançamento*",
                            placeholder="Ex: 3 meses, 6 meses...",
                            key="prazo")
    with col2:
        tem_orcamento = st.radio("Já tem um orçamento estimado?", ("Sim", "Não"), key="tem_orcamento")
        if tem_orcamento == "Sim":
            orcamento = st.text_input("Qual o orçamento estimado?",
                                    placeholder="Valor aproximado",
                                    key="orcamento")
    manutencao = st.radio("Precisará de manutenção contínua após lançamento?", ("Sim", "Não"), key="manutencao")

    st.subheader("Considerações Finais")
    consideracoes_finais = st.text_area("Alguma outra necessidade ou exigência não mencionada?",
                                      placeholder="Informações adicionais relevantes...",
                                      key="consideracoes_finais")

    # Botão de submissão
    submitted = st.form_submit_button("Gerar Briefing Completo")
    if submitted:
        # Validar campos obrigatórios
        campos_obrigatorios = {
            "nome_empresa": nome_empresa,
            "nome_responsavel": nome_responsavel,
            "cargo_responsavel": cargo_responsavel,
            "email_responsavel": email_responsavel,
            "telefone_responsavel": telefone_responsavel,
            "descricao_site": descricao_site,
            "objetivos_principais": objetivos_principais,
            "publico_alvo": publico_alvo,
            "diferenciais": diferenciais,
            "funcionalidades": funcionalidades,
            "conteudo_pronto": conteudo_pronto,
            "numero_paginas": numero_paginas,
            "paginas_desejadas": paginas_desejadas,
            "percepcao_visual": percepcao_visual,
            "prazo": prazo
        }
        
        campos_faltantes = [campo for campo, valor in campos_obrigatorios.items() if not valor]
        if campos_faltantes:
            st.error(f"Por favor, preencha todos os campos obrigatórios. Faltando: {', '.join(campos_faltantes)}")
        else:
            # Coletar todas as respostas em um dicionário
            respostas = {
                "nome_empresa": nome_empresa,
                "nome_responsavel": nome_responsavel,
                "cargo_responsavel": cargo_responsavel,
                "email_responsavel": email_responsavel,
                "telefone_responsavel": telefone_responsavel,
                "descricao_site": descricao_site,
                "objetivos_principais": objetivos_principais,
                "objetivos_secundarios": objetivos_secundarios,
                "publico_alvo": publico_alvo,
                "segmentos_especificos": segmentos_especificos,
                "concorrentes": concorrentes,
                "gosta_concorrentes": gosta_concorrentes,
                "nao_gosta_concorrentes": nao_gosta_concorrentes,
                "diferenciais": diferenciais,
                "funcionalidades": funcionalidades,
                "conteudo_pronto": conteudo_pronto,
                "numero_paginas": numero_paginas,
                "paginas_desejadas": paginas_desejadas,
                "percepcao_visual": percepcao_visual,
                "referencias_gosta": referencias_gosta,
                "referencias_nao_gosta": referencias_nao_gosta,
                "seo": seo,
                "otimizacoes_seo": otimizacoes_seo if seo == "Sim" else "",
                "mobile_prioritario": mobile_prioritario,
                "ssl": ssl,
                "plataforma": plataforma,
                "hospedagem": hospedagem,
                "uso_dados": uso_dados,
                "banner_cookies": banner_cookies,
                "tagueamento": tagueamento,
                "tags_especificas": tags_especificas if tagueamento == "Sim" else "",
                "integracoes": integracoes,
                "detalhes_integracoes": detalhes_integracoes if integracoes == "Sim" else "",
                "prazo": prazo,
                "tem_orcamento": tem_orcamento,
                "orcamento": orcamento if tem_orcamento == "Sim" else "",
                "manutencao": manutencao,
                "consideracoes_finais": consideracoes_finais
            }

            # Gerar o briefing
            with st.spinner("Gerando briefing profissional..."):
                briefing = gerar_briefing(respostas)
                
                if briefing:
                    st.success("Briefing gerado com sucesso!")
                    st.subheader("📄 Briefing Completo para Desenvolvimento de Site")
                    st.markdown(briefing)
                    
                    # Opção para download
                    st.download_button(
                        label="Baixar Briefing",
                        data=briefing,
                        file_name=f"briefing_site_{nome_empresa}_{datetime.now().strftime('%Y%m%d')}.md",
                        mime="text/markdown"
                    )
