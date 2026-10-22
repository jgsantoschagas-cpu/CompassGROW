import datetime
import html
import json
import os
import sqlite3
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("COMPASSGROW_DB_PATH", APP_DIR / "compassgrow.db"))

DEFAULT_STATE = {
    "diagnostico": {"Profissional": 5, "Financeiro": 5, "Saúde/Energia": 5, "Mental/Emocional": 5},
    "meta_smart": {"objetivo": "", "prazo": datetime.date.today().isoformat(), "metrica": "", "relevancia": ""},
    "plano_acao": {"rota_a": "", "rota_b": "", "micro_passo": "", "passo_concluido": False, "rota_ativa": "A"},
    "status_rota": "Ainda não avaliado",
    "historico_ajustes": [],
    "etapas_concluidas": {"diagnostico": False, "meta": False, "plano": False},
}

AREAS = ["Carreira e trabalho", "Finanças pessoais", "Saúde e energia", "Equilíbrio emocional"]

def esc(value):
    return html.escape(str(value))
AREA_KEYS = ["Profissional", "Financeiro", "Saúde/Energia", "Mental/Emocional"]
NAV = ["Início", "Realidade", "Objetivo", "Plano", "Execução", "Revisão", "Dados"]


def fresh_default():
    return json.loads(json.dumps(DEFAULT_STATE, ensure_ascii=False))


def get_password():
    password = os.environ.get("COMPASSGROW_PASSWORD", "")
    try:
        password = password or st.secrets.get("COMPASSGROW_PASSWORD", "")
    except Exception:
        pass
    return password


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS app_state (id INTEGER PRIMARY KEY CHECK (id = 1), payload TEXT NOT NULL)")
        row = conn.execute("SELECT payload FROM app_state WHERE id = 1").fetchone()
        if row is None:
            conn.execute("INSERT INTO app_state (id, payload) VALUES (1, ?)", (json.dumps(fresh_default(), ensure_ascii=False),))


def load_state():
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT payload FROM app_state WHERE id = 1").fetchone()
    if not row:
        return fresh_default()
    try:
        incoming = json.loads(row[0])
        state = fresh_default()
        state.update(incoming)
        for key in DEFAULT_STATE:
            if key not in state:
                state[key] = fresh_default()[key]
        for key, value in DEFAULT_STATE["meta_smart"].items():
            state["meta_smart"].setdefault(key, value)
        for key, value in DEFAULT_STATE["plano_acao"].items():
            state["plano_acao"].setdefault(key, value)
        return state
    except (json.JSONDecodeError, TypeError, AttributeError):
        return fresh_default()


def save_state():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO app_state (id, payload) VALUES (1, ?) ON CONFLICT(id) DO UPDATE SET payload = excluded.payload",
            (json.dumps(st.session_state.app_data, ensure_ascii=False),),
        )


def add_log(message):
    logs = st.session_state.app_data.setdefault("historico_ajustes", [])
    logs.insert(0, f"{datetime.datetime.now().strftime('%d/%m/%Y às %H:%M')} · {message}")
    del logs[100:]
    save_state()


def password_gate():
    password = get_password()
    if not password or st.session_state.get("authenticated"):
        return True
    st.markdown('<div class="login-mark">CG</div>', unsafe_allow_html=True)
    st.title("Bem-vindo ao CompassGROW")
    st.write("Seu espaço pessoal para transformar intenção em ação.")
    entered = st.text_input("Senha de acesso", type="password")
    if st.button("Entrar", type="primary", use_container_width=True):
        if entered == password:
            st.session_state.authenticated = True
            st.rerun()
        st.error("Senha incorreta.")
    return False


st.set_page_config(page_title="CompassGROW", page_icon="🧭", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { color-scheme: light; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f7f7f3; color: #202b29; }
.block-container { max-width: 790px; padding: 1.25rem 1.15rem 3rem; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
h1, h2, h3 { font-family: 'Manrope', sans-serif !important; color: #1e302c; letter-spacing: -0.045em; }
h1 { font-size: 2rem !important; font-weight: 800 !important; }
h2 { font-size: 1.45rem !important; font-weight: 750 !important; margin-top: .3rem !important; }
h3 { font-size: 1.05rem !important; font-weight: 700 !important; }
p, label, .stMarkdown { color: #465450; }
.hero { background: #203d36; color: #f8f7ef; padding: 1.35rem 1.3rem; border-radius: 22px; margin: .35rem 0 1rem; box-shadow: 0 10px 28px rgba(32,61,54,.08); }
.hero-kicker { color: #c6d9c7; font-size: .75rem; font-weight: 700; letter-spacing: .13em; text-transform: uppercase; margin-bottom: .55rem; }
.hero-title { font-family: 'Manrope', sans-serif; color: #fffdf5; font-size: 1.7rem; font-weight: 800; line-height: 1.15; letter-spacing: -.05em; }
.hero-copy { color: #d9e4da; margin-top: .65rem; font-size: .95rem; line-height: 1.5; }
.hero-progress { background: rgba(255,255,255,.14); height: 7px; border-radius: 99px; margin-top: 1.05rem; overflow: hidden; }
.hero-progress-fill { background: #c6d98f; height: 100%; border-radius: 99px; }
.eyebrow { color: #75817b; font-size: .72rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; margin: .9rem 0 .3rem; }
.card { background: #fffefa; border: 1px solid #e8e9df; border-radius: 17px; padding: 1rem 1.05rem; margin: .55rem 0; }
.card-label { color: #78837b; font-size: .78rem; font-weight: 600; }
.card-value { color: #203d36; font-family: 'Manrope',sans-serif; font-size: 1.45rem; font-weight: 800; letter-spacing: -.04em; margin-top: .15rem; }
.card-copy { color: #58645e; font-size: .9rem; line-height: 1.45; margin-top: .35rem; overflow-wrap: anywhere; }
.action-card { background: #edf1e5; border: 1px solid #dce5d2; border-radius: 18px; padding: 1.05rem; margin: .6rem 0 1rem; }
.action-label { color: #53694e; font-size: .72rem; font-weight: 800; letter-spacing: .11em; text-transform: uppercase; }
.action-text { color: #203d36; font-family: 'Manrope',sans-serif; font-size: 1.12rem; font-weight: 750; line-height: 1.4; margin-top: .35rem; }
.section-intro { color: #68736d; font-size: .94rem; line-height: 1.55; margin: -.15rem 0 1rem; }
div[data-testid="stMetric"] { background: #fffefa; border: 1px solid #e8e9df; padding: 14px 16px; border-radius: 15px; }
div[data-testid="stMetricLabel"] { color: #68736d; }
div[data-testid="stMetricValue"] { color: #203d36; font-family: 'Manrope',sans-serif; font-weight: 800; }
.stProgress > div > div { background: #567b62; }
.stProgress > div { background: #e4e8de; border-radius: 99px; }
div.stButton > button, div[data-testid="stFormSubmitButton"] button, .stDownloadButton button { border-radius: 12px; min-height: 2.9rem; font-weight: 700; border: 1px solid #d8ded5; background: #fffefa; color: #29443a; }
div.stButton > button[kind="primary"], div[data-testid="stFormSubmitButton"] button[kind="primary"] { background: #294d40; border-color: #294d40; color: white; }
div.stButton > button:hover, .stDownloadButton button:hover { border-color: #567b62; color: #203d36; }
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-testid="stDateInput"] input, [data-testid="stSelectbox"] div[data-baseweb="select"] { border-radius: 11px; }
[data-testid="stSlider"] [role="slider"] { background: #294d40; }
[data-testid="stAlert"] { border-radius: 13px; }
hr { border-color: #e3e6dc; margin: 1.4rem 0; }
.login-mark { width: 52px; height: 52px; border-radius: 17px; background: #294d40; color: #f8f7ef; display:flex; align-items:center; justify-content:center; font-family:'Manrope',sans-serif; font-weight:800; font-size:1.05rem; margin-bottom:1rem; }
.footer-note { text-align:center; color:#8a938a; font-size:.78rem; padding-top:1.2rem; }
@media (max-width: 640px) {
 .block-container { padding: .75rem .85rem 2rem; }
 h1 { font-size: 1.7rem !important; }
 h2 { font-size: 1.3rem !important; }
 .hero { padding: 1.15rem 1rem; border-radius: 19px; }
 .hero-title { font-size: 1.55rem; }
 .card { padding: .9rem; }
 div[data-testid="stMetric"] { padding: 10px 11px; }
 div[data-testid="stMetricValue"] { font-size: 1.35rem; }
}
</style>
""", unsafe_allow_html=True)

if not password_gate():
    st.stop()
if "app_data" not in st.session_state:
    st.session_state.app_data = load_state()

data = st.session_state.app_data
diagnostico = data["diagnostico"]
meta = data["meta_smart"]
plano = data["plano_acao"]

try:
    due_date = datetime.date.fromisoformat(meta.get("prazo", ""))
except (ValueError, TypeError):
    due_date = datetime.date.today()
days_left = (due_date - datetime.date.today()).days
completed = data.get("etapas_concluidas", {})
progress_items = [bool(completed.get("diagnostico")), bool(meta.get("objetivo") and meta.get("metrica") and meta.get("relevancia")), bool(plano.get("micro_passo")), bool(plano.get("passo_concluido"))]
progress = round(sum(progress_items) / len(progress_items) * 100)

# Brand header
st.markdown('<div class="eyebrow">SEU NAVEGADOR PESSOAL</div>', unsafe_allow_html=True)
st.markdown('<div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.35rem"><div style="background:#294d40;color:#f8f7ef;border-radius:12px;padding:.45rem .55rem;font-size:1.05rem">✳</div><div style="font-family:Manrope,sans-serif;font-size:1.1rem;font-weight:800;color:#203d36">CompassGROW</div></div>', unsafe_allow_html=True)
page = st.selectbox("Navegação", NAV, label_visibility="collapsed", key="current_page")

if page == "Início":
    st.markdown(f'''<div class="hero"><div class="hero-kicker">Um passo de cada vez</div><div class="hero-title">Sua vida não precisa<br>de mais complicação.</div><div class="hero-copy">Clareza sobre o que importa. Uma ação concreta para seguir em frente.</div><div class="hero-progress"><div class="hero-progress-fill" style="width:{progress}%"></div></div><div style="color:#e1eadf;font-size:.8rem;margin-top:.45rem">{progress}% do seu ciclo estruturado</div></div>''', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">SEU FOCO AGORA</div>', unsafe_allow_html=True)
    if meta.get("objetivo"):
        st.markdown(f'<div class="card"><div class="card-label">OBJETIVO ATUAL</div><div class="card-value" style="font-size:1.22rem"></div><div class="card-copy">{esc(meta["objetivo"])}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="card"><div class="card-label">OBJETIVO ATUAL</div><div class="card-value" style="font-size:1.15rem">Ainda não definido</div><div class="card-copy">Escolha algo importante para você e transforme isso em uma meta concreta.</div></div>', unsafe_allow_html=True)
    if plano.get("micro_passo"):
        st.markdown(f'<div class="action-card"><div class="action-label">PRÓXIMA AÇÃO</div><div class="action-text">{esc(plano["micro_passo"])}</div><div class="card-copy">{"✓ Ação concluída" if plano.get("passo_concluido") else "Uma ação pequena já é progresso."}</div></div>', unsafe_allow_html=True)
        if not plano.get("passo_concluido") and st.button("Marcar ação como concluída", type="primary", use_container_width=True):
            plano["passo_concluido"] = True
            add_log(f"Micro-passo concluído: {plano['micro_passo']}")
            st.rerun()
    else:
        st.markdown('<div class="action-card"><div class="action-label">PRÓXIMA AÇÃO</div><div class="action-text">Defina um próximo passo simples.</div><div class="card-copy">Algo que você consiga começar nas próximas 24 horas.</div></div>', unsafe_allow_html=True)
        if st.button("Definir meu próximo passo", type="primary", use_container_width=True):
            st.session_state.current_page = "Plano"
            st.rerun()
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="card"><div class="card-label">PRAZO DA META</div><div class="card-value">{days_left if days_left >= 0 else abs(days_left)}</div><div class="card-copy">{"dias restantes" if days_left >= 0 else "dias de atraso" if meta.get("objetivo") else "dias"}</div></div>', unsafe_allow_html=True)
    with c2:
        avg = sum(diagnostico.values()) / max(1, len(diagnostico))
        st.markdown(f'<div class="card"><div class="card-label">VISÃO DA REALIDADE</div><div class="card-value">{avg:.1f}<span style="font-size:.85rem;font-weight:500"> / 10</span></div><div class="card-copy">Média das áreas da sua vida</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">CONTINUE DE ONDE PAROU</div>', unsafe_allow_html=True)
    for label, desc in [("Realidade", "Entenda seu ponto de partida"), ("Objetivo", "Defina o que quer alcançar"), ("Plano", "Escolha o próximo passo"), ("Revisão", "Aprenda e ajuste a rota")]:
        with st.container(border=True):
            left, right = st.columns([4, 1])
            with left:
                st.markdown(f"**{label}**")
                st.caption(desc)
            with right:
                if st.button("Abrir", key=f"open_{label}", use_container_width=True):
                    st.session_state.current_page = label
                    st.rerun()

elif page == "Realidade":
    st.title("Onde você está?")
    st.markdown('<div class="section-intro">Não é uma nota sobre seu valor. É só uma fotografia honesta do momento atual.</div>', unsafe_allow_html=True)
    with st.form("diagnostico_form"):
        vals = []
        for key, label in zip(AREA_KEYS, AREAS):
            vals.append(st.slider(label, 0, 10, int(diagnostico.get(key, 5)), help="0 = muito insatisfeito; 10 = muito satisfeito"))
        if st.form_submit_button("Salvar avaliação", type="primary", use_container_width=True):
            data["diagnostico"] = dict(zip(AREA_KEYS, vals))
            data.setdefault("etapas_concluidas", {})["diagnostico"] = True
            add_log("Avaliação da realidade atualizada")
            st.success("Avaliação salva.")
            st.rerun()
    avg = sum(diagnostico.values()) / max(1, len(diagnostico))
    st.markdown('<div class="eyebrow">SUA VISÃO GERAL</div>', unsafe_allow_html=True)
    st.metric("Média atual", f"{avg:.1f} / 10")
    st.progress(avg / 10)
    lowest = min(diagnostico, key=diagnostico.get)
    st.info(f"Área com menor nota: **{dict(zip(AREA_KEYS, AREAS)).get(lowest, lowest)}** ({diagnostico[lowest]}/10). Pode ser um ponto útil para explorar — sem obrigação de escolher essa área como prioridade.")

elif page == "Objetivo":
    st.title("O que você quer mudar?")
    st.markdown('<div class="section-intro">Uma boa meta deixa claro o resultado desejado, como medir o avanço e por que isso importa.</div>', unsafe_allow_html=True)
    try:
        current_due = datetime.date.fromisoformat(meta.get("prazo", ""))
    except (ValueError, TypeError):
        current_due = datetime.date.today()
    with st.form("meta_form"):
        objetivo = st.text_area("Meu objetivo", value=meta.get("objetivo", ""), height=90, placeholder="Ex.: conseguir uma vaga melhor na minha área")
        metrica = st.text_input("Como vou saber que consegui?", value=meta.get("metrica", ""), placeholder="Ex.: receber uma proposta formal")
        prazo = st.date_input("Até quando?", value=current_due, format="DD/MM/YYYY")
        relevancia = st.text_area("Por que isso importa para mim?", value=meta.get("relevancia", ""), height=100, placeholder="O que vai melhorar na minha vida?")
        if st.form_submit_button("Salvar objetivo", type="primary", use_container_width=True):
            if not objetivo.strip() or not metrica.strip() or not relevancia.strip():
                st.error("Preencha o objetivo, como medir o sucesso e por que isso importa.")
            else:
                meta.update({"objetivo": objetivo.strip(), "metrica": metrica.strip(), "prazo": prazo.isoformat(), "relevancia": relevancia.strip()})
                add_log("Objetivo atualizado")
                st.success("Objetivo salvo.")
                st.rerun()
    if meta.get("objetivo"):
        st.markdown('<div class="eyebrow">RESUMO DO OBJETIVO</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card"><div class="card-value" style="font-size:1.15rem">{esc(meta["objetivo"])}</div><div class="card-copy"><b>Sucesso:</b> {esc(meta.get("metrica", "—"))}<br><b>Prazo:</b> {current_due.strftime("%d/%m/%Y")}<br><b>Motivo:</b> {esc(meta.get("relevancia", "—"))}</div></div>', unsafe_allow_html=True)

elif page == "Plano":
    st.title("Transforme em ação")
    st.markdown('<div class="section-intro">Você não precisa resolver tudo hoje. Defina um caminho e uma próxima ação pequena o bastante para começar.</div>', unsafe_allow_html=True)
    with st.form("plano_form"):
        rota_a = st.text_area("Caminho principal", value=plano.get("rota_a", ""), height=100, placeholder="Quais etapas me aproximam do objetivo?")
        rota_b = st.text_area("Alternativa se eu travar", value=plano.get("rota_b", ""), height=85, placeholder="Qual outro caminho posso tentar?")
        micro = st.text_area("Minha próxima ação (próximas 24 horas)", value=plano.get("micro_passo", ""), height=85, placeholder="Escreva uma ação específica e realizável")
        if st.form_submit_button("Salvar plano", type="primary", use_container_width=True):
            old_micro = plano.get("micro_passo", "")
            plano.update({"rota_a": rota_a.strip(), "rota_b": rota_b.strip(), "micro_passo": micro.strip()})
            if micro.strip() != old_micro:
                plano["passo_concluido"] = False
            data.setdefault("etapas_concluidas", {})["plano"] = bool(micro.strip())
            add_log("Plano de ação atualizado")
            st.success("Plano salvo.")
            st.rerun()
    if plano.get("micro_passo"):
        st.markdown('<div class="eyebrow">PRÓXIMA AÇÃO</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="action-card"><div class="action-text">{esc(plano["micro_passo"])}</div><div class="card-copy">Status: {"concluída" if plano.get("passo_concluido") else "pendente"}</div></div>', unsafe_allow_html=True)

elif page == "Execução":
    st.title("Um passo de cada vez")
    st.markdown('<div class="section-intro">O progresso acontece quando o plano encontra a vida real. Registre o que conseguiu fazer e siga sem buscar perfeição.</div>', unsafe_allow_html=True)
    if plano.get("micro_passo"):
        st.markdown(f'<div class="action-card"><div class="action-label">AÇÃO ATUAL</div><div class="action-text">{esc(plano["micro_passo"])}</div></div>', unsafe_allow_html=True)
        with st.form("acao_form"):
            concluiu = st.checkbox("Consegui concluir esta ação", value=bool(plano.get("passo_concluido")))
            if st.form_submit_button("Salvar andamento", type="primary", use_container_width=True):
                was_done = bool(plano.get("passo_concluido"))
                plano["passo_concluido"] = concluiu
                if concluiu and not was_done:
                    add_log(f"Ação concluída: {plano['micro_passo']}")
                else:
                    save_state()
                st.success("Andamento salvo.")
                st.rerun()
    else:
        st.warning("Você ainda não definiu uma próxima ação.")
        if st.button("Criar meu plano", type="primary", use_container_width=True):
            st.session_state.current_page = "Plano"
            st.rerun()
    st.divider()
    st.subheader("Situação atual")
    statuses = ["Ainda não avaliado", "Em andamento", "Atrasado ou fora da rota", "Bloqueado por um obstáculo"]
    current_status = data.get("status_rota", statuses[0])
    if current_status not in statuses:
        current_status = statuses[0]
    status = st.selectbox("Como está o andamento?", statuses, index=statuses.index(current_status))
    if status == "Em andamento":
        st.success("Continue com o próximo passo possível.")
    elif status == "Atrasado ou fora da rota":
        st.warning("Reduza o tamanho da ação ou reveja o prazo. Ajustar o plano faz parte do processo.")
    elif status == "Bloqueado por um obstáculo":
        st.info(f"Considere a alternativa: {plano['rota_b']}" if plano.get("rota_b") else "Registre uma alternativa na área Plano.")
    if st.button("Salvar situação", type="primary", use_container_width=True):
        data["status_rota"] = status
        add_log(f"Situação atualizada: {status}")
        st.success("Situação salva.")
        st.rerun()

elif page == "Revisão":
    st.title("Olhar, aprender, ajustar")
    st.markdown('<div class="section-intro">Uma revisão não serve para se julgar. Serve para entender o que funcionou e escolher o próximo movimento.</div>', unsafe_allow_html=True)
    with st.form("revisao_form"):
        funcionou = st.text_area("O que funcionou?", height=85, placeholder="Que ação, escolha ou condição ajudou?")
        obstaculo = st.text_area("O que dificultou?", height=85, placeholder="O que atrapalhou ou ficou fora do seu controle?")
        ajuste = st.text_area("O que vou mudar na próxima semana?", height=85, placeholder="Qual ajuste concreto vou experimentar?")
        if st.form_submit_button("Registrar revisão", type="primary", use_container_width=True):
            if not any([funcionou.strip(), obstaculo.strip(), ajuste.strip()]):
                st.error("Escreva pelo menos uma observação antes de salvar.")
            else:
                note = "Revisão semanal — " + " | ".join(x for x in [f"Funcionou: {funcionou.strip()}" if funcionou.strip() else "", f"Dificuldade: {obstaculo.strip()}" if obstaculo.strip() else "", f"Ajuste: {ajuste.strip()}" if ajuste.strip() else ""] if x)
                add_log(note)
                st.success("Revisão registrada.")
                st.rerun()
    st.markdown('<div class="eyebrow">HISTÓRICO RECENTE</div>', unsafe_allow_html=True)
    logs = data.get("historico_ajustes", [])
    if logs:
        for item in logs[:15]:
            with st.container(border=True):
                st.caption(item)
    else:
        st.caption("Suas revisões e ajustes aparecerão aqui.")

elif page == "Dados":
    st.title("Seus dados")
    st.markdown('<div class="section-intro">Você pode exportar seus dados para guardar uma cópia ou restaurar um backup anterior.</div>', unsafe_allow_html=True)
    export_payload = json.dumps(data, ensure_ascii=False, indent=2)
    st.download_button("Exportar backup (JSON)", data=export_payload, file_name=f"compassgrow-backup-{datetime.date.today().isoformat()}.json", mime="application/json", use_container_width=True)
    uploaded = st.file_uploader("Escolher um backup para restaurar", type=["json"])
    if uploaded is not None and st.button("Restaurar backup", type="primary", use_container_width=True):
        try:
            incoming = json.load(uploaded)
            required = {"diagnostico", "meta_smart", "plano_acao", "historico_ajustes"}
            if not required.issubset(incoming):
                raise ValueError("Este arquivo não parece ser um backup do CompassGROW.")
            restored = fresh_default()
            restored.update(incoming)
            st.session_state.app_data = restored
            save_state()
            st.success("Backup restaurado.")
            st.rerun()
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            st.error(f"Não foi possível restaurar: {exc}")
    st.divider()
    st.markdown("**Importante sobre armazenamento**")
    st.warning("Em hospedagens gratuitas, o arquivo local do banco pode ser apagado ou não persistir em reinicializações. Exporte backups regularmente e não confie no app como única cópia de informações importantes.")

st.markdown('<div class="footer-note">CompassGROW · Menos ruído. Mais clareza. Um passo de cada vez.</div>', unsafe_allow_html=True)
