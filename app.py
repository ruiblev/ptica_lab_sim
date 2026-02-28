import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulador Ótica AL", layout="wide")

st.title("Simulador: Fenómenos Óticos (AL 11.º Ano)")
st.markdown("""
Este simulador permite investigar experimentalmente os fenómenos de **reflexão, refração, reflexão total** e **difração da luz**, de acordo com as Aprendizagens Essenciais de Física e Química A (11.º Ano).
""")

# Abas para separar as duas partes da AL
tab1, tab2 = st.tabs(["Parte I: Reflexão, Refração e Reflexão Total da Luz", "Parte II: Difração da Luz"])

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
    
    col3, col4 = st.columns([1, 2])
    
    with col3:
        st.subheader("Parâmetros do Laser e Rede")
        wav_nm = st.slider("Comprimento de onda do Laser ($\\lambda$ em nm)", min_value=380, max_value=750, value=633, step=1)
        wav_m = wav_nm * 1e-9  # metros
        
        linhas_mm = st.slider("Constante da rede (linhas / mm)", min_value=10, max_value=600, value=300, step=10)
        d_m = 1 / (linhas_mm * 1000) # metros (distância d entre fendas)
        
        dist_D = st.slider("Distância ao Alvo ($D$ em metros)", min_value=0.1, max_value=3.0, value=1.0, step=0.1)
        
        # Cálculos de Difração - Máximos na Rede
        st.write("---")
        st.subheader("Tratamento de Resultados")
        
        st.write(f"**Distância entre fendas ($d$):** {d_m * 1e6:.2f} $\\mu$m")
        
        # Determinar posição X do máximo de 1.ª ordem (n=1)
        sin_theta = wav_m / d_m
        if sin_theta > 1:
            st.error("Não se formam máximos de 1.ª ordem para esta configuração.")
        else:
            theta_rad = np.arcsin(sin_theta)
            dist_X_m = dist_D * np.tan(theta_rad)
            dist_X_cm = dist_X_m * 100
            
            st.success(f"**Ângulo $\\theta$ (1.ª ordem):** {np.degrees(theta_rad):.2f}°")
            st.success(f"**Distância $X$ ao máximo central:** {dist_X_cm:.2f} cm")
            
    with col4:
        # 1. VISUALIZAÇÃO MACROSCÓPICA DA MONTAGEM (NOVO)
        if sin_theta <= 1:
            st.subheader("Visualização da Montagem")
            fig_setup, ax_setup = plt.subplots(figsize=(8, 2.5))
            
            # Correntes aproximadas para o feixe laser
            if wav_nm > 600:
                cor_laser = '#FF0000' # Vermelhos
            elif wav_nm > 500:
                cor_laser = '#00FF00' # Verdes
            elif wav_nm > 450:
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
            ax_setup.fill_between([laser_width, fenda_x], -0.1, 0.1, color=cor_laser, alpha=0.6)
            
            # Alvo / Ecrã móvel
            # Simular o ecrã a afastar-se usando dist_D para escalar a posição visual
            min_D, max_D = 0.1, 3.0
            # Mapear D real para posição gráfica (ex: 3.5 a 7.5 max)
            alvo_x = 3.5 + ((dist_D - min_D) / (max_D - min_D)) * 4.0 
            
            ax_setup.plot([alvo_x, alvo_x], [-1.2, 1.2], color='darkslategray', linewidth=6)
            ax_setup.text(alvo_x + 0.2, 1.0, f'D = {dist_D} m', ha='left', va='center', fontsize=9)
            
            # Cone de Difração (espalhamento) da Fenda para o Ecrã
            # A base do cone cresce com D e com Theta
            cone_y_max = alvo_x * np.tan(theta_rad) # Abertura visual baseada no ângulo principal
            # Limitar visualmente a abertura extrema para o gráfico não quebrar
            cone_y_max = min(1.2, max(0.2, cone_y_max)) * 1.5 
            
            ax_setup.fill_between([fenda_x, alvo_x], 
                                  [-0.1, -cone_y_max], 
                                  [0.1, cone_y_max], 
                                  color=cor_laser, alpha=0.2)
            
            # Eixo Principal
            ax_setup.plot([0, alvo_x+1], [0, 0], color='black', linestyle='--', linewidth=0.5, alpha=0.5)

            ax_setup.set_xlim(-0.5, 8.5)
            ax_setup.set_ylim(-1.5, 1.5)
            ax_setup.axis('off')
            st.pyplot(fig_setup)

        # 2. ILUSTRAÇÃO DOS MÁXIMOS NO ALVO (ANTERIOR)
        st.write("---")
        st.subheader("Padrão de Intensidade no Alvo")
        if sin_theta <= 1:
            fig2, ax2 = plt.subplots(figsize=(8, 4))
            
            # Mudar a cor dos pontos consoante o lambda aproximado
            for collection in ax2.collections:
              pass # (Isto é opcional e apenas estético)
            
            for line in ax2.lines:
                line.set_color(cor_laser)

            st.pyplot(fig2)
