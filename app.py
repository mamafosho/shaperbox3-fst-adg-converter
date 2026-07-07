import streamlit as st
import gzip
import os

# --- 1. 웹 UI 기본 설정 ---
st.set_page_config(page_title="FST to ADG Converter", page_icon="🎵", layout="centered")

# --- 2. 다크/라이트 모드 자동 적응 커스텀 CSS ---
st.markdown("""
    <style>
    /* --------------------------------------
       [라이트 모드 (기본)] 
    -------------------------------------- */
    /* 라이트 모드에서는 그라데이션 색상을 더 선명하고 화사하게(투명도 0.25, 0.2) 설정 */
    .stApp {
        background-color: #FFFFFF;
        background-image: 
            radial-gradient(at 10% 20%, rgba(47, 165, 114, 0.25) 0px, transparent 40%),
            radial-gradient(at 90% 80%, rgba(138, 43, 226, 0.20) 0px, transparent 40%);
        background-attachment: fixed;
    }
    
    /* 텍스트 색상 클래스 (라이트 모드용 진한 색상) */
    .desc-text { font-size: 16px; color: #555555; }
    .warn-text { font-size: 14px; color: #007BCC; line-height: 1.6; font-weight: 500; }
    .credit-text { text-align: center; font-size: 12px; color: #888888; }
    
    header { background: transparent !important; }

    /* --------------------------------------
       [다크 모드] 사용자의 기기가 다크 모드일 때 덮어씌워지는 설정 
    -------------------------------------- */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background-color: #0E1117;
            /* 다크 모드에서는 눈이 부시지 않게 차분하고 은은한 투명도(0.15, 0.12) 유지 */
            background-image: 
                radial-gradient(at 10% 20%, rgba(47, 165, 114, 0.15) 0px, transparent 40%),
                radial-gradient(at 90% 80%, rgba(138, 43, 226, 0.12) 0px, transparent 40%);
        }
        
        /* 텍스트 색상 클래스 (다크 모드용 밝은 색상) */
        .desc-text { color: #A0A0A0; }
        .warn-text { color: #5CC2F2; } /* 시안 블루 */
        .credit-text { color: #606060; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 언어 상태(세션) 초기화 ---
if 'lang' not in st.session_state:
    headers = st.context.headers
    accept_language = headers.get("Accept-Language", "en")
    
    if "ko" in accept_language.lower():
        st.session_state.lang = "KOR"
    else:
        st.session_state.lang = "ENG"

# --- 4. 우측 상단 언어 토글 버튼 배치 ---
col1, col2 = st.columns([8.5, 1.5])
with col2:
    if st.session_state.lang == "KOR":
        if st.button("🌐 ENG", use_container_width=True):
            st.session_state.lang = "ENG"
            st.rerun()
    else:
        if st.button("🌐 KOR", use_container_width=True):
            st.session_state.lang = "KOR"
            st.rerun()

# --- 5. 다국어 텍스트 데이터 사전 ---
if st.session_state.lang == "KOR":
    text = {
        "title": "ShaperBox 3 프리셋 변환기",
        "desc": "FL Studio의 .fst 프리셋을 Ableton Live의 .adg 포맷으로 변환합니다.",
        "warn": "⚠️ 주의: ShaperBox 3 하나만 단독으로 로드된 프리셋을 사용해 주세요.",
        "upload": ".fst 파일들을 선택하거나 드래그 앤 드롭하세요",
        "result": "### 변환 결과",
        "download": "⬇️ {filename} 다운로드",
        "error_no_vst": "'{filename}' 파일에서 VST 데이터를 찾을 수 없습니다.",
        "error_no_template": "서버에 template.xml 파일이 없습니다. 개발자에게 문의하세요."
    }
else:
    text = {
        "title": "ShaperBox 3 Preset Converter",
        "desc": "Convert FL Studio .fst presets to Ableton Live .adg format.",
        "warn": "⚠️ Note: Please ensure that the preset only has a single instance of ShaperBox 3 loaded.",
        "upload": "Drag and drop or select .fst files",
        "result": "### Conversion Results",
        "download": "⬇️ Download {filename}",
        "error_no_vst": "Could not find VST data in '{filename}'.",
        "error_no_template": "template.xml not found on the server. Contact the developer."
    }

# --- 6. 핵심 변환 로직 함수 ---
def process_fst_data(fst_bytes, template_xml):
    start_idx = fst_bytes.find(b'#zip#')
    if start_idx == -1:
        return None
    vst_chunk_binary = fst_bytes[start_idx:] 
    hex_string = vst_chunk_binary.hex().upper()
    formatted_hex = '\n\t\t\t\t\t\t\t'.join(
        [hex_string[i:i+300] for i in range(0, len(hex_string), 300)]
    )
    final_xml = template_xml.replace('{HEX_DATA}', formatted_hex)
    return final_xml

# --- 7. 메인 화면 렌더링 ---
st.title(text["title"])

# 설명 텍스트 (CSS 클래스 연동)
st.markdown(f"<div class='desc-text'>{text['desc']}</div>", unsafe_allow_html=True)
st.write("")

# 주의 문구 (CSS 클래스 연동)
st.markdown(f"<div class='warn-text'>{text['warn']}</div>", unsafe_allow_html=True)
st.write("")

# 템플릿 로드
template_path = 'template.xml'
try:
    with open(template_path, 'r', encoding='utf-8') as f:
        template_xml = f.read()
except FileNotFoundError:
    st.error(text["error_no_template"])
    st.stop()

# 파일 업로더
uploaded_files = st.file_uploader(text["upload"], type=['fst'], accept_multiple_files=True)

# 파일 처리 및 다운로드 버튼
if uploaded_files:
    st.write(text["result"])
    
    for uploaded_file in uploaded_files:
        fst_bytes = uploaded_file.read()
        final_xml = process_fst_data(fst_bytes, template_xml)
        
        if final_xml:
            compressed_data = gzip.compress(final_xml.encode('utf-8'))
            base_name = os.path.splitext(uploaded_file.name)[0]
            adg_filename = f"{base_name}.adg"
            
            st.download_button(
                label=text["download"].format(filename=adg_filename),
                data=compressed_data,
                file_name=adg_filename,
                mime="application/gzip"
            )
        else:
            st.warning(text["error_no_vst"].format(filename=uploaded_file.name))

# --- 8. 화면 맨 아래 서명(Credit) 추가 ---
st.markdown(
    """
    <br><br><br>
    <div class='credit-text'>
        @mamafosho
    </div>
    """, 
    unsafe_allow_html=True
)
