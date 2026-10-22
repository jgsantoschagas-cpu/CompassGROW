import datetime
import json
import os
import sqlite3
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("COMPASSGROW_DB_PATH", APP_DIR / "compassgrow.db"))

DEFAULT_STATE = {
    "diagnostico": {
        "Profissional": 5,
        "Financeiro": 5,
        "Saúde/Energia": 5,
        "Mental/Emocional": 5,
    },
    "meta_smart": {
        "objetivo": "",
        "prazo": datetime.date.today().isoformat(),
        "metrica": "",
        "relevancia": "",
    },
    "plano_acao": {
        "rota_a": "",
        "rota_b": "",
        "micro_passo": "",
        "passo_concluido": False,
        "rota_ativa": "A",
    },
    "status_rota": "Selecione o status atual...",
    "historico_ajustes": [],
    "etapas_concluidas": {
        "diagnostico": False,
        "meta": False,
        "plano": False,
    },
}


def get_password():
    """Optional password: COMPASSGROW_PASSWORD environment variable or Streamlit secret."""
    password = os.environ.get("COMPASSGROW_PASSWORD", "")
    try:
        password = password or st.secrets.get("COMPASSGROW_PASSWORD", "")
    except Exception:
        pass
    return password


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS app_state (id INTEGER PRIMARY KEY CHECK (id = 1), payload TEXT NOT NULL)"
        )
        row = conn.execute("SELECT payload FROM app_state WHERE id = 1").fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO app_state (id, payload) VALUES (1, ?)",
                (json.dumps(DEFAULT_STATE, ensure_ascii=False),),
            )


def load_state():
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT payload FROM app_state WHERE id = 1").fetchone()
    if not row:
        return json.loads(json.dumps(DEFAULT_STATE))
    try:
        loaded = json.loads(row[0])
        state = json.loads(json.dumps(DEFAULT_STATE))
        for key, value in loaded.items():
            state[key] = value
        return state
    except (json.JSONDecodeError, TypeError):
        return json.loads(json.dumps(DEFAULT_STATE))


def save_state():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO app_state (id, payload) VALUES (1, ?) "
            "ON CONFLICT(id) DO UPDATE SET payload = excluded.payload",
            (json.dumps(st.session_state.app_data, ensure_ascii=False),),
        )


def add_log(message):
    st.session_state.app_data["historico_ajustes"].insert(
        0, f"{datetime.datetime.now().strftime('%d/%m/%Y %H:%M')} — {message}"
    )
    save_state()


def password_gate():
    password = get_password()
    if not password:
        return True
    if st.session_state.get("authenticated"):
        return True
    st.title("🧭 CompassGROW")
    st.caption("Acesso pessoal protegido")
    entered = st.text_input("Senha de acesso", type="password")
    if st.button("Entrar", type="primary", use_container_width=True):
        if entered == password:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Senha incorreta.")
    st.info("A senha é configurada pelo responsável pela implantação.")
    return False


st.set_page_config(
    page_title="CompassGROW — Navegador Pessoal",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <meta name="theme-color" content="#172554">
    <style>
      :root { color-scheme: light; }
      .stApp { background: #f5f7fb; }
      .block-container { max-width: 980px; padding-top: 1.2rem; padding-bottom: 3rem; }
      h1, h2, h3 { letter-spacing: -0.025em; }
      div[data-testid="stMetric"] {
        background: white; border: 1px solid #e2e8f0; padding: 14px 16px;
        border-radius: 14px;
      }
      .stTabs [data-baseweb="tab-list"] { gap: 5px; flex-wrap: wrap; }
      .stTabs [data-baseweb="tab"] {
        background: white; border: 1px solid #e2e8f0; border-radius: 10px;
        padding: 9px 12px; white-space: normal;
      }
      .stTabs [aria-selected="true"] { background: #1d4ed8 !important; color: white !important; }
      div.stButton > button, div[data-testid="stFormSubmitButton"] button {
        border-radius: 10px; min-height: 2.7rem; font-weight: 600;
      }
      div.stButton > button[kind="primary"], div[data-testid="stFormSubmitButton"] button[kind="primary"] {
        background: #1d4ed8; border-color: #1d4ed8;
      }
      [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
        border-radius: 9px;
      }
      .small-note { color: #64748b; font-size: .88rem; }
      @media (max-width: 640px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; }
        h1 { font-size: 1.75rem !important; }
        h2 { font-size: 1.35rem !important; }
        .stTabs [data-baseweb="tab"] { padding: 8px 9px; font-size: .82rem; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

if not password_gate():
    st.stop()

if "app_data" not in st.session_state:
    st.session_state.app_data = load_state()

data = st.session_state.app_data
diagnostico = data["diagnostico"]
meta = data["meta_smart"]
plano = data["plano_acao"]

st.title("🧭 CompassGROW")
st.write("Transforme intenções em objetivos claros, próximos passos e revisões práticas.")
st.caption("Seu espaço pessoal de planejamento — simples, privado e focado em ação.")

completed = data.get("etapas_concluidas", {})
progress_items = [
    bool(completed.get("diagnostico")),
    bool(meta.get("objetivo") and meta.get("metrica") and meta.get("relevancia")),
    bool(plano.get("micro_passo")),
    bool(plano.get("passo_concluido")),
]
progress = round(sum(progress_items) / len(progress_items) * 100)
m1, m2 = st.columns(2)
with m1:
    st.metric("Preparação e execução", f"{progress}%")
with m2:
    due_date = datetime.date.fromisoformat(meta["prazo"])
    days_left = (due_date - datetime.date.today()).days
    if meta["objetivo"]:
        label = "prazo vencido" if days_left < 0 else "dias até o prazo"
        value = f"{abs(days_left)}" if days_left < 0 else str(days_left)
    else:
        label, value = "prazo", "Ainda não definido"
    st.metric(label, value)
st.progress(progress / 100)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📍 Realidade", "🎯 Meta", "🗺️ Plano", "⚡ Executar", "💾 Dados"]
)

with tab1:
    st.header("Onde estou?")
    st.write("Avalie cada área de 0 a 10, considerando como você está hoje.")
    with st.form("diagnostico_form"):
        c1, c2 = st.columns(2)
        with c1:
            profissional = st.slider("Carreira e trabalho", 0, 10, int(diagnostico["Profissional"]))
            financeiro = st.slider("Finanças pessoais", 0, 10, int(diagnostico["Financeiro"]))
        with c2:
            saude = st.slider("Saúde e energia", 0, 10, int(diagnostico["Saúde/Energia"]))
            mental = st.slider("Equilíbrio mental e emocional", 0, 10, int(diagnostico["Mental/Emocional"]))
        saved_diagnosis = st.form_submit_button("Salvar avaliação", type="primary", use_container_width=True)
    if saved_diagnosis:
        data["diagnostico"] = {
            "Profissional": profissional,
            "Financeiro": financeiro,
            "Saúde/Energia": saude,
            "Mental/Emocional": mental,
        }
        data["etapas_concluidas"]["diagnostico"] = True
        save_state()
        st.success("Avaliação salva.")
        st.rerun()

    average = sum(data["diagnostico"].values()) / len(data["diagnostico"])
    st.divider()
    st.metric("Média atual", f"{average:.1f}/10")
    if average < 5:
        st.warning("Ponto de partida: priorize estabilidade e fortalecimento da base.")
    elif average < 8:
        st.info("Você tem uma base razoável para escolher uma área e avançar.")
    else:
        st.success("Avaliação alta. Escolha desafios mantendo o equilíbrio.")

with tab2:
    st.header("Onde quero chegar?")
    st.write("Defina uma meta clara, uma forma de medir o resultado e um motivo relevante.")
    with st.form("meta_form"):
        objetivo = st.text_input("O que exatamente quero alcançar?", value=meta["objetivo"])
        metrica = st.text_input("Como vou medir o sucesso?", value=meta["metrica"])
        try:
            prazo_atual = datetime.date.fromisoformat(meta["prazo"])
        except (ValueError, TypeError):
            prazo_atual = datetime.date.today()
        prazo = st.date_input("Prazo desejado", value=prazo_atual, format="DD/MM/YYYY")
        relevancia = st.text_area("Por que isso importa agora?", value=meta["relevancia"], height=110)
        saved_goal = st.form_submit_button("Salvar meta", type="primary", use_container_width=True)
    if saved_goal:
        if objetivo.strip() and metrica.strip() and relevancia.strip():
            meta.update({
                "objetivo": objetivo.strip(),
                "metrica": metrica.strip(),
                "prazo": prazo.isoformat(),
                "relevancia": relevancia.strip(),
            })
            save_state()
            st.success("Meta salva. Revise-a sempre que as circunstâncias mudarem.")
            st.rerun()
        else:
            st.error("Preencha o objetivo, a métrica e a relevância antes de salvar.")
    if meta["objetivo"]:
        st.info(f"**Meta atual:** {meta['objetivo']}\n\n**Métrica:** {meta['metrica']}\n\n**Prazo:** {prazo_atual.strftime('%d/%m/%Y')}")

with tab3:
    st.header("Como chego lá?")
    st.write("Pense em um caminho principal, uma alternativa e uma ação pequena para começar.")
    with st.form("plano_form"):
        rota_a = st.text_area("Rota principal", value=plano["rota_a"], height=85, placeholder="Qual é o caminho mais provável?")
        rota_b = st.text_area("Plano alternativo", value=plano["rota_b"], height=85, placeholder="O que posso fazer se o caminho principal travar?")
        micro = st.text_input("Próximo passo concreto para as próximas 24 horas", value=plano["micro_passo"])
        saved_plan = st.form_submit_button("Salvar plano", type="primary", use_container_width=True)
    if saved_plan:
        plano["rota_a"] = rota_a.strip()
        plano["rota_b"] = rota_b.strip()
        plano["micro_passo"] = micro.strip()
        plano["passo_concluido"] = False if micro.strip() != data.get("_last_micro_step", micro.strip()) else plano["passo_concluido"]
        data["_last_micro_step"] = micro.strip()
        save_state()
        st.success("Plano salvo.")
        st.rerun()
    if plano["rota_ativa"] == "B" and plano["rota_b"]:
        st.warning(f"Rota ativa: plano alternativo — {plano['rota_b']}")
    elif plano["rota_a"]:
        st.info(f"Rota ativa: principal — {plano['rota_a']}")

with tab4:
    st.header("Agir e ajustar")
    st.subheader("Próxima ação")
    if plano["micro_passo"]:
        st.write(f"**{plano['micro_passo']}**")
        with st.form("acao_form"):
            concluiu = st.checkbox("Marcar esta ação como concluída", value=bool(plano["passo_concluido"]))
            salvar_conclusao = st.form_submit_button("Salvar andamento", type="primary", use_container_width=True)
        if salvar_conclusao:
            was_done = plano["passo_concluido"]
            plano["passo_concluido"] = concluiu
            if concluiu and not was_done:
                add_log(f"Micro-passo concluído: {plano['micro_passo']}")
            else:
                save_state()
            st.success("Andamento salvo.")
            st.rerun()
        if plano["passo_concluido"]:
            st.success("Boa. A ação foi marcada como concluída.")
    else:
        st.warning("Defina primeiro um micro-passo na aba Plano.")

    st.divider()
    st.subheader("Como está a rota?")
    statuses = [
        "Selecione o status atual...",
        "Em rota e dentro do prazo esperado",
        "Atrasado / desviado da rota",
        "Bloqueado por obstáculos imprevisíveis",
    ]
    current_status = data.get("status_rota", statuses[0])
    if current_status not in statuses:
        current_status = statuses[0]
    status = st.selectbox("Status atual", statuses, index=statuses.index(current_status))
    if status == "Em rota e dentro do prazo esperado":
        st.success("Continue com o plano e acompanhe os resultados.")
    elif status == "Atrasado / desviado da rota":
        st.warning("Reduza o tamanho do próximo passo. Escolha uma ação menor e revise o prazo se necessário.")
    elif status == "Bloqueado por obstáculos imprevisíveis":
        if plano["rota_b"]:
            st.error(f"Considere ativar o plano alternativo: {plano['rota_b']}")
        else:
            st.warning("Você ainda não definiu um plano alternativo.")
    if st.button("Salvar status da rota", use_container_width=True):
        data["status_rota"] = status
        save_state()
        add_log(f"Status da rota atualizado: {status}")
        st.success("Status salvo.")
        st.rerun()

    st.divider()
    st.subheader("Histórico de ajustes")
    if data["historico_ajustes"]:
        for item in data["historico_ajustes"]:
            st.caption(f"• {item}")
    else:
        st.caption("Seus ajustes registrados aparecerão aqui.")

with tab5:
    st.header("Seus dados")
    st.write("Exporte uma cópia de segurança ou restaure um arquivo JSON exportado anteriormente.")
    export_payload = json.dumps(data, ensure_ascii=False, indent=2)
    st.download_button(
        "⬇️ Exportar meus dados (JSON)",
        data=export_payload,
        file_name=f"compassgrow-backup-{datetime.date.today().isoformat()}.json",
        mime="application/json",
        use_container_width=True,
    )
    uploaded = st.file_uploader("Restaurar dados de um backup JSON", type=["json"])
    if uploaded is not None:
        if st.button("Restaurar backup", type="primary", use_container_width=True):
            try:
                incoming = json.load(uploaded)
                required = {"diagnostico", "meta_smart", "plano_acao", "historico_ajustes"}
                if not required.issubset(incoming):
                    raise ValueError("O arquivo não parece ser um backup válido do CompassGROW.")
                st.session_state.app_data = incoming
                save_state()
                st.success("Backup restaurado.")
                st.rerun()
            except (json.JSONDecodeError, ValueError, TypeError) as exc:
                st.error(f"Não foi possível restaurar: {exc}")
    st.divider()
    st.caption("O banco local fica em compassgrow.db. Faça backups regularmente.")
    st.warning(
        "Se você hospedar este app em um serviço de nuvem, confirme que o armazenamento é persistente. "
        "O disco local de algumas hospedagens pode ser temporário; exporte backups e configure um banco persistente antes de confiar nele para guardar dados importantes."
    )

st.divider()
st.caption("CompassGROW • Planejamento pessoal baseado em GROW e melhoria contínua.")
