import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. SAYFA AYARLARI (Browser Sekmesi) ---
st.set_page_config(
    page_title="Soru Canavarı",
    page_icon="🦉",
    layout="wide"
)

# --- 2. API ANAHTARI KONTROLÜ ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("API Anahtarı bulunamadı! Lütfen Streamlit panelinden Secrets ayarlarını yapın.")

# Model Seçimi (Senin hesabına uygun güçlü model)
model = genai.GenerativeModel('gemini-2.0-flash')

# --- 3. HAFIZA BAŞLATMA ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

# --- 4. GELİŞMİŞ YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3426/3426653.png", width=120)
    st.title("🦉 Soru Canavarı")
    st.markdown("---")
    
    # Özelleştirme Seçenekleri
    st.subheader("⚙️ Soru Ayarları")
    ders = st.selectbox("Ders Seç:", ["Matematik", "Geometri", "Fizik", "Kimya", "Biyoloji", "Türkçe/Paragraf", "Diğer"])
    seviye = st.selectbox("Seviye:", ["LGS (8. Sınıf)", "TYT (9-10. Sınıf)", "AYT (11-12. Sınıf)", "Üniversite"])
    
    st.markdown("---")
    st.write("📸 **Sorunu Yükle:**")
    uploaded_file = st.file_uploader("Görsel Seç (JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    # Temizle Butonu
    if st.button("🧹 Yeni Soru / Temizle", type="primary"):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.rerun()

# --- 5. ANA EKRAN TASARIMI ---
st.markdown(f"""
## 🎓 {ders} Çözüm Asistanı ({seviye})
**Hoş geldin!** Yapay zeka, senin seçtiğin **{seviye}** seviyesine uygun olarak anlatım yapacak.
""")

# Görsel yüklendi mi?
if uploaded_file:
    # Görseli ortada değil, sütun yapısında şık gösterelim
    col1, col2 = st.columns([1, 2])
    
    with col1:
        image = Image.open(uploaded_file)
        st.image(image, caption="Senin Sorun", use_column_width=True)
        
    with col2:
        # SOHBET MANTIĞI
        if not st.session_state.chat_session:
            with st.spinner(f"🦉 {ders} öğretmeni soruyu inceliyor..."):
                
                # GELİŞMİŞ PROMPT (Seçilen ders ve seviyeyi kullanır)
                baslangic_komutu = f"""
                Sen dünyanın en iyi {ders} öğretmenisin. Karşındaki öğrenci {seviye} düzeyinde.
                Görevin bu görseldeki soruyu analiz edip çözmek.
                
                Kurallar:
                1. Asla sadece cevabı verme. Konuyu kısaca özetle.
                2. {seviye} seviyesine uygun bir dil kullan (Çok karmaşık terimlere boğma).
                3. Matematiksel işlemleri LaTeX formatında yaz.
                4. Sonunda mutlaka motive edici bir söz söyle.
                """
                
                st.session_state.chat_session = model.start_chat(
                    history=[
                        {"role": "user", "parts": [baslangic_komutu, image]}
                    ]
                )
                
                response = st.session_state.chat_session.send_message("Çözümü yap.")
                st.session_state.messages.append({"role": "assistant", "content": response.text})

        # Sohbet Geçmişini Yazdır (Özel İkonlarla)
        for message in st.session_state.messages:
            role = message["role"]
            # Kullanıcıysa Öğrenci ikonu, Asistansa Baykuş ikonu
            avatar = "🧑‍🎓" if role == "user" else "🦉"
            
            with st.chat_message(role, avatar=avatar):
                st.markdown(message["content"])

        # Yeni Soru Girişi
        if prompt := st.chat_input("Anlamadığın yeri sor..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="🧑‍🎓"):
                st.markdown(prompt)

            with st.chat_message("assistant", avatar="🦉"):
                with st.spinner("Düşünüyor..."):
                    response = st.session_state.chat_session.send_message(prompt)
                    st.markdown(response.text)
            
            st.session_state.messages.append({"role": "assistant", "content": response.text})

else:
    # Görsel yoksa boş ekranda güzel bir karşılama
    st.info("👈 Başlamak için sol menüden dersini seç ve sorunun fotoğrafını yükle!")
    st.markdown("""
    ### Neleri Çözebilirim?
    * 📐 **Geometri:** Üçgenler, Çemberler...
    * 🧮 **Matematik:** Problemler, İntegral...
    * 🧬 **Fen Bilimleri:** Fizik kuvvetler, Kimyasal tepkimeler...
    * 📝 **Paragraf:** Uzun Türkçe soruları.
    """)
