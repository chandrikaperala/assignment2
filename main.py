import streamlit as st
import moviepy.editor as mp
import speech_recognition as sr
import re

# Function to extract audio from video
def extract_audio_from_video(video_file):
    # Your existing code for audio extraction goes here
    try:
        # Write the uploaded video file to a temporary location
        with open("temp_video.mp4", "wb") as f:
            f.write(video_file.read())

        # Load the video file and extract audio
        video = mp.VideoFileClip("temp_video.mp4")
        audio = video.audio

        # Save the audio to a temporary WAV file
        audio_file_path = "temp_audio.wav"
        audio.write_audiofile(audio_file_path)

        return audio_file_path
    except Exception as e:
        st.error(f"Error extracting audio: {e}")
        return None
# Function to transcribe audio to text
def transcribe_audio(audio_file_path):
    # Your existing code for audio transcription goes here
    try:
        # Initialize the recognizer
        recognizer = sr.Recognizer()

        # Load audio file
        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source)

        # Perform speech recognition
        text = recognizer.recognize_google(audio_data)

        return text
    except sr.RequestError as e:
        st.error(f"Speech recognition request failed: {e}")
        return None
    except sr.UnknownValueError:
        st.error("Could not understand audio")
        return None
    except Exception as e:
        st.error(f"An error occurred during transcription: {e}")
        return None
# Function to save text to a file
def save_text_to_file(text, output_file_path):
    try:
        # Write text to a text file
        with open(output_file_path, "w") as text_file:
            text_file.write(text)
    except Exception as e:
        st.error(f"Error saving text to file: {e}")

# Function to preprocess query
def preprocess_query(query):
    """Preprocess the query to focus on the main word."""
    # Add more patterns if needed
    unnecessary_words = ["what","is", "means", "meant by"]
    cleaned_query = query.lower()
    for word in unnecessary_words:
        cleaned_query = cleaned_query.replace(word, "")
    return cleaned_query.strip()

# Function to extract text from .txt documents
def extract_text_from_txt(uploaded_file):
    """Extract text from an uploaded .txt file."""
    return uploaded_file.getvalue().decode('utf-8')

# Function to perform keyword matching
def keyword_matching(query, document):
    """Perform keyword matching to find relevant parts of the document."""
    sentences = re.split(r' *[\.\?!][\'" \)\]]* *', document)
    relevant_sentences = []
    for sentence in sentences:
        if re.search(r'\b{}\b'.format(query.lower()), sentence.lower()):
            relevant_sentences.append(sentence)
    return ' '.join(relevant_sentences)

# Main function
def main():
    st.title("Video Audio to Text Converter")

    # Upload video file
    video_file = st.file_uploader("Upload a video file", type=["mp4"])

    if video_file is not None:
        st.video(video_file)

        if st.button("Extract Audio and Convert to Text"):
            with st.spinner("Processing..."):
                # Extract audio from video
                st.write("Extracting audio from the video...")
                audio_file_path = extract_audio_from_video(video_file)

                if audio_file_path is not None:
                    # Transcribe audio to text
                    st.write("Transcribing audio to text...")
                    text = transcribe_audio(audio_file_path)

                    if text is not None:
                        # Save text to file
                        output_file_path = "extracted_text.txt"
                        save_text_to_file(text, output_file_path)

                        st.success("Text extraction complete!")
                        st.download_button(label="Download Text File", data=open(output_file_path, "rb"), file_name="extracted_text.txt")

    # Sidebar for uploading .txt documents
    st.sidebar.title("Upload .txt Document")
    txt_file = st.sidebar.file_uploader("Upload .txt document")

    if txt_file is not None:
        # Process uploaded .txt document
        text = extract_text_from_txt(txt_file)

        # Main content for document retrieval
        st.header("Enter your query")
        query = st.text_input("")

        if st.button("Search") and query:
            # Preprocess the query
            cleaned_query = preprocess_query(query)

            # Perform keyword matching
            matching_text = keyword_matching(cleaned_query, text)

            if matching_text:
                st.subheader("Relevant part(s) of the document:")
                st.write(matching_text)  # Display the relevant text
            else:
                st.write("No relevant information found in the document.")

if __name__ == "__main__":
    main()
