import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Simulador Ótica AL", layout="wide")

st.title("Simulador: Fenómenos Óticos (AL 11.º Ano)")
st.markdown("""
Este simulador permite investigar experimentalmente os fenómenos de **reflexão, refração, reflexão total** e **difração da luz**, de acordo com as Aprendizagens Essenciais de Física e Química A (11.º Ano).
""")

import unicodedata
import re

# --- Motor de Avaliação Melhorado ---
def normalizar_texto(texto):
    """Remove acentos e normaliza o texto para melhor comparação."""
    texto = texto.lower().strip()
    # Remove acentos (e.g., 'refração' -> 'refracao')
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    # Remove pontuação excessiva
    texto = re.sub(r'[^a-z0-9\s=*/]', ' ', texto)
    return texto

def avaliar_resposta(user_text, reference_texts, keywords=None):
    """
    Motor híbrido: combina TF-IDF + verificação de palavras-chave obrigatórias.
    keywords: lista de listas de sinónimos aceitáveis (ex: [['velocidade', 'vel'], ['vacuo', 'vacuu']])
    """
    if not user_text or not user_text.strip():
        return 0, "Por favor, escreva uma resposta!"
    
    user_norm = normalizar_texto(user_text)
    ref_norm  = [normalizar_texto(r) for r in reference_texts]
    
    # --- 1. Similaridade TF-IDF ---
    all_texts = [user_norm] + ref_norm
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),   # bigramas para melhor contexto
        sublinear_tf=True,    # suavização TF para textos curtos
        min_df=1
    ).fit_transform(all_texts)
    vectors = vectorizer.toarray()
    similarities = cosine_similarity(vectors[0:1], vectors[1:])
    tfidf_score = float(np.max(similarities))
    
    # --- 2. Score de Palavras-Chave ---
    keyword_score = 1.0
    missing_kws = []
    if keywords:
        found = 0
        for kw_group in keywords:
            kw_norm = [normalizar_texto(k) for k in kw_group]
            if any(kw in user_norm for kw in kw_norm):
                found += 1
            else:
                missing_kws.append(kw_group[0])  # nome legível do grupo
        keyword_score = found / len(keywords)
    
    # --- 3. Score final ponderado (60% TF-IDF, 40% keywords) ---
    if keywords:
        final_score = 0.6 * tfidf_score + 0.4 * keyword_score
    else:
        final_score = tfidf_score
    
    # --- 4. Feedback detalhado ---
    if final_score > 0.70:
        msg = "✅ **Muito boa resposta!** Os conceitos científicos essenciais estão presentes e corretos."
    elif final_score > 0.40:
        if missing_kws:
            kw_list = ", ".join(f'`{k}`' for k in missing_kws[:3])
            msg = f"⚠️ **Resposta parcial.** Reveja e inclua os seguintes termos: {kw_list}."
        else:
            msg = "⚠️ **Resposta parcial.** Está no bom caminho, mas tente ser mais completo e preciso."
    else:
        if missing_kws:
            kw_list = ", ".join(f'`{k}`' for k in missing_kws[:4])
            msg = f"❌ **Resposta insuficiente.** Parece que faltam conceitos fundamentais como: {kw_list}."
        else:
            msg = "❌ **Resposta insuficiente.** Releia os conceitos teóricos e tente de novo."
    
    return final_score, msg

# Abas para separar as duas partes da AL e Questionário
tab1, tab2, tab3 = st.tabs([
    "Parte I: Reflexão, Refração e Reflexão Total", 
    "Parte II: Difração da Luz",
    "Avaliação & Questões"
])

with tab1:
    st.header("Reflexão e Refração da Luz")
    
    col1, col2 = st.columns([1.5, 2])
    
    with col1:
        st.subheader("Parâmetros")
        # Dicionário de meios e respetivos índices de refração
        meios = {
            "Ar (n ≈ 1.00)": 1.000,
            "Água (n ≈ 1.33)": 1.333,
            "Acetona (n ≈ 1.36)": 1.360,
            "Acrílico (n ≈ 1.49)": 1.490,
            "Vidro (n ≈ 1.52)": 1.520
        }
        
        meio1_nome = st.selectbox("Meio de Incidência (Meio 1)", options=list(meios.keys()), index=0)
        meio2_nome = st.selectbox("Meio de Refração (Meio 2)", options=list(meios.keys()), index=4)
        
        n1 = meios[meio1_nome]
        n2 = meios[meio2_nome]
        
        # Ocultar o número nativamente usando o formato (format=" ") para não poluir a Tab 2 com CSS global
        st.write("**Ângulo de incidência (mova a barra debaixo):**")
        angle_i_deg = st.slider(
            "Ângulo de incidência ($\\alpha_i$ em graus)", 
            min_value=0.0, 
            max_value=90.0, 
            value=30.0, 
            step=1.0, 
            label_visibility="collapsed",
            format=" "
        )
        
        # Ocultar APENAS o balão/min/max deste slider específico usando CSS sem estragar o Tab 2
        # Como o format=" " já retira o valor, apenas precisamos de esconder o min/max e o balão de cima.
        st.markdown(
            """
            <style>
                /* Ocultar os números Min e Max laterais do slider do ângulo */
                div[data-testid="stSliderTickBar"] {display: none !important;}
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # Cálculos de reflexão e refração (Fresnel Equations aproximado para alpha)
        angle_i_rad = np.radians(angle_i_deg)
        angle_refletido_deg = angle_i_deg
        
        # Lei de Snell-Descartes: n1 * sin(a_i) = n2 * sin(a_R)
        sin_R = (n1 / n2) * np.sin(angle_i_rad)
        
        reflexao_total = False
        angulo_critico = None
        angle_R_deg = None
        
        # Intensidades aproximadas (Fresnel) para reflexão e refração dinâmicas
        if sin_R >= 1:
            reflexao_total = True
            angulo_critico = np.degrees(np.arcsin(n2 / n1))
            R_intensity = 1.0
            T_intensity = 0.0
        else:
            angle_R_rad = np.arcsin(sin_R)
            angle_R_deg = np.degrees(angle_R_rad)
            if n1 > n2:
                angulo_critico = np.degrees(np.arcsin(n2 / n1))
                
            # Coeficientes Fresnel (aproximação mediação s-polarized e p-polarized para opacidade geral visual)
            rs = (n1 * np.cos(angle_i_rad) - n2 * np.cos(angle_R_rad)) / (n1 * np.cos(angle_i_rad) + n2 * np.cos(angle_R_rad))
            rp = (n1 * np.cos(angle_R_rad) - n2 * np.cos(angle_i_rad)) / (n1 * np.cos(angle_R_rad) + n2 * np.cos(angle_i_rad))
            
            # Intensidade refletida (Reflectance) = média
            R = (abs(rs)**2 + abs(rp)**2) / 2
            
            # Ajuste visual exagerado para a interface dependente da critica (se existir):
            # Muito próximo do angulo critico o raio T_intensity cai a pique
            if angulo_critico is not None:
              # Tornar a reflexão dependente da aproximação ao critico para um efeito dinâmico vistoso
              approach_to_critical = min(1.0, angle_i_deg / angulo_critico)
              R_intensity = approach_to_critical ** 3  # Crescimento exponencial para o final
              R_intensity = max(R, R_intensity)  # O que for maior salva para garantir reflexão normal também 
            else:
              R_intensity = R
              
            T_intensity = 1.0 - R_intensity 
            
            # Se a intensidade for inferior a 4%, corta a opacidade totalmente para não desenhar
            if R_intensity < 0.04:
                R_intensity = 0.0
            if T_intensity < 0.04:
                T_intensity = 0.0
                
            # Um pequeno truque visual, se a transmissão estiver quase nula (perto d ângulo crítico limite), desligar
            if reflexao_total or (angulo_critico is not None and angle_i_deg >= angulo_critico * 0.98):
               T_intensity = 0.0
               R_intensity = 1.0
                
        # Exibição de resultados na interface
        st.write("---")
        st.subheader("Medições Experimentais do Ângulo Crítico ($\\theta_c$)")
        
        # Inputs para os alunos preencherem o ângulo limite
        st.write("Determine experimentalmente o **ângulo crítico** (ou ângulo limite) para este par de meios. Este é o menor ângulo de incidência para o qual ocorre a reflexão total da luz (o raio refratado deixa de emergir no segundo meio).")
        
        col_med_1, col_med_2 = st.columns(2)
        with col_med_1:
            med_critico = st.number_input("Valor lido no transferidor (graus)", min_value=0.0, max_value=90.0, value=0.0, step=0.5, key="crit_val")
        with col_med_2:
            inc_critico = st.number_input("Incerteza do transferidor (± graus)", min_value=0.0, max_value=5.0, value=0.5, step=0.1, key="crit_inc", help="Metade da menor divisão da escala")
        
        verificar = st.button("Verificar Resultados Teóricos")
        
        if verificar:
            st.write("---")
            st.subheader("Resultados Teóricos e Avaliação")
            
            if angulo_critico is None:
                 st.warning("⚠️ **Nota:** Com os meios selecionados ($n_1 < n_2$), não é possível observar o fenómeno de reflexão total, logo não existe ângulo crítico!")
                 if med_critico > 0:
                     st.error("❌ Inseriu um valor de um ângulo crítico para uma montagem experimental onde tal fenómeno é fisicamente impossível.")
            else:
                 st.write(f"**Ângulo crítico teórico ($\\theta_c$):** {angulo_critico:.2f}°")
                 if abs(med_critico - angulo_critico) <= inc_critico:
                     st.success("✅ O valor medido é consistente com as Leis de Snell-Descartes!")
                 else:
                     st.error("❌ O valor medido apresenta um desvio superior à incerteza em relação ao valor teórico.")
                 
    with col2:
        # Gráfico interativo
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Superfície de separação
        ax.axhline(0, color='gray', linewidth=2, linestyle='--')
        ax.axvline(0, color='black', linewidth=1, linestyle=':') # Normal
        
        ax.fill_between([-2.0, 2.0], 0, 2.0, color='lightblue', alpha=0.3, label='Meio 1 ($n_1$)')
        ax.fill_between([-2.0, 2.0], -2.0, 0, color='lightgreen', alpha=0.3, label='Meio 2 ($n_2$)')
        
        # Desenhar Transferidor (Semicírculos)
        protractor_radius = 1.2
        circle = plt.Circle((0, 0), protractor_radius, color='gray', fill=False, linestyle='--', alpha=0.5)
        ax.add_patch(circle)
        
        # Marcas do transferidor (de 1 em 1 graus)
        for angle in range(0, 360, 1):
            rad = np.radians(angle)
            
            # Ajustar profundidade do traço consoante a divisão (10, 5, 1)
            if angle % 10 == 0:
                inner_r = 0.92
                alpha_line = 0.4
                lw = 1.2
            elif angle % 5 == 0:
                inner_r = 0.95
                alpha_line = 0.3
                lw = 0.8
            else:
                inner_r = 0.97
                alpha_line = 0.15
                lw = 0.5
                
            x_start = protractor_radius * inner_r * np.cos(rad)
            y_start = protractor_radius * inner_r * np.sin(rad)
            x_end = protractor_radius * np.cos(rad)
            y_end = protractor_radius * np.sin(rad)
            ax.plot([x_start, x_end], [y_start, y_end], color='black', alpha=alpha_line, linewidth=lw)
            
            # Textos a cada 10 graus (apenas)
            if angle % 10 == 0:
                # Ajustar ângulo para mostrar em torno da normal
                display_angle = abs((angle % 180) - 90)
                # Não escrever o '0' duas vezes e afastar o texto
                if display_angle >= 0:
                   ax.text(x_end * 1.08, y_end * 1.08, f"{display_angle}°", ha='center', va='center', fontsize=6, alpha=0.6)

        # Distância máxima de desenho do raio para que saiam do transferidor (1.2 -> 1.8)
        ray_length = 1.8
        
        # Traçar raios
        # Raio Incidente (Linha Vermelha, Seta Vermelha)
        x_inc = -ray_length * np.sin(angle_i_rad)
        y_inc = ray_length * np.cos(angle_i_rad)
        ax.plot([x_inc, 0], [y_inc, 0], 'r-', linewidth=1.5)
        ax.plot([], [], 'r-', linewidth=2, label='Raio Incidente') # Dummy para a legenda
        
        # Seta do raio incidente apenas com a cabeça (head) para evitar artefatos de "tail" superpostos longo do raio
        ax.annotate('', xy=(x_inc*0.4, y_inc*0.4), xytext=(x_inc*0.5, y_inc*0.5), 
                    arrowprops=dict(facecolor='r', edgecolor='r', width=0, headwidth=8, headlength=10, shrink=0))
        
        # Desenhar Laser na ponta do raio incidente
        laser_width = 0.2
        laser_length = 0.4
        dx = x_inc/np.linalg.norm([x_inc,y_inc])
        dy = y_inc/np.linalg.norm([x_inc,y_inc])
        
        # Transformar coordenadas para desenhar o rectângulo do laser
        angle_laser = np.degrees(np.arctan2(y_inc, x_inc))
        rect = plt.Rectangle((x_inc - dx*laser_length/2 + dy*laser_width/2, 
                              y_inc - dy*laser_length/2 - dx*laser_width/2), 
                              laser_length, laser_width, 
                              angle=angle_laser, color='darkred', zorder=10)
        ax.add_patch(rect)


        # Raio Refletido (Linha Vermelha, Seta Azul)
        x_refl = ray_length * np.sin(angle_i_rad)
        y_refl = ray_length * np.cos(angle_i_rad)
        ax.plot([0, x_refl], [0, y_refl], 'r-', linewidth=1.5, alpha=R_intensity)
        ax.plot([], [], 'b-', linewidth=2, label='Raio Refletido (Seta)') # Dummy para a legenda
        
        ax.annotate('', xy=(x_refl*0.5, y_refl*0.5), xytext=(x_refl*0.4, y_refl*0.4), 
                    arrowprops=dict(facecolor='b', edgecolor='b', width=0, headwidth=8, headlength=10, shrink=0, alpha=R_intensity))

        # Raio Refratado (Linha Vermelha, Seta Verde)
        if not reflexao_total:
            x_refr = ray_length * np.sin(angle_R_rad)
            y_refr = -ray_length * np.cos(angle_R_rad)
            ax.plot([0, x_refr], [0, y_refr], 'r-', linewidth=1.5, alpha=T_intensity)
            ax.plot([], [], 'g-', linewidth=2, label='Raio Refratado (Seta)') # Dummy para a legenda
            
            ax.annotate('', xy=(x_refr*0.5, y_refr*0.5), xytext=(x_refr*0.4, y_refr*0.4), 
                        arrowprops=dict(facecolor='g', edgecolor='g', width=0, headwidth=8, headlength=10, shrink=0, alpha=T_intensity))
            
        ax.set_xlim(-2.0, 2.0)
        ax.set_ylim(-2.0, 2.0)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.legend(loc="upper right")
        
        st.pyplot(fig)


with tab2:
    st.header("Difração da Luz")
    st.markdown(r"Equação da rede de difração: $n\lambda = d \sin\theta$, com $\tan\theta = \frac{X}{D}$")
    
    if "show_x_hint" not in st.session_state:
        st.session_state.show_x_hint = False
        
    col3, col4 = st.columns([1, 2])
    
    with col3:
        st.subheader("Parâmetros do Laser e Rede")
        cores_laser = {
            "Vermelho": 650,
            "Amarelo": 590,
            "Verde": 532,
            "Azul": 450,
            "Violeta": 400
        }
        cor_selecionada = st.selectbox("Cor do Laser", options=list(cores_laser.keys()), index=0)
        wav_nm = cores_laser[cor_selecionada]
        wav_m = wav_nm * 1e-9  # metros
        
        linhas_mm = st.slider("Constante da rede (linhas / mm)", min_value=10, max_value=600, value=300, step=10)
        d_m = 1 / (linhas_mm * 1000) # metros (distância d entre fendas)
        
        dist_D = st.slider("Distância ao Alvo ($D$ em metros)", min_value=0.1, max_value=3.0, value=1.0, step=0.1)
        
        # Cálculos de Difração - Máximos na Rede
        
        # Determinar posição X do máximo de 1.ª ordem (n=1)
        sin_theta = wav_m / d_m
        if sin_theta > 1:
            st.error("Não se formam máximos de 1.ª ordem para esta configuração.")
        else:
            theta_rad = np.arcsin(sin_theta)
            dist_X_m = dist_D * np.tan(theta_rad)
            dist_X_cm = dist_X_m * 100
            
            if st.session_state.show_x_hint:
                st.success(f"**Distância $X$ ao máximo central:** {dist_X_cm:.2f} cm")
            
    with col4:
        # 1. VISUALIZAÇÃO MACROSCÓPICA DA MONTAGEM (NOVO)
        if sin_theta <= 1:
            st.subheader("Visualização da Montagem")
            fig_setup, ax_setup = plt.subplots(figsize=(8, 2.5))
            
            # Correntes aproximadas para o feixe laser
            if wav_nm > 600:
                cor_laser = '#FF0000' # Vermelhos
            elif wav_nm >= 580:
                cor_laser = '#FFD700' # Amarelos (Gold)
            elif wav_nm > 500:
                cor_laser = '#00FF00' # Verdes
            elif wav_nm >= 450:
                cor_laser = '#0088FF' # Azuis claros
            else:
                cor_laser = '#4400FF' # Violetas
                
            # Laser Box
            laser_width = 0.4
            laser_height = 0.6
            rect = plt.Rectangle((0, -laser_height/2), laser_width, laser_height, color='gray', zorder=10)
            ax_setup.add_patch(rect)
            ax_setup.text(0.2, 0, 'Laser', ha='center', va='center', color='white', fontsize=10, zorder=11, rotation=90)
            
            # Fenda
            fenda_x = 2.0
            ax_setup.plot([fenda_x, fenda_x], [0.1, 1], color='black', linewidth=4)
            ax_setup.plot([fenda_x, fenda_x], [-1, -0.1], color='black', linewidth=4)
            
            # Raio primário (Laser até Fenda)
            ax_setup.fill_between([laser_width, fenda_x], -0.03, 0.03, color=cor_laser, alpha=0.6)
            
            # Alvo / Ecrã móvel em perspetiva pseudo-3D
            # Simular o ecrã a afastar-se usando dist_D para escalar a posição visual
            min_D, max_D = 0.1, 3.0
            alvo_x = 3.5 + ((dist_D - min_D) / (max_D - min_D)) * 4.0 
            
            # Desenhar o ecrã como um polígono inclinado (perspetiva)
            largura_ecra = 0.8
            altura_ecra = 1.3
            inclinacao = 0.5 # Deslocamento x para simular inclinação 3D
            
            ecra_coords = [
                (alvo_x, altura_ecra),                             # Topo Esquerda
                (alvo_x + inclinacao, altura_ecra - 0.2),          # Topo Direita
                (alvo_x + inclinacao, -altura_ecra - 0.2),         # Fundo Direita
                (alvo_x, -altura_ecra)                             # Fundo Esquerda
            ]
            
            ecra_patch = plt.Polygon(ecra_coords, closed=True, color='black', zorder=5)
            ax_setup.add_patch(ecra_patch)
            
            ax_setup.text(alvo_x + inclinacao/2, altura_ecra + 0.2, f'D = {dist_D} m', ha='center', va='bottom', fontsize=9)
            
            # Centro geométrico do ecrã em perspetiva
            centro_x = alvo_x + inclinacao/2
            centro_y = -0.1
            
            # Desenhar máximos de difração brilhantes NO ecrã inclinado
            # O eixo X do difratograma no papel milimétrico espalha-se na linha central do ecrã
            
            # Ajuste de escala visual para os pontos caberem no ecrã (X máx aprox 1.5 cm visuais)
            # Vamos limitar dist_X_m por questões visuais no gráfico
            escala_X = min(0.8, dist_X_m) if dist_X_m > 0 else 0
            
            # O eixo "horizontal" da difração no ecrã desenha-se unindo as laterais do ecrã
            # Equação da reta central do ecrã:
            dy_centro = (-altura_ecra - 0.2 - altura_ecra) / 2 # Ponto médio lateral direita
            
            # Máximo Central (Ordem 0)
            ax_setup.plot(centro_x, centro_y, 'o', color=cor_laser, markersize=5, alpha=0.9, zorder=6)
            
            if sin_theta <= 1:
                # O vetor diretor do plano ao longo do qual os pontos surgem: (inclinacao, -0.2)
                norma = np.sqrt(inclinacao**2 + (-0.2)**2)
                vx = inclinacao / norma
                vy = -0.2 / norma
                
                # Deslocamento visual baseado em dist_X_m ajustado para caber na moldura do ecrã
                desloc = min(0.25, dist_X_m * 0.8) 
                
                # Máximos de 1.ª Ordem
                x1_dir = centro_x + vx * desloc
                y1_dir = centro_y + vy * desloc
                x1_esq = centro_x - vx * desloc
                y1_esq = centro_y - vy * desloc
                
                # O limite do papel milimétrico é de +- 30 cm, vamos sincronizar as views
                if dist_X_cm <= 30.0:
                    ax_setup.plot(x1_dir, y1_dir, 'o', color=cor_laser, markersize=3, alpha=0.7, zorder=6)
                    ax_setup.plot(x1_esq, y1_esq, 'o', color=cor_laser, markersize=3, alpha=0.7, zorder=6)
                    
                    # Máximos de 2.ª Ordem se couberem e se existirem
                    sin_theta_2 = 2 * wav_m / d_m
                    if sin_theta_2 <= 1:
                         theta_rad_2 = np.arcsin(sin_theta_2)
                         dist_X2_m = dist_D * np.tan(theta_rad_2)
                         dist_X2_cm = dist_X2_m * 100
                         desloc2 = min(0.25, dist_X2_m * 0.8)
                         
                         if dist_X2_cm <= 30.0:
                             x2_dir = centro_x + vx * desloc2
                             y2_dir = centro_y + vy * desloc2
                             x2_esq = centro_x - vx * desloc2
                             y2_esq = centro_y - vy * desloc2
                             
                             ax_setup.plot(x2_dir, y2_dir, 'o', color=cor_laser, markersize=1.5, alpha=0.5, zorder=6)
                             ax_setup.plot(x2_esq, y2_esq, 'o', color=cor_laser, markersize=1.5, alpha=0.5, zorder=6)

            # Cone de Difração (espalhamento) da Fenda para o Ecrã
            # O cone primário limita-se um pouco para não cobrir o ecrã a 100% verticalmente
            cone_abertura = 0.4
            ax_setup.fill_between([fenda_x, alvo_x, alvo_x+inclinacao], 
                                  [-0.03, -cone_abertura, -cone_abertura-0.2], 
                                  [0.03, cone_abertura, cone_abertura-0.2], 
                                  color=cor_laser, alpha=0.2, zorder=1)
            
            # Eixo Principal
            ax_setup.plot([0, centro_x+0.5], [0, centro_y], color='black', linestyle='--', linewidth=0.5, alpha=0.5, zorder=4)


            ax_setup.set_xlim(-0.5, 8.5)
            ax_setup.set_ylim(-1.5, 1.5)
            ax_setup.axis('off')
            st.pyplot(fig_setup)

    st.write("---")
    col_padL, col_center, col_padR = st.columns([1, 4, 1])
    with col_center:
        # 2. ILUSTRAÇÃO DOS MÁXIMOS NO ALVO (ANTERIOR)
        st.subheader("Padrão de Intensidade no Alvo")
        if sin_theta <= 1:
            # Reduzir a altura para metade (10x5 em vez de 10x10) mantendo a largura
            fig2, ax2 = plt.subplots(figsize=(12, 6))
            
            # Ponto central intenso
            ax2.plot(0, 0, 'ro', markersize=14, label="Máximo Central", alpha=0.9)
            
            # Máximos de 1.ª Ordem (se couberem no papel <= 30cm)
            if dist_X_cm <= 30.0:
                ax2.plot(dist_X_cm, 0, 'ro', markersize=10, label="Máximo 1.ª Ordem", alpha=0.7)
                ax2.plot(-dist_X_cm, 0, 'ro', markersize=10, alpha=0.7)
                
                # Máximos de 2.ª Ordem (se existir e couber)
                sin_theta_2 = 2 * wav_m / d_m
                if sin_theta_2 <= 1:
                    theta_rad_2 = np.arcsin(sin_theta_2)
                    dist_X2_m = dist_D * np.tan(theta_rad_2)
                    dist_X2_cm = dist_X2_m * 100
                    if dist_X2_cm <= 30.0:
                        ax2.plot(dist_X2_cm, 0, 'ro', markersize=6, label="Máximo 2.ª Ordem", alpha=0.5)
                        ax2.plot(-dist_X2_cm, 0, 'ro', markersize=6, alpha=0.5)

            # As quadrículas do papel milimétrico não devem ser variáveis
            # Reduzir o eixo vertical a metade (+- 15cm vs +- 30cm horizontais)
            ax2.set_xlim(-30, 30)
            ax2.set_ylim(-15, 15)
            ax2.set_aspect('equal')
            
            # Formatar eixo interativo como papel milimétrico (quadriculado)
            from matplotlib.ticker import MultipleLocator
            
            # Eixo X: marcas maiores de 1 em 1 cm, marcas menores de 0.1 em 0.1 cm (1 mm)
            ax2.xaxis.set_major_locator(MultipleLocator(1))
            ax2.xaxis.set_minor_locator(MultipleLocator(0.1))
            
            # Ocultar os números do eixo X por completo, pois sobrepõem-se e tornam a escala ilegível.
            ax2.tick_params(axis='x', which='both', labelbottom=False)
            
            # Eixo Y: (Opcional, apenas para criar a malha quadrada do papel perfeitamente)
            ax2.yaxis.set_major_locator(MultipleLocator(1))
            ax2.yaxis.set_minor_locator(MultipleLocator(0.1))
            
            # Desenhar as linhas da grelha à semelhança do papel milimétrico clássico
            ax2.grid(True, which='major', color='black', linestyle='-', linewidth=0.6, alpha=0.3)
            ax2.grid(True, which='minor', color='gray', linestyle='-', linewidth=0.3, alpha=0.2)
            
            # Remover o eixo y visível (esconder as labels y para ter apenas o aspeto do papel)
            ax2.set_yticklabels([])
            
            # Remover as bordas fortes ('spines') do gráfico para parecer uma folha
            for spine in ax2.spines.values():
                spine.set_visible(False)
            
            ax2.set_xlabel("Distância $X$ no alvo")
            ax2.set_title("Padrão de Difração no Alvo (Papel Milimétrico)")
            
            # Adicionar nota explicativa da escala do papel milimétrico 
            # Colocar o texto fora da zona dos pontos para evitar a colisão visual
            ax2.text(0.01, 0.95, r'Cada quadrícula maior: $1\,cm \times 1\,cm$',
                     transform=ax2.transAxes, ha='left', va='top',
                     fontsize=11, color='darkred', weight='bold',
                     bbox=dict(facecolor='white', alpha=0.9, edgecolor='gray', boxstyle='round,pad=0.3'))
            
            # Legenda normal do lado direito
            ax2.legend(loc='upper right')
            
            # Mudar a cor dos pontos consoante o lambda aproximado
            for collection in ax2.collections:
              pass # (Isto é opcional e apenas estético)
            
            for line in ax2.lines:
                line.set_color(cor_laser)

            st.pyplot(fig2)
            
            if st.session_state.show_x_hint:
                st.info("💡 **Dica:** Para uma melhor leitura do valor $X$, tenta comparar as tuas medições no papel milimétrico com o valor de referência que o simulador te fornece.")

    st.write("---")
    st.subheader("Análise Gráfica: $X$ em função de $D$")
    st.markdown("Registe os valores medidos da distância $X$ ao máximo de 1.ª ordem para diferentes distâncias $D$ do ecrã à rede. O declive da reta de regressão linear corresponde a $\\tan(\\theta)$.")
    
    col_table, col_plot = st.columns([1, 2])
    
    with col_table:
        if "tabela_difracao" not in st.session_state:
            import pandas as pd
            st.session_state.tabela_difracao = pd.DataFrame({
                "D (m)": [0.2, 0.4, 0.6, 0.8, 1.0],
                "X (m)": [0.0, 0.0, 0.0, 0.0, 0.0]
            })
            
        edited_df = st.data_editor(st.session_state.tabela_difracao, num_rows="dynamic", width="stretch")
        st.session_state.tabela_difracao = edited_df
        
    with col_plot:
        df_valid = edited_df.dropna()
        # Verificar se há pelo menos dois pontos com D > 0 e X > 0 para traçar um gráfico significativo
        df_valid = df_valid[(df_valid["D (m)"] > 0) & (df_valid["X (m)"] > 0)]
        
        if len(df_valid) >= 2:
            x_vals = df_valid["D (m)"].values
            y_vals = df_valid["X (m)"].values
            
            try:
                # Ajuste linear y = mx + b
                m, b = np.polyfit(x_vals, y_vals, 1)
                
                fig3, ax3 = plt.subplots(figsize=(8, 4))
                ax3.plot(x_vals, y_vals, 'o', color='darkred', label='Dados experimentais')
                
                x_fit = np.linspace(0, max(x_vals)*1.1 if len(x_vals)>0 else 1, 100)
                y_fit = m * x_fit + b
                ax3.plot(x_fit, y_fit, '-', color='blue', alpha=0.6, label=f'Ajuste Linear: $X = {m:.4f} D {b:+.4f}$')
                
                ax3.set_xlabel('Distância ao Ecrã, $D$ (m)')
                ax3.set_ylabel('Posição do Máximo, $X$ (m)')
                ax3.set_title("Gráfico $X = f(D)$")
                ax3.grid(True, linestyle='--', alpha=0.7)
                ax3.legend()
                
                st.pyplot(fig3)
                
                st.info(f"**Declive obtido ($m$):** {m:.4f}")
                
                if sin_theta <= 1:
                    tan_theta_teorico = np.tan(theta_rad)
                    theta_teorico_deg = np.degrees(theta_rad)
                    
                    st.write("---")
                    st.write("Determine o ângulo de difração $\\theta$ a partir do declive da reta ($m = \\tan(\\theta)$):")
                    med_theta = st.number_input("O seu valor calculado para $\\theta$ (graus)", min_value=0.0, max_value=90.0, value=0.0, step=0.1, key="theta_calc")
                    
                    if st.button("Verificar Ângulo"):
                        if med_theta > 0:
                            erro_relativo = abs(med_theta - theta_teorico_deg) / theta_teorico_deg * 100
                            st.write(f"**Ângulo Teórico:** {theta_teorico_deg:.2f}°")
                            st.write(f"**Erro Relativo:** {erro_relativo:.1f}%")
                            
                            if erro_relativo < 5.0:
                                st.success("✅ Excelente precisão! O seu valor está muito próximo do valor teórico.")
                            elif erro_relativo >= 10.0:
                                st.warning("⚠️ Tiveste um erro superior a 10 %. Queres tentar de novo com dicas dadas pelo simulador?")
                                def enable_hint():
                                    st.session_state.show_x_hint = True
                                st.button("Sim, quero uma dica!", key="hint_btn", on_click=enable_hint)
                            else:
                                st.warning("⚠️ O erro é superior a 5%. Reveja os seus cálculos.")
                        else:
                            st.warning("Insira um valor maior que 0 para verificar.")
            except Exception as e:
                st.warning("Não foi possível realizar o ajuste linear. Verifique os valores inseridos.")
        else:
            st.info("Insira pelo menos 2 pontos (D > 0 e X > 0) na tabela para gerar o gráfico e o ajuste linear.")

with tab3:
    st.header("Questionário e Avaliação")
    st.markdown("""
    Responda às seguintes questões. O simulador analisa a qualidade das respostas com recurso a **Inteligência Artificial**, 
    verificando a presença de conceitos-chave e a proximidade com respostas de referência.
    """)
    
    # --- Questões Pré-Laboratoriais ---
    st.subheader("📚 I. Questões Pré-Laboratoriais")
    
    with st.expander("🔵 Pergunta 1: O que é o índice de refração de um meio?", expanded=True):
        st.caption("Dica: pense na relação entre a velocidade da luz e o meio de propagação.")
        resp1 = st.text_area("A sua resposta:", key="q1_pre", height=100,
                             placeholder="O índice de refração ...")
        if st.button("Submeter Resposta 1", type="primary"):
            modelos1 = [
                "O índice de refração é a razão entre a velocidade da luz no vácuo e a velocidade da luz no meio.",
                "Representa a dificuldade da luz se propagar num meio em relação ao vácuo. n = c dividido por v.",
                "O índice de refração mede quanto a velocidade da luz diminui ao entrar num meio óptico. Quanto maior o n, mais lenta a luz.",
                "n igual a c sobre v onde c e a velocidade da luz no vacuo e v a velocidade no meio.",
                "razao velocidade luz vacuo velocidade meio indice refracao formula n c v",
            ]
            kws1 = [
                ["indice", "índice", "n "],
                ["velocidade", "vel "],
                ["vacuo", "vácuo", "vacio"],
                ["razao", "razão", "quociente", "c/v", "c / v"],
            ]
            score1, feedback1 = avaliar_resposta(resp1, modelos1, kws1)
            if score1 > 0.70:
                st.success(feedback1)
            elif score1 > 0.40:
                st.warning(feedback1)
            else:
                st.error(feedback1)
            st.progress(min(score1, 1.0), text=f"Pontuação: {score1*100:.0f}%")
            with st.expander("Ver resposta modelo", expanded=False):
                st.info("O **índice de refração** ($n$) de um meio é definido como a razão entre a velocidade da luz no vácuo ($c$) e a velocidade da luz nesse meio ($v$): $n = c / v$. Um valor maior de $n$ indica que a luz se propaga mais lentamente.")

    with st.expander("🔵 Pergunta 2: Enuncie a Lei de Snell-Descartes para a refração."):
        st.caption("Dica: envolve os ângulos de incidência e de refração e os índices dos dois meios.")
        resp2 = st.text_area("A sua resposta:", key="q2_pre", height=100,
                             placeholder="n1 sen(theta1) = ...")
        if st.button("Submeter Resposta 2", type="primary"):
            modelos2 = [
                "n1 vezes seno de theta1 é igual a n2 vezes seno de theta2. Os índices de refração pelo seno dos ângulos.",
                "O produto do índice de refração pelo seno do ângulo de incidência é igual ao produto do índice de refração do segundo meio pelo seno do ângulo de refração.",
                "n1 sen theta1 n2 sen theta2. A lei relaciona os angulos de incidencia e refracao com os indices n1 e n2.",
                "n1 sin theta1 n2 sin theta2 lei snell refração angulos indices",
            ]
            kws2 = [
                ["n1", "indice 1", "indice de incidencia"],
                ["n2", "indice 2", "indice de refracao"],
                ["seno", "sen", "sin", "sin("],
                ["angulo", "ângulo", "theta"],
            ]
            score2, feedback2 = avaliar_resposta(resp2, modelos2, kws2)
            if score2 > 0.70:
                st.success(feedback2)
            elif score2 > 0.40:
                st.warning(feedback2)
            else:
                st.error(feedback2)
            st.progress(min(score2, 1.0), text=f"Pontuação: {score2*100:.0f}%")
            with st.expander("Ver resposta modelo", expanded=False):
                st.info(r"A Lei de Snell-Descartes establece que: $n_1 \sin\theta_1 = n_2 \sin\theta_2$, onde $n_1$ e $n_2$ são os índices de refração dos dois meios e $\theta_1$, $\theta_2$ os ângulos de incidência e refração, medidos em relação à normal.")

    # --- Questões Pós-Laboratoriais ---
    st.write("---")
    st.subheader("📊 II. Questões Pós-Laboratoriais")
    
    with st.expander("💫 Pergunta 3: O que acontece ao ângulo de difração se aumentarmos o comprimento de onda?"):
        st.caption("Dica: relacione $\\lambda$ com $\\sin\\theta$ através da equação da rede de difração.")
        resp3 = st.text_area("A sua resposta:", key="q3_pos", height=100,
                             placeholder="Se o comprimento de onda aumenta, o ângulo ...")
        if st.button("Submeter Resposta 3", type="primary"):
            modelos3 = [
                "Se o comprimento de onda aumenta, o ângulo de difração também aumenta. O seno do ângulo é proporcional ao lambda.",
                "Maior comprimento de onda resulta em maior desvio dos máximos. A luz vermelha difrata mais do que a azul.",
                "A equação n lambda d sin theta mostra que o angulo aumenta com o aumento do comprimento de onda.",
                "o angulo de difracao aumenta proporcional comprimento onda lambda maior seno theta",
            ]
            kws3 = [
                ["aumenta", "maior", "proporcional", "cresce"],
                ["comprimento de onda", "lambda", "λ"],
                ["angulo", "ângulo", "theta", "desvio"],
            ]
            score3, feedback3 = avaliar_resposta(resp3, modelos3, kws3)
            if score3 > 0.70:
                st.success(feedback3)
            elif score3 > 0.40:
                st.warning(feedback3)
            else:
                st.error(feedback3)
            st.progress(min(score3, 1.0), text=f"Pontuação: {score3*100:.0f}%")
            with st.expander("Ver resposta modelo", expanded=False):
                st.info(r"Da equação $n\lambda = d\sin\theta$, conclui-se que $\sin\theta$ é diretamente proporcional a $\lambda$. Logo, ao **aumentar o comprimento de onda**, **o ângulo de difração também aumenta** — por isso a luz vermelha se desvia mais do que a azul.")

    with st.expander("💫 Pergunta 4: Qual a vantagem de usar uma rede de difração com muitas fendas?"):
        st.caption("Dica: pense na precisão da medida e na nitidez dos máximos.")
        resp4 = st.text_area("A sua resposta:", key="q4_pos", height=100,
                             placeholder="Uma rede com mais fendas produz máximos...")
        if st.button("Submeter Resposta 4", type="primary"):
            modelos4 = [
                "Quanto mais fendas tiver a rede, mais nítidos e intensos são os máximos de difração. Isso permite medições mais precisas.",
                "Uma rede com muitas fendas produz picos mais estreitos e brilhantes, o que facilita a determinação da posição exata dos máximos.",
                "muitas fendas producam maximos mais nitidos estreito precisao medicao comprimento onda",
            ]
            kws4 = [
                ["nitidos", "nítidos", "nitidez", "estreitos", "definidos"],
                ["precisao", "precisão", "precisa", "exato"],
                ["intensidade", "intenso", "brilhante", "mais luz"],
            ]
            score4, feedback4 = avaliar_resposta(resp4, modelos4, kws4)
            if score4 > 0.70:
                st.success(feedback4)
            elif score4 > 0.40:
                st.warning(feedback4)
            else:
                st.error(feedback4)
            st.progress(min(score4, 1.0), text=f"Pontuação: {score4*100:.0f}%")
            with st.expander("Ver resposta modelo", expanded=False):
                st.info("Uma rede com muitas fendas produz **máximos muito mais nítidos e estreitos**, o que aumenta a **precisão** na determinação dos ângulos de difração e, consequentemente, do comprimento de onda da luz utilizada.")

