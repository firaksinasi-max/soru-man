import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. AYARLAR ---
st.set_page_config(
    page_title="SoruMan",
    page_icon="🎓",
    layout="wide"
)

# API Anahtarını buraya yapıştır
# Anahtarı gizli kasadan (secrets) çekeceğiz
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("API Anahtarı bulunamadı! Lütfen Secrets ayarlarını kontrol et.")

# Model (Senin hesabına uygun olan 2.0 Flash)
model = genai.GenerativeModel('gemini-2.0-flash')

# --- 2. HAFIZA SİSTEMİ (SESSION STATE) ---
# Eğer sohbet geçmişi yoksa oluştur
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

# --- 3. YAN MENÜ (SIDEBAR) TASARIMI ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712009.png", width=100)
    st.title("🎓 İbrahim Emre Şaşmaz Hoca")
    st.info("Sorunun fotoğrafını yükle, önce çözümü al, sonra anlamadığın yerleri sor.")
    
    # Dosya yükleyiciyi buraya aldık
    uploaded_file = st.file_uploader("Soru Görselini Yükle", type=["jpg", "jpeg", "png"])
    
    # Temizle butonu
    if st.button("Yeni Soru Sor"):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.rerun()

# --- 4. ANA EKRAN VE SOHBET MANTIĞI ---

st.header("🤖 YKS & LGS Soru Çözüm Asistanı")

# Görsel yüklendiyse işlemleri başlat
if uploaded_file:
    image = Image.open(uploaded_file)
    st.sidebar.image(image, caption="Yüklenen Soru")

    # Eğer bu görsel için henüz sohbet başlatılmadıysa
    if not st.session_state.chat_session:
        with st.spinner("Öğretmen soruyu inceliyor..."):
            # Sohbeti başlat (Görseli ilk mesaja ekle)
            st.session_state.chat_session = model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": [
                            "Sen uzman bir YKS/LGS öğretmenisin. Bu görseldeki soruyu adım adım, anlaşılır bir dille çöz. LaTeX kullan.",
                            image
                        ],
                    }
                ]
            )
            
            # İlk cevabı al
            response = st.session_state.chat_session.send_message("Çözümü yap.")
            
            # Cevabı geçmişe kaydet
            st.session_state.messages.append({"role": "assistant", "content": response.text})

    # --- SOHBET GEÇMİŞİNİ EKRANA YAZDIR ---
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- KULLANICIDAN YENİ SORU AL (INPUT) ---
    if prompt := st.chat_input("Anlamadığın yeri sor (Örn: 2. adım neden öyle oldu?)"):
        # 1. Kullanıcının sorusunu ekrana bas
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Gemini'ye soruyu gönder (Hafızayı kullanır)
        with st.chat_message("assistant"):
            with st.spinner("Düşünüyor..."):
                response = st.session_state.chat_session.send_message(prompt)
                st.markdown(response.text)
        
        # 3. Cevabı geçmişe kaydet
        st.session_state.messages.append({"role": "assistant", "content": response.text})

else:
    # Görsel yoksa karşılama ekranı

    st.info("👈 Başlamak için sol menüden bir soru fotoğrafı yükle.")

