import streamlit as st
import gzip
import os

st.set_page_config(page_title="FST to ADG Converter", page_icon="🎵", layout="centered")

if 'lang' not in st.session_state:
    headers = st.context.headers
    accept_language = headers.get("Accept-Language", "en")
    
    if "ko" in accept_language.lower():
        st.session_state.lang = "KOR"
    else:
        st.session_state.lang = "ENG"

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

if st.session_state.lang == "KOR":
    text = {
        "title": "ShaperBox 3 프리셋 변환기",
        "desc": "FL Studio의 .fst 프리셋을 Ableton Live의 .adg 포맷으로 변환합니다.",
        "warn": "⚠️ 주의: 변환하려는 .fst 파일(이펙트 체인) 내에 ShaperBox 3 외에 다른 플러그인이 함께 포함되어 있는 경우, 변환이 정상적으로 작동하지 않습니다. 반드시 ShaperBox 3 하나만 단독으로 로드된 프리셋을 사용해 주세요.",
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
        "warn": "⚠️ Note: If the .fst file contains any other plugins in the chain besides ShaperBox 3, the conversion will not work properly. Please ensure that the preset only has a single instance of ShaperBox 3 loaded.",
        "upload": "Drag and drop or select .fst files",
        "result": "### Conversion Results",
        "download": "⬇️ Download {filename}",
        "error_no_vst": "Could not find VST data in '{filename}'.",
        "error_no_template": "template.xml not found on the server. Contact the developer."
    }

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

st.title(text["title"])

st.markdown(f"<span style='font-size: 16px; color: #A0A0A0;'>{text['desc']}</span>", unsafe_allow_html=True)
st.write("")

st.markdown(
    f"""
    <div style='
        font-size: 14px; 
        color: #FF4B4B; 
        background-color: rgba(255, 75, 75, 0.1); 
        padding: 12px; 
        border-radius: 8px; 
        line-height: 1.6;
    '>
        {text['warn']}
    </div>
    """, 
    unsafe_allow_html=True
)
st.write("")

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

st.markdown(
    """
    <br><br><br>
    <div style='text-align: center; font-size: 12px; color: #606060;'>
        @mamafosho
    </div>
    """, 
    unsafe_allow_html=True
)
