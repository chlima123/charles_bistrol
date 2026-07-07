from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]
RECIFE_TZ = ZoneInfo("America/Recife")

BISTROL_OPTIONS = [
    "duro e separado",
    "alongado com caroço",
    "alongado e firme",
    "alongado e mole",
    "bola mole",
    "pedaços macios e irregulares",
    "diarreia liquida",
]


def get_sheets_service():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES,
    )
    return build("sheets", "v4", credentials=creds)


def append_row(sheet_id: str, day: str, hour: str, stool_type: int) -> None:
    service = get_sheets_service()
    body = {"values": [[day, hour, stool_type]]}
    service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range="Registros!A:C",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body=body,
    ).execute()


def main() -> None:
    st.set_page_config(page_title="Charles Diario Bistrol", page_icon="🩺", layout="centered")
    st.title("Charles Diario Bistrol")
    st.caption("Cada envio grava uma nova linha na planilha do Google Drive.")

    if "sheet_id" not in st.secrets:
        st.error("Defina `sheet_id` em `.streamlit/secrets.toml`.")
        st.stop()

    now = datetime.now(RECIFE_TZ)

    with st.form("registro_form"):
        day = st.date_input("Dia", value=now.date(), format="DD/MM/YYYY")
        hour = st.time_input("Hora", value=now.time().replace(second=0, microsecond=0))
        type_value = st.selectbox(
            "Tipo (escala Bistrol)",
            range(1, len(BISTROL_OPTIONS) + 1),
            format_func=lambda value: f"{value}. {BISTROL_OPTIONS[value - 1]}",
        )
        submitted = st.form_submit_button("Salvar registro")

    if submitted:
        day_str = day.strftime("%Y-%m-%d")
        hour_str = hour.strftime("%H:%M")

        try:
            append_row(st.secrets["sheet_id"], day_str, hour_str, type_value)
            st.success("Registro salvo com sucesso.")
        except Exception as exc:
            st.error(f"Erro ao salvar registro: {exc}")


if __name__ == "__main__":
    main()
