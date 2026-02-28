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
    
    col1, col2 = st.columns([1, 2])
    
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
        angle_i_deg = st.slider("Ângulo de incidência ($\\alpha_i$ em graus)", min_value=0.0, max_value=90.0, value=30.0, step=1.0)
        
        # Cálculos de reflexão e refração (Fresnel Equations aproximado para alpha)
        angle_i_rad = np.radians(angle_i_deg)
        angle_refletido_deg = angle_i_deg
        
        # Lei de Snell-Descartes: n1 * sin(a_i) = n2 * sin(a_R)
        sin_R = (n1 / n2) * np.sin(angle_i_rad)
        
        reflexao_total = False
        angulo_critico = None
        angle_R_deg = None
        
        # Intensidades aproximadas (Fresnel) apenas com r_s para visualização
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
                
            # Coeficientes Fresnel (aproximação s-polarized)
            num = n1 * np.cos(angle_i_rad) - n2 * np.cos(angle_R_rad)
            den = n1 * np.cos(angle_i_rad) + n2 * np.cos(angle_R_rad)
            R_intensity = abs(num / den)**2
            
            # Garantir uma visibilidade minima
            R_intensity = max(0.15, R_intensity) 
            T_intensity = 1.0 - R_intensity
                
        # Exibição de resultados na interface
        st.write("---")
        st.subheader("Medições Experimentais")
        
        # Inputs para os alunos preencherem
        col_med_1, col_med_2 = st.columns(2)
        with col_med_1:
            st.markdown("**Registo da Reflexão ($a_r$)**")
            med_refletido = st.number_input("Valor lido (graus)", min_value=0.0, max_value=90.0, value=0.0, step=0.5, key="ref_val")
            inc_refletido = st.number_input("Incerteza (± graus)", min_value=0.0, max_value=5.0, value=0.5, step=0.1, key="ref_inc")
        with col_med_2:
            st.markdown("**Registo da Refração ($a_R$)**")
            med_refratado = st.number_input("Valor lido (graus)", min_value=0.0, max_value=90.0, value=0.0, step=0.5, key="refr_val")
            inc_refratado = st.number_input("Incerteza (± graus)", min_value=0.0, max_value=5.0, value=0.5, step=0.1, key="refr_inc")
        
        verificar = st.button("Verificar Resultados Teóricos")
        
        if verificar:
            st.write("---")
            st.subheader("Resultados Teóricos e Avaliação")
            
            # Avaliação Reflexão
            st.write(f"**Ângulo de reflexão teórico:** {angle_refletido_deg:.2f}°")
            if abs(med_refletido - angle_refletido_deg) <= inc_refletido:
                st.success("✅ O valor medido para a reflexão é consistente com a lei da Reflexão!")
            else:
                st.error("❌ O valor medido para a reflexão apresenta desvios em relação à lei da Reflexão.")
            
            if reflexao_total:
                st.warning(f"⚠️ **Reflexão Total!** Não há refração para o meio 2.")
                st.write(f"**Ângulo limite (crítico) teórico:** {angulo_critico:.2f}°")
                if med_refratado > 0:
                   st.error("❌ Registou medições de refração quando este fenómeno não ocorre nestas condições.")
            else:
                # Avaliação Refração
                st.write(f"**Ângulo de refração teórico:** {angle_R_deg:.2f}°")
                if abs(med_refratado - angle_R_deg) <= inc_refratado:
                    st.success("✅ O valor medido para a refração é consistente com a lei de Snell-Descartes!")
                else:
                    st.error("❌ O valor medido para a refração apresenta desvios em relação à lei de Snell-Descartes.")
                    
                if angulo_critico:
                    st.info(f"**Ângulo limite (crítico) para a transição atual:** {angulo_critico:.2f}°")
                
    with col2:
        # Gráfico interativo
        fig, ax = plt.subplots(figsize=(6, 6))
        
        # Superfície de separação
        ax.axhline(0, color='gray', linewidth=2, linestyle='--')
        ax.axvline(0, color='black', linewidth=1, linestyle=':') # Normal
        
        ax.fill_between([-2.0, 2.0], 0, 2.0, color='lightblue', alpha=0.3, label='Meio 1 ($n_1$)')
        ax.fill_between([-2.0, 2.0], -2.0, 0, color='lightgreen', alpha=0.3, label='Meio 2 ($n_2$)')
        
        # Desenhar Transferidor (Semicírculos)
        protractor_radius = 1.2
        circle = plt.Circle((0, 0), protractor_radius, color='gray', fill=False, linestyle='--', alpha=0.5)
        ax.add_patch(circle)
        
        # Marcas do transferidor (de 10 em 10 graus)
        for angle in range(0, 360, 10):
            rad = np.radians(angle)
            x_start = protractor_radius * 0.95 * np.cos(rad)
            y_start = protractor_radius * 0.95 * np.sin(rad)
            x_end = protractor_radius * np.cos(rad)
            y_end = protractor_radius * np.sin(rad)
            ax.plot([x_start, x_end], [y_start, y_end], color='black', alpha=0.3, linewidth=1)
            
            # Textos a cada 30 graus
            if angle % 30 == 0:
                # Ajustar ângulo para mostrar em torno da normal
                display_angle = abs((angle % 180) - 90)
                if y_end >= 0:
                    ax.text(x_end * 1.08, y_end * 1.08, f"{display_angle}°", ha='center', va='center', fontsize=8, alpha=0.5)
                else:
                    ax.text(x_end * 1.08, y_end * 1.08, f"{display_angle}°", ha='center', va='center', fontsize=8, alpha=0.5)

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
        # Ilustrar graficamente no alvo
        if sin_theta <= 1:
            fig2, ax2 = plt.subplots(figsize=(8, 4))
            
            # Ponto central intenso
            ax2.plot(0, 0, 'ro', markersize=12, label="Máximo Central", alpha=0.9)
            
            # Máximos de 1.ª Ordem
            ax2.plot(dist_X_cm, 0, 'ro', markersize=8, label="Máximo 1.ª Ordem", alpha=0.7)
            ax2.plot(-dist_X_cm, 0, 'ro', markersize=8, alpha=0.7)
            
            # Máximos de 2.ª Ordem (se existir)
            sin_theta_2 = 2 * wav_m / d_m
            if sin_theta_2 <= 1:
                theta_rad_2 = np.arcsin(sin_theta_2)
                dist_X2_m = dist_D * np.tan(theta_rad_2)
                dist_X2_cm = dist_X2_m * 100
                ax2.plot(dist_X2_cm, 0, 'ro', markersize=5, label="Máximo 2.ª Ordem", alpha=0.5)
                ax2.plot(-dist_X2_cm, 0, 'ro', markersize=5, alpha=0.5)

            ax2.set_xlim(-min(30, dist_X_cm*3), min(30, dist_X_cm*3))
            ax2.set_ylim(-1, 1)
            ax2.set_xlabel("Distância X no alvo (cm)")
            ax2.set_yticks([])
            ax2.set_title("Padrão de Difração no Alvo")
            ax2.legend()
            ax2.grid(True, axis='x', linestyle='--')
            
            # Cor do laser (simplificado)
            cor_laser = '#FF0000' if wav_nm > 600 else ('#00FF00' if wav_nm > 500 else '#0000FF')
            
            # Mudar a cor dos pontos consoante o lambda aproximado
            for collection in ax2.collections:
              pass # (Isto é opcional e apenas estético)
            
            for line in ax2.lines:
                line.set_color(cor_laser)

            st.pyplot(fig2)
