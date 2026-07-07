import streamlit as st
import gzip
import os

# --- 웹 UI 기본 설정 ---
st.set_page_config(page_title="FST to ADG Converter", page_icon="🎵", layout="centered")

# 1. 언어 상태(세션) 초기화
if 'lang' not in st.session_state:
    headers = st.context.headers
    accept_language = headers.get("Accept-Language", "en")
    
    if "ko" in accept_language.lower():
        st.session_state.lang = "KOR"
    else:
        st.session_state.lang = "ENG"

# 2. 토글 버튼 우측 끝 밀착 배치 
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

# 3. 선택된 언어에 따라 텍스트 분기 처리
if st.session_state.lang == "KOR":
    text = {
        "title": "ShaperBox 3 프리셋 변환기",
        "desc": "FL Studio의 .fst 프리셋을 Ableton Live의 .adg 포맷으로 변환합니다.",
        "warn": "ShaperBox 3 단일 플러그인만 로드된 프리셋을 사용해 주세요.",
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
        "warn": "Please use a preset loaded with only a single ShaperBox 3 plugin.",
        "upload": "Drag and drop or select .fst files",
        "result": "### Conversion Results",
        "download": "⬇️ Download {filename}",
        "error_no_vst": "Could not find VST data in '{filename}'.",
        "error_no_template": "template.xml not found on the server. Contact the developer."
    }

# --- 변환 로직 ---
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

# --- 메인 화면 렌더링 ---
st.title(text["title"])

# 안내 문구 (깔끔한 회색톤)
st.markdown(f"<span style='font-size: 16px; color: #A0A0A0;'>{text['desc']}</span>", unsafe_allow_html=True)

# 주의 문구 (배경 박스 없이 빨간색 텍스트만 렌더링)
st.markdown(f"<span style='font-size: 14px; color: #FF4B4B;'>{text['warn']}</span>", unsafe_allow_html=True)

st.write("") # 간격 확보

# 템플릿 로드
template_path = 'template.xml'
try:
    with open(template_path, 'r', encoding='utf-8') as f:
        template_xml = f.read()
except FileNotFoundError:
    st.error(text["error_no_template"])
    st.stop()

# 파일 업로드 UI
uploaded_files = st.file_uploader(text["upload"], type=['fst'], accept_multiple_files=True)

# 결과 처리 및 다운로드 버튼
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

# --- 화면 맨 아래 크레딧 추가 ---
st.markdown(
    """
    <br><br><br>
    <div style='text-align: center; font-size: 12px; color: #606060;'>
        @mamafosho
    </div>
    """, 
    unsafe_allow_html=True
)
