import sys

content = open('/Users/ruicampos/.gemini/antigravity/scratch/otica/ptica_lab_sim/app.py').read()
lines = content.split('\n')
out = []
in_tab2 = False
found = False

for line in lines:
    if line.startswith('with tab2:'):
        out.append(line)
        continue
    
    if line.startswith('    st.markdown(r"Equação da rede de difração:'):
        out.append('    subtab_sim, subtab_data = st.tabs(["Simulador", "Tratamento de Resultados"])')
        out.append('    with subtab_sim:')
        in_tab2 = True
        found = True
        
    if in_tab2:
        if line.strip() == '':
            out.append(line)
        else:
            out.append('    ' + line)
    else:
        out.append(line)

new_tab_content = """
    with subtab_data:
        st.subheader("Guia de Tratamento de Resultados")
        st.markdown('''
**1.** Utilizando a calculadora gráfica ou uma folha de cálculo, trace o gráfico da distância ($X$) entre o máximo central e um dos máximos de 1.ª ordem em função da distância ($D$) entre a rede de difração e o alvo.

**2.** Determine a equação da reta que melhor se ajusta ao conjunto de pontos experimentais e indique o significado físico do declive da reta obtida.

**3.** Considerando o número de linhas por milímetro indicado na rede de difração utilizada, calcule a distância entre duas linhas consecutivas ($d$), em unidades do SI.

**4.** A partir dos dados experimentais e utilizando a expressão: $n \lambda = d \sin \theta$, determine o comprimento de onda da luz do *laser* utilizado.

**5.** Determine o erro relativo, em percentagem, associado ao valor obtido para o comprimento de onda da luz do *laser*.
        ''')
"""
if found:
    out.append(new_tab_content)
    with open('/Users/ruicampos/.gemini/antigravity/scratch/otica/ptica_lab_sim/app.py', 'w') as f:
        f.write('\n'.join(out))
    print("Success!")
else:
    print("Target line not found in app.py!")
