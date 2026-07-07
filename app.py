import streamlit as st
import gzip
import os

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

# --- 웹 UI 구성 ---
st.set_page_config(page_title="FST to ADG Converter", page_icon="🎵")

st.title("ShaperBox 3 프리셋 변환기")
st.write("FL Studio의 .fst 프리셋을 Ableton Live의 .adg 포맷으로 변환합니다.")

# 1. 템플릿 파일 읽어두기
template_path = 'template.xml'
try:
    with open(template_path, 'r', encoding='utf-8') as f:
        template_xml = f.read()
except FileNotFoundError:
    st.error("서버에 template.xml 파일이 없습니다. 개발자에게 문의하세요.")
    st.stop()

# 2. 파일 업로드 UI
uploaded_files = st.file_uploader(".fst 파일들을 선택하거나 드래그 앤 드롭하세요", type=['fst'], accept_multiple_files=True)

if uploaded_files:
    st.write("### 변환 결과")
    
    for uploaded_file in uploaded_files:
        # 업로드된 파일의 바이너리 데이터 읽기
        fst_bytes = uploaded_file.read()
        
        # 데이터 변환
        final_xml = process_fst_data(fst_bytes, template_xml)
        
        if final_xml:
            # Gzip 압축 (메모리 상에서 처리)
            compressed_data = gzip.compress(final_xml.encode('utf-8'))
            
            # 원본 이름 추출 및 새 이름 생성
            base_name = os.path.splitext(uploaded_file.name)[0]
            adg_filename = f"{base_name}.adg"
            
            # 다운로드 버튼 생성
            st.download_button(
                label=f"⬇️ {adg_filename} 다운로드",
                data=compressed_data,
                file_name=adg_filename,
                mime="application/gzip"
            )
        else:
            st.warning(f"'{uploaded_file.name}' 파일에서 VST 데이터를 찾을 수 없습니다.")