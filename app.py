import streamlit as st
import gzip
import os

# --- 웹 UI 기본 설정 ---
st.set_page_config(page_title="FST to ADG Converter", page_icon="🎵")

# 1. 언어 상태(세션) 초기화: 처음 접속 시에만 브라우저 언어를 감지해서 기본값 설정
if 'lang' not in st.session_state:
    headers = st.context.headers
    accept_language = headers.get("Accept-Language", "en")
    
    if "ko" in accept_language.lower():
        st.session_state.lang = "KOR"
    else:
        st.session_state.lang = "ENG"

# 2. 우측 상단 언어 토글 버튼 만들기 (화면을 8:2 비율로 쪼개서 오른쪽에 배치)
col1, col2 = st.columns([8, 2])
with col2:
    # 현재 한국어면 'ENG' 버튼을, 영어면 'KOR' 버튼을 띄워줍니다.
    if st.session_state.lang == "KOR":
        if st.button("🌐 ENG"):
            st.session_state.lang = "ENG"
            st.rerun() # 버튼을 누르면 화면을 즉시 새로고침하여 언어를 바꿈
    else:
        if st.button("🌐 KOR"):
            st.session_state.lang = "KOR"
            st.rerun()

# 3. 선택된 언어에 따라 텍스트 분기 처리
if st.session_state.lang == "KOR":
    text = {
        "title": "ShaperBox 3 프리셋 변환기",
        "desc": "FL Studio의 .fst 프리셋을 Ableton Live의 .adg 포맷으로 변환합니다.",
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
st.write(text["desc"])

template_path = 'template.xml'
try:
    with open(template_path, 'r', encoding='utf-8') as f:
        template_xml = f.read()
except FileNotFoundError:
    st.error(text["error_no_template"])
    st.stop()

uploaded_files = st.file_uploader(text["upload"], type=['fst'], accept_multiple_files=True)

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
