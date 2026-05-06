import streamlit as st


PRIORIDADES = ["baixa", "média", "alta", "crítica"]
ORIGENS = ["frontend", "backend", "infra", "banco", "outro"]


def render(report: dict) -> dict:
    """Exibe o relatório estruturado em campos editáveis. Retorna o dict atualizado."""
    st.subheader("Relato Estruturado")

    col1, col2 = st.columns(2)
    with col1:
        prioridade = st.selectbox(
            "Prioridade",
            PRIORIDADES,
            index=PRIORIDADES.index(report.get("prioridade", "média")),
        )
    with col2:
        origem = st.selectbox(
            "Origem",
            ORIGENS,
            index=ORIGENS.index(report.get("origem", "outro")),
        )

    relato = st.text_area("Relato", value=report.get("relato", ""), height=150)
    url = st.text_input("URL afetada", value=report.get("url") or "")

    return {
        **report,
        "prioridade": prioridade,
        "origem": origem,
        "relato": relato,
        "url": url or None,
    }
