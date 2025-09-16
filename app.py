import streamlit as st
import deepl
import polib
import time
import tempfile
import os

st.title("Tradutor PO com DeepL")
st.info("Cada utilizador deve inserir a sua própria chave API DeepL.")

# Inputs
api_key = st.text_input("Chave API DeepL", type="password")
target_lang = st.text_input("Idioma Alvo", value="PT-PT")
uploaded_file = st.file_uploader("Carregar Ficheiro PO", type=["po"])

if st.button("Traduzir"):
    if not api_key or not uploaded_file:
        st.error("Insira a chave API e carregue um ficheiro PO.")
    else:
        with st.spinner("Processando..."):
            # Processar ficheiro
            with tempfile.NamedTemporaryFile(delete=False, suffix=".po") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name

            po = polib.pofile(tmp_path)
            translator = deepl.Translator(api_key)

            progress_bar = st.progress(0)
            status_text = st.empty()
            log_area = st.empty()

            untranslated = [e for e in po if not e.translated()]
            total = len(untranslated)
            logs = []

            for i, entry in enumerate(untranslated):
                status_text.text(f"Traduzindo entrada {i+1}/{total}")
                progress_bar.progress((i+1) / total)
                try:
                    result = translator.translate_text(entry.msgid, target_lang=target_lang)
                    entry.msgstr = result.text
                    logs.append(f"Traduzido: {entry.msgid[:50]}...")
                except deepl.exceptions.TooManyRequestsException:
                    logs.append("Erro: Rate limit atingido. Tente novamente mais tarde.")
                    break
                except Exception as e:
                    logs.append(f"Erro: {str(e)}")
                    break
                time.sleep(1)  # Delay

            po.save(tmp_path)
            log_area.text_area("Logs", "\n".join(logs), height=200)
            st.success("Tradução concluída!")

            # Download
            with open(tmp_path, "rb") as f:
                st.download_button("Descarregar Ficheiro Traduzido", f, file_name="traduzido.po")

            os.unlink(tmp_path)  # Limpar temp