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
        n1 = st.slider("Índice de refração do Meio 1 ($n_1$)", min_value=1.0, max_value=2.5, value=1.0, step=0.01, help="Ex: Ar ≈ 1.0, Água ≈ 1.33")
        n2 = st.slider("Índice de refração do Meio 2 ($n_2$)", min_value=1.0, max_value=2.5, value=1.5, step=0.01, help="Ex: Vidro ≈ 1.5")
        angle_i_deg = st.slider("Ângulo de incidência ($\\alpha_i$ em graus)", min_value=0.0, max_value=90.0, value=30.0, step=1.0)
        
        # Cálculos de reflexão e refração
        angle_i_rad = np.radians(angle_i_deg)
        angle_refletido_deg = angle_i_deg
        
        # Lei de Snell-Descartes: n1 * sin(a_i) = n2 * sin(a_R)
        sin_R = (n1 / n2) * np.sin(angle_i_rad)
        
        reflexao_total = False
        angulo_critico = None
        angle_R_deg = None
        
        if sin_R > 1:
            reflexao_total = True
            angulo_critico = np.degrees(np.arcsin(n2 / n1))
        else:
            angle_R_deg = np.degrees(np.arcsin(sin_R))
            if n1 > n2:
                angulo_critico = np.degrees(np.arcsin(n2 / n1))
                
        # Exibição de resultados na interface
        st.write("---")
        st.subheader("Resultados")
        st.write(f"**Ângulo de reflexão ($\\alpha_r$):** {angle_refletido_deg:.2f}°")
        
        if reflexao_total:
            st.error(f"⚠️ **Reflexão Total!** Não há refração para o meio 2.")
            st.write(f"**Ângulo limite (crítico):** {angulo_critico:.2f}°")
        else:
            st.success(f"**Ângulo de refração ($\\alpha_R$):** {angle_R_deg:.2f}°")
            if angulo_critico:
                st.info(f"**Ângulo limite (crítico) para a transição atual:** {angulo_critico:.2f}°")
                
    with col2:
        # Gráfico interativo
        fig, ax = plt.subplots(figsize=(6, 6))
        
        # Superfície de separação
        ax.axhline(0, color='gray', linewidth=2, linestyle='--')
        ax.axvline(0, color='black', linewidth=1, linestyle=':') # Normal
        
        ax.fill_between([-1, 1], 0, 1, color='lightblue', alpha=0.3, label='Meio 1 ($n_1$)')
        ax.fill_between([-1, 1], -1, 0, color='lightgreen', alpha=0.3, label='Meio 2 ($n_2$)')
        
        # Traçar raios
        # Raio Incidente
        x_inc = -np.sin(angle_i_rad)
        y_inc = np.cos(angle_i_rad)
        ax.plot([x_inc, 0], [y_inc, 0], 'r-', linewidth=2, label='Raio Incidente')
        # Seta do raio incidente
        ax.arrow(x_inc/2, y_inc/2, x_inc/20, -y_inc/20, head_width=0.05, head_length=0.1, fc='r', ec='r')

        # Raio Refletido
        x_refl = np.sin(angle_i_rad)
        y_refl = np.cos(angle_i_rad)
        ax.plot([0, x_refl], [0, y_refl], 'b-', linewidth=2, label='Raio Refletido')
        ax.arrow(0, 0, x_refl/2, y_refl/2, head_width=0.05, head_length=0.1, fc='b', ec='b')

        # Raio Refratado
        if not reflexao_total:
            angle_R_rad = np.radians(angle_R_deg)
            x_refr = np.sin(angle_R_rad)
            y_refr = -np.cos(angle_R_rad)
            ax.plot([0, x_refr], [0, y_refr], 'g-', linewidth=2, label='Raio Refratado')
            ax.arrow(0, 0, x_refr/2, y_refr/2, head_width=0.05, head_length=0.1, fc='g', ec='g')
            
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
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
