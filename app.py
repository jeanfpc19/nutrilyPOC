import streamlit as st
import google.generativeai as genai

# 1. Configuración de la API
# Streamlit Cloud leerá la llave desde los "Secrets" en el panel de control
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la GOOGLE_API_KEY en la configuración de Secrets.")

st.title("Asistente de Nutrición con IA")

# Inicializar el estado de la sesión para guardar el plan de dieta
if "plan_dieta" not in st.session_state:
    st.session_state["plan_dieta"] = ""

# 2. Barra lateral para navegación
rol = st.sidebar.radio("Selecciona tu rol:", ["Nutricionista", "Paciente"])

# --- VISTA DEL NUTRICIONISTA ---
if rol == "Nutricionista":
    st.header("Cargar Plan del Paciente")
    entrada_dieta = st.text_area("Pega el plan de alimentación, restricciones y macros aquí:")
    
    if st.button("Guardar Plan"):
        st.session_state["plan_dieta"] = entrada_dieta
        st.success("¡Plan cargado exitosamente! Cambia a la vista de 'Paciente' para probar.")

# --- VISTA DEL PACIENTE ---
elif rol == "Paciente":
    st.header("Chatea con tu Asistente")
    
    # Verificar si existe un plan
    if not st.session_state["plan_dieta"]:
        st.warning("No se encontró ningún plan de alimentación. El nutricionista debe cargar los datos primero.")
    else:
        pregunta_usuario = st.text_input("Haz una pregunta sobre tu dieta:")
        
        if pregunta_usuario:
            # 3. La lógica RAG en Español
            prompt = f"""
            Eres un asistente de nutrición estricto y útil.
            Aquí está el perfil específico y las restricciones del paciente:
            {st.session_state['plan_dieta']}
            
            Pregunta del Paciente: {pregunta_usuario}
            
            Responde la pregunta en español, de forma clara y estrictamente basada en el perfil anterior. 
            Si el alimento no está permitido o contradice el plan, di que no.
            """
            
            # 4. Secuencia de Failover (Cascada de Modelos)
            modelos_disponibles = ['gemini-3-flash', 'gemini-2.5-flash', 'gemini-2.5-flash-lite']
            respuesta_generada = None
            
            with st.spinner("Consultando al asistente..."):
                for nombre_modelo in modelos_disponibles:
                    try:
                        modelo = genai.GenerativeModel(nombre_modelo)
                        respuesta = modelo.generate_content(prompt)
                        respuesta_generada = respuesta.text
                        
                        # Opcional: Mostrar qué modelo respondió para propósitos de depuración en el PoC
                        st.caption(f"*(Respondido usando: {nombre_modelo})*")
                        break # Si tiene éxito, rompemos el bucle y dejamos de intentar
                        
                    except Exception as e:
                        # Si el error es por límite de cuota (ResourceExhausted) o cualquier otro fallo,
                        # el bucle continúa con el siguiente modelo en la lista.
                        print(f"Fallo con {nombre_modelo}: {e}")
                        continue
            
            # 5. Mostrar el resultado
            if respuesta_generada:
                st.write(respuesta_generada)
            else:
                st.error("Todos los modelos están actualmente saturados por los límites de la capa gratuita. Por favor, espera un minuto e intenta de nuevo.")
