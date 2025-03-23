import streamlit as st
import requests
import io

# Backend API Adresi (Sunucu farklıysa değiştirin)
API_URL = "http://127.0.0.1:8000"

# Streamlit Uygulama Arayüzü
st.set_page_config(page_title="Türkçe Ses ve Metin Özetleyici", page_icon="🎙️", layout="centered")
st.title("🎙️ Türkçe Ses ve Metin Özetleyici")

# 📌 Kenar Çubuğu - Menü
st.sidebar.header("⚡ İşlem Seçin:")
option = st.sidebar.radio(
    "Ne yapmak istiyorsunuz?",
    ("📜 Metin Özetle", "🎤 Ses Kaydını Yazıya Döktür", "🎙️ Ses Kaydını Yazıya Döktür ve Özetle"),
)

st.sidebar.title("ℹ️ Hakkında")
st.sidebar.info(
    """
    **Türkçe Ses ve Metin Özetleyici** aşağıdaki işlemleri yapmanıza olanak tanır:
    - 🎙️ **Ses Kaydını Yazıya Döktürme**: Ses dosyasını yazıya çevirir.
    - ✍️ **Metin Özetleme**: Uzun bir metni anahtar noktaları içerecek şekilde özetler.
    - 🔄 **Ses Kaydını Yazıya Döktürme ve Özetleme**: Konuşmayı yazıya çevirir ve ardından metni özetler.
    """
)

# 📜 Metin Özetleme Bölümü
if option == "📜 Metin Özetle":
    st.subheader("📜 Türkçe Metni Özetleyin")
    text_input = st.text_area("Metninizi buraya yapıştırın:")
    
    if st.button("Özetle"):
        if len(text_input.split()) < 10:
            st.error("⚠️ Metin çok kısa! Özetleme için en az 10 kelime gereklidir.")
        else:
            with st.spinner("Özetleniyor... ⏳"):
                response = requests.post(f"{API_URL}/summarize/", data={"text": text_input})
                result = response.json()
                st.subheader("📝 Özet:")
                st.write(result.get("summary", "❌ Hata oluştu!"))

# 🎤 Ses Kaydını Yazıya Döktürme Bölümü
elif option == "🎤 Ses Kaydını Yazıya Döktür":
    st.subheader("🎤 Ses Kaydınızı Yükleyin veya Kaydedin")
    audio_file = st.audio_input("Ses kaydınızı yükleyin veya kaydedin:")

    if audio_file:
      
        
        if st.button("Yazıya Döktür"):
            with st.spinner("Ses yazıya çevriliyor... ⏳"):
                files = {"file": audio_file}
                response = requests.post(f"{API_URL}/transcribe/", files=files)
                result = response.json()
                st.subheader("📄 Yazıya Dökmek İçin Çıktı:")
                st.write(result.get("transcription", "❌ Hata oluştu!"))

# 🎙️ Ses Kaydını Yazıya Döktürme ve Özetleme Bölümü
elif option == "🎙️ Ses Kaydını Yazıya Döktür ve Özetle":
    st.subheader("🎙️ Ses Kaydınızı Yükleyin veya Kaydedin")
    audio_file = st.audio_input("Ses kaydınızı yükleyin veya kaydedin:")

    if audio_file:
        

        if st.button("Yazıya Döktür ve Özetle"):
            with st.spinner("İşleniyor... ⏳"):
                files = {"file": audio_file}
                response = requests.post(f"{API_URL}/transcribe-and-summarize/", files=files)
                result = response.json()
                
                st.subheader("📄 Yazıya Döktürme Sonucu:")
                st.write(result.get("transcription", "❌ Hata oluştu!"))
                
                st.subheader("📝 Özet:")
                st.write(result.get("summary", "❌ Hata oluştu!"))
